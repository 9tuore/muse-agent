# Issue draft — Capability-gated Calendar Host with independent readback

**DRAFT / NOT POSTED.** Target repository and current upstream baseline must be rechecked before submission.

Store Apps need to turn a user-approved plan into a system Calendar event, read it back, and later update that same event. At the OctoSense revision used by Muse (`7f962547cd8035ed2bb05962cf7824d8aa33e3a3`), the pinned upstream archive does not contain a Calendar host-service crate. Script bundles cannot carry their own native EventKit implementation.

Muse currently has a local extension offering status/access, bounded list/get, create, version-preconditioned update/delete and per-app durable request journals. The Shell registers it under the local `calendar` capability. It requires full EventKit access for readback and rejects unsafe retries after an uncertain mutation.

We would like to agree on an upstream contract before submitting implementation:

1. Should read and write capabilities be split? Should a host-owned trusted sheet bind the selected Calendar and authorize each mutation?
2. What shared namespace and ownership marker should replace the current Muse-specific event URL prefix?
3. What journal retention and reconcile contract should applications use after a crash or an accepted action whose local result could not be saved?
4. Is macOS 14+ full-access support an acceptable initial platform boundary? How should unsupported platforms be reported?
5. Can a write receipt be explicitly distinguished from an independent `calendar.get` verification in shared API documentation?

The proposed PR would contain Calendar policy support, a small Rust service and EventKit bridge, Shell integration and focused tests. It would exclude Muse product logic, Mail, model logging, UI localization, listing and publisher/signing changes.

Evidence currently available locally: exact SDK restoration, an Intel release build with resources and strict ad hoc signature verification, and pure validation/journal tests. These are not proof of current unmodified upstream admission or a final live Calendar chain. Final-version integration evidence and a minimal patch series will be attached after coordinator review.

No formal Issue/PR is created by this draft. User review is required before posting; no publisher key or release is created.
