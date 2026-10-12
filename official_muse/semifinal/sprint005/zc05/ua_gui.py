#!/usr/bin/env python3
"""Evidence helper for one explicitly handed-over native fixture window.

It never launches a host, injects product functions, or decides PASS. Import it
after the final candidate and GUI ownership are supplied by ZC-00.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "official_muse/phase2/tests"))
from remote import Remote


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


class GUIEvidence:
    def __init__(self, handoff_path, attempt_path):
        self.identity = json.loads(Path(handoff_path).read_text())
        identity = self.identity
        assert identity["stage"] == "GUI_OWNERSHIP_GRANTED"
        assert identity["gui_owner"] == "ZC-05" and identity["fixture_only"] is True
        assert 1 <= identity["port"] <= 65535 and identity["port"] != 9696
        assert identity["candidate_id"] and identity["owner_pid"] > 0
        assert identity["native_window_id"] > 0
        os.kill(identity["owner_pid"], 0)
        owners = subprocess.check_output([
            "/usr/sbin/lsof", "-n", "-P", "-t",
            f"-iTCP:{identity['port']}", "-sTCP:LISTEN"], text=True).split()
        assert set(owners) == {str(identity["owner_pid"])}
        for name in ("main", "manifest", "host"):
            entry = identity["frozen_files"][name]
            assert re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
            assert hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
        self.remote = Remote(identity["port"])
        self.path = Path(attempt_path).resolve()
        evidence_root = ROOT / "official_muse/semifinal/evidence/user-acceptance-3rounds"
        assert self.path.is_relative_to(evidence_root.resolve())
        self.path.mkdir(parents=True, exist_ok=True)
        identity_path = self.path / "identity.json"
        if identity_path.exists():
            assert json.loads(identity_path.read_text()) == identity
        else:
            save_json(identity_path, identity)
            save_json(self.path / "attempt.json", {"started_at_utc": now(), "status": "IN_PROGRESS"})
        self.sequence = sum(1 for _ in self.path.glob("snap-*.json"))

    def _journal(self, value):
        with (self.path / "ui-actions.jsonl").open("a") as stream:
            stream.write(json.dumps({"at_utc": now(), **value}, ensure_ascii=False) + "\n")

    def snapshot(self):
        self.sequence += 1
        data = json.loads(self.remote.request("/snap"))
        save_json(self.path / f"snap-{self.sequence:04d}.json", data)
        return data["s"]

    def _unique(self, key, widget_type):
        found = [w for w in self.snapshot() if w.get("ty") == widget_type
                 and (w.get("i") == key or w.get("t") == key)]
        assert len(found) == 1, f"Expected exactly one visible {widget_type}: {key}; got {len(found)}"
        widget = found[0]
        x, y, width, height = widget["r"]
        assert x >= 0 and y >= 0 and width >= 2 and height >= (24 if widget_type == "Button" else 2)
        assert "w" in widget, "Snapshot must identify the target native remote window"
        return widget

    def _input_once(self, path, **params):
        self._journal({"transport": "MAKEPAD_NATIVE_UI", "path": path,
                       "params": params, "event": "DISPATCH_ONCE"})
        try:
            answer = self.remote.request(path, **params)
        except Exception as error:
            self._journal({"event": "DISPATCH_ERROR_NO_RETRY", "error": repr(error)})
            raise
        self._journal({"event": "DISPATCH_RETURNED",
                       "response": answer.decode("utf-8", errors="replace")})
        return answer

    def click(self, key):
        widget = self._unique(key, "Button")
        x, y, width, height = widget["r"]
        self._journal({"event": "BUTTON_SELECTED", "widget": widget})
        return self._input_once("/click", w=widget["w"],
                                x=int(x + width / 2), y=int(y + height / 2))

    def type(self, key, value):
        widget = self._unique(key, "TextInput")
        assert isinstance(widget.get("val"), str)
        x, y, width, height = widget["r"]
        self._input_once("/click", w=widget["w"], x=int(x + width / 2), y=int(y + height / 2))
        if widget["val"]:
            self._input_once("/k", w=widget["w"], k="down", c="End")
            for _ in widget["val"]:
                self._input_once("/k", w=widget["w"], k="down", c="Backspace")
        self.wait(lambda rows: any(w.get("i") == key and w.get("val") == "" for w in rows))
        if value:
            self._input_once("/t", w=widget["w"], t=value)
        self.wait(lambda rows: any(w.get("i") == key and w.get("val") == value for w in rows))

    def scroll(self, pane_key, dy):
        found = [w for w in self.snapshot() if w.get("i") == pane_key]
        assert len(found) == 1 and "w" in found[0]
        widget = found[0]
        x, y, width, height = widget["r"]
        assert width >= 2 and height >= 2
        return self._input_once("/m", w=widget["w"], k="scroll", precise=1,
                                x=int(x + width / 2), y=int(y + height / 2), dy=dy)

    def wait(self, predicate, seconds=10):
        deadline = time.monotonic() + min(seconds, 30)
        while True:
            rows = self.snapshot()
            if predicate(rows):
                return rows
            if time.monotonic() >= deadline:
                raise TimeoutError("Visible state was not observed; business input was not retried.")
            time.sleep(0.2)

    def capture(self, filename):
        assert filename.endswith(".png") and Path(filename).name == filename
        window = subprocess.check_output([
            self.identity["window_id_tool"], str(self.identity["owner_pid"])], text=True).strip()
        assert window == str(self.identity["native_window_id"])
        target = self.path / filename
        assert not target.exists(), "Never overwrite an original screenshot"
        subprocess.run(["/usr/sbin/screencapture", "-x", "-l", window, str(target)], check=True)
        self._journal({"event": "NATIVE_CAPTURE", "native_window_id": window,
                       "file": filename, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return target


if __name__ == "__main__":
    print(__doc__)
