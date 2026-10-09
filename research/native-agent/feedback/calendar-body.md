Title: Feature request: shared Calendar reconciliation tools for updating an existing event and verifying exact absence

The built-in local Calendar provides shareable `calendar.events`, `calendar.add_event` and `calendar.notify`. Its actual update/delete implementations exist, but their descriptors omit `shareable`; there is no exact event-by-ID get tool. This is a compatibility feature request if that sharing policy is intentional, not a claim that an app should bypass consent or directly call the owning service.

Scope: OctoSense `3a4d1e1e557750eac69b412f34d36021306ea654`. Current main tools blob `243c04aa0b5d027fd0a79435c73b18d16ade8beb` and service blob `33f1a25f12960fa9db39dfc82de631bc40666866` were rechecked and are unchanged at this observation.

Use case: an authorized third-party app Agent reads a scheduling message, creates a local event, then receives a changed/cancelled instruction and must update/remove the same event and reconcile the resulting state. We specifically mean OctoSense's built-in local Calendar store, not Google Calendar, EventKit or `device_calendar`.

Minimal executed reproduction:

- Load the original Calendar tools JSON into the original relay `Catalog::grant/entry/shareable/may_call` methods.
- Explicitly grant `calendar.update_event` and `calendar.remove_event` to `muse-goals`. Both still return false from `may_call`, including with the developer flag; the owning `os.calendar` caller succeeds. `calendar.events` is a positive shared control, and an ungranted caller is a negative control. This is descriptor policy, not missing account authorization.
- Run the original Calendar service `handle`: direct calls with app ID `muse-goals` are refused by the owner check. `handle(os.calendar, "get", …)` returns an unavailable-method error; it does not return precise absence.
- A filtered `calendar.events` call can return an empty list while the exact event still exists. The list caps at 200 and has no ID filter/pagination descriptor, so absence from that result is insufficient deletion/reconciliation proof.

Execution layer: isolated original Rust logic, not a native Shell session. The pure Calendar core/UI/cards are unchanged; only the Host registration/import adapter is removed for the small harness. Four production relay methods are copied byte-for-byte into a minimal Catalog data container. No fake model/Calendar implementation is used. Seven existing upstream Calendar tests and two boundary tests passed. No native relay/consent/GUI approval or real model turn was executed; this does not establish native full-chain success.

Proposed local patch (not installed, submitted or accepted):

1. Mark existing `calendar.update_event` and `calendar.remove_event` shareable. Keep all per-tool grants, owning executor, account/admission/Agent consent and approval handling. Keep delete `risk: destructive`, `confirm: host`, and existing update `expected` stale-state check.
2. Add a read-only shareable `calendar.get_event` with exact `id`, returning `{found, event}`. An absent ID returns `found:false`; corrupt/unreadable storage is an error, not false absence. Return the saved event for caller-side exact field comparison; do not claim delivery/synchronization.
3. Include regression tests for same-ID update/readback, stale update refusal, delete/readback absence, lookup beyond the list cap and corrupt-store error.

The final local patched pure-core suite passed 9 tests (7 unchanged + 2 new), and one relay policy test passed. One test of the proposed seven descriptors passed against the unmodified actual App Hub `ToolManifest::validate`. Patch application was checked on fixed original files. None of these tests modifies a Gate or proves signed installation/native approval/model choice. Upstream maintainers should review the sharing policy and native consent/confirmation behavior before adopting it.

Related: #267 introduced Mail/Calendar agent cards; #411 and #382 concern engine/system agent reach. Searches for `calendar shareable`, `calendar update_event`, `calendar remove_event` and `calendar get_event` were repeated. No exact competing shared-update/get proposal was found in those captured results; this is scoped search, not exhaustive proof. Please link an existing design if this owner-only policy is intentional.

No private events, contacts, credentials, provider keys or personal store contents are needed: all executed service data was synthetic in temporary directories. This request does not ask for reserved identity impersonation, a custom tool loop, or deletion/recreation as an update substitute.
