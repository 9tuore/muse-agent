#!/usr/bin/env python3
"""Wait for bounded product receipt phases; retain old fixed-delay failures."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
A2 = ROOT / "official_muse/rc/remaining-20261005-r2/a2"
sys.path.insert(0, str(A2))
import run_receipt
out = (ROOT / sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=False)
source = (ROOT / "official_muse/app/source/main.splash").read_text()
os.environ["MUSE_CARD_HOST"] = str(run_receipt.HOST)
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import regression_run
regression_run.existing.WIDGET = regression_run.existing.WIDGET.replace("    Label{text:", "    mail_test_id := TextInput{width: Fill}\n    mail_to := TextInput{width: Fill}\n    mail_subject := TextInput{width: Fill}\n    mail_body := TextInput{width: Fill}\n    Label{text:", 1)
real_popen = subprocess.Popen
results = {}
for case in ["linked63_dense", "linked64", "linked63_completed_dense"]:
    folder = out / case
    folder.mkdir()
    seed = run_receipt.profile(case)
    if case == "linked63_completed_dense":
        seed["goals.json"]["goals"][0]["status"] = "completed"
        seed["goals.json"]["runs"][0]["status"] = "completed"
    text = (A2 / "receipt.splash").read_text().replace("__CASE__", case).replace("__MEMORY_COUNT__", str(len(seed["memory.json"]["claims"]))).replace("__ACTION_COUNT__", str(len(seed["goals.json"]["actions"])))
    # The phase counter is bounded, and final checks are identical to the old suite.
    text = text.replace("fn a2_assert(){", "let result_wait = 0\nfn a2_assert(){\n    if mail_verifying && result_wait < 100 { result_wait = result_wait + 1 start_timeout(0.05,|| a2_assert()) return }")
    probe = folder / "probe.splash"
    probe.write_text(text)
    def seeded(command, *args, **kwargs):
        state = Path(command[command.index("--app-data") + 1]) / "muse-goals"
        state.mkdir(parents=True)
        for name, value in seed.items():
            (state / name).write_text(run_receipt.encoded(value))
        return real_popen(command, *args, **kwargs)
    regression_run.subprocess.Popen = seeded
    try:
        results[case] = regression_run.run_suite("mail_calendar_chain", source, ROOT / "official_muse/app/bundle", folder / "first", 8509, probe)
        print(case, json.dumps(results[case]), flush=True)
    finally:
        regression_run.subprocess.Popen = real_popen
(out / "report.json").write_text(json.dumps(results, indent=2) + "\n")
raise SystemExit(int(any(result["failed"] for result in results.values())))
