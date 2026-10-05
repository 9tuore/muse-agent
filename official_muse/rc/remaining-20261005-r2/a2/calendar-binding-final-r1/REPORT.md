# A2 final rc29 binding addendum

Status: **FIXTURE_PASS** for the four final affected variants. Overall product remains **PARTIAL**.

Final readable `61b5f814d65b981a30a5befadfe5a3d4b536070cecd0f0be764fe2a98319bfb8`, compact `abcd49f9ec3f831b3073b4de0a0e835af0bb70aff8df5b28515d1aa34bea4a40`, locked CardHost `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`. Actual production functions, asynchronous synthetic Host replies, real jailed storage, owned serial port8509. Defaults unchanged; no real model, system Calendar, SMTP, permissions or production data.

| Final variant | Actual verification | Checks |
|---|---|---:|
|dense|63 memories,16 chats,32 Goals,127 Runs/actions,32 links,64 receipts; real phased approve/write/get/readback/receipt/Goal/result Memory|14 PASS|
|duplicate|Second click while pending preserves original approval; exactly one synthetic create, complete verified result|14 PASS|
|owner_after_accept|After real accepted action state, commit changed Goal owner; preserve accepted external evidence, stop with reconciliation error, no artifact/result Memory/completion or replay|13 PASS|
|payload_during_get|After get queued, commit changed original action payload; independent readback refuses changed binding, accepted state retained, no result/completion or replay|13 PASS|

Final-source total **54 runtime checks** plus **40 independent Python disk checks**. Disk comparison verifies unchanged historical records/Memory/source/link/receipt arrays, consistent result/action/Run/receipt identity on success, and accepted/not-completed state with no artifact/new receipt/new Memory on post-accept rejection. All pass.

## Version-aware prior results

`../CALENDAR_CALLBACK_REPORT.md` documents80 checks plus26 disk checks at earlier readable464/compactdb1. This includes original five门槛54, actualboot_restore no-action no-dispatch, and explicit create/update recovery26: old Run failed, same Goal v2planned, operation preserved, duplicate recovery unchanged,128 Run bound rejects further retry without mutation or host. These were not rerun wholesale on61 source.

`FUNCTION_BINDING.json` verifies17 of18 reviewed front-stage/restart/recovery helpers unchanged from464 to61. Only calendar_execute_step changed among those helpers (new write-binding persistence before dispatch); dense/duplicate were rerun on final61. Previous request/Goal-version rejection occurred before the newphase4 change, but retain their original observed SHA. No aggregation disguises prior-source tests as final-source reruns.

## Product fixes and observed failures

A2 found busy double-confirmation clearing calendar_preview and cancelling the initial approval. Root fixed busy early-return; actual final duplicate passes. Root also split execute/accepted/readback/finish callbacks without raising budgets, captures original update event before dispatch, binds original source/owner fields excluding lifecycle status, persists write_binding before dispatch, and checks original action payload across readback ticks. The two final post-accept tests demonstrate rejection with accepted evidence preserved.

Old baseline and all failed/errored attempts remain: fixture omitted core_boot_memory, duplicate initial timeout, in-memory-only version mutation mismatch, restart missing test widgets. See `../CALENDAR_CALLBACK_ERROR_SUMMARY.json`. No runtime failure is erased; no product fix was made by changing a test expectation. A2 did not write product/Host/SDK code, touch stable app or production data, commit or push.

Old5e dense also passed, so this fixture does not reproduce the native time-budget failure or prove all workloads fixed. Actual update/delete callbacks, system EventKit, native Shell, visual UI parity and source-digest/claim-revision mutation variants remain outside A2 verification. Root owns native integration and acceptance. This addendum supersedes the earlier report's specific untested owner/action-payload gap only; other limits remain.

## Evidence and staging

PUBLIC_RESULT.json, READBACK.json, FUNCTION_BINDING.json, summary and four first/report.json files bind the actual runs. Corresponding case probe.splash files are safe synthetic test inputs. CALENDAR_BINDING_EVIDENCE_MANIFEST.json hashes all small whitelisted files. Bundles, state, seed profiles, raw logs, databases/screenshots remain local. Own port8509 was closed after tests.

Runners require retained locked Host and A2 synthetic profile templates, so no fresh-checkout portability or installed-package claim. No READY, UI_PARITY_PASS, genuine external action or actual model invocation is claimed.
