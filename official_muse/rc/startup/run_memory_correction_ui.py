#!/usr/bin/env python3
"""Verify correction, a second single Save, and restart in a running synthetic Shell.

No model requests or external actions; existing data is edited only through UI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate, type_multiline, shot


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--search', required=True)
    ap.add_argument('--value', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert a.candidate.resolve().is_relative_to(ROOT / 'official_muse/app/build/ui-memory-20261003')
    meta = json.loads((a.candidate / 'candidate.json').read_text())
    assert meta['profile_kind'] == 'AUTHORIZED_MODEL_ONLY_SYNTHETIC'
    assert not (a.candidate / 'private/apps/.host/mail').exists()
    a.out.mkdir(mode=0o700)
    jail = a.candidate / 'private/apps/muse-goals'
    ledger = a.candidate / 'private/apps/.host/model/ledger.json'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
    usage = sha(ledger)
    r = Remote(a.port)
    report = {'status': 'RUNNING', 'version': meta['version'], 'application_commit': meta['commit'],
              'source_sha256': meta['source_sha256'], 'host_sha256': meta['host_sha256'],
              'steps': [], 'model_or_external_actions': False}

    def save():
        temporary = a.out / 'report.json.pending'
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(a.out / 'report.json')

    def click(key):
        for _ in range(20):
            try:
                widget = r.find(key)
                x, y, w, h = widget['r']
                if w > 2 and h >= 24:
                    break
            except AssertionError:
                pass
            x, y, w, h = r.find('page_content')['r']
            r.scroll(int(x+w-4), int(y+h/2), 80)
        else:
            raise AssertionError('Control not reachable: ' + key)
        try:
            r.request('/click', x=int(x+w/2), y=int(y+h/2), wait=1)
        except Exception as error:
            report.setdefault('remote_errors', []).append({'control': key, 'error': repr(error), 'no_replay': True})

    def claim(mid):
        return next(x['document'] for x in json.loads((jail / 'memory.json').read_text())['claims'] if x['document']['id'] == mid)

    try:
        try:
            r.find('goal_input')
        except AssertionError:
            r.click('打开')
        r.wait_for('goal_input', 20)
        navigate(r, '记忆')
        r.set_text('memory_search', a.search)
        click('更正 / 遗忘')
        r.wait_for('memory_correction', 20)
        before = next(x['document'] for x in json.loads((jail / 'memory.json').read_text())['claims'] if a.search in x['document']['payload']['value'])
        mid = before['id']
        assert before['payload']['value'] != a.value
        type_multiline(r, 'memory_correction', a.value)
        assert r.find('memory_correction')['val'] == a.value
        click('保存更正')
        first = claim(mid)
        field = r.find('memory_correction')['val']
        report['steps'].append({'save_click': 1, 'stored': first, 'field_after_render': field})
        save()
        assert first['revision'] == before['revision'] + 1 and first['payload']['value'] == field == a.value
        shot(r, a.out / 'after-first-save.png')
        protected = ['memory.json', 'memory.backup.json', 'activity.json', 'activity.backup.json']
        first_hashes = {n: sha(jail/n) for n in protected}
        click('保存更正')
        time.sleep(.2)
        second = claim(mid)
        report['steps'].append({'save_click': 2, 'stored': second, 'field_after_render': r.find('memory_correction')['val']})
        report['after_repeat_sha256'] = {n: sha(jail/n) for n in protected}
        save()
        assert second == first and report['after_repeat_sha256'] == first_hashes and sha(ledger) == usage
        shot(r, a.out / 'after-second-save.png')
        names = protected + ['chat-sessions.json', 'chat-sessions.backup.json', 'global-memory-settings.json', 'goals.json', 'calendar-state.json', 'mail-watch.json']
        before_restart = {n: sha(jail/n) for n in names}
        pid = json.loads(r.request('/s'))['pid']
        proc = subprocess.run([sys.executable, str(ROOT/'official_muse/ui_memory/launch_candidate.py'), '--candidate', str(a.candidate), '--port', str(a.port), '--restart'], capture_output=True, text=True, timeout=45)
        (a.out / 'restart-launch.txt').write_text(proc.stdout + proc.stderr)
        assert proc.returncode == 0
        r.click('打开')
        r.wait_for('goal_input', 20)
        assert json.loads(r.request('/s'))['pid'] != pid
        after_restart = {n: sha(jail/n) for n in names}
        report.update(protected_before_restart=before_restart, protected_after_restart=after_restart, first_restart_equal=before_restart == after_restart)
        assert before_restart == after_restart and claim(mid) == first and sha(ledger) == usage
        report.update(status='PASS', duplicate_save_did_not_write=True, model_ledger_unchanged=True, computer_restart=False)
        save()
        print(json.dumps({'status': report['status'], 'version': meta['version'], 'duplicate_save_did_not_write': True, 'first_restart_equal': True}), flush=True)
    except Exception:
        report['status'] = 'FAIL'
        (a.out / 'exception.txt').write_text(traceback.format_exc())
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
