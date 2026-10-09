# Muse upstream contribution audit — B branch

**Namespace feature request #182 is OPEN (posted by Root); Calendar feature request and local patch are prepared. No upstream change is accepted.**
This task provides compatibility evidence and deduplication for Root's decision.
Current instructions prohibit public posting. Production SDK implementation is unchanged. The later night section records local proposed patches; nothing is pushed.

## Fixed source evidence

OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`, App Hub
`18cd41d91b326db199fbed4129484a9ba1a8c63d`. Twenty-one narrowly fetched files have
Git blob SHA1 and SHA256 checks recorded in
`research/native-agent/upstream-sources.json`. The implementation includes
script tool admission/dispatch, the App Hub VM binding, bounded JSON serialization
and policy validation. This is stronger than a contract-only claim, but does not
prove the installed Muse target binary has that ABI.

`script-tools-v1` / `app_tools.dispatch@1` is implemented in this fixed source.
The PUBLISHING document retains a historical beta.2 table and then describes
RC1 open-app execution; reading the old table alone would produce a false
missing-feature report. Closing the owner app returns `app_not_running` by design.
Cold-start, phone and real-model acceptance are separate from open-app source
implementation and remain unverified in B.

## Deduplication performed

GitHub search/details were read through the authenticated CLI. Raw responses are
in `research/native-agent/upstream-search.json` and `upstream-related.json`.
These are observations captured during this audit, not a continuously current
status feed. The 139-result script-tool query retains only its first 30 results;
the audit does **not** claim exhaustive search or that no related issue exists.

| Existing item | Observed status | Relevance |
|---|---|---|
| [OctoSense PR #360](https://github.com/OctoSense-org/OctoSense/pull/360) | Merged 2026-10-08 01:11:44 UTC | Implements API discovery, backends and script tools; author explicitly separates source integration from published Host/phone/model acceptance |
| [OctoSense PR #414](https://github.com/OctoSense-org/OctoSense/pull/414) | Open, not merged in captured response | Native signed app-tool acceptance runner; useful future verification path, not model-selected/full-consent proof |
| [App Hub PR #119](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/119) | Merged 2026-10-07 00:31:12 UTC | Scoped connected-app services and reviewed tool mappings already exist |
| [App Hub issue #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172) | Open in captured response | Existing discussion of admission/API/widget compatibility coverage; avoid duplicate broad missing-admission claim |

Author-reported test counts in PR bodies are upstream reports, not tests executed
by B. The search includes `script tool`, `app_tools` and Hub `namespace` queries.
A zero-result exact `app_tools` query cannot override directly inspected source
or the related merged PR.

## Candidate disposition

| Finding | Status | Why no new public defect report |
|---|---|---|
| `muse-goals` cannot declare tools under current namespace policy | BLOCKED product integration | Base ID is legal; explicit tools policy rejects hyphen. No demonstrated policy implementation bug |
| Current B formal entry lacks Agent/tools declaration and hook | Verified local coverage gap | Muse integration work, not missing upstream implementation |
| Actual target Host ABI | UNKNOWN / NOT_TESTED | No target capability query or native runtime test; older pin/version lag is not upstream defect |
| Closed-app tool invocation | Documented limitation | `app_not_running` is intended behavior; no failing open-app reproduction supplied |
| Real model choice / complete production mail-calendar chain | NOT_TESTED in B | Neither static source nor synthetic protocol acceptance proves this chain |

Namespace evidence uses the real pinned `short_id` definition and
`ToolsManifest::validate` source, preserved in the compact excerpt. The static
predicate rejects the current ID; native Gate was not executed. Renaming the
app would change a storage/grant identity boundary, so this draft retains the
ID and reports BLOCKED. Root owns the migration decision.

## Delivery and remaining work

Delivered: coverage matrix, verified upstream inventory, dedup snapshots,
three unintegrated read-only tool proposals and reproducible static evidence.
Original audit snapshot: `ISSUE_OPENED=NO`, `PATCH_PREPARED=NO`, `PR_SUBMITTED=NO`, `PUSHED=NO`. The night status below supersedes the first two.

Root's A adapter/real-VM work is separate. The latest user direction uses the
official Shell Calendar service, not a private production bridge. After identity
and actual Host compatibility are resolved, acceptance needs a signed admitted
bundle, actual VM invocation/refusals, and model-selected calls with account,
consent and receipt checks. If that exposes a minimal reproducible upstream
failure, check related items again before Root decides on a public contribution.
B does not open a duplicate issue for an already implemented API.

## Built-in Calendar follow-up

The latest explicit choice is **official built-in Calendar**. Root's existing
`device_calendar` work stays isolated research, not the default production route.
This follow-up reads the pinned built-in bundle descriptors, owner service,
`ui.rs`, relay and contained Octos service. Total verified inventory is **21**
files. It does not run Calendar or export/modify its store.

Actual source findings, not table-name inference:

- `events`, `add_event`, `notify` explicitly have `shareable:true`.
- `update_event` exists and calls `ui::update`: exact-ID lookup, `expected` old
  record comparison, save and returned event. It lacks `shareable`.
- `remove_event` exists, `risk:destructive`, `confirm:host`, but lacks `shareable`.
- No declared `calendar.get` or get handler exists in this inspected service.
  Readback uses bounded `calendar.events`; omitted records are not delete proof.
- Calendar service accepts only `os.calendar`; relay makes the owner execute a
  granted shared tool. Other app IDs cannot call the underlying service directly.
- An official Splash App-Agent chat route does exist: exact declared `octos.*`
  services through `host.request`, with consent and Host-owned approval handling.
  Muse does not need a hand-built model/tool loop to reach that route.

The missing cross-app update/delete sharing is a **verified current compatibility
limitation**, not yet an upstream defect: policy may intentionally restrict it.
No native failure test or product requirement decision proving a policy bug is
provided, and no duplicate public issue is opened. Root should report the limit
for changed/cancelled scheduling before declaring the official-only chain complete.

The `muse-goals` namespace blocker applies to declaring Muse-owned `tools.json`.
It is not proof that an outbound-only Agent cannot request other apps' shared
tools: Hub review allows no own tool file at that stage. That exact preserved-ID
path still needs actual signed admission, consent and `octos.*` execution tests.
Neither a guessed relay API nor system impersonation is an acceptable substitute.
See the coverage report and `CALENDAR_STATIC_EVIDENCE.json` for source-bound detail.

## Night unit 1 — namespace compatibility feedback prepared

The original Hub policy/contract code was actually compiled and exercised in a
small single-job harness, with **1 test passed** (`night-repros/namespace.log`).
No source/Gate rule was changed; this is actual policy-method execution, not native
Host or full admission acceptance. Original source inventory:
`night-policy-sources.json`. Prepare script: `night-repros/prepare_policy.py`.

Fresh GitHub searches and current-main blob comparisons are captured in
`night-dedup.json` and `night-main-refresh.json`. Namespace/Calendar policy sources
still match pinned blobs. Search is targeted, not exhaustive.
`feedback/namespace-body.md` supplies an English feature-request body: legal ID
versus tools namespace is intended policy with an unresolved identity-preserving
upgrade path, not a fabricated Gate bug. Existing submission #112 is referenced.
Root owns public posting; **ISSUE_OPENED remains NO**. This unit adds reproducible
policy evidence but does not resolve the own-tools migration blocker.

## Night unit 2 — actual tests, patch and publication handoff

Namespace compatibility feedback was publicly posted by Root as
[App Hub #182](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/182).
Status: **OPEN, not accepted**. B did not create it or any duplicate. Captured
issue response: `feedback/namespace-issue-182.json`. The additional portable
synthetic namespace fixture passed one actual original-policy test. A proposed
regression-test-only patch is `patches/namespace-compatibility-regression.patch`;
it records current behavior and modifies no Gate or naming rule. It does not
implement a solution or authorize renaming.

Calendar feature-request English body: `feedback/calendar-body.md`. Fresh scoped
searches/related PR details are in `night-calendar-dedup.json`,
`night-calendar-related.json` and `night-dedup.json`; #267/#382/#411 are merged
related work, not evidence that cross-app update sharing already exists. Current
Calendar tool/service blobs were compared to main and are unchanged. This is
still a sharing/readback **feature request** if owner-only policy is intentional.
Root decides on public submission; B has not posted it.

Proposed patch `patches/calendar-shared-reconciliation.patch` changes only the
built-in Calendar descriptors/handler and adds regression tests. Sharing update/
delete retains explicit grants, owning executor, existing account/consent and
approval routes; delete remains destructive/host-confirmed, and update retains
expected old-record checks. New exact-ID readback distinguishes missing record
from malformed/unreadable storage. No Gate edit or system impersonation.

Executed evidence (all low-resource, serial, one Cargo job; no Host/model):

| Unit | Actual result | Scope |
|---|---|---|
| Original namespace methods, current fixture | 1/1 passed | Unmodified official policy/contract Rust |
| Portable namespace fixture | 1/1 passed | Regression patch; existing refusal, not a fix |
| Original Calendar core | 7 upstream + 2 boundary tests passed | Host registration adapter excluded; original algorithms preserved |
| Final patched Calendar core | 9 core + 1 relay policy test passed | Same-ID update, stale refusal, readback, delete/absence, list cap, corrupt store, grant/owner controls |
| Proposed descriptors | 1/1 passed | Actual unmodified `ToolManifest::validate`; not native Gate |
| Both patch applications | PASS | Fixed original source; tested/applied descriptors identical |

The initial offline dependency error is preserved; public dependency download
resolved it. Earlier intermediate patch tests (7 + 3) are retained separately;
final patch (9 + 1) includes the two service tests in upstream source. No counters
combine these repeated runs into full-chain evidence. `night-repros/README.md`
contains commands, source inventories, extraction boundaries and lockfile notes.

Current contribution states: namespace `ISSUE_OPENED_BY_ROOT=YES (#182 OPEN)`;
Calendar `BODY_READY=YES`, `PATCH_PREPARED=YES`, `PURE_CORE_TESTED=YES`,
`NATIVE_HOST_TESTED=NO`, `ISSUE_OPENED_BY_B=NO`, `PR_SUBMITTED=NO`, `PUSHED=NO`.
No official acceptance, version release or model-selected production chain is
claimed. Root receives these local artifacts for the second feedback decision.

The contained Agent uses merged app/account person/system conversation history,
not a caller-defined project session. This API boundary is recorded in coverage;
no third issue/patch is proposed without a distinct real reproduction and dedup.
