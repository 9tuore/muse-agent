# Stability integration — 2026-10-10

Status: BLOCKED_REFERENCE_HOST_API; no new GUI/build run.

## Verified diagnosis
- Candidate UI runtime-0.log admits rc18 policy, then evaluates 717 bytes. Candidate main.splash is 491529 bytes; goal_input missing is refusal UI, not application timeout.
- Reference native main.rs registers only calendar. appstore discovery intrinsically provides runtime.list@1; no Mail service registration/dependency exists in this native host.
- Exact missing requirements: mail.compose@1, mail.compose_status@1, mail.review_send@1. Host API matching requires exact major version.
- Offline experiment extracted actual refusal_card/wrap_script_text/escape_script_text from build/pivot-builtin-calendar-patched-r5/native/src/host.rs. rustc refusal_probe.rs; executable PASS, reconstructed refusal source exactly 717 bytes. This corroborates the missing-Mail cause; live refusal widget text was not re-read.
- Existing compact five-window proof remains separate and valid; current candidate rejection does not invalidate it. No 20-run claim.

## Minimal proposed integration
reference-mail-demo.patch adds the verified official octosense-mail-service dependency and calls register_demo() before host::run. No fake runtime-feature advertisement, no manifest weakening, no history clearing or budget adjustment. This patch is proposed and uncompiled. DemoTransport/FileVault means fixture only, no actual delivery. Full Mail native review presentation requires Shell callbacks; this registration alone does not establish review/send full-chain success.

## Central serial requests / exact next verification
1. Apply patch to regenerated native reference host, adapting dependency path to matching source checkout; verify unified appstore dependency/workspace resolution. Existing frozen Host stays preserved.
2. Central alone builds release with prior approved flags, freezes binary SHA and checks runtime.list has all four required APIs at version 1.
3. Central runs existing action_chain/tests/run_native.py with --help-confirmed options, same candidate manifest/main.splash, same 16-session/256-message/64-Memory synthetic fixture, fresh ignored output and exclusive GUI slot. Verify logs evaluate 491529 bytes and goal_input/content is real; capture five sizes plus restart. Do not use bare window presence as success.
4. If new refusal remains, preserve it and log the actual compatibility error in native host refusal branch (one error! line), rather than increasing budget.
5. T18 acceptance precedes final 20 iterations. No tests or production changes requested here beyond this bounded diagnosis.

No source/main.splash, shared reports, root bundle, installed application, production data, branch or commits changed.

## Reusable offline log checker

Added check_host_log.py and test_check_host_log.py in this owned directory. 8/8 parser tests pass (0.015s), including actual frozen refusal/time-budget logs and constructed SHA mismatch, explicit API refusal, empty checks, other error and window-only counterexamples. Initial test path parent index error was corrected; no product test rerun.

Usage from workspace root (repeat --log in report cases order):
```sh
python3 -B official_muse/semifinal/stability_integration/check_host_log.py --source build/NEW-RUN/bundle/main.splash --report build/NEW-RUN/report.json --log build/NEW-RUN/runtime-0.log
```
For five cases pass all five logs. Report/log count mismatch is a failure. Exit 0 means only payload byte count/view observed without detected errors and, if supplied, matching input SHA and complete true harness checks. It never means Mail success. JSON retains original requested_size, restart, checks, input_rect and runtime_errors through harness_case.

Classification distinguishes COMPATIBILITY_REFUSAL (explicit log text), SCRIPT_TIME_BUDGET_EXCEEDED, OTHER_RUNTIME_ERROR, ARTIFACT_SHA_MISMATCH, PAYLOAD_NOT_OBSERVED, PAYLOAD_EVALUATED_WITHOUT_VIEW and failed/incomplete harness. Old 717-byte log has no rejection text, so automated classification is PAYLOAD_NOT_OBSERVED; earlier exact offline refusal reconstruction supplies its diagnosis separately. Milliseconds are absent in timeout logs: matching historical Host source widget_async.rs:458-459 sets 64ms, but a new Host must have its own budget identity checked. Likewise eval logs do not contain SHA; checker explicitly limits byte-count evidence instead of asserting cryptographic executed identity.

No GUI/cargo/20-run, shared-file edits or Git operation performed for this addition.
