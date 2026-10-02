"""LOCAL real card-host: denied grants and missing services, not live TCC or Mail."""
import hashlib
import json
import shutil
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_core_logic import HERE, REPO, launch, quit_host
from remote import Remote


def main():
    port = 8264
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", port)) != 0
    root = HERE / ".local-state/service-negative-final"
    assert not root.exists(), "keep existing evidence"
    results = []
    for case in ("denied", "unavailable"):
        bundle, state = root / case / "bundle", root / case / "state"
        shutil.copytree(REPO / "official_muse/app/bundle", bundle)
        if case == "denied":
            path = bundle / "manifest.json"
            manifest = json.loads(path.read_text())
            manifest["capabilities"] = ["storage"]
            path.write_text(json.dumps(manifest, indent=2))
        jail = state / "muse-goals"
        try:
            launch(bundle, state, port)
            remote = Remote(port)
            remote.set_text("goal_input", "合成失败测试，请简短回复。")
            remote.click("发送")
            deadline = time.monotonic()+15
            while time.monotonic() < deadline:
                if (jail / "chat-sessions.json").exists():
                    data = json.loads((jail / "chat-sessions.json").read_text())
                    selected = next(s for s in data["sessions"] if s["id"] == data["selected_id"])
                    if len(selected["messages"]) == 2:
                        break
                time.sleep(.1)
            assert selected["messages"][-1]["state"] == "error"
            reply = selected["messages"][-1]["text"]
            if case == "denied":
                log = (state / "card-host.log").read_text()
                assert 'refused "model.complete": this app was not granted "model"' in log
                remote.click("日历")
                assert remote.find("page_title")["t"] == "日历"
                assert any("未获 calendar grant" in w.get("t", "") for w in remote.widgets() if w.get("ty") == "Label")
                assert not any(w.get("t") == "确认执行这项系统日历操作" for w in remote.widgets())
            activity = json.loads((jail / "activity.json").read_text())
            assert activity[-1]["kind"] == "error"
            results.append({"case": case, "reply": reply, "persisted_error": True,
                            "source_sha256": hashlib.sha256((bundle / "main.splash").read_bytes()).hexdigest()})
        finally:
            quit_host(port)
    report = {"evidence": "LOCAL card-host; modified grants only for denied harness; no host services",
              "status": "PASS", "cases": results}
    (root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
