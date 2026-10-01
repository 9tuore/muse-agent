"""Audit persisted Phase 2 state in an explicitly supplied test app jail.

This reads files only. It neither invents a service response nor upgrades a
fixture result into a Shell result. Pass the isolated Muse app-data directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit(jail: Path, min_goals: int, require_completed: bool) -> dict:
    state = read(jail / "goals.json")
    assert state["schema"] == 2
    goals = state["goals"]
    runs = state["runs"]
    actions = state["actions"]
    goal_ids = [g["id"] for g in goals]
    run_ids = [r["id"] for r in runs]
    request_ids = [a["id"] for a in actions]
    assert len(goals) >= min_goals, f"only {len(goals)} goals"
    assert len(goal_ids) == len(set(goal_ids)), "duplicate Goal ID"
    assert len(run_ids) == len(set(run_ids)), "duplicate Run ID"
    assert len(request_ids) == len(set(request_ids)), "duplicate external request ID"
    assert not state["selected_id"] or state["selected_id"] in goal_ids
    for run in runs:
        assert run["goal_id"] in goal_ids, f"orphan Run {run['id']}"
    for action in actions:
        assert action["goal_id"] == "" or action["goal_id"] in goal_ids
        assert action["run_id"] == "" or action["run_id"] in run_ids
        if action["run_id"]:
            linked = next(r for r in runs if r["id"] == action["run_id"])
            assert linked["goal_id"] == action["goal_id"]
    completed = [g for g in goals if g["status"] == "completed"]
    if require_completed:
        assert completed, "no completed Goal"
    verified_results = []
    for goal in completed:
        path = jail / goal["result_path"]
        assert path.is_file(), f"missing result {path}"
        result = read(path)
        assert result["task_id"] == goal["id"], f"wrong result owner {path}"
        verified_results.append(str(path))
    memory_path = jail / "memory.json"
    claims = []
    if memory_path.is_file():
        memory = read(memory_path)
        assert memory["schema"] == 1
        claims = memory["claims"]
        sources = {(s["source_id"], s["scope"]["account"]) for s in memory["sources"]}
        for entry in claims:
            document = entry["document"]
            account = document["scope"]["account"]
            payload = document["payload"]
            if payload["deleted"]:
                assert not payload["value"] and not payload["source_ids"]
            else:
                for source_id in payload["source_ids"]:
                    assert (source_id, account) in sources, f"orphan memory source {source_id}"
        for tombstone in memory["forget"]:
            assert (tombstone["source_id"], tombstone["account_scope"]) in sources
    activity_path = jail / "activity.json"
    events = read(activity_path) if activity_path.is_file() else []
    activity_unlinked = 0
    for event in events:
        event_goal = event.get("goal_id") or ""
        event_run = event.get("run_id") or ""
        if event_goal and event_goal not in goal_ids:
            # 0.1.10 kept only its current Goal; older Activity may outlive it.
            activity_unlinked += 1
        elif not event_goal and event.get("task_id") and event["task_id"] not in goal_ids:
            activity_unlinked += 1
        if event_run:
            assert event_run in run_ids, f"orphan Activity Run {event_run}"
    return {
        "goal_count": len(goals),
        "run_count": len(runs),
        "action_count": len(actions),
        "memory_claim_count": len(claims),
        "activity_event_count": len(events),
        "activity_without_current_goal": activity_unlinked,
        "selected_id": state["selected_id"],
        "completed_result_readbacks": verified_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jail", type=Path)
    parser.add_argument("--min-goals", type=int, default=1)
    parser.add_argument("--require-completed", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(args.jail, args.min_goals, args.require_completed), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
