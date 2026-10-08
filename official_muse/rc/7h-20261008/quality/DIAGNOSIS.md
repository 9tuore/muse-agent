# Quality / cold startup evidence

The rc10 baseline is the exact business compact SHA `0caaee7374e2446abafffeda33fe24bdcf8f9125757f881d664efabb83c36686`, unchanged Host `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`. No private account/profile copied. No external service writes, model submissions or budget changes.

## Prior three failures

`prior-cold-r3.json`: cold02/09 outer launcher timed out after40s, leaving missing logs/snapshot; cold03 previous Shell remained alive after quit. These records cannot establish a VM budget failure. The existing success range was18.81–49.37s to content. All historical failures retained in original evidence.

## Current observation

`baseline-rc10-r1/report.json`: actual visible Shell, editable input16.99s;16sessions/256longmessages,64claims/65sources and64mailseen restored. Protected files unchanged; all six navigation pages accessible; no error/budget lines. Correct visible screenshot inspected. This single pilot is not the final10+5matrix.

`profile-rc10-r2` and `profile-granular-r1` are explicitly diagnostic source variants. Timing from granular callback profile shows chat validation128callbacks:34.66ms inclusive total but~9.2s wall; memory index18+validation65callbacks:~3.4s wall,84.41ms execution. Calendar0.43ms, Mail0.55ms. This supports bounded slice-size tuning after worst-case tests, not raising Host execution budgets or skipping validation. Diagnostic timing writes add overhead.

Initial diagnostic publication reused rc10 version and was correctly refused (`diagnostic-publish-refused.txt`). Subsequent diagnostic versions are local-only and uniquely named.

## Next required gate

Root freezes candidate source/bundle/Host SHA. Run10complete new-process cold launches +5same-Shell app reopens with input edit/readback, nonempty memory/task recovery, unchanged protected bytes and no duplicate effects/errors. Standard official CLI provenance/check/scan must be bound separately; local rehearsal signatures are not official admission/publication.

## Chat slice and official CLI unit (2026-10-08)

Root changed only chat validation slice2→8; businessSHA `f5d45de6`. Four actual visible checks passed:256long messages,256entries each with6refs/16sourceIDs, bad final entry fail-closed with original/backup preserved, and corrupted primary recovered from intact backup without overwriting either. Input9.78/9.92s for valid stress variants versus16.99s baseline pilot; observations are not statistical claims. Evidence `chat-slice-checks.json`.

Official App Hub78dfda5f source242Git blobs matched official commit tree; archivegzip bytes differ from historical archive, explicitly retained in binding. CLI build d60570a5 passed locked offline release after isolated headless lock resolution. No admission Rust/library source changes or repository SDK lock changes. Generated exact headlessCargo manifests/lock retained under `official-cli-reproduction`.23upstream bundle_admission tests passed. Baseline rc10 stamp/check/scan allPASS with unsigned warning; review packet creation is not publication. Final candidate Gate awaits Root freeze.

## Preserved task-store failures

`corrupt-goal-shape-r1` and `corrupt-goal-tail-r1` reproduce two real cold-start blockers on the same businessSHA `f5d45de6`. A schema2 store whose `goals` is a string passes the current validator, then `core_goal_index` raises `cannot index 0 on string`. A goals array containing only `{id:"broken-goal"}` also passes, then task rendering raises `property model_summary not found`. Both leave the expected Chat focus/input unrestored; original files remain intact. These are FAIL, not startup successes. The first raw report's legacy record counter measured the corrupted string length as12; it is not12 valid goals. The runner now reports non-array counts as null.

Root received exact errors and a minimal recommendation: native root/array/type checks plus required render fields; corrupt files must fail closed or recover the intact backup without overwriting the originals. Quality does not modify the core implementation.

Pinned L0 dependency5991dfae source33Git blobs match official tree `c4c531f5`; provenance is recorded in `OFFICIAL_CLI_BUILD.json` alongside App Hub provenance. The rebuilt CLI's dependency resolution remains explicitly separate from the historical binary.

## Real-chat continuation on cceeaa009

Eight real visible Shell storage variants passed: prior bad shape/tail now fail closed without overwriting originals; valid nonempty Goal and intact shape/Run/Action backups restore a visible real card; corrupt Run/Action stores are refused with a clear error and no execute button. Same16sessions/256messages/64claims/65sources. `TASK_VARIANTS_SUMMARY.json` binds actual snapshots/reports. Local synthetic source has no live credentials and no model or external action was submitted.

10cold+5reopen is **FAIL/incomplete**. Matrixr1 got5cold successes then a navigation-driver clipping failure; actual Calendar became reachable with40px scroll. Matrixr2 then exposed an already-expanded More toggle mistake; bounded scan-before-toggle driver fixed and actual five-page navigation passed. Both driver failures remain. Matrixr3 cold01 had a **real runtime failure**: source preparation at227355/484257 bytes, kit_shared.rs script time budget exceeded(vm.rs:916), no content/input. No raising of deadlines/budgets and no passing-by-retry claim. Root needs to fix/freeze a new candidate before final matrix. Source/Host SHA in `QUALITY_REAL_CHAT_CHECKPOINT.json`.

Verified official CLI stamp/check/scan PASS in `official-gate-shape-r1`, not independent publication review or Calendar-extension acceptance.

Independent minimal actual Calendar HostService probe (sameHost, no product watcher/guard) returned status not_determined and request_access callback after2.117s with is_ok=true, not_determined, no error. Thus request dispatch occurs but grant remains absent. No popup proof, no automated system Allow, no Calendar CRUD. Source/UI/actual callback evidence in `calendar-minimal-live-r1`; native bridge ignores granted bool. This excludes simply assuming product pending-click logic is the cause. Full handoff in `HANDOFF_REAL_CHAT.md`.
