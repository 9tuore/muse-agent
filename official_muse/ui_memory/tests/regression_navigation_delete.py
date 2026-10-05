#!/usr/bin/env python3
"""Dense synthetic Goal navigation and independent delete readback on the real CardHost."""
import json, os, subprocess, sys
from pathlib import Path
import receipt_fixture
import regression_run
ROOT=Path(__file__).resolve().parents[3]
out=(ROOT/sys.argv[1]).resolve(); out.mkdir(parents=True,exist_ok=False)
seed=receipt_fixture.profile("linked63_dense")
for goal in seed["goals.json"]["goals"]:
    goal.update(goal="合成事项 "+goal["id"], source="合成来源", items=[], schema=1)
seed["goals.json"]["actions"][0].update(service="calendar.delete",goal_id="",run_id="",plan_revision=0,target_scope="a2-calendar",payload_json=receipt_fixture.encoded(dict(calendar_id="a2-calendar",event_id="a2-event")))
real_popen=subprocess.Popen
regression_run.existing.WIDGET=regression_run.existing.WIDGET.replace("    Label{text:","    mail_test_id := TextInput{width: Fill}\n    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n    Label{text:",1)
def seeded(command,*args,**kwargs):
    state=Path(command[command.index("--app-data")+1])/"muse-goals"; state.mkdir(parents=True)
    for name,value in seed.items(): (state/name).write_text(receipt_fixture.encoded(value))
    return real_popen(command,*args,**kwargs)
regression_run.subprocess.Popen=seeded
try:
    result=regression_run.run_suite("mail_calendar_chain",(ROOT/"official_muse/app/source/main.splash").read_text(),ROOT/"official_muse/app/bundle",out/"first",8508,Path(__file__).with_name("regression_navigation_delete.splash"))
    print(json.dumps(result),flush=True)
finally: regression_run.subprocess.Popen=real_popen
(out/"report.json").write_text(json.dumps(result,indent=2)+"\n")
raise SystemExit(int(bool(result["failed"])))
