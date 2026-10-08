# Final quality rc16 — 2026-10-09T02:08:44+08:00

**PASS_SINGLE_ROUND_10_COLD_5_REOPEN**. The new rc16 completed one uninterrupted matrix:10/10 full-process cold launches and5/5 app close/reopens. No supplemental launch, selector debugging or test retry was needed. The earlier rc15 reports remain rc15 evidence and were not counted.

Source SHA `dd2ce02517f8c7ab6c4dea9e10b017d27281bd49dcf94cf7d0fb1f7b41d5a9a4`; Host SHA `276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638`; version0.3.27-rc16. All10 cold PIDs are distinct. All5 reopens retained final Shell PID55064. The loaded bundle's complete file set, including manifest and assets, equals Root's signed `7h-live-candidate-r9/bundle` byte for byte.

| Check | Actual result |
|---|---|
| Visible input/history/card/Memory |15/15 pass; real input edit/readback, exact stored history label, meaningful Goal title+two-item plan and Memory正文; every run has visible Chat and Memory PNGs |
| Nonempty synthetic state |16 sessions/256 messages/64 claims/65 sources/1 planned Goal/1 failed Run/1 failed Action; ready synthetic mail baseline64 seen |
| Core pages |Chat/Mail/Calendar/Memory/Activity/Capabilities/Settings rendered with body content; Chat verified via input/history, no page_title required |
| Persistent core state |Exact original seed bytes throughout and at final reread; model ledger unchanged |
| Activity |Only authorized Calendar permission observation increments; original prefix and backup prefix validated; all-persistent-file SHA equality is false |
| Runtime |No15-run `[E]`, budget exceeded, source preparation failure or no-root-view log |
| Source prep max observed chunk |17.288ms; Host unchanged, chunk1024 and64ms budgets unchanged |
| Cold editable input |14.46–17.67s; median15.45s |
| Independent official signed gate |Exact signed bundle copy check/scan PASS with pinned official CLI, no stamp/sign/mutation |
| Eight malformed/backup scenarios |Original oldHost evidence reused only for unchanged exact restore-function call closure; not claimed as rc16 live reruns |
| Cleanup |Own PID55064 quit;8494 independently closed; other assigned ports untouched |
| Physical phone |DEVICE_NOT_TESTED |

`FINAL_SUMMARY_RC16.json` contains every actual PID, timing, per-run log/snapshot/PNG path and PNG hashes, with independent final core-seed/bundle equality checks. Raw matrix is `final-rc16-cold10-reopen5-r1/report.json`; signed gate `official-signed-rc16-r1/report.json`; reuse analysis `storage-reuse-rc16.json`; cleanup `cleanup-rc16.json`.

Root owns the specific newChat project inheritance and model recall variant acceptance. Quality performed no newChat creation, model submission, Mail/Calendar write or system authorization request. This PASS is synthetic desktop cold/reopen acceptance, not model/backend semantics, external delivery/Calendar CRUD, system grant or upstream Calendar extension acceptance. rc15 driver failures and the historical genuine source-budget failure remain unchanged and identified with their original SHAs. Only final_quality/** and ignored synthetic runtime were written; no shared source/SDK/Host/production modifications, new chats/subagents/messages or push.
