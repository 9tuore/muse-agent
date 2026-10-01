"""Drive one real Muse Goal in a visible card-host or OctoSense Shell.

The test uses synthetic text supplied by the caller and audits the app jail.
`--model` requires a real configured Shell model service; a card-host without
that service must not be counted as a model pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from remote import Remote


def wait_notice(remote: Remote, expected: str, seconds: float) -> str:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        actual = str(remote.find("notice").get("t") or "")
        if expected in actual:
            return actual
        if any(word in actual for word in ("失败", "错误", "未完成", "未通过", "暂不可用", "超时")):
            raise AssertionError(f"unexpected notice: {actual}")
        time.sleep(0.25)
    raise AssertionError(f"notice did not become {expected!r}; last={actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("jail", type=Path, help="isolated <app-data>/muse-goals")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--model", action="store_true")
    parser.add_argument("--shot", type=Path)
    args = parser.parse_args()

    remote = Remote(args.port)
    remote.click("对话")
    remote.set_text("goal_input", args.goal)
    remote.click("设为目标")
    remote.set_text("source_input", args.source)
    remote.click("生成计划")
    wait_notice(remote, "计划已生成", 10)

    if args.model:
        remote.click_scroll("请模型给建议", "detail_view")
        wait_notice(remote, "模型建议已返回", 120)

    remote.click_scroll("批准并执行", "detail_view")
    wait_notice(remote, "已保存并重新读取核对结果", 30)
    state = json.loads((args.jail / "goals.json").read_text(encoding="utf-8"))
    matching = [goal for goal in state["goals"] if goal["goal"] == args.goal]
    assert len(matching) == 1, f"expected exactly one Goal, found {len(matching)}"
    goal = matching[0]
    assert goal["status"] == "completed"
    result_path = args.jail / goal["result_path"]
    payload = result_path.read_bytes()
    result = json.loads(payload)
    assert result["task_id"] == goal["id"]
    assert result["source_text"] == args.source
    matching_runs = [r for r in state["runs"] if r["goal_id"] == goal["id"]]
    assert len(matching_runs) == 1 and matching_runs[0]["status"] == "completed"
    if args.model:
        assert result["model_summary"], "model call returned no persisted summary"
    if args.shot:
        remote.shot(args.shot)
    print(json.dumps({
        "goal_id": goal["id"],
        "run_id": matching_runs[0]["id"],
        "result": str(result_path),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "model_summary_present": bool(result.get("model_summary")),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
