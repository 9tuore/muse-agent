# Muse upstream contribution audit — B branch

**No new upstream defect sufficiently verified; no public issue or PR submitted.**
This task provides compatibility evidence and deduplication for Root's decision.
Current instructions prohibit public posting. No SDK implementation is changed,
no patch is prepared for submission, and nothing is pushed.

## Fixed source evidence

OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`, App Hub
`18cd41d91b326db199fbed4129484a9ba1a8c63d`. Fourteen narrowly fetched files have
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
`ISSUE_OPENED=NO`, `PATCH_PREPARED=NO`, `PR_SUBMITTED=NO`, `PUSHED=NO`.

Root's A adapter/real-VM work is separate. The latest user direction uses the
official Shell Calendar service, not a private production bridge. After identity
and actual Host compatibility are resolved, acceptance needs a signed admitted
bundle, actual VM invocation/refusals, and model-selected calls with account,
consent and receipt checks. If that exposes a minimal reproducible upstream
failure, check related items again before Root decides on a public contribution.
B does not open a duplicate issue for an already implemented API.
