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
sys.dont_write_bytecode = True
REMOTE_DRIVER_DIR = ROOT / "official_muse/phase2/tests"
if not (REMOTE_DRIVER_DIR / "remote.py").is_file():
    # ZC-00 explicitly handed over this existing shared UI driver after an
    # unrelated cleanup removed historical files from the acceptance checkout.
    REMOTE_DRIVER_DIR = Path("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/phase2/tests")
sys.path.insert(0, str(REMOTE_DRIVER_DIR))
from remote import Remote


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


class GuardBlocked(RuntimeError):
    """Missing isolation, frozen identity or complete native visual evidence."""


def require(condition, message):
    if not condition:
        raise GuardBlocked(message)


def check_data_dir(identity):
    data = Path(identity["data_dir"]).resolve(strict=True)
    require(data.is_dir(), "Fixture data_dir is not a directory")
    for marker in (data / "FIXTURE_ONLY", data / "apps/.host/FIXTURE_ONLY"):
        require(marker.resolve().is_relative_to(data) and marker.is_file() and not marker.is_symlink(),
                f"Missing real fixture marker inside data_dir: {marker}")
    production = identity.get("production_data_dirs")
    require(identity.get("production_scope_inventory_complete") is True and production,
            "ZC-00 must provide the complete forbidden production-state path inventory")
    for raw in production:
        forbidden = Path(raw).resolve()
        require(not (data == forbidden or data.is_relative_to(forbidden) or forbidden.is_relative_to(data)),
                "Fixture data_dir overlaps a forbidden production-state directory")
    return data


def check_hash(entry):
    require(isinstance(entry, dict) and isinstance(entry.get("sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]),
            "Missing full SHA256 frozen-file identity")
    require(hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
            f"Frozen file changed: {entry['path']}")


def check_frozen_identity(identity):
    require(isinstance(identity.get("git_commit"), str) and re.fullmatch(r"[0-9a-f]{40}", identity["git_commit"]), "Missing full Git commit")
    require(isinstance(identity.get("version"), str) and identity["version"], "Missing candidate version")
    fingerprint = identity.get("bundle_fingerprint")
    require(isinstance(fingerprint, dict) and fingerprint.get("algorithm") in {"sha256", "blake3"}
            and isinstance(fingerprint.get("value"), str)
            and re.fullmatch(r"[0-9a-f]{64}", fingerprint["value"]), "Missing bundle fingerprint")
    required = ("main", "manifest", "host", "kernel", "launcher", "launcher_config", "catalog_summary")
    files = identity.get("frozen_files", {})
    require(all(name in files for name in required), "Incomplete Kernel/Launcher/config/catalog frozen identity")
    for name in required:
        check_hash(files[name])
    manifest = json.loads(Path(files["manifest"]["path"]).read_text())
    require(manifest.get("version") == identity["version"], "Candidate version differs from actual manifest")
    if fingerprint["algorithm"] == "blake3":
        require(manifest.get("integrity", {}).get("bundle_blake3") == fingerprint["value"],
                "Bundle fingerprint differs from actual manifest")
    else:
        require("bundle_archive" in files, "SHA256 bundle fingerprint requires the frozen bundle archive")
        check_hash(files["bundle_archive"])
        require(files["bundle_archive"]["sha256"] == fingerprint["value"], "Bundle archive fingerprint differs")
    for plugin in identity.get("plugin_hashes", []):
        check_hash(plugin)


def inside(rect, bounds, margin=0):
    x, y, width, height = rect
    bx, by, bw, bh = bounds
    return width > 0 and height > 0 and x >= bx + margin and y >= by + margin and x + width <= bx + bw - margin and y + height <= by + bh - margin


def check_visible_widget(widget, pane, window_rect):
    require(widget.get("enabled") is not False and widget.get("visible") is not False,
            "Control is disabled or hidden")
    require("w" in widget and widget["w"] == pane.get("w"), "Control/pane window identity differs")
    require(inside(widget["r"], window_rect), "Control extends outside target window")
    require(inside(widget["r"], pane["r"]), "Control is clipped by its pane; scroll first")
    require(widget["r"][2] >= 2 and widget["r"][3] >= 2, "Control has no complete positive-area geometry")


def candidate_key(identity):
    return {key: identity[key] for key in ("candidate_id", "git_commit", "version", "bundle_fingerprint", "frozen_files", "plugin_hashes")}


def widgets_digest(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class GUIEvidence:
    def __init__(self, handoff_path, attempt_path):
        self.identity = json.loads(Path(handoff_path).read_text())
        identity = self.identity
        assert identity["stage"] == "GUI_OWNERSHIP_GRANTED"
        assert identity["gui_owner"] == "ZC-05" and identity["fixture_only"] is True
        assert 1 <= identity["port"] <= 65535 and identity["port"] != 9696
        assert identity["candidate_id"] and identity["owner_pid"] > 0
        assert identity["native_window_id"] > 0
        check_data_dir(identity)
        check_frozen_identity(identity)
        require(len(identity["remote_window_rect"]) == 4, "Missing actual target-window bounds")
        os.kill(identity["owner_pid"], 0)
        owners = subprocess.check_output([
            "/usr/sbin/lsof", "-n", "-P", "-t",
            f"-iTCP:{identity['port']}", "-sTCP:LISTEN"], text=True).split()
        assert set(owners) == {str(identity["owner_pid"])}
        self.remote = Remote(identity["port"])
        self.path = Path(attempt_path).resolve()
        if identity.get("acceptance_phase") == "PRE_FLIGHT_BUG_DISCOVERY_NOT_THREE_ROUND_ACCEPTANCE":
            evidence_root = ROOT / "official_muse/semifinal/sprint005/zc05/preflight"
        else:
            require(identity.get("acceptance_phase") == "FROZEN_THREE_ROUND_ACCEPTANCE",
                    "Formal round evidence requires explicit final freeze phase")
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

    def _unique(self, key, widget_type, pane_key, visual_proof):
        rows = self.snapshot()
        found = [w for w in rows if w.get("ty") == widget_type
                 and (w.get("i") == key or w.get("t") == key)]
        assert len(found) == 1, f"Expected exactly one visible {widget_type}: {key}; got {len(found)}"
        widget = found[0]
        panes = [w for w in rows if w.get("i") == pane_key and w.get("w") == widget.get("w")]
        require(len(panes) == 1, "Missing unique corresponding pane/container")
        check_visible_widget(widget, panes[0], self.identity["remote_window_rect"])
        require(visual_proof and Path(visual_proof).is_file(), "No inspected native-image proof; BLOCKED, scroll/capture first")
        proof = json.loads(Path(visual_proof).read_text())
        image = self.path / proof["image_file"]
        require(image.parent == self.path and image.is_file(), "Missing native visual evidence in this attempt")
        require(hashlib.sha256(image.read_bytes()).hexdigest() == proof["image_sha256"], "Native visual evidence changed")
        require(proof["native_window_id"] == self.identity["native_window_id"]
                and proof["widgets_sha256"] == widgets_digest(rows), "Visual proof is for another window or UI state")
        require(proof.get("inspected_at_utc") and proof.get("observed"), "Native image has not been inspected")
        controls = [row for row in proof.get("controls", []) if row.get("key") == key
                    and row.get("rect") == widget["r"] and row.get("pane_rect") == panes[0]["r"]]
        require(len(controls) == 1 and controls[0].get("fully_visible") is True,
                "No independent native-image confirmation that the complete control is visible")
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

    def click(self, key, pane_key, visual_proof):
        widget = self._unique(key, "Button", pane_key, visual_proof)
        x, y, width, height = widget["r"]
        self._journal({"event": "BUTTON_SELECTED", "widget": widget})
        return self._input_once("/click", w=widget["w"],
                                x=int(x + width / 2), y=int(y + height / 2))

    def type(self, key, value, pane_key, visual_proof):
        widget = self._unique(key, "TextInput", pane_key, visual_proof)
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
        require(inside(widget["r"], self.identity["remote_window_rect"], margin=0), "Scroll pane exceeds window bounds")
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
        rows = self.snapshot()
        subprocess.run(["/usr/sbin/screencapture", "-x", "-l", window, str(target)], check=True)
        save_json(target.with_suffix(".visual-template.json"), {
            "image_file": filename, "image_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "native_window_id": self.identity["native_window_id"], "widgets_sha256": widgets_digest(rows),
            "inspected_at_utc": None, "observed": None, "controls": []})
        self._journal({"event": "NATIVE_CAPTURE", "native_window_id": window,
                       "file": filename, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return target


if __name__ == "__main__":
    print(__doc__)
