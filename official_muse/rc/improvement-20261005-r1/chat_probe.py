#!/usr/bin/env python3
"""One real UI chat turn, with durable response evidence and no action replay."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import shot


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    r = Remote(args.port)
    sessions = read(args.data / 'chat-sessions.json')
    session_id = sessions['selected_id']
    current = next(s for s in sessions['sessions'] if s['id'] == session_id)
    count = len(current['messages'])
    r.set_text('goal_input', args.input)
    button = r.find('send_button')
    x, y, width, height = button['r']
    assert button['ty'] == 'Button' and width > 2 and height >= 24
    intent = {'input': args.input, 'session_id': session_id, 'before_count': count,
              'single_dispatch': True, 'button_rect': button['r'],
              'started_at': time.time(), 'source_sha256': hashlib.sha256(
                  (ROOT / 'official_muse/app/source/main.splash').read_bytes()).hexdigest()}
    (args.output / 'intent.json').write_text(json.dumps(intent, ensure_ascii=False, indent=2))
    dispatch_error = None
    try:
        r.request('/click', x=int(x + width / 2), y=int(y + height / 2))
    except Exception as error:
        dispatch_error = str(error)  # Observe durable state; never resend a timeout.
    deadline = time.monotonic() + 45
    added = []
    while time.monotonic() < deadline:
        sessions = read(args.data / 'chat-sessions.json')
        current = next(s for s in sessions['sessions'] if s['id'] == session_id)
        added = current['messages'][count:]
        if len(added) >= 2 and added[-1].get('role') == 'assistant':
            break
        time.sleep(.5)
    observed = {'session_id': session_id, 'new_messages': added,
                'dispatch_error': dispatch_error, 'finished_at': time.time(),
                'response_observed': len(added) >= 2 and added[-1].get('role') == 'assistant'}
    trace = args.data / 'model-last-response.json'
    if trace.exists():
        observed['model_trace'] = read(trace)
    (args.output / 'observed.json').write_text(json.dumps(observed, ensure_ascii=False, indent=2))
    shot(r, args.output / 'after.png')
    print(json.dumps(observed, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
