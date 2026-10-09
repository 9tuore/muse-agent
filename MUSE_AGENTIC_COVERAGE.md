# Muse native Agent coverage — B branch audit

**Current B entry: no native Agent tools; prototype BLOCKED.** Existing model-assisted
workflow is useful product logic, but it does not establish model-selected tool
execution. This is a static audit of B's canonical bundle, not final Root/A
integration acceptance.

Baseline: branch `codex/muse-semifinal-b-layout-20261009`, source HEAD
`c800cfcc08fd3c15b5a4b8b751a4b8112f92e5ee`, canonical `bundle/`, version
`0.3.27-rc17`, application ID `muse-goals`.
`bundle/main.splash` SHA256:
`90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`.
`official_muse/app/bundle` points to this canonical bundle. There is no `tools.json`,
`AGENT.md`, `app_tool` hook or `mod.app_tools` call in that entry; manifest `agent`
is null. The three research declarations are outside the bundle and unintegrated.

## What was counted

A covered operation needs a declared/admitted tool, execution through the official
Agent/runtime interface, and evidence that a model selected that tool. A UI click,
fixed automatic pump, model classification, compiled window or proposal card
alone does not meet that definition. On the 16 grouped entry paths below, native
Agent coverage is **0/16** in this B baseline. This denominator is an audit grouping,
not an exhaustive capability count or a product quality percentage.

| Entry path in `bundle/main.splash` | Existing mechanism | Native Agent evidence |
|---|---|---|
| Chat dispatch, `chat_model_config` 7663 / `send_chat` 7808 | Keyword routing chooses bounded task modes | None |
| Model response, `muse_model_request` 7980 / `model.complete` 8071 | Model completion within fixed workflow | None |
| Proposal/application, `chat_add_proposal` 8127 / `chat_apply_proposal` 8199 | UI proposal and explicit application | None |
| Memory retrieval, `gm_context` 6403 | Scoped retrieval with persisted trace | None |
| Memory save, `gm_save` 6475 | Existing local write path | None |
| Memory correction, `gm_correct` 6524 | Existing local correction path | None |
| Memory forgetting, `gm_forget` 6600 | Existing local deletion policy | None |
| Mail watcher, `mail_watch_boot` 3398 | Deterministic background watcher | None |
| Mail analysis, `mail_analysis_pump` 2077 | Fixed orchestration with bounded model calls | None |
| Mail reply preparation, source around 3705–3751 | Fixed intent/preview sequence | None |
| Mail sending, source around 3919 / Host send 4634 | Controlled external write path | None |
| Calendar availability/read, status 705 / list 898 | UI and Host request paths | None |
| Calendar conflict preview, 1020 / 1515 | Fixed validation and preview | None |
| Calendar mutation, confirm 1585 / dispatch 1867 | Fixed approval/action sequence | None |
| Calendar readback/recovery, 1217 / 1277 / 1311 | Transactional verification/reconciliation | None |
| Action receipts, `core_begin_action` 5279 / `core_finish_action` 5306 | Local action lifecycle/receipt storage | None |

These paths preserve valuable scope, approval, idempotency and UNKNOWN handling.
Their presence does not prove model choice. This task did not rerun their existing
mail/calendar business acceptance and does not replace old test evidence.

## Official contract and two independent gates

Pinned upstream: OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654` and
App Hub `18cd41d91b326db199fbed4129484a9ba1a8c63d`. Fourteen targeted files were
checked against Git blob SHA1 and SHA256, recorded in
`research/native-agent/upstream-sources.json`; no whole SDK was downloaded.

| Contract | Verified source | Consequence |
|---|---|---|
| Tool namespace is last app ID segment | Hub `manifest.rs` 601–606 | `muse-goals` remains `muse-goals` |
| Tool namespace `[a-z0-9_]{1,24}` | Hub `agent.rs` 63, 325–336 | Hyphen refuses tool declaration; **BLOCKED** |
| `script-tools-v1` requires `app_tools.dispatch@1` | Hub `manifest.rs` 775–784 | Target binary must advertise compatible ABI |
| Hook `app_tool(name, call_id)` with request/complete/fail | Hub PUBLISHING 655–701 and actual `script_tools.rs` | Existing live app VM executes bounded calls |
| Closed app/account change invalidate invocation | Hub PUBLISHING 701–721 / OctoSense `script_apps.rs` | Closed app returns `app_not_running`; no implicit second VM |

[Official namespace policy at the pinned Hub commit](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/crates/app-policy/src/agent.rs#L325)
contains the refusal. The base application ID is legal; declaring tools under its
current namespace is the incompatible step. `namespace-policy-excerpt.txt` and
`verify_static.py` reproduce this static finding. **Native `hub check` was NOT_RUN**;
the Python predicate is not presented as execution of the native gate.

Source implementation of the ABI exists. Actual installed target Host ABI is
**UNKNOWN / NOT_TESTED** in this audit. B's dependency lock is an older source
pin; it is not proof of the executing binary's capabilities. Source freshness,
compilation and runtime API discovery must remain separate evidence.

## Minimal prototype and handoff

`research/native-agent/prototype/` proposes `memory.search`, `pending.list` and
`receipt.get`, with unchanged `muse-goals` prefix, read risk, private data,
nonshareable results and no background execution. Reads use current scope and
stored records; pending includes only scoped mail-linked goals. Results cap at
six and never promote missing/unknown receipts to success. The proposal avoids
memory retrieval trace writes. It has no external/model request or production
mutation, and no declaration is admitted or counted as covered.

Static checks PASS: 14 upstream blobs, JSON declarations, seven real helper
functions, eleven real globals and absence of prohibited side-effect calls.
A draft reference to nonexistent `core_goals_ready` was corrected to actual
`core_storage_ready` plus `gm_ready` before recording the evidence. This is symbol
verification, not a Splash syntax/runtime proof. Native admission, VM execution,
trusted account mapping and model-selected tool calls are **NOT_TESTED**.

Root must resolve the identity compatibility boundary before integrating tools;
this B task does not rename IDs or choose a workaround. Any solution needs explicit
data/grant/publisher continuity and rollback evidence. Root reports A has added
`device_calendar` and `mail.compose/review_send` adapters and is running real VM
synthetic protocol checks; that is coordination context, not B verification.
The user's current calendar direction is official Shell; no private Calendar
production bridge is proposed here. Final coverage must be re-audited against
Root's eventual frozen bundle and actual admitted Host.

Reproduce: `python3 research/native-agent/verify_static.py` from B worktree root.
Recorded result: `research/native-agent/STATIC_EVIDENCE.json`.
No model call, provider operation, account permission, public issue or push occurred.
