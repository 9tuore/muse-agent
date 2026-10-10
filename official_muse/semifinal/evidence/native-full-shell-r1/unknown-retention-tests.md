# UNKNOWN restart and synthetic history retention

On 2026-10-11 the central runner executed two separate reference processes (60622/60625), one fresh synthetic jail, source SHA2253e9f0 and Host78ab9efc. Both exited normally through Remote quit, code0, with no final Script error. All required original recovery, identity/payload, duplicate rejection, unchanged journal and zero-transport checks passed.

The supplementary `unknown_synthetic_retention.patch` seeds history with an explicitly synthetic verified-state input. Every phase records `SYNTHETIC_RETENTION_INPUT_NOT_INDEPENDENT_CALENDAR_EVIDENCE`. This checks persistence of an existing status, not whether a real Calendar action earned that status. No Calendar callback, native consent, Relay or external transport was fabricated.

The original r1 Host-API refusal and r2 `PARTIAL_MISSING_VERIFIED_HISTORY` remain intact. This supplementary fixture is a separate run with a separate probe; it does not replace or relabel those failures. The production source functions and the original proposal file remain unchanged.

`run_unknown_restart.py --probe` selects the additional copied probe; the default is still the original probe. The explicit rc17 fixture manifest is not rc18 candidate admission evidence. Public result: `unknown-retention-result.json`; full logs/jail/input origin: ignored `build/runtime-closure-unknown-retention-r3` and `build/runtime-closure-unknown-retention-input-r1`.

No real Calendar write, SMTP send, model turn, permission change or duplicate execution occurred. Full same-candidate business acceptance remains pending.
