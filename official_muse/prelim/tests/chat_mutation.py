#!/usr/bin/env python3
"""Execute the concrete P0 chat cases against a frozen source. FIXTURE only."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
p=argparse.ArgumentParser()
p.add_argument("--probe",type=Path);p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
a=p.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False)
shutil.copytree(a.source.parent,a.out / "source-bundle")
source=(a.out / "source-bundle" / "main.splash").read_text()
r=regression_run.run_suite("chat_mutation",source,a.out / "source-bundle",a.out / "chat_mutation",8484,a.probe or Path(__file__).with_suffix(".splash"))
print(json.dumps(r,ensure_ascii=False));sys.exit(bool(r["failed"]))
