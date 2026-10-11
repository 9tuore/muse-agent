# History and async preparation

State: PREPARED_NOT_RUN. This is a read-only/fault protocol worksheet for the centrally compiled bridge. It does not change the driver, introduce a new Host build or claim runtime success. Apply the Host registry R3 patch first and wait for a genuine fixture.ready; failure before that frame means admission is still blocked.

Read-only baseline requests (one JSON object per line; correlate every reply by request_id):

```jsonl
{"request_id":"history-open-1","method":"octos.session.open","payload":{}}
{"request_id":"history-owner-before-1","method":"fixture/logsideeffects","payload":{}}
{"request_id":"history-current-1","method":"octos.session.history","payload":{}}
```

These requests do not start a model turn or mutate a Calendar event. Record actual frames and the SHA256 of the isolated apps/.host/calendar/events.json if it exists; absence is not an empty-array receipt. fixture/logsideeffects returns the actual owner events response, not a guessed count. Do not print or scan broker-state or runtime peer tokens.

For an existing successful create/update/remove run, request octos.session.history only after its terminal reply. Inspect the actual data.messages tool rows. The SDK calendar_history.rs binds host_calendar_receipt only when turn_id/thread_id, tool_call_id and canonical tool name match exactly one current-generation receipt for that session. A qualifying receipt carries source=broker_tool_result, owner=os.calendar, caller=muse-goals or card.muse-goals, real nonempty session_id/turn_id/tool_call_id/call_id, terminal and the actual result or result_omitted. kernel_persisted=true must already be in the actual bound row. An awaiting_confirmation acknowledgement or fixture model text is not a terminal result. Keep failed/cancelled receipts as failures; do not rewrite them into success or merge receipts across sessions.

Graceful restart check: finish or interrupt all operations, request fixture/quit, wait for actual quitting reply and process exit, restart the wrapper with the same fixture_root and exact same candidate bytes, then request:

```jsonl
{"request_id":"history-archive-after-restart-1","method":"fixture/history-sessions","payload":{}}
{"request_id":"history-owner-after-restart-1","method":"fixture/logsideeffects","payload":{}}
{"request_id":"history-current-after-restart-1","method":"octos.session.history","payload":{}}
```

fixture/history-sessions opens/hydrates only session IDs actually observed earlier; call it while no turn is pending because its host_request calls are synchronous. Its raw_kernel_history is persisted Kernel evidence for that archived session. broker_receipts_reconstructed=false is intentional: the new Broker does not restore missing old RAM receipts. Empty current history after a new nonce-specific context does not prove old history loss. Archive hydrate errors are actual errors, not proof that history or event deletion succeeded. Compare owner bytes/count/IDs with the pre-restart snapshot; do not combine a new-session receipt with an old raw tool row.

Harmless protocol faults, sent in an idle context:

```jsonl
{"request_id":"fault-read-write-method-1","method":"fixture/read-owner","payload":{"method":"update_event","args":{}}}
{"request_id":"fault-unsupported-1","method":"fixture/not-a-method","payload":{}}
{"request_id":"fault-owner-after-1","method":"fixture/logsideeffects","payload":{}}
```

First two must return their actual bridge_error and leave the owner store unchanged; the third must return an actual owner result. A separate malformed JSON line must yield the actual parse error (null request_id) and the next valid request must still work. These are bridge protocol rejections, not Kernel/Relay denials. None should produce a model request or a Calendar write.

Async request sequence: use a new request_id, the original VM prompt and an explicit read-only fixture_tool_plan containing only calendar.events/get_event. Send octos.turn.interrupt with a different request_id without waiting for the turn terminal frame, then read owner/history after both operations settle. The driver accepts an interrupt while a turn is pending and invokes the real ContextOp::Interrupt. Observe actual ordering: a turn that completes first is a completion/interruption race, not a proven cancellation. A second turn is rejected only if the first is still in the pending vector; require evidence of that condition before counting rejection. Do not add delays, mutate the candidate or manufacture a slow model solely to claim coverage.

While a turn is actually pending, fixture/quit returns a protocol error and keeps the process alive. EOF instead initiates shutdown after pending operations settle or the 180-second deadline. Deadline errors explicitly mean result unknown: re-read the owner and persisted history before deciding what happened, and never automatically redispatch a write. If interrupt times out or reports an error, keep the original error and resulting state; successful interrupt alone is not proof that an earlier action had no side effect.

Evidence to retain: frozen config/candidate/source identities; complete bridge-harness stdout/stderr; bridge-replies.jsonl and actual-kernel-events.jsonl; original owner snapshots/SHAs; actual model requests/resolved calls and fixture approval records for any authorized model run; exact request/reply order and process exit status. Mark NOT_TESTED for any scenario not actually observed. Synthetic planning and sheet gestures remain fixture authorization throughout.
