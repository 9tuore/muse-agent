# A2 rc29 Calendar callback and recovery verification

Status: **FIXTURE_PASS** for these seven narrow variants; whole product remains **PARTIAL**.

Frozen final readable `464cd4caa46ed88b1dde2231e4dc3d4249879707c1102a6e4bb977573bb87253`, compact `db1d828b3eee8bc41ef9ef5f9c32d1361577218d873af290da18c021694f7040`, locked real CardHost `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`. Actual production functions execute in serial owned port8509 and jailed synthetic storage, unchanged default budgets. Rendering is reduced to test widgets and Host transport is synthetic asynchronous data. No real model, EventKit, SMTP, production data or permissions.

## Results

| Variant | Actual path | PASS |
|---|---|---:|
| dense |63 memories,16 chats,32 Goals,127 prior Runs/actions,32 links,64 receipts; actual approve→split execute→accepted→get→verified→artifact/readback→result memory|14|
| duplicate |Second confirm while pending retains first approval, exactly one synthetic create and one complete task|14|
| request_changed |Change request in running/no-action phase; zero dispatch/zero original action|9|
| version_changed |Actually commit new Goal version in running/no-action phase; original approval rejected before dispatch|10|
| restart_no_action |New Host starts from synthetic persisted running Run + waiting_user link without action; actual boot_restore does not dispatch or silently complete|7|
| recover_create |Actually call calendar_recover_unstarted: old Run failed, same Goal v2 planned, create capability retained; duplicate recovery unchanged;128 Run bound rejects retry unchanged|13|
| recover_update |Same recovery, update capability and update step retained; no dispatch;128 Run bound rejects retry unchanged|13|

Total **80 runtime checks**, plus **26 independent Python disk checks**. Independent checks compare historical Goals/Runs/actions/claims/sources/links/receipts against seed, align artifact/action/Run/receipt request and event IDs, validate appended result Memory and verify recovery changed only target task while preserving historical entries/actions. All pass.

## Concrete bug found and fix verified

In initial rc29, calendar_confirm_action handled calendar_pending in the same branch as expired/invalid approval and cleared calendar_preview. A second click during the new50ms execution steps invalidated the first approval. The old r1 duplicate test timed out with no dispatch, not a runtime budget error. Root added an early `if calendar_pending {return}`; final r3 duplicate then completed exactly once. Product edits were Root's; A2 wrote only its diagnostics and reports.

The preceding 023/9897 source dense test passed. Old5e/4ce dense also passed after correcting fixture setup. Therefore this synthetic profile does **not** reproduce the native Shell time-budget failure and cannot prove every live workload is fixed. Root owns actual Shell/Calendar acceptance.

## Failures retained

- Initial baseline probe omitted core_boot_memory before gm_boot: memory_loaded/primary_readback false; corrected fixture passed. Not a product failure.
- Initial duplicate: no report within25s, zero dispatch; the duplicate product bug above was reported and fixed. No budget error in log.
- Initial version mutation changed only in-memory version and then asserted disk equality: only primary_readback failed. Corrected probe uses real core_upsert_goal; final PASS.
- Three restart attempts lacked test-only widgets required by actual boot_restore/mail startup (`mail_to/right_content`, then `right_page_content`, then `chat_list`). Every original error/log/jail is preserved; final actual boot_restore PASS. No restoration function was mocked.

## Read-only phase review and limits

Initial execute, accept, readback and finish-link chained several full storage transactions. Root split these into50ms callbacks without raising budgets and preserved legitimate planned→running/in_flight binding changes. Final r3 guards nil action payload, captures pre-request update original-event rather than later current UI selection, and fixes duplicate confirmation.

These tests cover **create** transport only and preparation of update recovery. They do not exercise actual update/delete callbacks or system Calendar. Readback/finish phases still warrant targeted future source/ownership-change tests: current readback guards action service/status/target/Goal/Run but not original payload_json; finish-link verifies source ID/account permission and Goal version, not every original source digest/claim revision/owner/link-event field. Such states must stop or request reconciliation and never replay external actions. No unexecuted variant is marked PASS.

Diagnostic runs use an owned copied manifest whose historical label is0.3.26-rc27; the source/compact/Host hashes above establish code identity. This is not a signed rc29 install, UI screenshot, native full-chain pass or READY claim. Current default profile capacities are unchanged. No product source, SDK, Host, stable app, Git commit/push or shared reports were modified by A2.

## Reproduce and stage

`run_calendar_callbacks.py --source <frozen-main> --expected-sha256 <hash> --out <new-owned-dir> --cases <variant...>` uses retained locked Host and synthetic record templates from A2. The runner stops at the first failing variant and retains all artifacts. It is a local diagnostic runner, not a fresh-checkout portable installer.

Only small probes/reports/public summaries are whitelisted in CALENDAR_CALLBACK_EVIDENCE_MANIFEST.json and SAFE_STAGE_LIST.txt. Bundles, jails, seeds, full databases, screenshots and raw logs remain local. Port8509 was closed after the runs. Root performs source integration, final staging and native live acceptance.
