#!/usr/bin/env python3
"""Observe real model Calendar clarification without confirming external actions.

Run against an already authorized model-only synthetic candidate. A successful
proposal is checked against the user's dates; it is never a system-write proof.
Every input is submitted once, including when the remote frame wait fails.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import shot


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--date-only', action='store_true', help='Observe the related pure-date routing repair only')
    a = ap.parse_args()
    c = a.candidate.resolve(strict=True)
    meta = read(c / 'candidate.json')
    assert meta['profile_kind'] == 'AUTHORIZED_MODEL_ONLY_SYNTHETIC'
    jail = c / 'private/apps/muse-goals'
    assert not (c / 'private/apps/.host/mail').exists()
    assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
    assert sha(Path(meta['host_app_path']) / 'Contents/MacOS/octosense') == meta['host_sha256']
    assert not a.out.exists(), 'Retain original failures'
    a.out.mkdir(parents=True, mode=0o700)
    ledger = c / 'private/apps/.host/model/ledger.json'
    protected = {name: sha(jail / name) for name in ['memory.json', 'goals.json',
        'mail-watch.json', 'mail-draft.json', 'calendar-state.json']}
    r = Remote(a.port)
    report = {'status': 'RUNNING', 'version': meta['version'],
        'source_sha256': meta['source_sha256'], 'host_sha256': meta['host_sha256'],
        'source_state': meta.get('source_state', 'FROZEN'), 'steps': [],
        'usage_before': read(ledger)['apps']['muse-goals'],
        'system_calendar_write': False, 'original20_complete': False}
    last = 0

    def save():
        (a.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def current():
        d = read(jail / 'chat-sessions.json')
        return next(s for s in d['sessions'] if s['id'] == d['selected_id'])

    def submit(key, text, waiting, day_offset=None):
        nonlocal last
        gap = 13 - (time.monotonic()-last)
        if gap > 0:
            time.sleep(gap)
        before = current()
        sid, count = before['id'], len(before['messages'])
        r.set_text('goal_input', text)
        box = r.find('send_button')['r']
        error = None
        last = time.monotonic()
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date()
        try:
            r.request('/click', x=int(box[0]+box[2]/2), y=int(box[1]+box[3]/2))
        except Exception as exc:
            error = repr(exc)
        deadline = time.monotonic()+90
        while time.monotonic() < deadline:
            session = next(s for s in read(jail / 'chat-sessions.json')['sessions'] if s['id'] == sid)
            added = session['messages'][count:]
            replies = [m for m in added if m['role'] == 'assistant']
            if replies:
                break
            time.sleep(.25)
        else:
            raise AssertionError('One request timed out; no repeat submission')
        reply = replies[-1]
        row = {'step': key, 'input': text, 'reply': reply,
            'submit_remote_error': error, 'proposals': session['proposals'],
            'seconds': time.monotonic()-last,
            'usage_after': read(ledger)['apps']['muse-goals']}
        report['steps'].append(row)
        save()
        assert len([m for m in added if m['role'] == 'user']) == 1
        if waiting:
            assert reply['state'] == 'waiting_user' and not session['proposals']
            assert reply['clarification_action'] == 'calendar_candidate'
        else:
            assert reply['state'] == 'success' and len(session['proposals']) == 1
            p = session['proposals'][0]
            assert p['action'] == 'calendar_candidate'
            expected = str(today + datetime.timedelta(days=day_offset))
            assert p['payload']['start'] == expected+'T15:00:00+08:00'
            assert p['payload']['end'] == expected+'T16:00:00+08:00'
            assert p['payload']['time_zone'] == 'Asia/Shanghai'
            assert '开会' in p['payload']['title']
            row['expected_date'] = expected
        assert all(sha(jail / n) == digest for n, digest in protected.items())
        row['pass'] = True
        save()
        shot(r, a.out / (key+'.png'))
        print(json.dumps({'step': key, 'state': reply['state'], 'pass': True}), flush=True)

    save()
    try:
        if a.date_only:
            r.click('＋ 新对话')
            submit('vague_date_with_range', '安排日历：过几天开会，下午15点到16点。', True)
            date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date()+datetime.timedelta(days=2)
            submit('explicit_date_only', date.strftime('%Y年%m月%d日'), False, 2)
        else:
            assert current()['messages'][-1]['text'] == '请补充明确的开始时间、结束时间。'
            assert current()['messages'][-1]['state'] == 'waiting_user'
            submit('d05_time_only', '下午15点到16点。', False, 1)
            r.click('＋ 新对话')
            submit('vague_date', '安排日历：过几天开会，下午15点到16点。', True)
            submit('date_only', '改成后天。', False, 2)
            r.click('＋ 新对话')
            submit('tomorrow_missing_time', '安排日历：明天下午开会。', True)
            submit('correct_to_after_tomorrow', '改成后天下午15点到16点。', False, 2)
        assert all(sha(jail / n) == digest for n, digest in protected.items())
        report['status'] = 'PASS_ACTUAL_MODEL_CANDIDATES_NO_EXTERNAL_ACTION'
    except Exception:
        report['status'] = 'FAIL_RETAINED'
        (a.out / 'exception.txt').write_text(traceback.format_exc())
        raise
    finally:
        report['usage_after'] = read(ledger)['apps']['muse-goals']
        (a.out / 'snap.json').write_bytes(r.request('/snap'))
        (a.out / 'log.json').write_bytes(r.request('/log', n=400))
        save()


if __name__ == '__main__':
    main()
