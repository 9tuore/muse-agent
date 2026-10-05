#!/usr/bin/env python3
"""Narrow production payload construction; synthetic Host transport only."""
import importlib.util
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
CASES=("routing","edit_mail","edit_calendar","time_formats")
if __name__=="__main__":
    out=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
    assert out.is_relative_to(HERE) and not out.exists()
    spec=importlib.util.spec_from_file_location("query_boundary_runner",HERE.parent/"run.py")
    runner=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.CASES,runner.HELPER_CASES=CASES,()
    raise SystemExit(runner.main())
