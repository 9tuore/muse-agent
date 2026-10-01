#!/usr/bin/env python3
"""Isolated official OctoSense AppCard -> Octos desktop launch probe."""

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OFFICIAL = Path("/Users/mima0000/Documents/Codex/2026-09-24/gosim-agentic-app-2026-git-gosim-2/work/official/octosense")


def process_rows():
    result = subprocess.run(["ps", "-axo", "pid=,ppid=,command="], capture_output=True, text=True, check=True)
    rows = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            rows.append((int(parts[0]), int(parts[1]), parts[2]))
    return rows


def exact_child(rows, host_pid, kernel, data_dir):
    # macOS ps renders non-ASCII executable paths as M- escapes under some
    # locales. The private data-dir and exact argv suffix remain intact.
    marker = "/" + kernel.name + " serve --stdio --data-dir " + str(data_dir) + " --config " + str(data_dir / "config.json")
    matches = [(pid, command) for pid, parent, command in rows
               if parent == host_pid and marker in command]
    return matches[0] if len(matches) == 1 else None


def still_ours(pid, kernel, data_dir):
    marker = "/" + kernel.name + " serve --stdio --data-dir " + str(data_dir) + " --config " + str(data_dir / "config.json")
    return any(row_pid == pid and marker in command
               for row_pid, _, command in process_rows())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, default=DEFAULT_OFFICIAL)
    parser.add_argument("--seconds", type=int, default=45)
    args = parser.parse_args()
    official = args.official.resolve()
    host = official / "target/debug/octosense"
    kernel = ROOT / "runtime/octos-lean-target/debug/octos"
    if not host.is_file() or not kernel.is_file() or not os.access(host, os.X_OK) or not os.access(kernel, os.X_OK):
        raise SystemExit("official_host_or_kernel_missing")
    if not 10 <= args.seconds <= 90:
        raise SystemExit("probe_duration_out_of_range")
    before = process_rows()
    if any("test_muse_desktop_package.py" in command and "--soak-seconds" in command
           for _, _, command in before):
        raise SystemExit("g03_ui_soak_still_running")
    if any(command.startswith(str(host) + " ") for _, _, command in before):
        raise SystemExit("official_host_already_running")

    run = Path(tempfile.mkdtemp(prefix="g01-oc-", dir="/tmp"))
    host_home, core_dir = run / "host", run / "core"
    for directory in (host_home, core_dir, run / "home", run / "tmp", run / "xdg-config", run / "xdg-data"):
        directory.mkdir()
    # The desktop AppCard supplies an explicit --config path to Octos. An
    # absent file makes the child exit before the stdio transport can start.
    (core_dir / "config.json").write_text("{}\n", encoding="utf-8")
    image = run / "appcard.png"
    log_path = run / "host.log"
    env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "USER", "LOGNAME")
           if key in os.environ}
    env.update(HOME=str(run / "home"), TMPDIR=str(run / "tmp"), XDG_CONFIG_HOME=str(run / "xdg-config"),
               XDG_DATA_HOME=str(run / "xdg-data"), OCTOSENSE_HOME=str(host_home),
               OCTOS_APP_CORE_BIN=str(kernel), OCTOS_APP_CORE_DIR=str(core_dir),
               OCTOS_NO_NETWORK="1", RUST_LOG="info")
    command = [str(host), "--module", "appcard", "--test-action", "launch-appcard",
               "--test-action", "capture:" + str(image)]
    started_at = datetime.now(timezone.utc).isoformat()
    host_process = None
    child_seen = None
    snapshots = []
    try:
        with log_path.open("wb") as log:
            host_process = subprocess.Popen(command, cwd=str(official), env=env, stdin=subprocess.DEVNULL,
                                            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            deadline = time.monotonic() + args.seconds
            while time.monotonic() < deadline:
                rows = process_rows()
                child = exact_child(rows, host_process.pid, kernel, core_dir)
                if child:
                    child_seen = child
                    snapshots.append({"pid": child[0], "ppid": host_process.pid, "command": child[1]})
                if host_process.poll() is not None:
                    break
                time.sleep(0.5)
    finally:
        if host_process is not None and host_process.poll() is None:
            host_process.terminate()
            try:
                host_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                host_process.kill()
                host_process.wait(timeout=5)
        if child_seen and still_ours(child_seen[0], kernel, core_dir):
            os.kill(child_seen[0], signal.SIGTERM)
            time.sleep(1)
            if still_ours(child_seen[0], kernel, core_dir):
                os.kill(child_seen[0], signal.SIGKILL)

    log_bytes = log_path.read_bytes()
    log_text = log_bytes.decode("utf-8", errors="replace")
    linked = 'modules linked: ["appcard"]' in log_text
    in_process = "launched appcard as client" in log_text and "(in-process)" in log_text
    child_stopped = not child_seen or not still_ours(child_seen[0], kernel, core_dir)
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    log_output = evidence / "muse-g01-octosense-kernel-host-20260928.log"
    log_output.write_bytes(log_bytes[-5_000_000:])
    image_output = evidence / "muse-g01-octosense-kernel-host-20260928.png"
    captured = image.is_file() and image.stat().st_size > 0
    if captured:
        shutil.copy2(image, image_output)
    core_logs = sorted((core_dir / "logs").glob("serve.*.log")) if (core_dir / "logs").is_dir() else []
    core_log_output = evidence / "muse-g01-octosense-kernel-host-20260928-core.log"
    if core_logs:
        shutil.copy2(core_logs[-1], core_log_output)
    revision = subprocess.run(["git", "-C", str(official), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    result = {"run_dir": str(run), "host_binary": str(host), "host_sha256": hashlib.sha256(host.read_bytes()).hexdigest(),
              "official_revision": revision, "kernel_binary": str(kernel),
              "kernel_sha256": hashlib.sha256(kernel.read_bytes()).hexdigest(),
              "started_at": started_at, "stopped_at": datetime.now(timezone.utc).isoformat(),
              "command": command, "host_home": str(host_home), "core_dir": str(core_dir),
              "host_pid": host_process.pid if host_process else None,
              "host_exit_code": host_process.returncode if host_process else None,
              "child": snapshots[-1] if snapshots else None, "child_stopped": child_stopped,
              "child_samples": len(snapshots), "core_log_path": str(core_log_output) if core_logs else None,
              "seeded_config": "{}",
              "appcard_linked": linked, "appcard_in_process": in_process,
              "screenshot_bytes": image_output.stat().st_size if captured else 0,
              "log_path": str(log_output), "screenshot_path": str(image_output) if captured else None,
              "raw_log_sha256": hashlib.sha256(log_bytes).hexdigest()}
    summary = evidence / "muse-g01-octosense-kernel-host-20260928.json"
    summary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
