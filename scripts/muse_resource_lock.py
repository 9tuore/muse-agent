#!/usr/bin/env python3
"""Serialize this sprint's GUI, build, or shared-model test command."""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource", choices=("gui", "build", "qwen"))
    parser.add_argument("--owner", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--wait-seconds", type=int, default=120)
    parser.add_argument("--command-seconds", type=int, default=900)
    try:
        split = sys.argv.index("--")
    except ValueError:
        parser.error("separate options from command with --")
    args = parser.parse_args(sys.argv[1:split])
    command = sys.argv[split + 1:]
    if not command or not args.owner.strip() or not args.purpose.strip():
        parser.error("owner, purpose and command are required")
    if not 0 <= args.wait_seconds <= 3600 or not 1 <= args.command_seconds <= 3600:
        parser.error("invalid timeout")
    root = Path("/tmp/gosim-muse-5agent-20260928")
    root.mkdir(mode=0o700, exist_ok=True)
    path = root / (args.resource + ".lock")
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    deadline = time.monotonic() + args.wait_seconds
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    print("resource_busy:" + args.resource, file=sys.stderr)
                    return 75
                time.sleep(0.2)
        record = {"resource": args.resource, "owner": args.owner.strip()[:80],
                  "purpose": args.purpose.strip()[:200], "pid": os.getpid(),
                  "started_at": datetime.now(timezone.utc).isoformat()}
        os.ftruncate(fd, 0)
        os.write(fd, (json.dumps(record, ensure_ascii=False) + "\n").encode())
        os.fsync(fd)
        try:
            return subprocess.run(command, timeout=args.command_seconds, check=False).returncode
        except subprocess.TimeoutExpired:
            print("resource_command_timeout:" + args.resource, file=sys.stderr)
            return 124
        finally:
            os.ftruncate(fd, 0)
            os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    raise SystemExit(main())
