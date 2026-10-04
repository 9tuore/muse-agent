# Final ModelHost and limited SelfMail acceptance

Latest status: actual V9 Shell/ModelHost protocol passed 41 assertions across four scenarios and six localhost POSTs. Exact source/Shell/SDK/Hub evidence is in `PUBLIC_TEST_SUMMARY.json`. This does not establish RC_READY: controller subsequently reported a new application boot-budget failure and is preparing a limited startup delta. The steps below remain the reproducible acceptance gate; do not replace exact verified hashes with old RC5 v5 hashes.

## Required controller inputs

1. Absolute path of a fresh `LOCAL_MODEL_ONLY_SYNTHETIC` candidate, never started, without chat state, Mail account store or real provider settings.
2. Full SHA-256 of the final compact source, matching candidate inventory and installed bundle.
3. Full SHA-256 of the final Shell `Contents/MacOS/octosense`. The new CardHost hash `efd7...` is **not** this value.
4. Actual Hub CLI path and SHA-256. Current `packaging/HUB_BUILD_RESULTS.json` identifies a local extended Hub with a declared overlay; it is not unmodified upstream.
5. Controller-verified public trust Anchor for this exact mirror. Do not derive a trust root from the untrusted catalog being verified.

The older prepare/launch helpers still contain a fixed legacy Anchor. A2 runner requires an explicit value and now executes `hub verify <candidate>/mirror/catalog.json --anchor <anchor>` using the inventoried CLI. It records exit code, CLI SHA, catalog SHA and verification output. Hex shape alone is insufficient. Verified syntax is in `vendor/app-hub/crates/app-hub/src/bin/hub.rs:229` and `hub-usage.txt`; `hub verify --help` is not supported by this CLI.

## Two-stage execution

Replace every placeholder with a controller-supplied actual value. Always use a new output directory.

```sh
python3 official_muse/rc/core_chain/run_modelhost_fixture.py \
  --candidate /ABS/FINAL/FRESH/CANDIDATE \
  --expected-source-sha256 FINAL_COMPACT_SHA256 \
  --expected-host-sha256 FINAL_OCTOSENSE_EXECUTABLE_SHA256 \
  --hub-cli /ABS/VERIFIED/HUB \
  --expected-hub-sha256 FINAL_HUB_EXECUTABLE_SHA256 \
  --hub-anchor CONTROLLER_VERIFIED_PUBLIC_ANCHOR \
  --out official_muse/rc/core_chain/evidence/final-modelhost-preflight \
  --preflight-only
```

Preflight checks files, fresh isolation, loopback model route, free ports and catalog signature. It starts no Shell, CardHost or HTTP backend. After preflight passes, use a different output directory and omit `--preflight-only` to start actual Shell 8490 and synthetic localhost backend 8879. Occupied ports stop the test; other instances are not closed.

Four scenarios: bad JSON followed by valid JSON; bad JSON twice; refusal; truncation. Expected six HTTP POSTs across four logical requests, at most two posts each. Actual ModelHost FORMAT_ERROR/RETRY/FINAL_FAILURE logs, application success/error readback and unchanged default budgets are required. No external actions. A pass is only `SYNTHETIC_HOST_PROTOCOL_PASS`, not real inference, T17/T18 or RC_READY.

Only the runner's own Shell/backend are stopped. Protect 8484/8486/8487/8509/8510. Final visual screenshots are separate. Syntax/readiness checks and actual V9 protocol runs passed; original preparation and zero-POST readiness failures remain retained. No further repeat is needed unless a concrete changed protocol path requires it.

## Two limited self-to-self messages

See `SELFMAIL_TEST_INPUTS.json`. They are prepared inputs, not sent messages. Controller alone verifies that sender and recipient are the same authorized account and performs real operations serially. Send the first message once, read its actual server-generated RFC Message-ID, then send the second once with that real ID in `in_reply_to` and `references`. No guessed message headers and no real contact testing. SMTP accepted alone is not inbox delivery.

Calendar permission currently covers reading, not creation/update/deletion. No new API fees or permission requests.

### Same-Goal acceptance limit

`scheduling.splash:215` requires same account, nonempty linked event ID, a usable link state, and a unique RFC-reference/direct-reply or exact matter-ID match. `schedule_replan_original` further requires `status=verified` and independent `calendar.get`.

Thus two new messages with matching RFC headers do not establish a real same-Goal reschedule. Without an existing real verified Calendar link, read-only authorization cannot complete first real create followed by same-event update. Record that gate as blocked; never attach a fixture verified link or fabricated event ID to a real account. If a real verified link exists, controller determines the observable read-only portion; no mutation approval is implied.

## Evidence

- Protocol: actual Host log, preflight and Hub verify output, bounded POST metadata/hashes, model trace readback, no Mail/Calendar mutation journal.
- SelfMail: exact send confirmation, service acceptance, independent inbox read, actual thread headers, incoming card/source display, duplicate polling without extra card, no automatic reply.
- Preserve all prior timeout failures. Unexecuted branches cannot become PASS.

A2 remains fixture-only and writes only `rc/core_chain/`.
