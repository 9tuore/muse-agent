Follow-up implementation proposal for #427: shared Calendar reconciliation and exact saved-event lookup

This revises the existing feature request, not a new issue. #427 is OPEN; the patch is not installed, submitted as a PR or accepted upstream.

The current `apps/AGENTS.md` explicitly says that `calendar.update_event` belongs to Calendar's UI and own Agent, not new Mail/system grants. Accordingly, sharing update/delete is a requested policy change for maintainers to review, not a fix for an accidentally missing permission. No caller gets a tool merely by asking for it.

The attached patch changes exactly two files at OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`:

- `apps/calendar/host-service/src/lib.rs`: add read-only exact-ID `get_event` and two regression tests. Unreadable/corrupt storage is an error; an absent ID returns `{found:false,event:{}}` instead of relying on a bounded list. Existing owner guard, stale-state update behavior and service registration remain unchanged.
- `apps/calendar/bundle/tools.json`: declare `calendar.get_event`; propose sharing the existing update/delete tools. Delete keeps `risk: destructive` and `confirm: host`. Per-tool grants, signed admission, account/Agent consent, owning executor and Host approval mechanisms remain required. This intentionally broadens the shareable surface if adopted.

Validation actually run after normalizing the added Rust into readable blocks:

| Check | Result | Execution layer |
|---|---|---|
| Original core baseline | 7 existing + 2 boundary tests passed | Isolated original Calendar/UI/cards logic and four exact relay methods |
| Final revised patch | 9 core tests + 1 grant/owner policy test passed | Isolated patched core; includes same-ID update/readback, stale refusal, delete/absence, list cap and corrupt-store errors |
| Proposed seven descriptors | 1 test passed | Unmodified official Hub `ToolManifest::validate` |
| Patch application/scope | Passed | Exactly the two files above; applied core/descriptors match the tested candidate |

The harness removes only the Host registration/import adapter to avoid building a complete Shell. It is not a replacement runtime. Original and patched harness packages now have distinct Cargo names: a preliminary rerun omitted the two new test names despite exit 0, so that output was treated as insufficient and preserved; the corrected run explicitly lists both new tests. No omitted tests are counted as passes. Rustfmt is unavailable in the installed toolchain, so formatting was reviewed manually; no rustfmt success is claimed.

Unverified: complete official workspace/service build, native Shell cold-start, admission offer registration, real Agent consent/approval routing, actual model-selected calls, device/UI acceptance and real scheduling effects. No Gate changes, identity impersonation, secret/private event data, provider calls or production integration are included.

Official root/apps `AGENTS.md` requirements were read at the fixed revision (no applicable `CONTRIBUTING.md` or Calendar rustfmt configuration was found in its tree). Before adoption, maintainers must review the owner-only policy change, update the requesting app's grants and shipped admission offer, update English/Chinese documentation together, and run the documented workspace/service/Shell acceptance checks. Those integration/docs changes are intentionally outside this narrow two-file review patch. Full official CI/setup checks were not run by this isolated test task. Any public Git commit should use the public identity required by the root instructions.

Patch SHA256: `e5545d88382f689faf99d050f0053c4bdf7a99486dc07384195314880f1a4d9b`.
