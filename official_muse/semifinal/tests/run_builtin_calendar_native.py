#!/usr/bin/env python3
"""Visible, original os.calendar UI on a reference host and synthetic store.

--system applies only to the shipped os.calendar bundle, never to Muse.
This is not an installed OctoSense Shell or third-party grant test.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
from remote import Remote


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--host-cwd', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8671)
    p.add_argument('--service-report', type=Path, required=True, help='Frozen tested service identity, original or proposed patch')
    a = p.parse_args()
    out = a.out.resolve(); assert out.is_relative_to(ROOT/'build') and not out.exists()
    assert json.loads((a.bundle/'manifest.json').read_text())['id'] == 'os.calendar'
    out.mkdir(parents=True)
    with socket.socket() as s: assert s.connect_ex(('127.0.0.1',a.port)) != 0
    remote = Remote(a.port)
    state = out/'state'
    store = state/'.host/calendar/events.json'
    title = 'MUSE-PIVOT-NATIVE-20261010'
    checks = {}; process = None
    service = json.loads(a.service_report.read_text())
    host_sha = hashlib.sha256(a.host.read_bytes()).hexdigest()
    assert host_sha == service['muse-calendar-reference-host_sha256']
    report = {'kind':'VISIBLE_ORIGINAL_CALENDAR_REFERENCE_UI', 'status':'ERROR', 'checks':checks,
              'boundary':'Actual original os.calendar UI with the declared original/proposed service, synthetic store only. Not installed Shell, Muse admission or Agent/tool approval.',
              'service_source_byte_identical':service['source_byte_identical'], 'service_patch_sha256':service.get('patch_sha256'),
              'bundle_source_sha256':hashlib.sha256((a.bundle/'main.splash').read_bytes()).hexdigest(),
              'host_sha256':host_sha}

    def records():
        return json.loads(store.read_text()) if store.exists() else []

    def start(number):
        nonlocal process
        env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_FOCUS='1', OCTOSENSE_HOME=str(out/'home'),
                   OCTOSENSE_APP_DATA=str(state), MAKEPAD_APP_CONFIG='{}')
        env.pop('MAKEPAD_HIDE_WINDOWS',None)
        stream = (out/f'runtime-{number}.log').open('w')
        process = subprocess.Popen([str(a.host.resolve()),'--bundle',str(a.bundle.resolve()),'--app-data',str(state),
            '--system','--size','900x800'],cwd=a.host_cwd.resolve(),env=env,stdout=stream,stderr=stream)
        stream.close()
        deadline = time.monotonic()+35
        while True:
            try:
                remote.widgets(); break
            except OSError:
                if process.poll() is not None or time.monotonic()>deadline: raise
                time.sleep(.1)
        remote.wait_for('month_title',35)
        remote.wait_for('Your schedule, all in one place',15)

    def stop():
        nonlocal process
        if process:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            process = None

    def click(label):
        w = next(w for w in remote.widgets() if w.get('t') == label and w.get('ty') == 'Button')
        x,y,width,height = w['r']; assert width>2 and height>20
        remote.request('/click',x=int(x+width/2),y=int(y+height/2)); time.sleep(.25)

    def wait(test):
        deadline = time.monotonic()+10
        while not test():
            if time.monotonic()>deadline: raise RuntimeError('Independent state check did not settle')
            time.sleep(.1)

    def shot(name):
        # A newly swapped native pane can have no capture frame yet. This is
        # read-only; never repeat a write/confirmation to obtain a screenshot.
        for attempt in range(8):
            try:
                remote.shot(out/name); return
            except HTTPError:
                if attempt == 7: raise
                time.sleep(.25)

    try:
        start(0); shot('01-empty.png')
        checks['empty_original_calendar_visible'] = not records()
        click('+ Event')
        remote.set_text('e_title',title)
        remote.set_text('e_start','19:00'); remote.set_text('e_end','19:30')
        click('Save')
        wait(lambda: len(records()) == 1)
        event = records()[0]; event_id = event['id']
        checks['native_create_independent_read'] = event['title']==title and event['start'].endswith('T19:00')
        remote.wait_for(title,10); shot('02-created.png')
        click('View event  ›'); click('Edit')
        remote.set_text('e_start','20:00'); remote.set_text('e_end','20:30'); click('Save')
        wait(lambda: records()[0]['start'].endswith('T20:00'))
        checks['native_edit_same_id'] = len(records())==1 and records()[0]['id']==event_id
        remote.wait_for(title,10); shot('03-updated.png')
        stop(); start(1); remote.wait_for(title,10)
        checks['native_restart_restores_same_event'] = records()[0]['id']==event_id and records()[0]['start'].endswith('T20:00')
        shot('04-restored.png')
        click('View event  ›'); click('Delete event')
        checks['first_delete_click_does_not_delete'] = len(records())==1
        shot('05-delete-confirm.png')
        click('Confirm delete'); wait(lambda: records()==[])
        checks['native_delete_independent_absence'] = records()==[]
        shot('06-deleted.png')
        stop(); start(2)
        checks['native_restart_after_delete_no_replay'] = records()==[]
        errors = [line for log in out.glob('runtime-*.log') for line in log.read_text().splitlines()
                  if '[E]' in line or 'script time budget exceeded' in line]
        report['runtime_errors']=errors
        report['status']='PASS_NATIVE_CALENDAR_REFERENCE' if all(checks.values()) and not errors else 'FAIL'
    except Exception as error:
        report['error']=str(error)
        import traceback
        report['traceback']=traceback.format_exc()
    finally:
        stop()
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='PASS_NATIVE_CALENDAR_REFERENCE' else 1


if __name__=='__main__': raise SystemExit(main())
