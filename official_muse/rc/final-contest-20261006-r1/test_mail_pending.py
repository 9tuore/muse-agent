#!/usr/bin/env python3
"""Exercise pending receipt archive with production functions, synthetic services."""
import argparse, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
regression_run.existing.HOST = regression_run.existing.HOST.resolve(strict=True)
p = argparse.ArgumentParser()
p.add_argument("--source",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
p.add_argument("--cases",nargs="+",default=["unknown","accepted","unknown_linked","accepted_linked","unknown_corrupt","accepted_corrupt"])
a = p.parse_args(); a.out = a.out.resolve(); a.source = a.source.resolve(strict=True); a.out.mkdir(parents=True,exist_ok=False)
source = a.source.read_text(); template = (HERE / "mail_pending.splash").read_text()
report = {"kind":"FIXTURE_PRODUCTION_MAIL_GUARDS","real_mail":False,"real_calendar":False,"source_sha256":hashlib.sha256(source.encode()).hexdigest(),"cases":{}}
for case in a.cases:
    parts=case.split("_",1); state=parts[0]; variant=parts[1] if len(parts)>1 else "flow"
    assert state in ("unknown","accepted") and variant in ("flow","linked","corrupt")
    probe=a.out / (case+".splash");probe.write_text(template.replace("__STATE__",state).replace("__VARIANT__",variant))
    try:
        result=regression_run.run_suite("incoming_suite",source,ROOT / "official_muse/app/bundle",a.out / case,8510,probe)
    except Exception as error:
        result={"failed":[type(error).__name__],"error":str(error)}
    report["cases"][case]=result
    (a.out / "RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(case,json.dumps(result,ensure_ascii=False),flush=True)
report["pass"]=all(not x["failed"] for x in report["cases"].values())
(a.out / "RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
raise SystemExit(not report["pass"])
