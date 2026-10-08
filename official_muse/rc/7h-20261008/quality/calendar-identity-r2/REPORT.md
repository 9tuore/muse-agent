# Actual Calendar authorization identity/refusal

Status: **observed refusal; proposed packaging repair not yet verified**.

Same frozen Host SHA `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`; quality-only PID50602 / remote8494. No Host/SDK/main changes. One additional real request in this round, no automatic grant, no Calendar CRUD, no TCC database access/change/reset.

The independent minimal probe has no product watcher/shared pending flag. It performed real `calendar.status` then `calendar.request_access`. Request dispatch timestamp1791474609.349478 and callback1791474609.503117; callback is_ok=true, permission=not_determined, error empty. `observation.json` holds actual results.

During that request a bounded live unified-log stream correlated Calendar daemon request `534.280` with audit PID50602. `calendar-request-correlated-events.json` retains the13 relevant actual entries and raw indexes. It proves:

1. Calendar request is `preflight=no`.
2. Actual accessing/responsible process identifier is inner `dev.makepad.octosense.musecleanroom.local`.
3. TCC authorization **subject** is outer `org.xinghai.muse.tmall.rc10`.
4. `No usage string found (key:NSCalendarsUsageDescription) for client[50602] in bundle:<private>`.
5. `Refusing authorization request for service kTCCServiceCalendar` for that subject.
6. Result `authValue=0, authReason=8, authVersion=2, error=(null)`.

Read-only bundle metadata confirms outer Muse.app lacks both FullAccess and legacy Calendar usage descriptions, while inner Host has FullAccess description. Code signature is ad hoc with no entitlements, but missing entitlement is **not claimed as this cause**: the real daemon refusal names the missing usage string. `launchctl procinfo` was not run because its manual requires root; no escalation attempted. Native bridge's ignored granted boolean explains why empty NSError becomes is_ok=true despite refusal; actual permission must always be checked.

## Minimal Root-owned candidate change to validate

Add truthful `NSCalendarsFullAccessUsageDescription` and `NSCalendarsUsageDescription` to the **isolated packaged outer Muse.app** actually attributed by TCC; retain the existing inner full-access explanation. Preserve binary/code/security limits. Regenerate existing local ad-hoc resource signatures as needed. No formal signing, stable installation replacement, TCC reset or privileged entitlement addition. Then request from that real packaged candidate and require the user's system decision plus a real full_access status/readback. This suggested repair is not itself tested or marked PASS.

Raw broad stream and launch environment stay in quality `.local-state/calendar-identity-r2/`; public evidence contains only exact Calendar request records and selected nonsecret metadata. No Secret/credential search. Other Root/user ports untouched.
