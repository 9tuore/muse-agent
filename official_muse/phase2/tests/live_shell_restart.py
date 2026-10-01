"""Restart only the supplied isolated packaged Shell and verify durable state."""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from audit_state import audit
from remote import Remote


def snapshot(jail):
    files = [jail / name for name in
             ("goals.json", "memory.json", "chat-sessions.json", "calendar-state.json")]
    files.extend(sorted((jail / "results").glob("*.json")))
    return {
        "hashes": {str(p.relative_to(jail)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in files},
        "audit": audit(jail, 3, True),
        "activity": json.loads((jail / "activity.json").read_text()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", type=int)
    for name in ("app", "home", "apps", "hub", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--anchor", required=True)
    args = parser.parse_args()
    assert args.app.is_dir() and args.app.suffix == ".app"
    jail = args.apps / "muse-goals"
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    before = snapshot(jail)
    (args.output / "before.json").write_text(json.dumps(before, ensure_ascii=False, indent=2))
    remote.request("/quit")
    for _ in range(100):
        try:
            urlopen(remote.base + "/s", timeout=0.3).close()
        except OSError:
            break
        time.sleep(0.1)
    else:
        raise TimeoutError("isolated Shell did not stop; do not launch a second instance")
    command = ["open", "-n"]
    for name, value in {
        "OCTOSENSE_HOME": args.home.resolve(),
        "OCTOSENSE_APP_DATA": args.apps.resolve(),
        "OCTOSENSE_HUB": args.hub.resolve(),
        "OCTOSENSE_HUB_ANCHOR": args.anchor,
        "MAKEPAD_REMOTE": args.port,
    }.items():
        command.extend(["--env", f"{name}={value}"])
    command.extend([str(args.app.resolve()), "--args", "--test-action", "launch-apphub"])
    subprocess.run(command, check=True)
    for _ in range(120):
        try:
            remote.find("Open")
            break
        except (OSError, AssertionError):
            time.sleep(0.25)
    else:
        raise TimeoutError("App Hub did not render its Open control")
    remote.click("Open")
    remote.wait_for("page_title", 30)
    time.sleep(1)
    after = snapshot(jail)
    assert before["hashes"] == after["hashes"], "durable files changed during restart"
    counts = ("goal_count", "run_count", "action_count", "memory_claim_count")
    assert all(before["audit"][k] == after["audit"][k] for k in counts)
    old = before["activity"]
    assert after["activity"][:len(old)] == old
    extra = after["activity"][len(old):]
    assert len(extra) == 1 and extra[0]["kind"] == "restart restore", extra
    remote.shot(args.output / "restart.png")
    report = {"evidence": "LIVE normal Launch Services packaged Shell restart",
              "hashes_unchanged": True, "run_and_action_counts_unchanged": True,
              "history_prefix_unchanged": True, "new_activity": [e["kind"] for e in extra],
              "audit": after["audit"], "hashes": after["hashes"]}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"hash_count": len(after["hashes"]), "audit": after["audit"]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
