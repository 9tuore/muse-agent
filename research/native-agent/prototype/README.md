# Read-only prototype — BLOCKED, not integrated

This directory is a proposed three-tool interface, not an installed bundle. The
manifest is a fragment, not a signed/admitted manifest. Production Muse was not
changed. Its ID remains `muse-goals`; no alias or replacement application is created.

Run from this worktree root:

```sh
python3 research/native-agent/verify_static.py
```

The script checks the current production entry, the 21 cached pinned upstream
Git blobs/SHA256s, declared read-only flags, production helper/global definitions,
and the official namespace predicate. It writes `../STATIC_EVIDENCE.json` and
`../namespace-policy-excerpt.txt`. Cache input is intentionally ignored; exact
URLs, Git blobs and SHA256s for reproducing those inputs are in
`../upstream-sources.json`. These are static checks, not native admission or a
Splash VM parser/execution test.

`muse-goals` fails the official `[a-z0-9_]{1,24}` tool namespace rule. The proposed
names deliberately retain that identity so the problem stays visible. Do not
install this draft. A native gate, real VM and model-selected tool call were not
run. Target Host support for `app_tools.dispatch@1` is independently unverified.
A future migration must preserve data, account grants, publisher identity and
rollback; this audit does not select an identity workaround.

The hook uses the documented `app_tool(name, call_id)` and
`mod.app_tools.request/complete/fail` ABI. It proposes scoped reads of existing
memory, unfinished mail-linked goals and action/Calendar receipts. Scope must
match the trusted Host account and currently selected project/owner; unavailable
scope fails closed. This account binding still needs actual integration testing.
Memory scoring uses existing helpers, with ephemeral score caches; it avoids
`gm_context`, which writes a retrieval trace. It is not a new ranking engine.

Pending results intentionally exclude unscoped and non-mail-linked legacy goals.
A missing Calendar receipt or an accepted/unknown action is never promoted to
verified delivery. Receipt lookup is not a mail provider delivery query. Only
three declarations exist; none counts toward current native Agent coverage.
All reads cap list results at six. No external request, model call, persistence,
permission prompt, background turn or destructive operation is implemented.
Output item schemas remain broad proposals; runtime schema handling and syntax
are NOT_TESTED. A valid namespace alone would not prove safe execution.

## Five-tool loader probe

`five-tools.proposed.json` expands the interface proposal to five names, preserving
`muse-goals`: existing memory.search, pending.list and receipt.get, plus proposed
transaction.get and followup.inspect. The last two have no Splash handlers; even
the existing three remain unintegrated/unexecuted. They are interface research,
not implemented/admitted tools. No production or identity is changed.

`night-repros/five_tools.rs` executes three tests against unmodified official
policy/contract code. A synthetic digest-bound five-tool bundle is refused by
`AgentBundle::load`. A cloned unrelated namespace control proves descriptor shapes
validate without asserting a migration workaround. A synthetic outbound-only
bundle with the same muse-goals ID loads with calendar.events/add_event/notify and
ask_user_question, but zero own tools. Its loader result is not signed admission,
Host consent, model choice or access to Muse memory/transactions.

Five desired reads and current limits:

| Proposed tool | Intended information | Verified implementation status |
|---|---|---|
| memory.search | Scoped existing memory | Existing research hook only, VM NOT_TESTED |
| pending.list | Scoped unfinished mail-linked matters | Existing research hook only, VM NOT_TESTED |
| receipt.get | Stored action/Calendar receipts | Existing research hook only, VM NOT_TESTED |
| transaction.get | One scoped mail-linked goal by exact ID | Declaration proposal only; no handler |
| followup.inspect | Raw stored statuses for further handling | Declaration proposal only; no decision/handler |

No five-tool model selection test can start from this refused own-tool bundle
without resolving the official namespace limitation. Providing data in a prompt,
calling private helpers or implementing a custom tool loop would not prove these
five tools. The minimum legal outbound path is Root's independent integration
subject to actual Host/consent tests; it does not replace Muse-owned reads.
