# Complete SDK Calendar component acceptance — 2026-10-11

SDK pin `4ccf8e068399b1da139771a9ed94cef05fa6ae60`, Hub pin `95e4831afca7227b640f075b252c04355bb63865`, reviewed companion Calendar patch `f40635f6`. This is an isolated companion proposal, not an accepted official release.

## Observed tests

- `octosense-calendar-service --lib`: 10 passed, 0 failed. Includes exact create/update/delete reconciliation, corrupt-store refusal, lookup beyond the 200-item list cap and ambiguous-key refusal. These are temporary synthetic stores.
- `octosense-shell --lib`: three exact tests, each 1 passed, 0 failed: Calendar bundle metadata; cold Mail loading the real Calendar host without preparing its Agent; admitted Mail routing/deduplication and refusal of missing/cross-app grants. The last tests use the existing `World` fixture and actual temporary service store, not physical Person consent or a live Muse Agent turn.
- Input maps were independently rechecked unchanged after each test sequence. Public hashes/counts/boundary are in `calendar-component-test-result.json`; original logs/maps remain in ignored `build/runtime-closure-calendar-full-sdk-r1` and `-r2`.

Commands use `--offline --locked --release`, SDK working directory, features `app-hub,octos-core,app-muse-native-prototype`, two Cargo jobs and one test thread. There was one central Cargo pipeline, and no parallel GUI verification.

## Preserved failure and correction

The first added contract assertion failed: catalog `confirm` was null rather than the string `host`. Official `script_apps::declaration` deliberately omits default Host and writes only App; both the App Hub `Confirm` policy and kernel `HostToolConfirm` default to Host. This was an incorrect test assumption.

The original `calendar-tool-contract-test.patch` and failing log are retained. The revised `calendar-tool-contract-test-r2.patch` keeps all original checks and explicitly verifies raw `Confirm::Host`, `Supervision::HostApproval`, destructive risk, `auto_approvable:false`, required expected snapshot, shareability and the exact get declaration. No admission, identity, consent or production execution code was changed to make this test pass.

## Scope

Shareability does not grant Muse access or approve a write. The Native prototype still has only `os.calendar/calendar.events`. Store admission, trusted Person consent, real Muse Relay, independent live UI/Agent readback, Mail delivery, T18 and the final same-candidate 20 cold starts remain separate gates. All real Calendar writes, SMTP sends and model turns in this test sequence were zero.
