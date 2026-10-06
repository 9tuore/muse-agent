#!/usr/bin/env python3
"""Exercise the packaged entry's checks only; never launch or access accounts."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('delivery', type=Path)
    args = parser.parse_args()
    delivery = args.delivery.resolve()
    state = Path.home() / 'Library/Application Support/Muse Tmall Experience rc51'
    before = state.exists()
    rows = []

    def check(root, flags, code, text):
        result = subprocess.run(['/bin/sh', str(root / 'RUN_MUSE.command'), *flags],
                                capture_output=True, text=True)
        assert result.returncode == code, (result.returncode, result.stderr)
        assert text in result.stdout + result.stderr
        rows.append(dict(flags=flags, expected_exit=code, observed_exit=result.returncode))

    check(delivery, ['--check'], 0, '0.3.26-rc51')
    check(delivery, ['--unknown'], 1, '[--check]')
    with tempfile.TemporaryDirectory(prefix='tmall-entry-check-') as temp:
        root = Path(temp)
        shutil.copy2(delivery / 'RUN_MUSE.command', root / 'RUN_MUSE.command')
        check(root, ['--check'], 1, 'Runtime')
        (root / 'runtime').mkdir()
        (root / 'runtime/OctoSense Host.app').symlink_to(delivery / 'runtime/OctoSense Host.app')
        shutil.copytree(delivery / 'runtime/mirror', root / 'runtime/mirror')
        payload = root / 'runtime/mirror/artifacts/muse-goals-0.3.26-rc51.bundle/main.splash'
        with payload.open('a') as out:
            out.write('\n// deliberately altered copy\n')
        check(root, ['--check'], 1, 'Muse')
    assert state.exists() == before
    print(json.dumps(dict(status='PASS', checks=len(rows), cases=rows, no_state_directory_created=True,
                          GUI_started=False, model_called=False)))


if __name__ == '__main__':
    main()
