# A2 manual original-matter selection: latest tested state

Status: **PARTIAL**. Latest tested readable4e0269b9267f6e047c22c7e48906eb03a6f8aa56fc4927914a2e8da56176f7ec (rc33), compact20cf8dff2d3926b816ce6de2bf0b4b3c4bf9a07bfc77317a3b42c9cce6e7aefd. Default20M instruction/heap/wallclock budgets unchanged. No real model/Calendar/SMTP, production data, permissions, source/Host/SDK edits or Git operations by A2.

## Scope and version-specific outcomes

- d17 rc30: small explicit selection11PASS; five initial refusal guards plus selected-message change during get56PASS; full independent disk comparisons18PASS.
- 0a16 rc32: message change during get10PASS; ownership withdrawn after actual phase0source save10PASS; independent disk11PASS. The latter preserves the prepared source at its original scope but does not append a claim/replan Goal/change link/dispatch model or external action. It does not claim a blanket rollback.
- 4e0269 rc33: legal dense profile **ERROR, instruction limit exceeded**. New source/claim and same-Goal update plan persisted; no model request or calendar mutation occurred. Earlier PASS counts retain their observed SHA and were not rerun on rc33.

## Actual failures retained and fixes tested

1. d17 dense exhausted instructions inside core_utc_iso after cumulative source→claim→Goal→link→selection→model preparation. Root split these into50ms phases.
2. rc31 legal selection was falsely rejected before writing: context.link_binding came from JSON-cloned link while current guard compared original object serialization. Own diagnostic observed different bytes for the same roundtrip. Root captures original live link bytes. The original failed report and an initial probe missing-history error are preserved.
3. rc32 split preparation persisted correctly but model preflight exhausted instructions in gm_score. Actual code scored every non-preference twice, first in gm_context then again before checking memory_type in policy completeness loop. Root put the cheap preference predicate first without removing any preference or lowering retrieval.
4. rc33 got through gm_context (real trace5hits,2069bytes,truncated59reasons), then the same callback exhausted instructions inside chat_context_refs (5hits×64entry scans). Host model.complete was never reached. Root is preparing a separate bounded tail callback with exact memory/current binding; this report contains no unexecuted pass for that change.

The limits are cumulative; logged source spans identify exhaustion locations, not standalone proof that time conversion/string search/reference conversion APIs are faulty. No budget/capacity was raised. Runs/actions in failed dense profiles remain identical to the synthetic seed; the original event ID is preserved. Failed dense preparation does not mean a system reschedule happened.

## Concrete evidence

MANUAL_REPLAN_FAILURE.json (rc30), manual-replan-rc31-r2/FAILURE_SUMMARY.json (false stale), MANUAL_REPLAN_LATER_FAILURES.json (rc31/32/33 raw-log SHA and spans), MANUAL_REPLAN_GUARD_READBACK.json and MANUAL_REPLAN_RC32_GUARD_READBACK.json. Full raw logs/bundles/jails remain local; only small safe reports/probes are whitelisted.

Fixture records are copied from A2's actual earlier verified synthetic CardHost chain, with matching Goal/Run/action/link/receipt/artifact. Dense profile is32Goals,128Runs/actions,63initialclaims; preparation adds the64th claim but no Run/action. Get replies and model account preflight are synthetic; model callback only queues. No credentials or real account traffic.

The first small probe lacked synthetic mail.accounts response for actual model preflight; its failure is preserved and the corrected same-source small run passed. A592-source start was refused before Host startup when main had changed. This is not relabeled as592 testing.

## Remaining gates

Dense model-preparation must pass before this task can be accepted. No actual update/delete/real inference/native Shell visual UI or EventKit acceptance is claimed. Root owns product source, integration and native acceptance. The historical copied manifest label is not a tested install; actual code identity comes from source/compact/Host hashes. The diagnostic runner needs retained local synthetic materials, not a portable fresh-checkout install.
