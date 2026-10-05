# A2 rc30 manual original-matter selection

Status: **PARTIAL**. Source `d17be7228f3ac8349ab7e012cfd80c2101508daa6d1081f9c48012d04d8c24a0`, compact `54bbd6452a553577850922138f11f3f60c6a64128869e91a17cfb2602b9c4d49`, locked CardHost `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`. No product source/SDK/Host/stable app/production data/Git changed by A2. Own serial port8509, unchanged20M instruction/default wallclock/heap budget.

## Real fixture outcomes

The original verified matter is copied from A2's earlier actual final61 CardHost synthetic create/get/readback/completion test, preserving a matching Goal, completed Run, verified action, link, receipt and artifact. The source/claim graph is narrowed to source+result claims for small cases; dense case retains32 Goals,128 Runs/actions,63 claims and matching sources. All account/message/event values are synthetic. Model transport only queues callbacks; no real model/system Calendar/SMTP.

| Variant | Outcome |
|---|---|
|Legal explicit choice, no RFC message_id/in_reply_to/references and no automatic match|11 PASS: same Goal v2planned, original event preserved, precise new message/source bound, old-message history retained, update capability, actual source/claim readback, one synthetic candidate model request, no new Run/action or external mutation|
|Wrong account|9 PASS|
|Wrong project|9 PASS|
|Wrong owner|9 PASS|
|Current selected message differs from confirmed exact message ID|9 PASS|
|Original link not verified|10 PASS|
|Message changed while calendar.get queued|10 PASS: one actual synthetic get, confirmation callback rejected; no model/mutation and original disk bytes unchanged|
|Legal dense profile|**ERROR: script instruction limit exceeded**; not PASS|

The six rejection variants total56 runtime checks. Independent Python comparison of full parsed Goals/Memory/calendar-state against their synthetic seed adds18 PASS. Legal small adds11 PASS. Do not aggregate the failed dense run into success.

## Dense failure and partial persistence

`MANUAL_REPLAN_FAILURE.json` preserves the observed error and original log hash. Instrumented line4850 is inside core_utc_iso (`let month=mp+3`). This is the reported exhaustion location, not proof that date conversion itself is the root cause.

At failure: new source/claim already persisted (63→64), same Goal v2planned, original event ID retained, linkcandidate/new message bound, active generation record present. Runs/actions128 remained exactly equal to their seed; no calendar mutation occurred. This is partial persistence, not a finished candidate or successful model call. Complete raw log, copied bundle and isolated jail remain local under manual-replan-rc30-r3/legal_dense/first.

Current get callback performs source→claim→Goal replan→calendar-save→calendar-select/chat-bind→model generation/preflight/context in one cumulative callback. Minimal proposal sent to Root: separate these persistent operations into50ms phases, revalidate captured account/message/scope and source/version while recognizing only each phase's own legitimate updates. Keep idempotent source/claim handling, preserve partial state, and do not replay external actions or increase budgets. Dense retry is paused until a new frozen implementation is supplied.

## Preserved development failures

An attempted592-source start was refused by SHA check before creating an output or starting Host because Root had updated main. No592 runtime was performed.

The first d17 small probe refused mail.accounts from real model preflight, so model queue and transport allowlist checks failed while Goal/source/link transition succeeded. Its report/log/jail remains manual-replan-rc30-r2/legal. Fixture was corrected to return a synthetic authorized account for that read query; same-source small legal then passed. No real account or credentials were read.

## Boundaries

All get results are synthetic and model replies are not executed. This validates actual production preparation, confirmation guards and jailed persistence only. No real reschedule/update/delete, official mail thread metadata, native Shell UI, real inference or complete end-user Calendar flow is claimed. Root handles native acceptance. The copied manifest retains a historical label; source/compact/Host hashes establish actual code identity.

No later feature is silently upgraded. Previous Calendar, capacity and forget evidence remains separate at its observed SHA. Runtime/jail/seed bundles are excluded from the safe staging list. The runner requires A2 retained synthetic verified test materials and locked Host; no fresh-checkout portability claim.
