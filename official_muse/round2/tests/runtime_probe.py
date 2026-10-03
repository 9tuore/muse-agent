#!/usr/bin/env python3
"""Execute production Splash functions in a real card-host with queued synthetic Host responses.
Only the Host transport, render function and root widgets are substituted. No external service.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
HOST = Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/release/card-host')


def replace_function(text, name, replacement):
    start = text.index('fn ' + name + '(')
    brace = text.index('{', start)
    depth, quoted, escaped = 1, False, False
    pos = brace + 1
    while depth:
        c = text[pos]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '{': depth += 1
        elif c == '}': depth -= 1
        pos += 1
    return text[:start] + replacement + text[pos:]


TRANSPORT = '''
let fixture_queue = []
let fixture_calls = []
let fixture_events = []
let fixture_writes = 0
let fixture_calendar_writable = true
fn fixture_request(service,payload,callback){
    fixture_calls.push({service: service payload: payload})
    if service == "model.complete" { fixture_queue.push(callback) return }
    if service == "calendar.status" {
        callback({is_ok: true data: {permission: "full_access" calendars: [{id: "fixture-calendar" writable: fixture_calendar_writable}]}})
        return
    }
    if service == "calendar.list" {
        callback({is_ok: true data: {events: fixture_events truncated: false}})
        return
    }
    if service == "calendar.get" {
        callback({is_ok: true data: {event: {id: "fixture-event" calendar_id: "fixture-calendar" version: "fixture-v2"}}})
        return
    }
    fixture_writes = fixture_writes + 1
}
fn fixture_seed(){
    core_boot_goals()
    core_boot_activity()
    core_boot_memory()
    calendar_permission = "full_access"
    calendar_calendars = [{id: "fixture-calendar" writable: true}]
    calendar_calendar_id = "fixture-calendar"
    ui.calendar_title.set_text("MUSE-R2-SYNTHETIC")
    ui.calendar_start.set_text("2026-10-04T15:00:00+08:00")
    ui.calendar_end.set_text("2026-10-04T16:00:00+08:00")
    ui.calendar_timezone.set_text("Asia/Shanghai")
    ui.calendar_location.set_text("synthetic")
}
'''
WIDGET = '''
View{width: Fill height: Fill flow: Down
    calendar_title := TextInput{width: Fill}
    calendar_start := TextInput{width: Fill}
    calendar_end := TextInput{width: Fill}
    calendar_timezone := TextInput{width: Fill}
    calendar_location := TextInput{width: Fill}
    calendar_delete_id := TextInput{width: Fill}
    calendar_actions := View{width: Fill height: Fit on_render: || {}}
    goal_input := TextInput{width: Fill}
    source_input := TextInput{width: Fill}
    Label{text: "Muse 第二轮合成运行探针"}
}
'''


def run(name, output, port, source_path=None):
    text = (source_path or ROOT / 'official_muse/app/bundle/main.splash').read_text()
    prefix = text[:text.index('start_timeout(0.05, || boot())')]
    prefix = prefix.replace('host.request(', 'fixture_request(')
    prefix = replace_function(prefix, 'redraw', 'fn redraw(){}')
    prefix = replace_function(prefix, 'set_page', 'fn set_page(next){ page = next }')
    prefix = replace_function(prefix, 'calendar_enabled', 'fn calendar_enabled(){ return true }')
    if name == 'incoming_suite':
        prefix = prefix.replace('fixture_request(', 'incoming_fixture_request(')
        prefix = replace_function(prefix, 'mail_enabled', 'fn mail_enabled(){ return true }')
        prefix = replace_function(prefix, 'mail_watch_refresh', 'fn mail_watch_refresh(){}')
        prefix = replace_function(prefix, 'mail_redraw', 'fn mail_redraw(){ mail_watch_draft_status() }')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    bundle, state = output / 'bundle', output / 'state'
    shutil.copytree(ROOT / 'official_muse/app/bundle', bundle, dirs_exist_ok=True)
    probe = (Path(__file__).parent / (name + '.splash')).read_text()
    widget = WIDGET
    if name == 'incoming_suite':
        widget = widget.replace('    Label{text:', '''    mail_to := TextInput{width: Fill}
    mail_subject := TextInput{width: Fill}
    mail_body := TextInput{width: Fill}
    mail_intent := TextInput{width: Fill}
    Label{text:''', 1)
    (bundle / 'main.splash').write_text(prefix + TRANSPORT + probe + widget)
    env = dict(os.environ, MAKEPAD_REMOTE=str(port))
    with (output / 'runtime.log').open('w') as log:
        # Match the verified harness launch: compiled resources resolve from
        # the host workspace, and synthetic probes need no visual window.
        env['MAKEPAD_HIDE_WINDOWS'] = '1'
        env.pop('MAKEPAD_FOCUS', None)
        proc = subprocess.Popen([str(HOST), '--bundle', str(bundle), '--app-data', str(state),
                                 '--allow-unsigned', '--stamp', '--size', '600x700'],
                                env=env, cwd=HOST.parents[2], stdout=log, stderr=log)
        try:
            report = state / 'muse-goals/probe.json'
            deadline = time.monotonic() + 25
            while not report.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError((output / 'runtime.log').read_text()[-6000:])
                time.sleep(.2)
            result = json.loads(report.read_text())
            result['source_sha256'] = hashlib.sha256(text.encode()).hexdigest()
            result['transport'] = 'synthetic queued responses, real card-host and production Splash functions'
            (output / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps({k: v for k, v in result.items() if k not in {'activity', 'model_requests', 'resumed_context'}}, ensure_ascii=False, indent=2))
            if name.endswith('_suite'):
                assert all(v is True for k, v in result.items() if k not in {'activity', 'source_sha256', 'transport'}), result
            return result
        finally:
            try: urlopen(f'http://127.0.0.1:{port}/quit', timeout=2).read()
            except Exception: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8471)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    run(args.name, args.output, args.port,args.source)
