#!/usr/bin/env python3
"""Build the actual isolated official Home for an x86_64 Android emulator."""
import os
from pathlib import Path
import subprocess
import sys
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
    RUSTUP_HOME=str(tools / "rustup"), RUSTC=str(tools / "bin/phone-rustc"),
    CARGO_TARGET_DIR=str(state / "android-target"), CARGO_HOME=str(state / "cargo-home"),
    CARGO_BUILD_JOBS="2", CARGO_PROFILE_RELEASE_DEBUG="0",
    CARGO_PROFILE_RELEASE_INCREMENTAL="false", CARGO_PROFILE_RELEASE_OPT_LEVEL="1")
kernel = state / "android-target/x86_64-linux-android/release/octos"
if not kernel.is_file():
    raise SystemExit("Required official locked octos kernel is not built; refusing kernel-free Home")
env["MAKEPAD_ANDROID_EXTRA_LIBS"] = "liboctos.so=" + str(kernel)
public = json.loads((state / "validation-public.json").read_text())
env["MUSE_PHONE_VALIDATION_HUB"] = "http://10.0.2.2:8571"
env["MUSE_PHONE_VALIDATION_ANCHOR"] = public["public_keys"]["anchor"]
env["PATH"] = str(tools / "bin") + os.pathsep + env["PATH"]
command = [str(tools / "bin/cargo-makepad"), "makepad", "android",
    "--sdk-path=" + str(tools / "android-sdk"), "--abi=x86_64",
    "--package-name=dev.makepad.octosense",
    "build", "-p", "octosense-home", "--release", "--locked", "--offline"]
if "--online" in sys.argv:
    command.remove("--offline")
attempt = 1
while (p / "evidence" / f"home-x86-build-r{attempt}.log").exists():
    attempt += 1
log_name = f"home-x86-build-r{attempt}.log"
print("build log:", log_name, flush=True)
with (p / "evidence" / log_name).open("w") as output:
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
