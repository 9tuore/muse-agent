# MUSE-7H ownership and interfaces

Start: 2026-10-08 19:43:07 Asia/Shanghai. Deadline: 2026-10-09 02:43:07.
Base: 5126afc4, same rc10 business bytes as b4b55623; standalone edition packaging commits remain in their existing branch.

- Root: sole writer of official_muse/app/source/main.splash, app/bundle, global_memory.splash, scheduling.splash, incoming_mail.splash, core.splash and final executive/handoff files. Reliability fixes, final integration, all real mailbox/calendar UI operations.
- Business: only official_muse/rc/7h-20261008/business/**. Production-function fixtures, full isolated chain and failure injection. Report proposed business changes to Root; never edit shared business sources.
- Android: only official_muse/rc/7h-20261008/phone/**, private candidate SDK copy and explicitly agreed new sdk-overlays phone patch files. Read existing SDK at muse-rc-finalization/vendor; never mutate it. No device writes, ROM operations, credentials or external mail/calendar calls.
- Quality: only official_muse/rc/7h-20261008/quality/**. Current frozen rc10 cold baseline, profiling and candidate cold/reopen matrix, official Gate/scan, static checks. No writes to application sources or dependency lock. Never use hidden rendering for final visual proof.

All tests bind to actual source, bundle and Host SHA. Never increase VM/script budgets or silently alter tests to pass. Preserve failure evidence. Private mail/calendar data stays in .local-state, never Git or public reports. Agents commit only owned files; no broad git add and no push. No further agents. Root will freeze each test candidate and communicate SHA before final tests.

Separate live and isolated evidence. Default real-mail limit is 20; Root owns the send ledger and whitelist checks. UNKNOWN actions require read-only reconciliation. Permission pages can be opened; system grants are the user's action.

## Real-chat handoff (latest user instruction)

The user explicitly replaced sub-agents with existing real Codex chats. Child
agents were interrupted; no more child agents may be started. Each real chat keeps its configured model. Reasoning rises only when observed output needs it.

- Final quality: `01a11c66-4ced-7bc3-afc9-d13421301a46` (local), port8494, medium, owns `final_quality/**`. Old quality delegation ended after context drift; its evidence stays retained.
- Business: `01a0fc7a-bfc0-7bd3-b0c8-860d8a5ed3d9` (local), low, port8661.
- Phone: `01a105ce-9313-74b1-abe3-abb7e7e47a3d` (local), high after observed resource/build failures; earlier low and medium retained in checkpoints.

Directory ownership and test boundaries above stay in force. Each chat writes
its checkpoint to its own `HANDOFF_REAL_CHAT.md`; Root observes files and
compact thread status. No orchestrator reply messages are needed.

## Historical rc15 candidate freeze

2026-10-09 01:04: source cef7d576b2de31e5c22a813e70e68370ff0ddd043ef1bbcd57acae75eb81b546, version0.3.27-rc15; Host276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638. Source-preparation chunk1024 bytes, existing64ms budgets retained. All final runs bind these hashes; old passing evidence is identified by its original hash. Root8492 and user8765 remain protected from collaborators.

## Final rc16 freeze and integration

Post-window storage recovery: legacy Quality delegation has ended; Root alone may transparently compress its idle tracked public `quality/**` evidence with SHA/mode/size checks, preserving paths and raw bytes. FinalQuality owns its separate `final_quality/**` compression; Phone owns its separate caches. No source changes or repeated PASS counts arise from filesystem compression.

Final version0.3.27-rc16, compact dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4, readable7fcc94e1b7d3d1a63968bcdc990abf15c2a59208b79d39badf40b4ae91f644d4, same Host276b2b68. Rootr9 signed six-file bundle equals tracked official_muse/app/bundle. FinalQuality single-round10cold+5reopen and official signed Gate passed. Business rc16 scope checks use referencecard-host and retain rc15 chain/recovery identity. No more main/SDK/bundle edits after this freeze; only owned Phone results, packaging and final handoff/report. Root8492 stays open, user8765 stays protected. External full chain remains incomplete for actual credential/system-grant reasons; never upgrade it based on synthetic tests.
