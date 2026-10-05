#!/usr/bin/env python3
"""Open the approved real Shell with one private candidate profile.

The explicit core directory keeps provider settings in that same clone.
An optional local observation relay forwards to the existing free model.
"""
import argparse
import hashlib
import json
import socket
from pathlib import Path
import subprocess
import sys
import time
from http.client import RemoteDisconnected
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote

APP = Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/muse-calendar-test/OctoSense Muse 中文版 0.2.10-r2.app')
ANCHOR = '3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--port', type=int, default=8411)
    p.add_argument('--model-port', type=int)
    p.add_argument('--restart', action='store_true')
    a = p.parse_args()
    candidate = a.candidate.resolve()
    assert candidate.is_relative_to(ROOT / 'official_muse/app/build/ui-memory-20261003')
    assert 8402 <= a.port <= 8499, 'The user stable Shell on 8401 is protected'
    record = json.loads((candidate / 'candidate.json').read_text())
    app = Path(record.get('host_app_path', str(APP)))
    binary = app / 'Contents/MacOS/octosense'
    assert binary.is_file(), 'Candidate test Host is missing'
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == record['host_sha256'], 'Test Host differs from candidate inventory'
    private = Path(record.get('runtime_private_path', str(candidate / 'private'))).resolve()
    assert private.is_relative_to(ROOT / 'official_muse/app/build/ui-memory-20261003')
    installed = private / 'apps/muse-goals/bundle/main.splash'
    assert hashlib.sha256(installed.read_bytes()).hexdigest() == record['source_sha256']
    core = private / 'home/octos-home/.octos'
    profile = core / 'profiles/_main.json'
    assert profile.is_file()
    if a.model_port is not None:
        assert 1024 <= a.model_port <= 65535
        data = json.loads(profile.read_text())
        primary = data['config']['llm']['primary']
        assert primary['family_id'] == 'local' and primary['model_id'] == 'local-default'
        primary['route']['base_url'] = f'http://127.0.0.1:{a.model_port}/v1'
        profile.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
        profile.chmod(0o600)
    r = Remote(a.port)
    def port_open():
        with socket.socket() as probe:
            probe.settimeout(.3)
            return probe.connect_ex(('127.0.0.1',a.port)) == 0
    if a.restart:
        try:
            urlopen(r.base+'/quit', timeout=5).read()
        except HTTPError as error:
            # A delivered remote action can return 404 while awaiting a frame.
            # It is safe to proceed only after independently observing shutdown.
            if error.code != 404: raise
        except URLError as error:
            # A previous failed test may already have shut this port down.
            if not isinstance(error.reason,ConnectionRefusedError): raise
        except RemoteDisconnected:
            # Quit may close its connection before replying; still require
            # independent port shutdown below before launching a new process.
            pass
        for _ in range(100):
            if not port_open(): break
            time.sleep(.1)
        else:
            raise RuntimeError('Previous candidate Shell is still running')
    elif port_open():
        raise RuntimeError('Remote port is occupied; use explicit restart for this candidate')
    cmd = ['open', '-n']
    values = {'OCTOSENSE_HOME': private / 'home', 'OCTOSENSE_APP_DATA': private / 'apps',
              'OCTOS_APP_CORE_DIR': core, 'OCTOSENSE_HUB': candidate / 'mirror',
              'OCTOSENSE_HUB_ANCHOR': ANCHOR, 'MAKEPAD_REMOTE': a.port,
              'MAKEPAD_APP_CONFIG': '{}'}
    for key, value in values.items():
        cmd += ['--env', f'{key}={value}']
    cmd += [str(app), '--args', '--test-action', 'launch-apphub']
    subprocess.run(cmd, check=True)
    for _ in range(120):
        try:
            r.find('已安装')
            print(json.dumps({'ready': True, 'port': a.port, 'version': record['version'],
                              'source_sha256': record['source_sha256'], 'isolated_core': True}))
            return
        except (AssertionError, OSError):
            time.sleep(.25)
    raise RuntimeError('App Hub did not become ready')


if __name__ == '__main__':
    main()
