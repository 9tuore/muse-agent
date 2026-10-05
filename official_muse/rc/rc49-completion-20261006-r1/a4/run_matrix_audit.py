#!/usr/bin/env python3
"""Run the existing bounded matrix unchanged, audit errors, quit our test port."""
import argparse
import hashlib
import json
import re
import socket
import subprocess
import sys
import time
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote

ERROR = re.compile(r'\[E\]|budget exceeded|source preparation failed|no root view|'
                   r'compil(?:e|ation|ing)[^\n]*(?:fail|error)|failed[^\n]*compil|'
                   r'parse error|syntax error|unexpected token|编译失败|语法错误', re.I)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    assert args.port == 8492, 'This wrapper owns only port 8492'
    runner = ROOT / 'official_muse/rc/startup/run_shell_matrix.py'
    runner_hash = hashlib.sha256(runner.read_bytes()).hexdigest()
    command = [sys.executable, str(runner), '--candidate', str(args.candidate),
               '--out', str(args.out), '--port', str(args.port), '--cold-count', '10',
               '--reopen-count', '5', '--restart-count', '0', '--compact-evidence']
    result = subprocess.run(command)
    report = json.loads((args.out / 'report.json').read_text())
    audit = {'runner_sha256': runner_hash, 'runner_exit_code': result.returncode,
             'original_report': 'report.json', 'cases': [],
             'budget': 'Host and policy unchanged; legacy report.wall_budget_ms=64 not independently audited',
             'scope': '10 new Shell processes and 5 app reopens, synthetic state, no submissions or OS restart'}
    cold_pids = []
    owned_pids = set()
    for mode in ('cold', 'reopen'):
        for run in report[mode]:
            directory = args.out / f"{mode}-{run['index']:02d}"
            findings = []
            log = directory / 'log.json'
            if log.exists():
                lines = json.loads(log.read_text())['l']
                findings += [line for line in lines if ERROR.search(line)]
                for line in lines:
                    match = re.search(r'listening on 127\.0\.0\.1:8492 pid=(\d+)', line)
                    if match:
                        owned_pids.add(int(match[1]))
            else:
                findings.append('Missing log evidence')
            snapshot = directory / 'snap.json'
            if snapshot.exists():
                findings += [w['t'] for w in json.loads(snapshot.read_text())['s']
                             if w.get('ty') == 'Label' and isinstance(w.get('t'), str) and ERROR.search(w['t'])]
            else:
                findings.append('Missing snapshot evidence')
            launch = directory / 'launch.txt'
            if launch.exists():
                findings += [line for line in launch.read_text().splitlines() if ERROR.search(line)]
            if mode == 'cold' and 'pid' in run:
                if run['pid'] in cold_pids:
                    findings.append('Cold launch reused an earlier Shell PID')
                cold_pids.append(run['pid'])
                owned_pids.add(run['pid'])
            if mode == 'reopen' and 'pid' in run and cold_pids and run['pid'] != cold_pids[-1]:
                findings.append('App reopen did not preserve the final cold Shell PID')
            audit['cases'].append({'mode': mode, 'index': run['index'], 'original_pass': run['pass'],
                                   'pass': run['pass'] and not findings, 'error_findings': findings})
    audit['runner_unchanged'] = hashlib.sha256(runner.read_bytes()).hexdigest() == runner_hash
    remote = Remote(args.port)
    try:
        pid = json.loads(remote.request('/s'))['pid']
        # This process was launched by the exact matrix candidate on our fixed port.
        assert pid in owned_pids, 'Refusing to quit an unrecorded process'
        try:
            urlopen(remote.base + '/quit', timeout=5).read()
        except HTTPError as error:
            if error.code != 404:
                raise
        except URLError as error:
            if not isinstance(error.reason, ConnectionRefusedError):
                raise
        except RemoteDisconnected:
            pass
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            with socket.socket() as probe:
                probe.settimeout(.3)
                port_open = probe.connect_ex(('127.0.0.1', args.port)) == 0
            if not port_open:
                audit['cleanup'] = {'pid': pid, 'remote_port_released': True}
                break
            time.sleep(.1)
        else:
            audit['cleanup'] = {'pid': pid, 'remote_port_released': False}
    except Exception as error:
        audit['cleanup'] = {'error': str(error)}
    audit['cold_pass'] = sum(c['pass'] for c in audit['cases'] if c['mode'] == 'cold')
    audit['reopen_pass'] = sum(c['pass'] for c in audit['cases'] if c['mode'] == 'reopen')
    audit['pass'] = (result.returncode == 0 and audit['runner_unchanged']
                     and audit['cold_pass'] == 10 and audit['reopen_pass'] == 5
                     and audit['cleanup'].get('remote_port_released', False))
    (args.out / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(audit, ensure_ascii=False), flush=True)
    raise SystemExit(0 if audit['pass'] else 1)


if __name__ == '__main__':
    main()
