# Mail edit header merge: minimal isolated proposal

Status: **PROPOSAL_FIXTURE_PASS_ROOT_REVIEW**. A2 has not modified product or SDK.

## Root cause and smallest boundary

Actual source entry is `send_chat`; no `chat_submit` was found. Mail model schema requests complete `to/subject/body`. An edit prompt says to preserve unmodified fields, but `chat_add_proposal` adopts all returned strings. Only `chat_mail_reference` (“回复他说/她说/对方说”) restores the original recipient; no deterministic subject preservation exists. A body-only edit may therefore silently replace headers.

The proposal changes one acceptance block and adds one helper. It does not modify provider/model prompts, schema, field validators, candidate bindings, whole-request keep logic, form consistency, memory, approval or sending:

1. For an editing `mail_compose` request, parse the already-bound original payload.
2. Preserve original `to` and `subject` unless the user gave a recognized explicit command for that field.
3. Field-specific negative/preserve expressions take priority. Positive field commands must begin a sentence/clause, preventing a simple quoted header command in body content from authorizing a header edit.
4. A question ending in 吗/么/?/？ is refused as an edit, preserving the candidate.
5. Pass the merged payload through all original validation/current-binding/open-form guards. No sending or confirmation is added.

Concrete fixture-only helper: `mail_header_proposal.splash`. Exact replacement block: `NEW` in `run_mail_header_delta.py`. These files are proposals; root chooses whether to apply them.

## Results

Base readable source SHA: `92c4838e50c183e162f425287881219caaf2942acf9cf9521fffd1e98e30a22b`.

Final isolated proposal source SHA: `61c784c987551151f7c4b3a379699e907edb25438fe89ec317271ff33d0b501a`.

Actual CardHost SHA: `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`.

Original: **68 pass / 18 fail**. Proposal: **16 variants / 86 assertions pass**.

| Variant | Verified proposal behavior |
|---|---|
| Body intent only, matching the reported E04 edit type | Keeps subject/recipient, changes body |
| Body edit while model returns another recipient | Restores original headers |
| Explicit subject command | Changes subject; recipient preserved |
| Explicit recipient command | Changes recipient; subject preserved |
| Both header commands | Both requested headers editable |
| Negative subject suffix / subject-first negative | Keeps headers while changing body |
| 不改主题，只改正文 | Body changes; headers retained |
| 不要改主题，只改正文 | Existing whole-request keep rejects; unchanged |
| 主题要改吗？ | Refuses edit; card unchanged |
| Informational mention of existing subject | Does not authorize header change |
| Quoted “请修改主题” in body-only command | Does not authorize header change |
| Reference reply body edit | Original headers preserved |
| Overall 不要修改 | Existing keep guard preserved |
| Opened form with different handwritten body | Rejects; handwritten draft and card unchanged |
| Opened form while draft status is sending | Rejects; draft and card unchanged |

Accepted changes retain card identity, increment revision once and remain unapproved candidates. All drafts remain untouched in these tests. A stale candidate payload binding is rejected and its card preserved. No Host request, model call, Goal/Run/Action or send confirmation occurs.

## Known boundaries

The helper recognizes conservative Chinese field commands; it is not a complete natural-language parser. Unrecognized wording retains original headers. The existing whole-request keep prefix uses 不要/不用/别 rather than plain 不; it remains untouched. A compound “不要改主题，只改正文” therefore keeps the entire candidate rather than processing the body clause. No claim is made that this pre-existing routing behavior was improved.

These are actual production merge/guard functions with synthetic proposed output in isolated CardHost. Rendering is suppressed. No real SMTP, model inference, complete GUI interaction or new product candidate was tested. Root reported the real E03/E04 private driver as RUNNING after ENOSPC; A2 did not read that private data and does not claim its full driver passed.

## Attempts, capacity and evidence

r1 retained original failures and two fixture expectation failures: plain 不改主题 was mistakenly expected to trigger whole-request keep. The proposal already changed body and preserved headers.

r2 corrected that fixture expectation and separately tested the actual 不要 prefix: 80 proposal checks passed.

r3 anchored explicit positive field commands and added the directly related quoted-body case: 86 checks passed. Original failures remain separately preserved. No original 20-case expectations were changed.

Each run uses a thin template containing **only the actual manifest**; no image/resource files or builds are copied. Final r3 evidence occupies approximately **1.43 MB**. Original source text, instrumented original/proposal scripts, logs and isolated state stay local.

Local evidence: `evidence/rc7-mail-header-delta-20261005-r3/{summary.json,original/report.json,proposal/report.json}`. Earlier r1/r2 attempts are retained under matching evidence folders.

`MAIL_HEADER_PUBLIC_ALLOWLIST.json` independently lists six deidentified files. Prior public lists and summaries were not overwritten. Raw evidence, full sources, state and logs are excluded. A2 made no product/SDK/Git edits, stage, commit, push or publication. Port8509 released.
