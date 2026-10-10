#!/usr/bin/env python3
"""Existing Memory behavior plus shared-view checks in a real reference VM.

Synthetic data and transport, real jailed storage. No model, external write,
native approval, full Shell or final-candidate claim.
"""
import argparse
import importlib.util
import json
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--suite", choices=("memory", "task"), default="memory")
    parser.add_argument("--port", type=int, default=8711)
    parser.add_argument("--host", type=Path, required=True, help="Explicit existing reference VM executable")
    args = parser.parse_args()
    host = args.host.resolve(strict=True)
    if not os.access(host, os.X_OK):
        raise ValueError("Reference Host is not executable")
    os.environ["MUSE_CARD_HOST"] = str(host)
    out = args.out.resolve()
    if not out.is_relative_to(ROOT / "build"):
        raise ValueError("Fixture output must stay in this worktree build/")
    out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location("dsl_vm_runner", ROOT / "official_muse/ui_memory/tests/regression_run.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    if args.suite == "task":
        probe = ROOT / "official_muse/semifinal/stability_integration/task_context_view_suite.splash"
        suite_kind = "task_focus"
    else:
        suite = (ROOT / "official_muse/ui_memory/tests/memory_suite.splash").read_text()
        anchor = '    mr.M01_cross_session = ctx.hits.len() == 1 && ctx.text.search("三项重点") >= 0'
        if suite.count(anchor) != 1:
            raise ValueError("Memory suite anchor changed")
        suite = suite.replace(anchor, anchor + '''
        mr.DSL01_retrieval_version = ctx.text.search("muse.view/1") >= 0
        mr.DSL02_retrieval_read_only = ctx.text.search("read_only") >= 0 && ctx.text.search("tool_authority") >= 0
        let synthetic_record = {status: "unknown"}
        synthetic_record["scope"] = {project_id: "synthetic-project" owner_id: "personal"}
        let view = dsl_view("memory_context",[synthetic_record]).to_json().parse_json()
        mr.DSL03_shared_roundtrip = view.schema_version == "muse.view/1" && view.kind == "memory_context" && view.read_only && !view.tool_authority
        mr.DSL04_unknown_preserved = view.records[0].status == "unknown"
        mr.DSL05_scope_preserved = view.records[0]["scope"].project_id == "synthetic-project" && view.records[0]["scope"].owner_id == "personal"
        mr.DSL06_context_bound = ctx.text.len() <= 2200 && ctx.hits.len() <= 6
    ''')
        marker = 'fs.write("memory-report.json",mr.to_json())'
        if suite.count(marker) != 1:
            raise ValueError("Memory suite result marker changed")
        transport = '''let metadata_calls=[]
    fn chain_fixture_request(method,args,cb){metadata_calls.push(method) cb({is_ok:false error:"Synthetic DSL fixture; no tools"})}
    '''
        probe = out / "probe.splash"
        probe.write_text(transport + suite.replace(marker,
            'mr.DSL07_no_tool_requests = metadata_calls.len() == 0\n    fs.write("probe.json",mr.to_json())'))
        suite_kind = "mail_calendar_chain"
    source = (ROOT / "official_muse/app/source/main.splash").read_text()
    try:
        result = runner.run_suite(suite_kind, source, ROOT / "bundle", out / "run", args.port, probe)
    except Exception as error:
        result = {"status": "ERROR", "error": str(error), "failed": ["probe_execution"]}
    result.update(boundary=__doc__.strip(), suite=args.suite,
                  source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  host_sha256=hashlib.sha256(host.read_bytes()).hexdigest(),
                  probe_sha256=hashlib.sha256(probe.read_bytes()).hexdigest())
    (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
