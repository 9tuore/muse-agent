#!/usr/bin/env python3
"""Read-only local AI inventory. GET metadata only; never infer or start services."""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'official_muse/app/build/ui-memory-20261003/mail-host-033'
HOST = WORK / 'OctoSense'
APP = WORK / 'OctoSense Muse 0.3.3 UI-candidate.app'
OUT = ROOT / 'official_muse/prelim/evidence/ai'
ENV = dict(os.environ, LC_ALL='en_US.UTF-8', LANG='en_US.UTF-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, env=ENV)
    return result.returncode, result.stdout.strip()


def safe_url(value):
    parts = urlsplit(value)
    host = parts.hostname or ''
    if parts.port:
        host += ':' + str(parts.port)
    return urlunsplit((parts.scheme, host, parts.path, '', ''))


def main():
    report = {
        'at': datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'kind': 'SOURCE_READ_AND_LIVE_READONLY_METADATA',
        'new_runtime_started': False, 'inference_requests': 0,
        'paid_requests': 0, 'user_windows_operated': False,
    }
    report['branch'] = command(['git', '-C', str(ROOT), 'branch', '--show-current'])[1]
    report['head_at_inventory'] = command(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'])[1]
    report['host_binary_sha256'] = sha(APP / 'Contents/MacOS/octosense')
    names = ['Cargo.toml', 'Cargo.lock', 'docs/ai-services.zh-CN.md',
             'crates/ai-host/src/lib.rs', 'crates/ai-host/build.rs',
             'crates/ai-host/src/contained.rs', 'crates/app-peers/src/broker.rs',
             'crates/kernel/src/launch.rs', 'crates/shell/src/approvals/mod.rs',
             'crates/shell/src/host_tools/script_apps.rs']
    report['host_source_sha256'] = {name: sha(HOST / name) for name in names}
    manifest = json.loads((ROOT / 'official_muse/app/bundle/manifest.json').read_text())
    report['muse_at_inventory'] = {key: manifest[key] for key in ['id', 'version', 'capabilities', 'integrity']}
    report['muse_main_sha256_at_inventory'] = sha(ROOT / 'official_muse/app/bundle/main.splash')
    fingerprints = {}
    for pattern in ['octosense-*/bin-octosense.json', 'octosense-ai-host-*/lib-octosense_ai_host.json']:
        for path in (WORK / 'target/release/.fingerprint').glob(pattern):
            fingerprints[str(path.relative_to(ROOT))] = json.loads(path.read_text())['features']
    report['release_features'] = fingerprints
    report['source_links'] = {}
    for link in (HOST / '.sources').iterdir():
        if not link.is_symlink():
            continue
        target = link.resolve()
        code, head = command(['git', '-C', str(target), 'rev-parse', 'HEAD'])
        status_code, status = command(['git', '-C', str(target), 'status', '--porcelain'])
        report['source_links'][link.name] = {'path': str(target), 'git_head': head if code == 0 else None,
                                           'git_status_available': status_code == 0,
                                           'changed_entry_count': len(status.splitlines()) if status_code == 0 else None}
    checkout = Path('/Users/mima0000/.cargo/git/checkouts/octos-a74a59bdc2c07a30/c608384')
    report['cached_kernel_source'] = {'path': str(checkout), 'git_head': command(['git', '-C', str(checkout), 'rev-parse', 'HEAD'])[1]}
    candidates = [Path('/Users/mima0000/Documents/ChatGPT/Agent APP黑客松/runtime/octos-lean-target/debug/octos'),
                  Path('/Users/mima0000/.cargo/bin/octos'), checkout / 'target/release/octos',
                  HOST / 'target/octos-kernel/target/release/octos']
    report['bounded_kernel_artifact_check'] = [{'path': str(path), 'exists': path.is_file()} for path in candidates]
    report['profiles_nonsecret'] = []
    for name in ['candidate-035-user-20261003', 'candidate-036-mail-cleanup']:
        path = WORK.parent / name / 'private/home/octos-home/.octos/profiles/_main.json'
        config = json.loads(path.read_text()).get('config', {}).get('llm', {})
        providers = []
        for item in [config.get('primary')] + config.get('fallbacks', []):
            if not isinstance(item, dict):
                continue
            route = item.get('route', {})
            providers.append({'family_id': item.get('family_id'), 'model_id': item.get('model_id'),
                              'api_type': route.get('api_type'), 'base_url': safe_url(route.get('base_url', ''))})
        report['profiles_nonsecret'].append({'path': str(path.relative_to(ROOT)), 'providers': providers})
    process_rows = command(['ps', '-axo', 'pid=,comm='])[1]
    shared_pids = set(command(['lsof', '-t', '-iTCP:8080', '-iTCP:8081', '-sTCP:LISTEN'])[1].splitlines())
    processes = []
    for row in process_rows.splitlines():
        parts = row.strip().split(None, 1)
        if len(parts) != 2:
            continue
        pid, executable = parts
        if not (executable.endswith('/octosense') or executable.endswith('/octos') or pid in shared_pids):
            continue
        _, raw = command(['ps', 'eww', '-p', pid, '-o', 'command='])
        environment = {}
        for key in ['OCTOS_APP_CORE_BIN', 'OCTOS_APP_CORE_DIR', 'OCTOSENSE_CONTAINED_APPS',
                    'OCTOSENSE_HOME', 'OCTOSENSE_APP_DATA', 'MAKEPAD_REMOTE']:
            match = re.search(r'(?:^| )' + key + r'=(.*?)(?= [A-Za-z_][A-Za-z0-9_]*=|$)', raw)
            environment[key] = match.group(1) if match else None
        processes.append({'pid': int(pid), 'executable': executable, 'nonsecret_environment': environment})
        if executable.endswith('/llama-server'):
            _, arguments = command(['ps', '-p', pid, '-o', 'command='])
            safe = {}
            for flag in ['--alias', '--ctx-size', '--port', '--host']:
                match = re.search(re.escape(flag) + r'\s+(\S+)', arguments)
                safe[flag] = match.group(1) if match else None
            match = re.search(r'(?:-m|--model)\s+(.*?)(?=\s+--|$)', arguments)
            safe['model_file'] = match.group(1) if match else None
            processes[-1]['nonsecret_model_arguments'] = safe
    report['processes'] = processes
    report['port_inventory'] = command(['lsof', '-nP', '-iTCP:8080', '-iTCP:8081', '-iTCP:8416', '-iTCP:8486', '-sTCP:LISTEN'])[1]
    report['metadata_http'] = []
    for port in [8080, 8081]:
        for route in ['/health', '/v1/models']:
            row = {'port': port, 'method': 'GET', 'route': route}
            try:
                with urlopen(f'http://127.0.0.1:{port}{route}', timeout=8) as response:
                    payload = json.loads(response.read(50000))
                    row.update(status=response.status, health=payload.get('status'),
                               model_ids=[item.get('id') for item in payload.get('data', [])])
            except HTTPError as error:
                row.update(status=error.code, result='GET unsupported or refused; no response body copied')
            except (URLError, OSError, ValueError) as error:
                row.update(error_type=type(error).__name__)
            report['metadata_http'].append(row)
    relay = Path('/Users/mima0000/.codex/worktrees/muse-round2-improvements/Agent APP黑客松/official_muse/round2/tests/model_relay.py')
    report['running_relay_source'] = {'path': str(relay), 'sha256': sha(relay),
                                      'GET_handler_present': 'def do_GET' in relay.read_text(),
                                      'POST_destination': 'http://127.0.0.1:8080',
                                      'records_request_messages': True, 'private_wire_logs_read': False}
    code, plan = command(['python3', str(HOST / 'tools/kernel-artifact.py'), '--host', '--plan'])
    report['kernel_plan_exit_code'] = code
    report['kernel_plan'] = json.loads(plan) if code == 0 else None
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'evidence': str(OUT / 'inventory.json'), 'host_sha256': report['host_binary_sha256'],
                      'http_statuses': [row.get('status') for row in report['metadata_http']],
                      'inference_requests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
