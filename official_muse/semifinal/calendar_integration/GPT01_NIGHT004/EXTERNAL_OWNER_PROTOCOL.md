# External synthetic Calendar owner update

Status: OWNED_HELPER_PASS; CENTRAL_FULL_CHAIN_NOT_RUN. The old gpt01-night004-calendar accepts central roots only with --read-only and cannot perform the requested central update. Its binary is unchanged. A separate gpt01-night004-external-owner executable uses the same copied CalendarService source; all four service files were byte-compared with the actual central SDK before the 1.38-second owned build.

Mapping is exact:

| Input | Actual location / identity |
|---|---|
| Selected Kernel bridge config | Its explicit fixture_root value |
| Calendar Host directory | fixture_root/apps/.host |
| Authoritative store | fixture_root/apps/.host/calendar/events.json |
| Service owner | os.calendar |
| Allowed external operation | update_event on exactly one existing event |
| Writer | Separate gpt01-night004-external-owner process; actual CalendarService::call/handle/ui::update/save |

Existing binary / wrapper paths:

```text
/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-calendar-history/target/debug/gpt01-night004-external-owner
/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/external_calendar_update.py
```

New executable SHA256 is e7dc890860d1a17d2fbc08e68ed98aa39c75eaee370bb18a6eb2281b2ed6c265. Original readonly binary remains b603e2549e4e9e2f374d0c385171e2057c5aa3cb8531f2bde64c6be85e3ebc38. To reproduce this small build, run prepare_external_owner.py, then nice -n 10 cargo build --offline --locked --manifest-path build/gpt01-night004-calendar/service/Cargo.toml --target-dir build/gpt01-calendar-history/target -j 1 --bin gpt01-night004-external-owner from the owned worktree. No central driver/SDK/target rebuild is involved.

Central must choose an actual synthetic event ID and its stable request_id from the already successful Kernel/owner get_event result. Save that exact event object, with all original fields, as the --expected-file. Do not manufacture or edit expected. Select this same ID/request_id for the entire CAS test. The wrapper changes only the explicitly supplied title/notes, preserves remaining fields, performs no add/delete, and does not retry a rejected update.

Required existing markers: fixture_root/FIXTURE_ONLY and fixture_root/apps/.host/FIXTURE_ONLY. Central must additionally create apps/.host/EXTERNAL_CALENDAR_OWNER_WRITE_OK.json, with this exact scope:

```json
{"purpose":"NIGHT004_SYNTHETIC_EXTERNAL_OWNER","host_dir":"<canonical fixture_root>/apps/.host","event_id":"<actual selected event ID>","fixture_request_id":"<actual selected stable request_id>"}
```

This marker is a synthetic test scope, not a person's Calendar/Agent consent. Neither wrapper nor binary creates it. The binary requires the canonical root to be a child of central build/night-004, or an explicitly marked gpt01-night004-* temporary root for its local check. It refuses symlink root/apps/host/calendar/store/markers, missing markers, mismatched scope/event/request IDs, foreign owner and methods other than update_event. It calls the real get_event to verify the selected target already exists with that request_id, then passes the supplied old expected unchanged into real update_event; it does not replace expected with its fresh read.

Runnable central invocation, after setting paths/IDs to the actual selected fixture and event:

```sh
OWNER_WRAPPER='/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/external_calendar_update.py'
python3 "$OWNER_WRAPPER" --config "$KERNEL_CONFIG" --event-id "$EVENT_ID" --fixture-request-id "$FIXTURE_REQUEST_ID" --expected-file "$OLD_EVENT_FILE" --notes 'NIGHT004 synthetic external owner revision' --check-only
python3 "$OWNER_WRAPPER" --config "$KERNEL_CONFIG" --event-id "$EVENT_ID" --fixture-request-id "$FIXTURE_REQUEST_ID" --expected-file "$OLD_EVENT_FILE" --notes 'NIGHT004 synthetic external owner revision'
```

--check-only performs real owner get_event and returns current_owner_result plus prepared_owner_request; it never updates. Without that flag the one actual owner update executes. stdout contains fixture_authorization, external_owner_process, actual process_id, kernel:false and result:{ok,data|error}. The wrapper exits 2 on actual rejection; retain stdout/stderr and do not auto-retry. A card projection warning does not negate an authoritative successful event update, but retain it.

Full-chain CAS sequence must be serialized:

1. Finish current Kernel operations, get the existing event through the real Kernel and save its original event snapshot/IDs. Record actual owner/store bytes/count before mutation.
2. Central enables the exact write marker and runs the external helper once. Wait for the actual process exit. Require result.ok, the same event id/request_id, changed notes/title and count still 1.
3. Kernel get_event for the same ID must now show that external revision. For the intended conflict, the following Kernel update must still carry the ORIGINAL saved expected from step 1. Using step 3's fresh snapshot as expected would be a valid update and cannot prove stale CAS rejection.
4. The real Kernel/Relay/CalendarService update must reject the stale expected with its actual error. Read back the same ID and require external revision preserved, store bytes/count unchanged by that rejected update. Inspect the actual Kernel History tool row/terminal error receipt and retain actual session/turn/tool_call/call IDs; this helper creates no History or receipt.
5. Remove only the external write marker when the scenario ends. Event cleanup, if desired, stays in the authorized real Kernel/owner flow with a fresh actual snapshot.

This helper does not provide cross-process writer locking. Do not race concurrent writers; only run the external owner after the Kernel is idle, and start the stale Kernel update after the external process exits. Its authorization/transport adapter is an explicit synthetic fixture around unchanged production CalendarService. Local EXTERNAL_OWNER_RESULT.json records 12 actual steps: seed/create/read; six rejection guards; check-only; separate wrapper update; production stale CAS rejection; actual readback. Central store writes and final Kernel/full-chain CAS evidence remain NOT_RUN here.
