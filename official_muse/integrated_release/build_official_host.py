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
    parser.add_argument("--phase", choices=("check", "host", "kernel", "hub", "tests", "startup-tests"), required=True)
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
    makepad = sdk / ".sources/makepad"
    makepad_lock = json.loads((sdk / "runtime-patches.lock.json").read_text())["makepad"]
    makepad_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=makepad, text=True).strip()
    makepad_tree = subprocess.check_output(["git", "write-tree"], cwd=makepad, text=True).strip()
    if makepad_revision != makepad_lock["base_revision"] or makepad_tree != makepad_lock["tree"] or subprocess.check_output(["git", "diff", "--binary"], cwd=makepad):
        raise SystemExit("makepad: run prepare_official_host.py to apply the reviewed cold-source fix")
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
        def run(command, cwd=sdk, command_env=env, output=log):
            receipt["commands"].append([str(part) for part in command])
            log.write("COMMAND " + json.dumps(receipt["commands"][-1]) + "\n")
            log.flush()
            subprocess.run(command, cwd=cwd, env=command_env, stdout=output,
                           stderr=log if output is not log else subprocess.STDOUT, check=True)
        try:
            if args.phase == "check":
                run(["python3", "tools/setup.py", "--check", "--cargo"])
                run(["python3", "tools/native_apps.py", "--check"])
            elif args.phase in ("tests", "startup-tests"):
                base = ["cargo", "test", "--locked", "--release"]
                if args.offline:
                    base.append("--offline")
                packages = ("octosense-shell", "makepad-script", "makepad-widgets") if args.phase == "startup-tests" else tuple(
                    "octosense-" + name for name in ("calendar-service", "app-peers", "app-hub", "appstore", "shell"))
                for name in packages:
                    base += ["-p", name]
                base += ["--no-default-features", "--features",
                         "octosense-shell/app-hub,octosense-shell/octos-core,octosense-app-peers/octos-core",
                         "--lib"]
                if args.phase == "tests":
                    base += ["--test", "per_app_offer", "--test", "muse_calendar_offers"]
                base += ["--no-run", "--message-format=json"]
                messages_path = work / (args.phase + "-artifacts.jsonl")
                with messages_path.open("w") as messages:
                    run(base, output=messages)
                artifacts = [json.loads(line) for line in messages_path.read_text().splitlines() if line.strip()]
                cases = [("octosense_calendar_service", None), ("octosense_app_peers", None),
                         ("per_app_offer", None), ("muse_calendar_offers", None),
                         ("octosense_shell", "host_tools::script_apps::tests::calendar_offers_its_tools_from_its_bundle"),
                         ("octosense_shell", "host_tools::tests::admitted_mail_calendar_grants_route_to_the_real_calendar_store")]
                if args.phase == "startup-tests":
                    cases = [("makepad_script", "vm::tests::source_preparation_does_not_execute_partial_application"),
                             ("makepad_script", "vm::tests::hard_time_budget_drains_its_uncatchable_error"),
                             ("makepad_widgets", "splash::style_tests::large_cold_source_is_prepared_before_one_application_run"),
                             ("makepad_widgets", "splash::style_tests::closing_a_partly_prepared_source_cancels_the_remaining_frames"),
                             ("makepad_widgets", "splash::style_tests::a_failed_cold_preparation_cannot_restart_through_style_reapply")]
                receipt["test_suites"] = []
                for target, test_filter in cases:
                    binaries = [row["executable"] for row in artifacts
                                if row.get("reason") == "compiler-artifact" and row.get("executable")
                                and row.get("profile", {}).get("test") and row["target"]["name"] == target]
                    if len(binaries) != 1:
                        raise RuntimeError(f"Expected one compiled test executable for {target}, got {binaries}")
                    executable = binaries[0]
                    selected = [test_filter, "--exact"] if test_filter else []
                    listing_path = work / ("test-list-" + target + ("-" + test_filter.rsplit("::", 1)[-1] if test_filter else "") + ".log")
                    with listing_path.open("w") as listing:
                        run([executable, *selected, "--list"], output=listing)
                    if not any(line.endswith(": test") for line in listing_path.read_text().splitlines()):
                        raise RuntimeError(f"No tests selected for {target}: {test_filter}")
                    result = {"target": target, "filter": test_filter, "exit_code": 0}
                    try:
                        run([executable, *selected])
                    except subprocess.CalledProcessError as error:
                        result["exit_code"] = error.returncode
                    receipt["test_suites"].append(result)
                if any(suite["exit_code"] != 0 for suite in receipt["test_suites"]):
                    raise RuntimeError("One or more selected test suites failed; see test_suites and the preserved log")
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
            if hashlib.sha256(subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=sdk)).hexdigest() != receipt["sdk_patch_sha256"]:
                raise RuntimeError("SDK compatibility patch changed during the build")
            for name, identity in receipt["frameworks"].items():
                repo = sdk / ".sources" / name
                if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != identity["revision"] or hashlib.sha256(
                    subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=repo)).hexdigest() != identity["patch_sha256"]:
                    raise RuntimeError(f"{name}: source identity changed during the build")
            receipt["status"] = "PASS" if args.phase in ("check", "tests", "startup-tests") else "BUILT_NOT_RUNTIME_VERIFIED"
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
