#!/usr/bin/env python3
"""Repackage retained Home through the single-function-patched official tool."""
import argparse
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
    parser.add_argument('--emulator-state', type=Path, required=True)
    parser.add_argument('--trim-finished-rust-cache', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    state = args.retained_state.resolve(strict=True)
    out = args.out.resolve()
    emulator = args.emulator_state.resolve(strict=True)
    assert out.is_relative_to(root / 'build') and not out.exists()
    assert emulator.is_relative_to(root / 'build')
    tool = root / 'build/phone-packager-target/release/cargo-makepad'
    assert tool.is_file()
    tools = state / 'tools'
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR') if k in os.environ}
    env.update(LANG='en_US.UTF-8', LC_ALL='en_US.UTF-8',
               JAVA_HOME=str(tools / 'jdk-17.0.2.jdk/Contents/Home'),
               ANDROID_HOME=str(tools / 'android-sdk'), RUSTUP_HOME=str(tools / 'rustup'),
               RUSTC=str(tools / 'bin/phone-rustc'), CARGO_HOME=str(state / 'cargo-home'),
               CARGO_TARGET_DIR=str(state / 'android-target'), CARGO_BUILD_JOBS='2',
               CARGO_PROFILE_RELEASE_DEBUG='0', CARGO_PROFILE_RELEASE_INCREMENTAL='false',
               CARGO_PROFILE_RELEASE_OPT_LEVEL='1')
    env['PATH'] = str(tools / 'bin') + os.pathsep + env['PATH']
    env['MAKEPAD_ANDROID_EXTRA_LIBS'] = 'liboctos.so=' + str(state / 'kernel-artifacts/octos-x86_64')
    public = json.loads((state / 'validation-public.json').read_text())
    env['MUSE_PHONE_VALIDATION_HUB'] = 'http://10.0.2.2:8571'
    env['MUSE_PHONE_VALIDATION_ANCHOR'] = public['public_keys']['anchor']
    env['AWS_LC_SYS_CMAKE_BUILDER_x86_64_linux_android'] = '0'
    command = [str(tool), 'makepad', 'android', '--sdk-path=' + str(tools / 'android-sdk'),
               '--abi=x86_64', '--package-name=dev.makepad.octosense', '--min-sdk-version=33',
               'build', '-p', 'octosense-home', '--release', '--locked', '--offline']
    native = state / 'android-target/x86_64-linux-android/release/liboctosense_home.so'
    if args.trim_finished_rust_cache:
        assert native.is_file()
    reserve = 200_000_000 if args.trim_finished_rust_cache else 1_300_000_000
    assert allocated(state) + allocated(emulator) + reserve < 10_500_000_000
    assert shutil.disk_usage(state).free > 3_300_000_000
    out.mkdir(parents=True)
    with (out / 'build.log').open('w') as log:
        child = subprocess.Popen(command, cwd=state / 'sdk/octosense/phone', env=env,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        print('Owned package build PID:', child.pid, flush=True)
        trimmed = False
        while child.poll() is None:
            time.sleep(10)
            # The official tool prints this only after rust_build has returned.
            # Keep final/native shared libraries; packaging also searches deps
            # for .so files. Only finished compiler caches are expendable.
            if args.trim_finished_rust_cache and not trimmed and 'Building APK (package=' in (out / 'build.log').read_text():
                removed = []
                for release in ('release', 'x86_64-linux-android/release'):
                    for path in (state / 'android-target' / release / 'deps').glob('*'):
                        if path.is_file() and not path.is_symlink() and path.suffix in ('.rlib', '.rmeta', '.d'):
                            removed.append({'path': str(path), 'size': path.stat().st_size})
                            path.unlink()
                (out / 'finished-cache-trim.json').write_text(json.dumps(
                    {'removed': removed, 'final_native_preserved': native.is_file(),
                     'stage': 'After official rust_build, before APK packaging'}, indent=2) + '\n')
                trimmed = True
            used = allocated(state) + allocated(emulator)
            free = shutil.disk_usage(state).free
            if used > 10_500_000_000 or free < 2_000_000_000:
                (out / 'resource-stop.json').write_text(json.dumps(
                    {'combined_phone_allocated': used, 'free': free, 'pid': child.pid}, indent=2) + '\n')
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                break
    (out / 'build-result.json').write_text(json.dumps(
        {'exit': child.returncode, 'scope': 'Historical rc16 Home / patched packager only; no rc18 runtime claim'}, indent=2) + '\n')
    print('Build exit:', child.returncode, flush=True)
    raise SystemExit(child.returncode)


if __name__ == '__main__':
    main()
