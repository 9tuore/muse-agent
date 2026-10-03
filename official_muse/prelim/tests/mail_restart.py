#!/usr/bin/env python3
"""Actual exit/relaunch of the exact fixture bundle and isolated state."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/round2/tests'))
import runtime_probe as runtime


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--module', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8485)
    a = p.parse_args()
    script = Path(__file__).with_name('mail_run.py')
    subprocess.run([sys.executable, str(script), '--module', str(a.module), '--out', str(a.out),
        '--suite', str(script.with_name('mail_restart.splash')), '--port', str(a.port)], check=True)
    a.out = a.out.resolve()
    jail = a.out / 'state/muse-goals'
    probe = jail / 'probe.json'
    probe.rename(jail / 'probe-before-restart.json')
    watch_before = hashlib.sha256((jail / 'mail-watch.json').read_bytes()).hexdigest()
    env = dict(os.environ, MAKEPAD_REMOTE=str(a.port), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    with (a.out / 'restart-runtime.log').open('w') as log:
        proc = subprocess.Popen([str(runtime.HOST), '--bundle', str(a.out / 'bundle'),
            '--app-data', str(a.out / 'state'), '--allow-unsigned', '--stamp', '--size', '600x700'],
            env=env, cwd=runtime.HOST.parents[2], stdout=log, stderr=log)
        try:
            deadline = time.monotonic()+50
            while not probe.exists():
                if proc.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError('Restart report missing; original logs retained')
                time.sleep(.2)
            result = json.loads(probe.read_text())
            result['watch_bytes_unchanged'] = watch_before == hashlib.sha256((jail / 'mail-watch.json').read_bytes()).hexdigest()
            result.update(kind='FIXTURE_REAL_PROCESS_RESTART', module_sha256=hashlib.sha256(a.module.read_bytes()).hexdigest(),
                host_sha256=hashlib.sha256(runtime.HOST.read_bytes()).hexdigest(), real_mail=False, real_model=False)
            checks = {k: v for k, v in result.items() if isinstance(v, bool) and not k.startswith('real_')}
            result['failed'] = [k for k, v in checks.items() if not v]
            result['passed'] = len(checks)-len(result['failed'])
            (a.out / 'restart-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps(result, ensure_ascii=False))
            return int(bool(result['failed']))
        finally:
            try: urlopen(f'http://127.0.0.1:{a.port}/quit', timeout=2).read()
            except OSError: proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()


if __name__ == '__main__':
    raise SystemExit(main())
