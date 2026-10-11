# Real Kernel bridge: prepared, not compiled or run

Current integration patch: NIGHT004_kernel_and_bridge_r2.patch on the b9765284 format-fixed R4 baseline. It combines the corrected destructive-update Deny journey and the ignored JSONL bridge so CENTRAL can compile once. Alternatively apply denial_r5 first, then kernel_bridge_on_r5. Old bridge R1 is retained as evidence. No production gate/schema changes. Exact bridge filter:

`host_tools::real_kernel_tests::night004_kernel_jsonl_bridge_fixture_driver`

After CENTRAL compiles the test binary, run the JSONL wrapper:

```text
python3 kernel_bridge/bridge.py --test-binary <CENTRAL compiled Shell test binary> --kernel <pinned octos-kernel> --config <explicit fixture config.json>
```

Config fields (all required):

```json
{"fixture_root":"CENTRAL/build/night-004/<new-isolated-bridge-state>","signed_bundle":"<frozen public signed muse-goals bundle directory>","mirror":"<same candidate public mirror directory>","main_sha256":"<actual frozen main.splash SHA256>","anchor_public":"<trusted release public anchor hex>"}
```

The root must already exist under CENTRAL/build/night-004 and have FIXTURE_ONLY. The driver only copies the explicitly supplied public bundle/catalog; it never creates signing keys, searches credentials or reads production profiles. Actual manifest/catalog signature and bundle digest admission must succeed. On restart, copied public files must match existing bytes, so a changed candidate is refused. Use the same state for actual owner store/Core ledger/SDK-managed peer resume state; no release/remove-state on graceful quit.

stdout is one JSON per reply, flushed. The first unsolicited method fixture.ready carries actual source main SHA/version/paths and pinned Kernel SHA. The wrapper only removes the libtest prefix; it retains complete stdout/stderr in root/bridge-harness-*.log. Parent requests use {request_id,method,payload}; response is {request_id,method,is_ok,data|error}. data is the actual Broker/Core/owner result. Multiple requests may be pending; match responses by request_id. An interrupt can arrive while a turn is pending.

Methods:

- octos.session.open: actual ContextOp::Open on the Muse request context.
- octos.turn.start: payload.text is the original VM prompt, passed unchanged to Broker. payload.fixture_tool_plan and fixture_approval are separate test model/authorization inputs, not a replacement prompt/result.
- octos.session.history: actual ContextOp::History -> Kernel session/hydrate -> actual Broker calendar receipt attachment. No synthetic kernel_persisted field is added by the bridge.
- octos.turn.interrupt: actual ContextOp::Interrupt.
- fixture/read-owner: payload {method: get_event|events,args:{...}}, actual Calendar owner handler, read-only.
- fixture/logsideeffects: actual owner events result; data.events.length is the actual stored count.
- fixture/history-sessions: raw actual Kernel hydrate for only session IDs previously observed from actual context events/receipts. This is separate history evidence; it does not reconstruct/attach missing Broker RAM receipts after restart.
- fixture/quit: graceful close only when no operations pending. Interrupt or finish first. EOF also shuts down after pending completion/timeout.

Tool-plan example for create -> same-request-id get (synthetic fields only):

```json
{"request_id":"vm-turn-1","method":"octos.turn.start","payload":{"text":"<ORIGINAL VM PROMPT, verbatim>","fixture_approval":"once","fixture_tool_plan":[{"tool":"calendar.add_event","args":{"title":"Synthetic","start":"2026-10-13T15:00","end":"2026-10-13T15:30","timezone":"Asia/Shanghai","location":"Fixture room","notes":"Fixture notes","request_id":"vm-stable-1"}},{"tool":"calendar.get_event","args":{"request_id":"vm-stable-1"}}]}}
```

Update three phases: get_event(id) -> update_event(id,expected ref to actual step-0 event, complete new fields) -> get_event(id). Delete three phases: get_event(id) -> remove_event(id,expected actual step-0 event) -> get_event(id). An argument object {"$tool_result":0,"path":["event"]} refers to the parsed actual previous tool message; the fixture only unwraps an explicit successful {ok:true,data:...} envelope if present. Indexes/paths must exist. Failed actual tool results stop the plan; missing refs return fixture model error rather than inventing a snapshot.

The local OpenAI-compatible plan_model.py uses the actual offered function names and actual tool messages. It never forges a tool result. It records full actual model requests, decisions and resolved tool args in model-requests.jsonl/resolved-model-calls.jsonl. ApprovalRouter answers Once only for the actual Calendar owner/Muse caller and args matching the current resolved plan; all gestures are TEST fixture gestures. Any other pending request is denied. Unknown trigger stays Unknown; no standing/developer blanket approval.

Official Calendar add_event is act and has no mandatory Host confirmation sheet. A bridge plan containing add_event therefore requires explicit fixture_approval:once before dispatch. Missing/deny causes a fixture protocol error before a Kernel turn; this is not labeled a real Kernel Deny. update_event/remove_event are destructive plus confirm:host, so fixture_approval:deny exercises their actual Kernel/Router denial. Do not change official risk declarations to manufacture a create sheet.

Persistent evidence: bridge-replies.jsonl, actual-kernel-events.jsonl, fixture-approvals.jsonl, observed-kernel-sessions.json, model requests/resolved calls, actual Calendar store and actual Core ledger. The SDK's broker state contains its private runtime token and is never printed or scanned. Old contexts are nonce-specific; restart creates a new context. fixture/history-sessions re-reads original persisted contexts, while octos.session.history remains the current genuine Broker history. Do not merge old raw rows into current receipt proof or write kernel_persisted:true yourself.

GPT02/VM integration: retain the frozen production business functions and original generated prompt. Add the explicit plan in the parent driver only. Return bridge is_ok/data/error to VM callbacks and preserve full raw logs/source identity. Native verification must use actual current Kernel History; absence/error/unknown is a real failure/UNKNOWN. Rust helper success or an admitted source identity alone is not L3 PASS. Mail uses its separately supplied real service/fixture transport boundary.

Validation so far: patch apply/byte comparison, syn parse of every resulting whole Rust file, Python py_compile PASS. Not typechecked, compiled or runtime-tested here. CENTRAL owns the unique full build. Combined R2 before SHA b9765284ef9a08e0c4c8f2a00f96df608462cda5dcfebce765477fccd90f8e7f; after SHA fb74bd8eeb3cfba81adf2e6d44698b3aa4e1ac51e642a59182a086f44be0a7f1. Fingerprints and R4 original failure SHA are in KERNEL_DENIAL_AND_BRIDGE_R2_RESULT.json. R1 identities remain historical.
