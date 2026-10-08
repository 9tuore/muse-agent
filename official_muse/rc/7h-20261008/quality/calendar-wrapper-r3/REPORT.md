# Calendar wrapper r3 — actual final result

Status: **PROMPT_PATH_VERIFIED_AUTHORIZATION_NOT_COMPLETED**.

Root-owned isolated outer bundle `org.xinghai.muse.7h.rc14` contains both Calendar purpose strings. Strict deep verification of wrapper and inner Host passed. Host binary stayed `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`.

Quality PID82773, port8494, minimal no-watcher probe made exactly one `calendar.request_access` in this wrapper round. Actual TCC Calendar message534.584 was preflight=no, subject=new outer rc14. Live daemon logged AUTHREQ_PROMPTING and found NSCalendarsFullAccessUsageDescription with a usage string. The old immediate missing-purpose-string refusal is eliminated for this request. No visual claim about the OS dialog is made.

Native callback completed after120.324359s with is_ok=false, empty permission and `Calendar permission request timed out; check the system prompt`. This establishes the prompting path, not a completed user authorization or full_access. Initial20s pending observation is historical; latest-callback.json and final-observation.json contain the final callback. No second request, Calendar CRUD or system Allow click. No TCC database access or Host/SDK/source/package modification by Quality.

Exact own-PID Calendar chain: calendar-request-events.json (18 entries). Broad stream remains private in .local-state/calendar-wrapper-r3, not committed. Wrapper/Host signatures and binding identify tested bytes. Native request timed out; the system prompt may still be awaiting a human decision, so the Shell is retained until Root coordinates cleanup.
