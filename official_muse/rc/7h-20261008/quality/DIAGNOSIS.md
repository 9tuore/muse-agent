# Quality / cold startup evidence

The rc10 baseline is the exact business compact SHA `0caaee7374e2446abafffeda33fe24bdcf8f9125757f881d664efabb83c36686`, unchanged Host `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`. No private account/profile copied. No external service writes, model submissions or budget changes.

## Prior three failures

`prior-cold-r3.json`: cold02/09 outer launcher timed out after40s, leaving missing logs/snapshot; cold03 previous Shell remained alive after quit. These records cannot establish a VM budget failure. The existing success range was18.81–49.37s to content. All historical failures retained in original evidence.

## Current observation

`baseline-rc10-r1/report.json`: actual visible Shell, editable input16.99s;16sessions/256longmessages,64claims/65sources and64mailseen restored. Protected files unchanged; all six navigation pages accessible; no error/budget lines. Correct visible screenshot inspected. This single pilot is not the final10+5matrix.

`profile-rc10-r2` and `profile-granular-r1` are explicitly diagnostic source variants. Timing from granular callback profile shows chat validation128callbacks:34.66ms inclusive total but~9.2s wall; memory index18+validation65callbacks:~3.4s wall,84.41ms execution. Calendar0.43ms, Mail0.55ms. This supports bounded slice-size tuning after worst-case tests, not raising Host execution budgets or skipping validation. Diagnostic timing writes add overhead.

Initial diagnostic publication reused rc10 version and was correctly refused (`diagnostic-publish-refused.txt`). Subsequent diagnostic versions are local-only and uniquely named.

## Next required gate

Root freezes candidate source/bundle/Host SHA. Run10complete new-process cold launches +5same-Shell app reopens with input edit/readback, nonempty memory/task recovery, unchanged protected bytes and no duplicate effects/errors. Standard official CLI provenance/check/scan must be bound separately; local rehearsal signatures are not official admission/publication.
