#!/usr/bin/env python3
"""Prepare the pending acceptance packet, or validate it without any GUI call."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = ROOT / "official_muse/semifinal/evidence/user-acceptance-3rounds"
CATALOG = HERE / "cases.json"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def manifest():
    files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if path.is_file() and path.name != "evidence-manifest.json":
            files.append({"path": str(path.relative_to(EVIDENCE)),
                          "bytes": path.stat().st_size,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(EVIDENCE / "evidence-manifest.json", {
        "schema": 1, "stage": "PREPARATION_ONLY",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gui_evidence_count": 0, "files": files,
        "note": "Hashes cover prepared documents and pending indices, not GUI execution."})


def prepare():
    if EVIDENCE.exists() or (ROOT / "MUSE_USER_ACCEPTANCE_MATRIX.md").exists():
        raise SystemExit("Packet already exists; refusing to overwrite evidence.")
    catalog = json.loads(CATALOG.read_text())
    functions = catalog["functions"]
    matrix = {"schema": 1, "stage": "PREPARATION_ONLY",
              "candidate_identity": None, "candidate_status": "AWAITING_FREEZE",
              "functions": functions, "results": []}
    for number in range(1, 4):
        round_id = f"round-{number:02d}"
        entries = []
        for function in functions:
            result = {"test_id": function["test_id"], "round_id": round_id,
                      "status": "NOT_TESTED", "started_at_utc": None,
                      "ended_at_utc": None, "candidate_id": None,
                      "attempts": [], "evidence": [], "bug_ids": [],
                      "next_attempt_path": f"{round_id}/{function['test_id']}/attempt-01"}
            entries.append(result)
            matrix["results"].append(result)
        write_json(EVIDENCE / round_id / "round-index.json", {
            "schema": 1, "round_id": round_id, "stage": "PREPARATION_ONLY",
            "scenario": functions[0]["rounds"][number - 1]["scenario"],
            "candidate_identity": None, "results": entries})
    write_json(EVIDENCE / "acceptance-matrix.json", matrix)
    rows = ["# Muse 用户功能三轮验收矩阵", "", "当前阶段：**准备完成，GUI 尚未交接**。所有结果为 `NOT_TESTED`；没有 PASS。", "",
            "最终候选以总控后续冻结的包、宿主、插件 SHA256 和实际运行身份为准。源码与旧根 bundle 的差异仅是覆盖线索，不是候选身份。", "",
            "每个功能三轮：正常流程；交互变化（取消、切会话、改时间等）；正常退出后的重启与重复。", "",
            "| 用例 | 可见功能/分支 | 第一轮 | 第二轮 | 第三轮 | 实现范围 |", "| --- | --- | --- | --- | --- | --- |"]
    for function in functions:
        rows.append(f"| {function['test_id']} | {function['feature']} | NOT_TESTED | NOT_TESTED | NOT_TESTED | PENDING_GUI_DISCOVERY |")
    rows.extend(["", f"共 {len(functions)} 个原子覆盖项、{len(matrix['results'])} 个独立结果格。", "",
                 "用例步骤和前置条件见 `official_muse/semifinal/sprint005/zc05/cases.json`；可恢复结果索引见 `official_muse/semifinal/evidence/user-acceptance-3rounds/acceptance-matrix.json`。", "",
                 "最终 GUI 中新增的入口追加独立用例；不可达功能经实际发现后再记 NOT_IMPLEMENTED，不预设通过。", ""])
    (ROOT / "MUSE_USER_ACCEPTANCE_MATRIX.md").write_text("\n".join(rows))
    report = """# Muse 用户三轮验收报告

当前结论：**NOT_TESTED**。本文件只是正式验收的准备记录，尚无最终固定候选 GUI 实测。

已准备 81 个原子覆盖项、243 个三轮结果格。生产端口 9696 未访问，未启动或点击任何宿主窗口。没有沿用开发者 PASS、历史报告、编译或模型文字作为验收证据。

最终验收身份、开始结束时间、执行计数、失败与限制待专属窗口交接后填写。合成模型/邮件/输运只能标 SIMULATION_PASS；真实外部结果缺前置条件时标 BLOCKED 或 HUMAN_REQUIRED。

每项每轮须有独立 attempt 目录，保存候选及运行身份、实际 UI 步骤、鼠标键盘请求日志、未修改原生窗口截图、逐张视觉检查记录、必要的持久化独立读回、时间及 SHA 清单。失败原样保留并报告 Bug；修复后在同一新冻结候选重新完成受影响三轮。

所需交接：固定候选 package/main/manifest/host/plugin 哈希；ZC-05 独占 fixture 端口、PID、原生窗口 ID、数据目录及正常重启命令；明确 FIXTURE_ONLY 的合成用户、邮箱、日历和模型；只读的独立收件与持久化结果出口。

覆盖包括基础交互、Memory、Mail、官方 Calendar、行动链及 Agentic。旧私有系统日历 UI 的不可达状态与窄范围自动安排是否有可见实现，需在冻结 GUI 独立发现，尚未判定。
"""
    (ROOT / "MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md").write_text(report)
    (EVIDENCE / "acceptance-summary.md").write_text(report)
    manifest()


def validate():
    matrix = json.loads((EVIDENCE / "acceptance-matrix.json").read_text())
    ids = [row["test_id"] for row in matrix["functions"]]
    assert len(ids) == len(set(ids)) == 81
    pairs = [(row["test_id"], row["round_id"]) for row in matrix["results"]]
    assert len(pairs) == len(set(pairs)) == 243
    assert Counter(round_id for _, round_id in pairs) == {f"round-{i:02d}": 81 for i in range(1, 4)}
    for number in range(1, 4):
        index = json.loads((EVIDENCE / f"round-{number:02d}" / "round-index.json").read_text())
        assert len(index["results"]) == 81
    if matrix["stage"] == "PREPARATION_ONLY":
        assert matrix["candidate_identity"] is None
        assert all(row["status"] == "NOT_TESTED" and not row["evidence"] and not row["attempts"] for row in matrix["results"])
    packet = json.loads((EVIDENCE / "evidence-manifest.json").read_text())
    for entry in packet["files"]:
        path = EVIDENCE / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    print(json.dumps({"validation": "PREPARATION_PACKET_VALID", "functions": 81,
                      "result_slots": 243, "statuses": dict(Counter(r["status"] for r in matrix["results"])),
                      "gui_calls": 0, "candidate_frozen": False}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    validate() if args.validate else prepare()
