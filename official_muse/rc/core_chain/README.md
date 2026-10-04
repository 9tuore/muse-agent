# Muse core-chain test maintenance

These tests run actual production Splash functions in isolated card-host storage with **synthetic Host transport**. They do not prove live Mail/Calendar/model inference or final GUI acceptance. ModelHost protocol tests separately use a real isolated Shell with a localhost HTTP fixture.

## Source sharing boundary

`PUBLIC_SOURCE_ALLOWLIST.json` lists exact repository-relative files for controller staging. Do not stage this directory recursively. `evidence/`, copied production source, repeated bundles, private/state data and raw logs remain local. Public summaries contain only hashes, counts, classifications and local evidence references. Original failures are preserved, not deleted or relabeled as success.

V8 with the 4K-frame CardHost passed the specified production-function fixtures on their first attempts. Real final Shell/ModelHost and live acceptance remain pending. Historical RC5 v5 successes and failures are retained separately. Consult `PUBLIC_TEST_SUMMARY.json` and `PUBLIC_FAILURE_INDEX.json`.

## Required existing helpers

Keep these existing repository helpers; do not copy them into this directory:

- `official_muse/ui_memory/tests/regression_run.py`
- `official_muse/round2/tests/runtime_probe.py`
- `official_muse/phase2/tests/remote.py`

Python 3.9+ and the controller-supplied actual signed CardHost/Shell/Hub binaries are required. Do not install or replace the user's production app/model/account environment to run these tests.

## Production-function replay

Controller supplies a final compact source and exact CardHost hash. Verify those first. Use a fresh output directory each run and one card-host process at a time. Port 8509 must be free.

```sh
MUSE_CARD_HOST='/ABS/FINAL/CARD/HOST/Contents/MacOS/card-host' \
python3 official_muse/rc/core_chain/run_fault_matrix.py \
  --source /ABS/FINAL/COMPACT/main.splash \
  --out official_muse/rc/core_chain/evidence/final-fault

MUSE_CARD_HOST='/ABS/FINAL/CARD/HOST/Contents/MacOS/card-host' \
python3 official_muse/rc/core_chain/run_t18.py \
  --source /ABS/FINAL/COMPACT/main.splash \
  --out official_muse/rc/core_chain/evidence/final-core

MUSE_CARD_HOST='/ABS/FINAL/CARD/HOST/Contents/MacOS/card-host' \
python3 official_muse/rc/core_chain/run_t18.py \
  --source /ABS/FINAL/COMPACT/main.splash \
  --out official_muse/rc/core_chain/evidence/final-proposal \
  --proposal-restart
```

Expected production-function checks: twenty fault cases, three independent fault restarts, core 28 plus restart 4, proposal 25 plus restart 6. Do not use the historical `--storage-wrappers` patch-suggestion mode for release acceptance. No real accounts or paid models are used. Hidden-window logic results are not visual evidence.

## Real ModelHost protocol fixture

Follow `MODELHOST_FINAL_RUNBOOK.md`: fresh key-free localhost candidate, explicit final source/Shell/Hub hashes and controller-trusted Anchor; actual Hub catalog verification; preflight before Shell/backend startup. Shell 8490 and backend 8879 are reserved. Protect other instances. Four protocol scenarios and unchanged budgets must pass. A successful protocol fixture still does not prove real inference or RC_READY.

Only stop processes created by the test. Preserve failure logs and isolated data locally. Controller owns production changes, public staging, commits and any real-account operation.
