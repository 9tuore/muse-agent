# PR draft — Add bounded Calendar Host and mutation reconciliation

**DRAFT / NO PR CREATED.** The contribution has not been split into commits yet.

Calendar workflows in contained Store Apps need host-controlled system access, a stable system event identifier and an independent readback. This proposed change adds a Calendar service and EventKit bridge, with capability checks, full-access handling, bounded input/query ranges, per-app mutation ownership, stale-version rejection and durable request receipts. A pending or uncertain request must be reconciled before a new mutation is attempted.

## Intended patch

- App Hub policy: declare and test the agreed Calendar capability boundary.
- OctoSense service: `status`, `request_access`, `list`, `get`, `create`, `update`, `delete`; Rust validation/version/journal and Objective-C EventKit bridge.
- Shell: register the service for `app-hub`, add workspace/feature wiring and a Calendar full-access usage description.
- Tests/docs: malformed ranges/IDs, damaged journal, same-ID replay, changed-payload rejection, stale/pending outcomes, fake-native failure/reconcile, platform/permission and independent-get documentation.

## Validation to attach before review

Existing local checks have built the Intel Host and local-extended Hub and restored the exact locked SDK trees. The three existing Calendar pure fixtures passed (3/3, exit 0); `CALENDAR_PURE_TEST_RESULTS.json` records the command and source SHA. They do not call EventKit or request OS permission and must not be described as live Calendar tests. A final PR needs the exact minimal patch commit, a fresh build from that commit, focused test output and clearly labeled synthetic versus live integration results.

No Mail/model/UI-localization patches belong in this PR. Current full SDK tree/Host hashes cover additional local extensions, so they are supporting context rather than the Calendar-only patch identity.

## Review decisions still open

Host-owned target selection and per-action approval, read/write capability granularity, generic event ownership URI, bounded journal retention, unsupported-platform behavior and privacy/lifecycle documentation. Current implementation uses a Muse-specific URI and app-layer confirmation; these must be stated explicitly. Repeat events, attendee-bearing events and events owned by another app are intentionally outside current mutation scope.

The final reviewer should see a real before/after behavior change and independent readback evidence. This draft does not claim publication, upstream acceptance or production readiness. User chooses whether to post it after the overnight work.
