#!/usr/bin/env python3
"""Production attachment path, synthetic transport and real jailed storage only."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--port", type=int, default=8510)
a = p.parse_args()
a.source = a.source.resolve(strict=True)
a.out = a.out.resolve()
regression_run.existing.HOST = regression_run.existing.HOST.resolve(strict=True)
result = regression_run.run_suite("mail_calendar_chain", a.source.read_text(), ROOT / "official_muse/app/bundle", a.out, a.port, Path(__file__).with_name("mail-attach-rc50.splash"))
print(json.dumps(result))
raise SystemExit(bool(result["failed"]))
