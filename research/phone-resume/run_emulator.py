#!/usr/bin/env python3
"""Resume the verified r7 APK on a fresh, isolated official emulator.

Uses the retained verified SDK read-only. Creates no physical-device connection,
account grant or production state. Old Phone evidence and AVD remain unchanged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def allocated(path):
    return int(subprocess.check_output(['du', '-sk', str(path)]).split()[0]) * 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--retained-state', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    old = args.retained_state.resolve(strict=True)
    out = args.out.resolve()
    assert out.is_relative_to(root / 'build') and not out.exists()
    sdk = old / 'tools/android-sdk'
    apk = old / 'kernel-artifacts/octosense-home-r7.apk'
    expected = '70a318d1ccef68f62449a77ebc4b8d6d6dad79f6722a5b41b449ee8b534a62f1'
    assert hashlib.sha256(apk.read_bytes()).hexdigest() == expected
    assert (sdk / 'emulator/emulator').is_file()
    assert (sdk / 'system-images/android-35/default/x86_64/system.img').is_file()
    free = shutil.disk_usage(old).free
    baseline = allocated(old)
    assert free >= 7_730_941_133
    assert baseline + 1024**3 + 66 * 1024**2 < 10_500_000_000
    out.mkdir(parents=True)
    avd = out / 'avd/MuseNightAPI35.avd'
    avd.mkdir(parents=True)
    config = (old / 'avd/MusePhoneAPI35.avd/config.ini').read_text()
    assert 'disk.dataPartition.size = 6442450944' in config
    # Reuse the previously created official Pixel 2 definition, with fresh data.
    (avd / 'config.ini').write_text(config)
    (avd.parent / 'MuseNightAPI35.ini').write_text(
        f'avd.ini.encoding=UTF-8\npath={avd}\ntarget=android-35\n')
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR') if k in os.environ}
    env.update(LANG='en_US.UTF-8', LC_ALL='en_US.UTF-8',
               ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk),
               ANDROID_USER_HOME=str(out / 'android-user'),
               ANDROID_AVD_HOME=str(avd.parent), ANDROID_ADB_SERVER_PORT='5041')
    command = [str(sdk / 'emulator/emulator'), '-avd', 'MuseNightAPI35',
               '-no-window', '-no-audio', '-no-snapshot', '-memory', '1024',
               '-gpu', 'swiftshader_indirect', '-port', '5580']
    record = {'kind': 'ISOLATED_OFFICIAL_PHONE_RUNTIME', 'apk_sha256': expected,
              'status': 'STARTING', 'physical_device': 'DEVICE_NOT_TESTED',
              'old_state_allocated': baseline, 'initial_data_free': free,
              'serial': 'emulator-5580', 'adb_server_port': 5041,
              'original_avd_unchanged': True, 'external_operations': 0,
              'candidate': 'Historical rc16/r7 APK; not current rc18/Desktop'}
    began = time.monotonic()
    with (out / 'emulator.log').open('w') as log:
        child = subprocess.Popen(command, env=env, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        record['pid'] = child.pid
        (out / 'identity.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record), flush=True)
        while child.poll() is None:
            time.sleep(10)
            used = baseline + allocated(out)
            free = shutil.disk_usage(out).free
            if used > 10_500_000_000 or free < 2_000_000_000 or time.monotonic() - began > 3600:
                record.update(status='GUARD_STOP', combined_phone_allocated=used,
                              data_free=free, elapsed=time.monotonic() - began)
                (out / 'stop.json').write_text(json.dumps(record, indent=2) + '\n')
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                break
        record.update(status='EXITED', exit=child.returncode,
                      elapsed=time.monotonic() - began)
        (out / 'exit.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
