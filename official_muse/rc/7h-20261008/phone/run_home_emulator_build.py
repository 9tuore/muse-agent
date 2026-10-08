#!/usr/bin/env python3
"""Build the actual isolated official Home for an x86_64 Android emulator."""
import os
from pathlib import Path
import subprocess
import time
import shutil
import signal
import json

p = Path(__file__).resolve().parent
state = p / ".local-state"
tools = state / "tools"
env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR") if k in os.environ}
env.update(LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8",
    JAVA_HOME=str(tools / "jdk-17.0.2.jdk/Contents/Home"),
    ANDROID_HOME=str(tools / "android-sdk"),
    RUSTUP_HOME=str(tools / "rustup"),
    CARGO_TARGET_DIR=str(state / "home-target"),
    CARGO_BUILD_JOBS="2", CARGO_PROFILE_RELEASE_DEBUG="0",
    CARGO_PROFILE_RELEASE_INCREMENTAL="false", CARGO_PROFILE_RELEASE_OPT_LEVEL="1")
command = [str(tools / "bin/cargo-makepad"), "makepad", "android",
    "--sdk-path=" + str(tools / "android-sdk"), "--abi=x86_64",
    "--package-name=dev.makepad.octosense",
    "build", "-p", "octosense-home", "--release", "--locked", "--offline"]
with (p / "evidence/home-x86-build-r1.log").open("w") as output:
    process = subprocess.Popen(command, cwd=state / "sdk/octosense/phone",
        env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
    while process.poll() is None:
        time.sleep(20)
        used = int(subprocess.check_output(["du", "-sk", str(state)]).split()[0]) * 1024
        free = shutil.disk_usage(state).free
        if used > 9_000_000_000 or free < 5 * 1024**3:
            (p / "evidence/home-build-resource-stop.json").write_text(json.dumps(
                {"own_bytes": used, "free_bytes": free, "reason": "authorized resource boundary"}, indent=2))
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            break
raise SystemExit(process.returncode)
