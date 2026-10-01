#!/usr/bin/env python3
"""Run a copied packaged app with isolated state and sample idle health."""
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def process_row(pid):
    result = subprocess.run(['/bin/ps', '-o', 'pid=,ppid=,%cpu=,rss=,etime=', '-p', str(pid)],
                            text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def worker_pid(parent):
    rows = subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,command='], text=True)
    for row in rows.splitlines():
        parts = row.strip().split(maxsplit=2)
        if len(parts) == 3 and parts[1] == str(parent) and 'desktop_worker.py' in parts[2]:
            return int(parts[0])
    return None


def usage(workspace):
    path = workspace / '.muse_model_usage.json'
    if not path.exists():
        return {'used_tokens': 0, 'remote_calls': 0, 'reservations': 0}
    state = json.loads(path.read_text())
    return {'used_tokens': state.get('used_tokens', 0), 'remote_calls': state.get('remote_calls', 0),
            'reservations': len(state.get('reservations', {}))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--duration-seconds', type=int, default=3600)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    copied = out / 'Muse-Soak.app'
    shutil.copytree(args.app.resolve(strict=True), copied, symlinks=True)
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(copied)], check=True)
    workspace = out / 'workspace'
    workspace.mkdir()
    env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_LOCAL_INBOX='0',
               GOSIM_BACKGROUND_TEST='1', GOSIM_DEV_UI='0', PYTHONNOUSERSITE='1')
    lock_path = Path('/tmp/gosim-muse-5agent-20260928/gui.lock')
    lock_path.parent.mkdir(mode=0o700, exist_ok=True)
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    os.ftruncate(lock_fd, 0)
    os.write(lock_fd, (json.dumps({'resource': 'gui', 'owner': 'G-04',
                                   'purpose': 'candidate idle soak', 'pid': os.getpid()}) + '\n').encode())
    start = time.monotonic()
    samples = []
    worker = None
    result = None
    with (out / 'app.stdout').open('w') as stdout, (out / 'app.stderr').open('w') as stderr:
        proc = subprocess.Popen([str(copied / 'Contents/MacOS/GOSIM-Local-Agent')],
                                env=env, stdout=stdout, stderr=stderr)
        try:
            ready_deadline = time.monotonic() + 15
            while time.monotonic() < ready_deadline and worker is None and proc.poll() is None:
                worker = worker_pid(proc.pid)
                if worker is None:
                    time.sleep(0.25)
            if worker is None:
                raise AssertionError('owned worker did not start')
            while time.monotonic() - start < args.duration_seconds:
                worker = worker_pid(proc.pid) or worker
                sample = {'at': datetime.now(timezone.utc).isoformat(),
                          'elapsed_seconds': round(time.monotonic() - start, 1),
                          'app': process_row(proc.pid), 'worker': process_row(worker) if worker else None,
                          'usage': usage(workspace)}
                samples.append(sample)
                (out / 'samples.jsonl').write_text(''.join(json.dumps(s) + '\n' for s in samples))
                if not sample['app'] or not sample['worker']:
                    raise AssertionError('app or owned worker exited during soak')
                time.sleep(min(30, max(0, args.duration_seconds - (time.monotonic() - start))))
            assert all(item['usage']['used_tokens'] == 0 and item['usage']['remote_calls'] == 0
                       and item['usage']['reservations'] == 0 for item in samples)
            result = {'status': 'PASS_LOCAL', 'duration_seconds': round(time.monotonic() - start, 1),
                      'sample_count': len(samples), 'app_pid': proc.pid, 'worker_pid': worker,
                      'idle_model_usage': usage(workspace), 'gui_lock_held': True}
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
            deadline = time.monotonic() + 5
            while worker and process_row(worker) and time.monotonic() < deadline:
                time.sleep(0.1)
            if worker and process_row(worker):
                raise AssertionError('owned worker remained after app exit')
    if result is not None:
        subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(copied)], check=True)
        result['signature_valid_before_and_after'] = True
        result['owned_worker_cleanup'] = True
        (out / 'result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    os.ftruncate(lock_fd, 0)
    os.close(lock_fd)


if __name__ == '__main__':
    main()
