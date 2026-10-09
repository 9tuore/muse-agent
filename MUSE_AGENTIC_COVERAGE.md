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
App Hub `18cd41d91b326db199fbed4129484a9ba1a8c63d`. Twenty-one targeted files were
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

Static checks PASS: 21 upstream blobs, JSON declarations, seven real helper
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

## Built-in Calendar follow-up — latest user direction

**Default production direction is now the official built-in `os.calendar`.**
`device_calendar` is a separate OS-calendar adapter retained by Root as isolated
research; Root reports 22 synthetic real-VM protocol checks, which B did not run.
It must not enter the default product route or be called built-in Calendar proof.
No private production bridge or impersonated system ID is proposed.

Six more targeted Calendar/relay files plus the contained Octos service were
fetched at the same fixed OctoSense commit and Git-blob verified: total **21**
source files. `research/native-agent/CALENDAR_STATIC_EVIDENCE.json` records the
actual six Calendar descriptors and source checks.

| Actual declared tool | Risk | Shareable to another app | What source proves |
|---|---|---|---|
| `calendar.events` | read | yes | Read/filter stored events; limit defaults 50, maximum 200 |
| `calendar.add_event` | act | yes | Save local event; stable request_id reuses an exact retry and rejects conflicting reuse |
| `calendar.notify` | act | yes | Publish Calendar-owned saved-event/card notification; not an alarm or invitation |
| `calendar.update_event` | act | no: field absent | Actual update implementation exists, requires exact `expected` record; unavailable as cross-app shared tool |
| `calendar.remove_event` | destructive, confirm host | no: field absent | Actual delete exists for owner; another app does not gain it by requesting it |
| `calendar.agenda` | act | no: field absent | Owner's agenda card; not a cross-app shared endpoint |

There is **no `calendar.get` descriptor or get handler** in the fixed inspected
service. `calendar.events` is the available readback route: read matching range,
find exact returned ID and compare saved fields/timezone/request_id. The list has
no ID filter/pagination descriptor and caps at 200; absence from a bounded/filtered
list is not proof of deletion or nonexistence. `ui::view` supplies owner UI state,
not a declared shareable get tool. `ui::update` really finds the ID, deserializes
`expected`, compares it to stored state, writes the changed event and returns it;
that return is distinct from a later read. No live mutation/readback was run here.

Events live in `<host_dir>/calendar/events.json`, shared by Calendar UI and tools.
They are local OctoSense records; do not claim OS Calendar/Google synchronization,
mail invitation delivery or scheduled alarm. The source header omits update from
its method table, but the actual match handler and `ui.rs` implement it; neither a
header table nor a database path was used as proof of missing/present behavior.

### Exact app-to-Calendar route and authorization

1. A reviewed Muse manifest's `agent.tools` requests the named external tools,
   e.g. `calendar.events`, `calendar.add_event`, `calendar.notify`. This is a
   proposed declaration change only; B has not changed/sealed/admitted the bundle.
2. `script_apps::from_bundle` treats dotted generic tools as external requests;
   `install` maps them to their owner and registers per-tool relay grants.
   `calendar.*` is owned/executed by `os.calendar`.
3. Relay `Catalog::may_call` requires the owner descriptor's `shareable == true`
   and caller grant for cross-app calls. Call-time checks also enforce signed
   admission, user's app-Agent consent, account state and argument schema. Tools
   remain subject to Agent profile and host approval routing; a declaration,
   supplied text or developer override is not production authorization evidence.
4. Calendar's executor invokes its Host service using `os.calendar` identity.
   Its service explicitly refuses any other app ID. Muse's direct
   `host.request("calendar.*")` is not the cross-app relay and is refused.

The official Splash-to-own-Agent entry **exists** in
`crates/ai-host/src/contained.rs`: declare each exact capability
`octos.session.open`, `octos.turn.start`, `octos.session.history`,
`octos.turn.interrupt`, then invoke with the existing `host.request` API.
Open/history/interrupt accept empty objects. Start accepts nonempty bounded
`text` and optional `trigger`/`from` only. Unknown keys are refused. This targets
Muse's own Host-owned `card.muse-goals` peer; it does not open arbitrary Calendar
sessions. Input can ask Muse's Agent to use its granted Calendar tools. App
calls cannot choose provider/session/profile, grant tools or approve writes;
user first-use consent and Host tool-calling configuration are prerequisites.
History supplies results; the contained service does not push streaming events
to Splash. It checks both consent and exact manifest service declaration.

**Two blockers must not be conflated:** Muse's own `tools.json` still fails the
hyphen namespace predicate. Hub review checks that predicate when an own tools
file exists; it accepts the absence of that file at that step. Thus this rule
alone does not demonstrate that an outbound-only Muse Agent requesting existing
shared Calendar tools is impossible. Its admission/live Octos/model path remains
NOT_TESTED. In contrast, cross-app update/delete is unavailable in this pinned
Calendar tool set because the descriptors are not shareable. No custom tool loop,
identity rename, direct service bypass or delete/recreate workaround is added.

Required follow-up for Root: test a signed outbound-only Agent with preserved ID
through actual `octos.*`, consent and shared `events/add_event/notify`; capture
model choice and readback. For full changed/cancelled scheduling semantics, report
the built-in shareability limitation explicitly rather than silently switching
back to `device_calendar`. B publishes no issue and alters no production source.

## Night unit 1 — executed official policy reproduction

Night instruction attachment was read in full. B remains limited to these two
reports and `research/native-agent`; latest built-in Calendar choice overrides
the attachment's older device-calendar suggestion. Root owns production and
public feedback. Deadline is 2026-10-10 07:00 Asia/Shanghai, not an execution claim.

The original policy/contract crate sources at pinned Hub commit were fetched
(25 files, 223285 bytes, blob/SHA256 inventory `night-policy-sources.json`). A
harness changes only Cargo dependency selection to avoid optional GUI resolution;
**official Rust source is unmodified**. Actual `AppManifest::parse`,
`ToolManifest::parse`, `ToolManifest::check` and `validate` were executed.
`namespace.log`: **1 passed, 0 failed**, legal-ID parse accepted and official
namespace refusal reproduced; legal namespace control passed. Native Gate,
installation/Host/model remain NOT_TESTED. This supersedes the earlier static-only
status for this specific policy unit, not the overall Agent coverage result.

Reproduction: run `prepare_policy.py`, then `cargo test --offline --manifest-path
.local-state/night-policy/Cargo.toml -p octosense-app-policy --test muse_namespace
--jobs 1 -- --nocapture`. Cache-source URLs/hashes are in the inventory. Test input
uses this B manifest and three read-only prototype declarations; no production
writes or external calls. Official main `agent.rs` blob was freshly rechecked and
unchanged. Feedback body: `feedback/namespace-body.md`, classified feature request.

## Night unit 2 — executed Calendar reproduction and proposed patch

Source main blobs for Calendar tools/service remain unchanged from the fixed
commit. The latest choice remains built-in `os.calendar`; no EventKit/device
adapter enters the default route. A tiny harness removes only the Host service
registration/import adapter and compiles the original handler, owner guard,
UI/card/persistence logic and original tests. Four original relay methods are
byte-extracted into a minimal Catalog containing their two required data fields;
this is isolated logic, **not** the full native relay/consent runtime.

Baseline results: 7 original upstream tests + 2 boundary tests passed. Explicit
cross-app grants cannot overcome absent shareable flags, developer mode still
cannot invent sharing, own-app calls are positive controls, and ungranted callers
are negative controls. Actual service rejects direct Muse identity. Missing get
method errors, and a filtered empty list can coexist with a stored event.

Proposed local patch `patches/calendar-shared-reconciliation.patch` adds no Gate,
identity alias or runtime. It marks existing update/delete descriptors shareable,
retains delete's destructive/host-confirm flags and existing stale-update check,
and proposes read-only `calendar.get_event` for exact-ID saved-state readback.
Unreadable/corrupt store fails visibly; absence is only an explicit query result.
The patch includes two upstream regression tests. Final results: **9 core tests
(7 existing + 2 new), 1 relay policy test, 1 original Hub tool-policy test passed**.
Patch applies to fixed source and applied descriptors equal the tested candidate.
This demonstrates pure-service/descriptor behavior, not actual native approval,
installation, Account consent, model tool choice or real scheduling acceptance.

An initial offline Calendar command failed to resolve chrono-tz 0.10.4; its log
is preserved. A serial online retry downloaded public crate dependencies and ran
tests successfully. No Host/GUI, private event store or paid model was used.
Exact prepare/test commands and limits: `night-repros/README.md`. Raw success,
initial error logs and lockfiles are committed. The prototype remains unadmitted;
this does not raise B native Agent coverage above 0/16.

Contained conversation boundary: the original `contained.rs` documents merged
person/system history for one `card.<app id>` peer scoped by Host account. Its
parser accepts only text/trigger/from for a turn, empty args for open/history/
interrupt, and rejects arbitrary session/account/project keys. **There is no
proven per-Muse-project conversation isolation**. Root reports isolation tests
only and is keeping this path out of formal Chat pending evidence. This B unit
does not submit a third issue or claim a new isolation mechanism.

## Night unit 3 — five owned reads / preserved-ID loader boundary

`prototype/five-tools.proposed.json` describes five scoped reads: memory.search,
pending.list, receipt.get, transaction.get and followup.inspect. The original
three research handlers remain unexecuted; transaction/followup are **declaration
proposals without handlers**. This is not five implemented tools or model coverage.
Follow-up output is proposed stored state, not inferred permission or success.

Actual official `AgentBundle::load` was exercised with synthetic temporary,
digest-bound fixtures using unchanged `muse-goals` ID. **Three tests passed**:

- Five own-tool declarations are refused by the actual review/loader namespace
  check, before any Host or model execution.
- Descriptor shapes pass a pure validator control using a cloned unrelated
  namespace. This is a control only; no Muse ID/name/production storage is changed.
- An outbound-only Agent with no own tools loads under the same `muse-goals` ID;
  its tool_names are calendar.events/add_event/notify and ask_user_question.
  It has zero Muse-owned reads. Digest/review loading does not prove signature
  admission, native Host consent, actual Calendar dispatch or model choice.

Evidence `night-repros/five-tools.log`, executable `five_tools.rs`, commands in
`night-repros/README.md`. Entry fixture deliberately contains no executable UI;
no new Runtime or model loop is created. Real model-selected own-tool prototype
remains **BLOCKED** under the current identity policy; Root owns the independent
contained/outbound work. Agent coverage of B production remains 0/16.

Project-scoped history remains **NOT_TESTED**. Source shows merged app/account
history and rejects arbitrary caller session keys, but that alone is not an
executed two-project leakage/isolation reproduction. No third feature request
or claim of a project-isolation bug is made by this unit. A third public item
would require a distinct executed reproduction, configuration checks and dedup.

## Calendar review-code revision boundary

The Calendar patch's added helper/tests now use readable Rust blocks. The exact
two-file candidate was re-tested: original core 7+2, patched distinct-package core
9+1, original Hub descriptor policy 1 passed; application/core correspondence
checks passed. `calendar-review-patch.log` omits two new names and is retained as
insufficient evidence; corrected `calendar-review-patch-distinct.log` lists them.
Rustfmt is not installed, so only manual formatting/actual compilation is claimed.

Official `apps/AGENTS.md` intentionally confines update to Calendar UI/own Agent.
Sharing it is a policy-change proposal under #427, still OPEN, not accepted. The
current narrow lib.rs/tools.json patch does not complete official shipped admission
offer/caller grants, bilingual docs, cold-start or native approval/model tests.
Those are required integration follow-ups for Root/maintainers; this is reviewable
isolated implementation, not native Agent coverage. No other tools were expanded.
