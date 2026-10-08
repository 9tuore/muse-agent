# MUSE-7H ownership and interfaces

Start: 2026-10-08 19:43:07 Asia/Shanghai. Deadline: 2026-10-09 02:43:07.
Base: 5126afc4, same rc10 business bytes as b4b55623; standalone edition packaging commits remain in their existing branch.

- Root: sole writer of official_muse/app/source/main.splash, app/bundle, global_memory.splash, scheduling.splash, incoming_mail.splash, core.splash and final executive/handoff files. Reliability fixes, final integration, all real mailbox/calendar UI operations.
- Business: only official_muse/rc/7h-20261008/business/**. Production-function fixtures, full isolated chain and failure injection. Report proposed business changes to Root; never edit shared business sources.
- Android: only official_muse/rc/7h-20261008/phone/**, private candidate SDK copy and explicitly agreed new sdk-overlays phone patch files. Read existing SDK at muse-rc-finalization/vendor; never mutate it. No device writes, ROM operations, credentials or external mail/calendar calls.
- Quality: only official_muse/rc/7h-20261008/quality/**. Current frozen rc10 cold baseline, profiling and candidate cold/reopen matrix, official Gate/scan, static checks. No writes to application sources or dependency lock. Never use hidden rendering for final visual proof.

All tests bind to actual source, bundle and Host SHA. Never increase VM/script budgets or silently alter tests to pass. Preserve failure evidence. Private mail/calendar data stays in .local-state, never Git or public reports. Agents commit only owned files; no broad git add and no push. No further agents. Root will freeze each test candidate and communicate SHA before final tests.

Separate live and isolated evidence. Default real-mail limit is 20; Root owns the send ledger and whitelist checks. UNKNOWN actions require read-only reconciliation. Permission pages can be opened; system grants are the user's action.
