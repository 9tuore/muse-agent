#!/usr/bin/env python3
"""Build the actual isolated official Home for an x86_64 Android emulator."""
import os
from pathlib import Path
import subprocess

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
    CARGO_PROFILE_RELEASE_INCREMENTAL="false")
command = [str(tools / "bin/cargo-makepad"), "makepad", "android",
    "--sdk-path=" + str(tools / "android-sdk"), "--abi=x86_64",
    "--package-name=dev.makepad.octosense.phonecandidate",
    "build", "-p", "octosense-home", "--release", "--locked", "--offline"]
with (p / "evidence/home-x86-build-r1.log").open("w") as output:
    result = subprocess.run(command, cwd=state / "sdk/octosense/phone",
        env=env, stdout=output, stderr=subprocess.STDOUT)
raise SystemExit(result.returncode)
