#!/usr/bin/env python3
"""Build Muse's host tools from one checked-out official OctoSense release.

Uses upstream packaging and kernel helpers. Each phase writes a command log
and a receipt; neither user profiles nor credentials are accessed.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

FEATURES = "app-hub,octos-core"


def sha(path):
    with Path(path).open("rb") as stream:
        value = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
        return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--phase", choices=("check", "host", "kernel", "hub", "tests"), required=True)
    parser.add_argument("--release-tag", default="desktop-v0.1.0-rc.6")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    sdk, work = args.sdk.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=sdk, text=True).strip()
    tag_revision = subprocess.check_output(["git", "rev-parse", args.release_tag + "^{commit}"], cwd=sdk, text=True).strip()
    if revision != tag_revision:
        raise SystemExit("SDK HEAD differs from the requested release tag")
    cargo_config = sdk / ".cargo/config.toml"
    if not cargo_config.is_file():
        raise SystemExit("Missing official .cargo/config.toml; include .cargo in the SDK checkout")
    official_config = subprocess.check_output(["git", "show", "HEAD:.cargo/config.toml"], cwd=sdk)
    if cargo_config.read_bytes() != official_config:
        raise SystemExit("SDK Cargo configuration differs from the official release")
    system_apps_path = sdk / "desktop/system-apps.json"
    system_apps = json.loads(system_apps_path.read_text())["apps"]
    if not {"mail", "calendar"}.issubset(system_apps):
        raise SystemExit("The host system app selection must include Mail and Calendar")
    patch_root = Path(__file__).resolve().parent / "upstream-rc6"
    for name, repo in (("sdk", sdk), ("app-hub", sdk / ".sources/app-hub")):
        expected = (patch_root / (name + ".patch")).read_bytes()
        actual = subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=repo)
        if actual != expected:
            raise SystemExit(f"{name}: build source differs from the reviewed compatibility patch")
    spec = importlib.util.spec_from_file_location("official_packaging", sdk / "desktop/scripts/package.py")
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    env = package.build_env(package.package_env("macos", sdk, os.environ), os.environ)
    env["CARGO_BUILD_JOBS"] = str(args.jobs)
    env["CARGO_INCREMENTAL"] = "0"
    env["CARGO_TARGET_DIR"] = str(work / "host-target")
    env["OCTOSENSE_RELEASE_TAG"] = args.release_tag
    if args.offline:
        env["CARGO_NET_OFFLINE"] = "true"
    lock_sha = sha(sdk / "Cargo.lock")
    log_path = work / (args.phase + "-build.log")
    receipt_path = work / (args.phase + "-receipt.json")
    receipt = {"phase": args.phase, "sdk_revision": revision, "release_tag": args.release_tag,
               "sdk_lock_sha256": lock_sha, "features": FEATURES, "jobs": args.jobs,
               "status": "RUNNING", "commands": [], "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    receipt["sdk_patch_sha256"] = hashlib.sha256(subprocess.check_output(
        ["git", "diff", "HEAD", "--binary"], cwd=sdk)).hexdigest()
    receipt["cargo_config_sha256"] = sha(cargo_config)
    receipt["system_apps_sha256"] = sha(system_apps_path)
    receipt["system_apps"] = system_apps
    receipt["frameworks"] = {}
    for name in ("makepad", "octoscript", "octoscript-makepad", "app-hub"):
        path = sdk / ".sources" / name
        if path.is_dir():
            receipt["frameworks"][name] = {
                "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip(),
                "patch_sha256": hashlib.sha256(subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=path)).hexdigest(),
            }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    start = time.monotonic()
    code = 0
    with log_path.open("w") as log:
        def run(command, cwd=sdk, command_env=env):
            receipt["commands"].append([str(part) for part in command])
            log.write("COMMAND " + json.dumps(receipt["commands"][-1]) + "\n")
            log.flush()
            subprocess.run(command, cwd=cwd, env=command_env, stdout=log, stderr=subprocess.STDOUT, check=True)
        try:
            if args.phase == "check":
                run(["python3", "tools/setup.py", "--check", "--cargo"])
                run(["python3", "tools/native_apps.py", "--check"])
            elif args.phase == "tests":
                base = ["cargo", "test", "--locked", "--release"]
                if args.offline:
                    base.append("--offline")
                run(base + ["-p", "octosense-calendar-service", "--lib"])
                run(base + ["-p", "octosense-app-peers", "--features", "octos-core", "--lib"])
                run(base + ["-p", "octosense-app-hub", "--test", "per_app_offer"])
                run(base + ["-p", "octosense-appstore", "--test", "muse_calendar_offers"])
                shell = base + ["-p", "octosense-shell", "--no-default-features", "--features", FEATURES, "--lib"]
                run(shell + ["host_tools::script_apps::tests::calendar_offers_its_tools_from_its_bundle", "--", "--exact"])
                run(shell + ["host_tools::tests::admitted_mail_calendar_grants_route_to_the_real_calendar_store", "--", "--exact"])
            elif args.phase == "kernel":
                kernel_env = {key: value for key, value in env.items()
                              if not key.startswith("MAKEPAD") and key not in ("CARGO_BUILD_TARGET", "CARGO_TARGET_DIR")}
                tool = package.kernel_tool()
                steps, binary, source = tool.kernel_plan(host=True, work=work / "kernel-build", offline=args.offline)
                for directory, command in steps:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    run(command, directory, kernel_env)
                staged = tool.stage(binary, work / "kernel", tool.octos_revision(), source)
                receipt["kernel"] = staged
                receipt["artifact"] = str(work / "kernel" / tool.STAGED_NAME)
                receipt["artifact_sha256"] = sha(receipt["artifact"])
            else:
                command = ["cargo", "build", "--locked", "--release"]
                if args.phase == "host":
                    command += ["-p", "octosense", "--bin", "octosense", "--no-default-features", "--features", FEATURES]
                    binary = work / "host-target/release/octosense"
                else:
                    command += ["-p", "octosense-app-hub", "--bin", "hub"]
                    binary = work / "host-target/release/hub"
                if args.offline:
                    command.append("--offline")
                run(command)
                out = work / "artifacts" / binary.name
                out.parent.mkdir(exist_ok=True)
                shutil.copy2(binary, out)
                if args.phase == "host":
                    package.record_release_identity(out, args.release_tag)
                receipt["artifact"] = str(out)
                receipt["artifact_sha256"] = sha(out)
                receipt["artifact_bytes"] = out.stat().st_size
            if sha(sdk / "Cargo.lock") != lock_sha:
                raise RuntimeError("Cargo.lock changed during a locked build")
            receipt["status"] = "PASS" if args.phase in ("check", "tests") else "BUILT_NOT_RUNTIME_VERIFIED"
        except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
            code = error.returncode if isinstance(error, subprocess.CalledProcessError) else 1
            receipt.update(status="FAILED", error=str(error))
    receipt.update(exit_code=code, elapsed_seconds=round(time.monotonic() - start, 3), log_sha256=sha(log_path),
                   finished_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
