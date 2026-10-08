# Calendar permission: read-only narrowing

This is static/local metadata evidence, **not** a successful system authorization request. Quality has not reset TCC, modified host code, granted access, or initiated a permission popup.

- Current compact source SHA: `cceeaa009f029c951d8e0a61a8a1cf0ac91802746868d2f38d3de892a889be78`.
- The product button invokes `calendar_request_access`; it calls the real `host.request("calendar.request_access",{},callback)`.
- The function silently returns while `calendar_pending` is true. A five-second permission watcher also calls `calendar_status_load(true)`, which sets this same pending flag until its asynchronous callback returns. Therefore a click during a pending status read can be silently discarded. **This is a verified code path, not yet a verified cause of the observed failed click.** A product-side dispatch trace or a minimal request probe is required to distinguish it from host/native behavior.
- Native calendar service registration, worker-thread dispatch, full-access EventKit request, completion callback and 120-second wait exist in the overlay. No evidence supports inventing a different service name.
- Actual installed rc10 Host Info.plist includes `NSCalendarsFullAccessUsageDescription` with a nonempty Chinese usage explanation. Bundle ID: `dev.makepad.octosense.musecleanroom.local`. A missing usage-description is not demonstrated.
- Calendar status and access-request are separate methods. `status=not_determined` proves a read response, not that request_access was dispatched or macOS displayed a prompt.

Next minimal distinction: on the quality port only, a dedicated app with a request button and explicit dispatch/callback labels (no watcher, no shared pending guard) can observe the same host service. Request must be a deliberate user action; callback must report actual permission/error. No EventKit CRUD, credentials or model are required. Such a diagnostic has not been executed and cannot count as product acceptance.

## Actual independent diagnostic, later in this round

Following Root's explicit authorization to trigger the real request, the minimal app was executed on8494 with the same pinned Host. Its source is `calendar_permission_probe.splash`, SHA6816e2047584302cde274069ef324f3c478829b1dfa506e3d59d8c62e9488fe5. Real status callback succeeded with not_determined. One real request_access then returned in2.117s: is_ok=true, permission=not_determined, empty error. It is not pending and not granted. Actual user-facing screenshot and dispatch/callback records are under `calendar-minimal-live-r1`. No system Allow was selected by quality, no Calendar CRUD occurred. Popup appearance is not established by Shell-only capture.

This reproduces the ungranted response without the product watcher/guard; the earlier guard hypothesis cannot be treated as the observed root cause. Native bridge currently discards granted boolean and treats empty NSError as success; caller must separately test actual permission.

Read-only system log limited to octosense permission messages produced two entries (TCCAccessRequest IPC and tccd connection); raw records remain private. Host-binding report confirms macOS14.8.7 and a nonempty usage-description. A separate identity-filtered tccd log query hit its30s timeout; no conclusion from that query, no retry, and no TCC DB accessed or changed.
