#!/usr/bin/env python3
"""Record one manually observed attempt; never derive PASS from a service log."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from ua_gui import candidate_key, check_data_dir, check_frozen_identity

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "official_muse/semifinal/evidence/user-acceptance-3rounds"
STATUSES = {"PASS", "SIMULATION_PASS", "FAIL", "BLOCKED", "HUMAN_REQUIRED", "NOT_IMPLEMENTED"}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def record(result_path):
    path = result_path.resolve()
    assert path.is_relative_to(EVIDENCE.resolve()) and path.name == "result.json"
    result = json.loads(path.read_text())
    assert result["status"] in STATUSES
    for field in ("test_id", "round_id", "started_at_utc", "ended_at_utc", "candidate_id", "expected", "observed"):
        assert isinstance(result[field], str) and result[field]
    assert result["actual_gui_steps"] and result["result_class"] in {
        "GUI_ONLY", "LOCAL_REAL_STORAGE", "FIXTURE_TRANSPORT", "LIVE_EXTERNAL", "NO_EXECUTION"}
    attempt = path.parent
    identity = json.loads((attempt / "identity.json").read_text())
    assert result["candidate_id"] == identity["candidate_id"]
    assert identity["owner_pid"] > 0 and identity["native_window_id"] > 0
    check_data_dir(identity)
    check_frozen_identity(identity)
    shots = sorted(attempt.glob("*.png"))
    inspection = json.loads((attempt / "visual-inspection.json").read_text())
    inspected = {row["file"] for row in inspection["images"] if row["observed"] and row["inspected_at_utc"]}
    assert shots and all(shot.name in inspected for shot in shots)
    if result["status"] in {"PASS", "SIMULATION_PASS"}:
        assert (attempt / "ui-actions.jsonl").stat().st_size > 0
        assert result["result_class"] != "NO_EXECUTION"
        if result["result_class"] == "FIXTURE_TRANSPORT":
            assert result["status"] == "SIMULATION_PASS"
        if result["result_class"] == "LIVE_EXTERNAL":
            assert not identity["fixture_only"]
        if result["readback_required"]:
            readback = attempt / "independent-readback.json"
            assert readback.exists() and json.loads(readback.read_text())["observed"]
    files = [{"path": str(p.relative_to(attempt)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
              "bytes": p.stat().st_size} for p in sorted(attempt.rglob("*"))
             if p.is_file() and p.name != "attempt-manifest.json"]
    write(attempt / "attempt-manifest.json", {"schema": 1, "files": files})
    matrix_path = EVIDENCE / "acceptance-matrix.json"
    matrix = json.loads(matrix_path.read_text())
    if matrix["candidate_identity"] is not None:
        assert matrix["candidate_identity"] == candidate_key(identity), "New runtime cannot reuse another candidate's prior rounds"
    else:
        matrix["candidate_identity"] = candidate_key(identity)
    matches = [row for row in matrix["results"] if row["test_id"] == result["test_id"]
               and row["round_id"] == result["round_id"]]
    assert len(matches) == 1
    row = matches[0]
    relative = str(attempt.relative_to(EVIDENCE))
    assert relative not in row["attempts"], "Attempt was already indexed; preserve the prior attempt and use a new directory"
    row.update({key: result[key] for key in ("status", "started_at_utc", "ended_at_utc", "candidate_id")})
    row["attempts"].append(relative)
    row["evidence"].append(str(path.relative_to(EVIDENCE)))
    row["bug_ids"] = list(dict.fromkeys(row["bug_ids"] + result.get("bug_ids", [])))
    matrix["stage"] = "ACCEPTANCE_IN_PROGRESS"
    write(matrix_path, matrix)
    round_path = EVIDENCE / result["round_id"] / "round-index.json"
    round_index = json.loads(round_path.read_text())
    round_index["stage"] = "ACCEPTANCE_IN_PROGRESS"
    round_index["results"] = [entry for entry in matrix["results"] if entry["round_id"] == result["round_id"]]
    write(round_path, round_index)
    print(json.dumps({"recorded": relative, "status": result["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    record(parser.parse_args().result)
