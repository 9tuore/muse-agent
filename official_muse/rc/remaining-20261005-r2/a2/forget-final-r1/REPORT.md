# A2 Final-source forget and isolation addendum

Status: **FIXTURE_PASS** for the narrow affected paths. Whole product remains **PARTIAL**.

## Frozen binding

Readable source `5e9318464390741f31c5deb12cf94571521aefd22efe2d02d1731ba0174c6f0a`; compact source `4ce3a734d94e1cedea8260f9b74ca54ce2a8339d0db2e6200f702b5f2bb71ee6`; real locked CardHost `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`. Serial own port8509, independent synthetic jail, default budget unchanged. Product files, production data, stable installation and other processes were not changed.

## Actual execution

| Run | Scope | Checks |
| --- | --- | --- |
| choose_old first process | Save, correct, conflicting claim, resolve, unchanged other history/sources, selected-only retrieval, duplicate resolution refusal |20 PASS|
| second new process | Restore resolved claim, actually invoke gm_forget, sanitize dependent/history/source data, value tombstones, reject pre-forget export and reindex |21 PASS|
| third new process | Restore after actual forget, deleted/empty claim/history/source state, tombstones, no retrieval, reject old import and reindex, clean primary/backup |12 PASS|
| other_project corrected timing | Both isolated retrieval contexts, reject cross-project resolution, unchanged primary/backup/activity/sources/tombstones |15 PASS|
| other_owner corrected timing | Both isolated retrieval contexts, reject cross-owner resolution, unchanged primary/backup/activity/sources/tombstones |15 PASS|
| Python independent disk readback | Three product snapshots clean, all source excerpts/history cleared, tombstone hashes, scope consistency, isolation bytes unchanged |20 PASS|

Runtime total83 PASS; independent disk checks20 PASS. This fills the actual-forget gap explicitly left in FINAL_CAPACITY_REPORT; it does not broaden that report to all Memory, GUI, OS or official full-chain acceptance.

## Retained initial failures and correction

The original existing fixture took its read-only baseline30ms after gm_save; final product emits the saved activity in a50ms timeout. Both isolation variants initially failed only `guard_activity_unchanged` (14 other checks PASS each). Independent baseline/final comparison confirms an unchanged prefix plus exactly one `memory saved` event, not a resolution event. Their complete original reports/logs/jails remain in this r1 directory.

Only the owned fixture waits150ms before that baseline. The same final product source and unchanged default budgets then pass both variants in `../forget-final-r2/`. Successful choose_old was not redundantly rerun. No failure was erased or silently reclassified as a pass.

## Evidence and limits

`PUBLIC_RESULT.json`, `READBACK.json`, `ORIGINAL_ACTIVITY_RACE.json`, first/restart/forgotten reports and corrected isolation reports are safe small evidence. Raw bundles/jails/export data/logs stay local and are excluded from staging. Synthetic pre-forget export and baseline intentionally retain the original synthetic texts so rejected reimport can be demonstrated. Cleanup claims apply to memory.json, memory.backup.json and memory-forget-candidate.json only.

`../run_forget.py` and `../readback_forget.py` reproduce these isolated checks with the retained locked Host/templates. They are local diagnostics, not a fresh-checkout portable installer. No real model, email, Calendar, production deletion or new permission was used. This is not a hidden-window visual screenshot test, UI_PARITY_PASS, READY or full-capacity forget guarantee.
