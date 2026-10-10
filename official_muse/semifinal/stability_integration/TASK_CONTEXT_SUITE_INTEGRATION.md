# Task context view VM increment — central execution only

Prepared, VM NOT_TESTED. task_context_view_suite.splash contains 17 boolean checks plus forbidden_calls guard; suite SHA256 96e77951104ee10c78475e3d7b05632cf3802f94583c38ffe04857d2fb4f42aa. Production function symbols verified in current source; no syntax/VM/visible-UI claim. All records, accounts, receipts, domain capability labels and private-args sentinels are SYNTHETIC. The suite directly injects memory records, reads production chat_task_focus/dsl_view, and writes only the isolated test jail. It does not validate persisted Goal schema or real consent/Agent/host actions.

## Integrate with existing harness

regression_run.run_suite(name, source, bundle_source, output, port, probe_path=None) supports an explicit probe_path. Use name='task_focus', this owned suite as probe_path, frozen current source text, a matching snapshot bundle and a new ignored central output directory. No new shared own_suites entry needed. Existing fixture transport/widget substitutions must remain as reported; forbidden_calls/no_transport_calls fail if task projection dispatches anything.

Observed current regression_run.run_suite uses existing.HOST and launches with cwd=existing.HOST.parents[2]; its CLI has no --host. Central must resolve the intended reference Host explicitly before launch, set regression_run.existing.HOST to that verified Path in the invoking Python process and verify the resulting cwd/resources match the tested Host. Do not silently fall back to the removed historic binary. Record Host/source/suite SHA, runtime.log and fixture substitution identity. If Host unavailable or no fresh probe report, mark NOT_TESTED/ERROR and preserve failure, never infer PASS.

Conceptual invocation using central-established values (not a newly invented CLI):
```python
regression_run.existing.HOST = verified_host_path
result = regression_run.run_suite(
    'task_focus', frozen_source_text, frozen_bundle_path,
    new_output_path, exclusive_port,
    owned_path / 'task_context_view_suite.splash')
```
All values above must be resolved by central before execution. Check exactly 17 booleans present/true, forbidden_calls empty, runtime errors absent; empty or partial check object is not success. This suite schedules one probe at 0.1s through the existing instrumented widget runner. No paid model/network/system calendar/mail execution.

## Coverage

muse.view/1 kind=task_context, read_only=true/tool_authority=false; UNKNOWN retained without completion/result_count despite synthetic receipt; cross-session/project/owner and revoked-account isolation; archived exclusion; first eight valid ordered step identities only; no tool args/grants/authority export; large optional plan omitted while core goal survives; complete serialized envelope <=1600; dynamically sized ASCII core exactly1600 then one-character excess excluded; no new transport calls and stored goals/receipt unchanged after projection. The introductory natural-language sentence is outside the JSON cap, matching current requirement. ASCII JSON makes these boundary length counts equal UTF-8 bytes; no claim of non-ASCII byte semantics.

## Existing suite compatibility patch

legacy_task_focus_envelope.patch adapts existing focus_items() to require muse.view/1/task_context/read_only/no-authority and return records. Existing boundary check now measures full serialized envelope rather than array only. Original shared test untouched. Central may apply it before rerunning affected task-focus regression; this is distinct from the new 17-check increment. Preserve old failure output. No repeat of unchanged 37-check action projection.

## r1 failure retained / revised suite

First actual central run build/runtime-closure-task-dsl-vm-r1 failed because goals.json was absent; no PASS claimed. Suite now explicitly writes a synthetic snapshot before reading stored_before. Added three checks: completed receipt count survives oversized optional plan; empty steps and missing schema do not produce plan. Current expected count is 20 boolean checks plus empty forbidden_calls (supersedes earlier 17). Source currently accepts object+steps without schema/nonempty validation, so the last two are intended bug-revealing checks; keep failures until central fixes production. New suite SHA256 251b264d0d7790945e7c3a1ce66013f41776df78722d368cdae57272f794f95a. VM rerun not performed here.

## GoalSpec actual-contract alignment

Valid SYNTHETIC inputs now use observed muse.goal/0.1, goal_id=synthetic-goal, revision=1. Missing-schema and empty-steps fixtures retain matching goal_id/revision so unrelated invalid fields cannot hide failure. Added wrong schema, wrong goal_id and wrong revision counterexamples: each must retain the core goal and omit plan. Current expected count 23 booleans plus forbidden_calls; suite SHA 4df6a33e26173814787b14b049b561a58f52ab5fc8aff4215220d5001c927bba. VM NOT_TESTED here; original r1 file-not-found evidence retained. Current source still builds empty plan for matching-schema empty steps; its strict no-plan check remains, potentially exposing a remaining boundary bug. No weakened expectations or source edits.

## Actual central Task23 result observed

Read build/runtime-closure-task-dsl-vm-r3/run/report.json: passed23, failed[], FIXTURE_PRODUCTION_FUNCTIONS, Host78ab9efce55cb692552a3566e7b579d2e8c304eadfd6b107c51b2efb027e34db. This supersedes prepared/NOT_TESTED for that frozen suite execution only; real model/Mail/Calendar/consent/full-chain remain false/unverified. Preserve first file-not-found and bare scope-key JSON budget failures.

Legacy regression remains separate: r3 had10 true/3 false without runtime errors. New legacy_task_focus_plan_binding.patch SHA 38311007c302df8982ea4adbf199ceac2b6b2c68ebfc83296e74eec3f2fa73c5 waits for production make_plan-returned id to bind the original session before synthetic run/finish. No manual session binding. Await central next VM; do not transfer Task23 PASS to legacy.
