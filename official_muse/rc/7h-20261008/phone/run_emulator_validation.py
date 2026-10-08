#!/usr/bin/env python3
"""Run only the isolated Phone AVD, with the existing resource boundaries."""
from pathlib import Path
import json
import os
import shutil
import signal
import subprocess
import sys
import time

p = Path(__file__).resolve().parent
state = p / ".local-state"
sdk = state / "tools/android-sdk"
env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR") if k in os.environ}
env.update(LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8", ANDROID_HOME=str(sdk),
           ANDROID_SDK_ROOT=str(sdk), ANDROID_USER_HOME=str(state / "android-user"),
           ANDROID_AVD_HOME=str(state / "avd"), ANDROID_ADB_SERVER_PORT="5041")
command = [str(sdk / "emulator/emulator"), "-avd", "MusePhoneAPI35",
           "-no-window", "-no-audio", "-no-snapshot", "-memory", "1024",
           "-partition-size", "1024", "-gpu", "swiftshader_indirect", "-port", "5580"]
if "--wipe-data" in sys.argv:
    command.append("-wipe-data")
free = shutil.disk_usage(state).free
used = int(subprocess.check_output(["du", "-sk", str(state)]).split()[0]) * 1024
# Actual API35/37.2.12 first boot enforces6GiB and a1.2 free-space factor.
# r2/r3 receipts preserve failures;1GiB startup/config overrides do not work.
assert free >= 7_730_941_133, "API35 first boot requires at least7730941133 bytes free"
assert free > 2_000_000_000 + 1024**3 + 300_000_000
assert used + 1024**3 + 66 * 1024**2 < 10_500_000_000
attempt = 1
while (p / "evidence" / f"emulator-boot-r{attempt}.log").exists():
    attempt += 1
log = p / "evidence" / f"emulator-boot-r{attempt}.log"
print("emulator log:", log.name, flush=True)
config = state / "avd/MusePhoneAPI35.avd/config.ini"
assert "disk.dataPartition.size = 6442450944" in config.read_text()
with log.open("w") as output:
    child = subprocess.Popen(command, env=env, stdout=output,
                             stderr=subprocess.STDOUT, start_new_session=True)
    (p / "evidence" / f"emulator-r{attempt}-preflight.json").write_text(json.dumps({
        "pid": child.pid, "data_free_bytes": free, "own_bytes": used,
        "requested_partition_mb": 1024, "actual_first_boot_data_partition_bytes": 6442450944,
        "emulator_required_free_bytes": 7730941133, "requested_memory_mb": 1024,
        "reason": "API35 emulator enforces6GiB at first boot; resource guards remain unchanged",
        "serial": "emulator-5580", "adb_server_port": 5041,
        "command": command, "fixture_only": True, "no_physical_devices": True,
        "resource_policy": "own10.5GB/Data2GB unchanged"
    }, indent=2))
    while child.poll() is None:
        time.sleep(10)
        used = int(subprocess.check_output(["du", "-sk", str(state)]).split()[0]) * 1024
        free = shutil.disk_usage(state).free
        if used > 10_500_000_000 or free < 2_000_000_000:
            (p / "evidence" / f"emulator-r{attempt}-resource-stop.json").write_text(json.dumps({
                "own_bytes": used, "data_free_bytes": free,
                "reason": "authorized resource boundary", "pid": child.pid
            }, indent=2))
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            break
raise SystemExit(child.returncode)
