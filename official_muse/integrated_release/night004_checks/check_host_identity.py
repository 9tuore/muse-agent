#!/usr/bin/env python3
"""Read-only macOS dynamic code identity check for one explicit Host PID."""
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def positive_pid(value):
    number = int(value)
    if number <= 0 or number > 2147483647:
        raise argparse.ArgumentTypeError("PID must be in 1..2147483647")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=positive_pid, required=True)
    parser.add_argument("--expected-executable", required=True,
                        help="Expected exact absolute executable path")
    args = parser.parse_args()
    if not os.path.isabs(args.expected_executable):
        parser.error("--expected-executable must be an absolute path")
    probe = Path(__file__).resolve().with_name("signature_probe")
    result = {
        "scope": "read_only_dynamic_code_identity",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "pid": args.pid,
        "expected_main_executable": args.expected_executable,
        "guest_status": None,
        "dynamic_validity_status": None,
        "signing_information_status": None,
        "identifier": None,
        "main_executable": None,
        "secured_info_plist_present": None,
        "main_executable_matches": False,
        "probe_exit_code": None,
        "keychain_items_accessed": False,
        "gui_actions_performed": False,
    }
    try:
        completed = subprocess.run([str(probe), str(args.pid)],
                                   capture_output=True, text=True, timeout=10)
        result["probe_exit_code"] = completed.returncode
        fields = dict(line.split("=", 1) for line in completed.stdout.splitlines()
                      if "=" in line)
        for key in ("guest_status", "dynamic_validity_status", "signing_information_status"):
            if key in fields:
                result[key] = int(fields[key])
        for key in ("identifier", "main_executable"):
            if key in fields:
                result[key] = fields[key]
        if fields.get("secured_info_plist_present") in ("true", "false"):
            result["secured_info_plist_present"] = fields["secured_info_plist_present"] == "true"
        result["main_executable_matches"] = result["main_executable"] == args.expected_executable
        passed = (completed.returncode == 0
                  and fields.get("pid") == str(args.pid)
                  and result["main_executable_matches"]
                  and all(result[key] == 0 for key in
                          ("guest_status", "dynamic_validity_status", "signing_information_status")))
        result["status"] = "VALIDATED" if passed else "FAILED"
        exit_code = 0 if passed else 1
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        result["status"] = "ERROR"
        result["error_type"] = type(error).__name__
        exit_code = 1
    result["check_exit_code"] = exit_code
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
