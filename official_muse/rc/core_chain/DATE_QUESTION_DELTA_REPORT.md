# Narrow Calendar missing-date question suggestion

Status: **PROPOSAL_FIXTURE_PASS_ROOT_DECISION_REQUIRED**. Product remains unchanged.

## Observed cause

Canonical source `47c56065ab8be64c48734c4c2b1afdb96de1a6fb391dd360e5dd20a4b5b60966` first handles ambiguity words “过几天／改天”, then returns `chat_payload_error` for empty endpoints. Generic missing-date input has neither ambiguity word, so an empty start/end returns a time-only question before the later source-input date check.

In actual isolated CardHost, three generic missing-date cases all returned “请补充明确的开始时间、结束时间。” and failed the requirement to ask for a date. The product safely rejected candidate creation; the failure is incomplete clarification wording, not unauthorized action.

## Only the suggested condition changed

In a copied fixture source, the leading condition of `chat_candidate_input_error` changed from:

```text
action == "calendar_candidate" && chat_calendar_input_ambiguous(message)
```

to:

```text
action == "calendar_candidate" &&
(chat_calendar_input_ambiguous(message) || (!editing && !chat_calendar_date_known(message)))
```

All remaining source bytes are unchanged. Existing date-known vocabulary is reused. Proposal fixture source SHA: `bbcb6a72fcf4357628f6522bec8980bc7a5b6e08b71bf03581197626e6657ce8`.

## Actual results

Original: **29 checks passed, 3 expected semantic checks failed**.

Isolated suggestion: **32 / 32 checks passed**.

| Variant | Original | Suggestion |
|---|---|---|
| Generic which-day evening question, endpoints unknown | Misses date | Asks date, start and end |
| Generic when-to-meet question, endpoints unknown | Misses date | Asks date, start and end |
| Evening time range with no day, empty dated payload | Misses date | Asks date, start and end |
| No date but model supplies guessed complete timestamps | Rejected with date question | Rejected with date question |
| 明天 with missing endpoints | Asks only missing start/end | Exact same question |
| Valid explicit date and complete range | Valid | Valid |
| editing=true, location-only change, valid original times | Validation allows edit | Validation allows edit |
| editing=true but new day remains ambiguous | Rejected | Same rejection |
| Clear explicit supplement corrects earlier ambiguity | Valid | Valid |
| Latest supplement makes an earlier clear day ambiguous | Rejected | Same rejection |
| End before start | Error | Same error |

Additional guards verify a legal waiting question, valid followup, other project/owner rejection, a genuinely expired Memory reference and a missing Memory reference. Unsupported generic date words remain unsupported; no new vocabulary was added. Invalid non-editing inputs cannot create candidates. Both runs have zero Host requests and zero Goal/Run/Action execution.

These are direct production validation/followup functions in a real CardHost with synthetic inputs and native isolated storage. The location edit case verifies input validation; it does not claim a complete GUI edit or external Calendar action. No real model was called, and no original H05 model output was replayed as live inference.

## Attempts retained

r1 failed before probe execution: the fixture-local name `ok` was parsed as Splash special syntax. Both original and suggestion logs remain. Renaming only that variable corrected the test fixture.

r2 reproduced the three original semantic failures and passed all suggestion checks. Original report, suggestion report and source snapshots remain separate; no first-attempt success is claimed. Product, SDK and Git were never modified by A2, and the product source hash remained the canonical original when this report was generated. Root decides whether to apply the suggestion.

## Versions and evidence

- Base canonical product commit: `b9cf26b8dc0a9bdb51e493cb6a420636a1291e73`.
- CardHost SHA: `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`.
- SDK lock SHA: `3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e`.
- Local comparison summary: `evidence/rc6-date-question-delta-20261005-r2/summary.json`.
- Original failures: `evidence/rc6-date-question-delta-20261005-r2/original/report.json`.
- Suggestion pass: `evidence/rc6-date-question-delta-20261005-r2/proposal/report.json`.
- First parser errors: `evidence/rc6-date-question-delta-20261005-r1/`.

`DATE_QUESTION_PUBLIC_ALLOWLIST.json` is an independent five-file deidentified list; existing 21-file `PUBLIC_SOURCE_ALLOWLIST.json` and its summaries were not overwritten or changed. Raw fixtures/state/full sources/logs remain local and excluded. No external publication, staging, commit or push was performed. Port8509 released.
