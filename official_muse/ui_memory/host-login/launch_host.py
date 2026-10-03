#!/usr/bin/env python3
"""Start the separately signed candidate with isolated storage."""
import argparse
import json
import os
import socket
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(json.loads((HERE / 'source_provenance.json').read_text())['isolated_source']).parent
BUNDLE = WORK / 'OctoSense Muse 0.3.3 UI-candidate.app'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo-ui', action='store_true', help='no network or keychain; blank login UI probe')
    parser.add_argument('--hidden', action='store_true')
    parser.add_argument('--port', type=int, default=8494)
    args = parser.parse_args()
    assert BUNDLE.is_dir(), 'build and package the candidate first'
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(('127.0.0.1', args.port))
    state = WORK / ('ui-probe-state' if args.demo_ui else 'user-candidate-state')
    state.mkdir(exist_ok=True)
    env = {
        'OCTOSENSE_HOME': str(state / 'home'),
        'OCTOSENSE_APP_DATA': str(state / 'apps'),
        'OCTOS_APP_CORE_DIR': str(state / 'octos'),
        'MAKEPAD_REMOTE': str(args.port),
        'MAKEPAD_APP_CONFIG': json.dumps({'mail_demo': args.demo_ui}),
    }
    if args.hidden:
        env['MAKEPAD_HIDE_WINDOWS'] = '1'
    command = ['open', '-n']
    for key, value in env.items():
        command.extend(['--env', f'{key}={value}'])
    command.extend(['--stdout', str(state / 'stdout.log'), '--stderr', str(state / 'stderr.log'),
                    str(BUNDLE), '--args', '--test-action', 'launch-mail'])
    launcher_env = dict(os.environ)
    launcher_env.pop('MAKEPAD_HIDE_WINDOWS', None)
    subprocess.run(command, check=True, env=launcher_env)
    print(json.dumps({'bundle': str(BUNDLE), 'isolated_state': str(state),
                      'remote_port': args.port, 'mail_demo': args.demo_ui}, ensure_ascii=False))


if __name__ == '__main__':
    main()
