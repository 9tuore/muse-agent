# Final quality rc15 — 2026-10-09T01:38:44+08:00

**PASS_WITH_TWO_DRIVER_SUPPLEMENT_RUNS** for the authorized synthetic desktop quality scope. Accepted10 distinct full-process cold launches and5 app close/reopen runs, all on source `cef7d576b2de31e5c22a813e70e68370ff0ddd043ef1bbcd57acae75eb81b546` and Host `276b2b688b759e2d0e026a6999118e25f857bb21ebf23c93cea2d24b03daf638`. This was11 cold attempts and6 reopen attempts in the final r6+supplement r7; it was not one uninterrupted15/15 matrix. Earlier driver rehearsal failures r1-r5 are preserved separately.

| Check | Observed result |
|---|---|
| Visible Shell/input/history |15 accepted runs pass; each has real Chat and Memory PNGs, actual input edit/readback, exact nonempty stored history |
| Nonempty state |16 sessions/256 messages/64 claims/65 sources/1 planned Goal/1 failed Run/1 failed Action; synthetic ready mail baseline64 seen |
| Goal result card |Real persisted title and two-item plan rendered; no approval click |
| Core pages |Chat, Mail, Calendar, Memory, Activity, Capabilities and Settings rendered with body content |
| Core persistent bytes |Exact match to original synthetic seed, including backups; model ledger unchanged |
| Activity |Authorized permission-observation increments only; original prefix unchanged, backup prefix valid; all-file SHA equality is false |
| Runtime |No accepted-run `[E]`, budget exceeded, source preparation failure or no-root-view log |
| Source prep timing |Maximum observed chunk 7.959ms;64ms budgets untouched |
| Cold input time |14.64–15.70s; median15.00s |
| Official signed gate |Pinned official CLI check+scan PASS on exact Root-signed bundle copy, no stamp or mutation |
| Loaded bundle |Every loaded bundle file equals Root's final signed bundle, including manifest and assets |
| Bad data/backup eight cases |Limited reuse of actual old-Host evidence; exact final restore-function call closure unchanged; no new-Host rerun claim |
| Cleanup |Own PID29339 exited,8494 independently confirmed closed; other assigned ports untouched |
| Physical device |DEVICE_NOT_TESTED |

Authoritative accepted-run mapping is `FINAL_SUMMARY.json`, with per-run PID/timing/evidence references. `FINAL_EVIDENCE_CHECK.json` independently rereads all15 logs and PNG headers/hashes. Main final matrix is `final-rc15-cold10-reopen5-r6/report.json`; supplement is `final-rc15-supplement-r7/report.json`. Cold10 More-menu driver failure and reopen04 redundant snapshot race were corrected only in the owned driver and each received one full supplement check. The failed runs remain false in the original report. Their failed-attempt PID was not separately captured; successful-run PIDs are recorded.

Official signed acceptance: `official-signed-rc15-r4/report.json`. Earlier signed-stamp refusals remain in `official-gate-rc15-r1` and `official-gate-rc15-r2`; these altered signed copies before verification, so are invalid-input rehearsal failures, not refusal of the final exact signed bundle. `official-structural-rc15-r3` is explicitly an unsigned-copy structural check.

Historical actual budget failure `../quality/shape-nonempty-cold10-reopen5-r3` is preserved and is not reclassified. `storage-reuse-final.json` scopes the eight old storage cases. This quality PASS does not establish real Mail/Calendar writes, model backend acceptance, user system grants, publisher review or upstream Calendar host-extension acceptance. No shared app/source/SDK/Host/production file was edited, no model or external write submitted, no system authorization requested, no push or message sent.
