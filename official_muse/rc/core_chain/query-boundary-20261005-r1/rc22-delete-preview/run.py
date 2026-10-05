#!/usr/bin/env python3
"""Actual CardHost, synthetic transport, delete preview only. No confirmation."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASES = ("allowed", "wrong_id", "title_mismatch", "non_test", "nil_selected", "prefix_only", "truncated_id",
         "legacy_phase2", "legacy_test", "legacy_final", "legacy_r2", "space_boundary", "newline_boundary", "regex_dot", "regex_alternative")

if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--out") + 1]).resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    spec = importlib.util.spec_from_file_location("query_boundary_runner", HERE.parent / "run.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.CASES, runner.HELPER_CASES = CASES, ()
    raise SystemExit(runner.main())
