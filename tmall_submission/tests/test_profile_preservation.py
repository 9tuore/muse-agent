#!/usr/bin/env python3
"""Verify an existing synthetic provider profile is preserved byte for byte.

Opens an isolated real Host, never calls the configured route or any account.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('delivery', type=Path)
    args = parser.parse_args()
    launcher = args.delivery.resolve() / 'Muse.app/Contents/MacOS/muse-launcher'
    with tempfile.TemporaryDirectory(prefix='tmall-synthetic-profile-') as temp:
        state = Path(temp)
        profile = state / 'home/octos-home/.octos/profiles/_main.json'
        profile.parent.mkdir(parents=True)
        data = dict(id='_main', name='Synthetic custom provider', enabled=True,
                    config=dict(llm=dict(primary=dict(family_id='custom', model_id='synthetic-model',
                        route=dict(base_url='http://127.0.0.1:9/v1', api_type='openai')),
                        fallbacks=[]), env_vars=dict(SYNTHETIC_FLAG='preserve-me')))
        original = (json.dumps(data, indent=2) + '\n').encode()
        profile.write_bytes(original)
        env = {k: os.environ[k] for k in ('HOME', 'PATH', 'USER', 'TMPDIR', 'LANG') if k in os.environ}
        env['MUSE_TMALL_STATE'] = str(state)
        with (state / 'entry-output.txt').open('w') as out:
            child = subprocess.Popen([str(launcher)], env=env, stdout=out, stderr=out)
            try:
                deadline = time.monotonic() + 50
                while not (state / 'logs/host.log').exists():
                    assert child.poll() is None, 'Entry exited before Host was launched'
                    assert time.monotonic() < deadline, 'Host launch deadline'
                    time.sleep(.2)
                time.sleep(1)
                assert profile.read_bytes() == original
                assert not (state / 'local-model.json').exists()
                assert not (state / 'logs/model.log').exists()
            finally:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=25)
        assert profile.read_bytes() == original
        print(json.dumps(dict(status='PASS', synthetic_fixture=True, profile_exact=True,
                              configured_provider_preserved=True, bundled_runner_not_started=True,
                              model_called=False, external_actions=False)))


if __name__ == '__main__':
    main()
