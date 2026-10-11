# Actual bridge L4 parent

State: PREPARED_NOT_RUN. run_l4_bridge.py is for Root to execute after its one R8 build. It does not change the Rust bridge, production Main, parent VM, SDK or target. This is an actual signed candidate/Broker/Kernel bridge check with synthetic model plans and approval gestures; it does not itself evaluate the production Main VM and cannot be presented as product L3 acceptance.

Pinned identities: signed compact main 643009fed5065fd0cb43c2b2210c175cd162f31a9eb6bf5f67004f8f504223dc; actual SDK test source 0426f4db13d86b577166b334c4686668c81cf8c7fa62d0f05e44e43c54eee1b9; Kernel 56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270. The compiled R8 test binary SHA must come from Root's real build result; the preparation does not guess it. The parent validates each identity before launching.

Root setup: use a NEW existing directory under central build/night-004, with FIXTURE_ONLY and an otherwise empty Calendar owner store. Supply the existing bridge config schema with this new fixture_root and the exact signed 643009 bundle/mirror/public anchor. Do not reuse the business-chain state or its selected event. The output must be a new child directory of this fixture root. All state, writes, catalog transitions and evidence stay inside this marked synthetic fixture; symlink roots/marker/store ancestors are refused.

Root command (set variables from actual build/config identities):

```sh
L4_PARENT='/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/kernel_bridge/run_l4_bridge.py'
python3 "$L4_PARENT" --config "$L4_CONFIG" --test-binary "$R8_TEST_BINARY" --test-binary-sha256 "$R8_TEST_BINARY_SHA256" --kernel "$PINNED_KERNEL" --withdrawal-catalog "$PUBLIC_SIGNED_WITHDRAWAL_CATALOG" --out "$L4_FIXTURE_ROOT/l4-evidence"
```

Only Root executes this command. The preparation chat has run Python syntax/AST/help and static checks only; no Kernel, GUI, service mutation or central build was launched for this L4 driver.

Required scenarios and actual evidence:

| Scenario | Required evidence |
|---|---|
| Stable request retry + restart | Two separate Kernel turns repeating exact add arguments and stable business request_id, plus another after graceful actual process restart. Actual add receipt reports reused=true; same owner id/request_id/all fields, event count=1 and bytes unchanged. Actual persisted archived Kernel tool rows retained separately from new Broker RAM receipts. |
| Destructive update Deny | New real pending sheet fixture answer for exact owner/tool/args, audit id hosttool: plus the actual Kernel receipt call_id, by=person/result=denied/reason=denied on the sheet, and a bound persisted Kernel declined receipt. Owner event/count/bytes unchanged. Gesture remains explicitly synthetic. |
| Destructive remove Deny | Same exact occurrence/confirmation/audit/declined binding for remove_event; selected event still exists and bytes/count unchanged. |
| Interrupt and reconcile | Resolve an actual update plan after actual get, call genuine ContextOp::Interrupt, retain both actual interrupt and original turn terminal replies. Require a nonempty actual interrupted list for interruption coverage. Completion race is NOT_TESTED. No write retry. Actual owner and a subsequent read-only Kernel get must agree, identity/count remain one, and bytes reveal whether the permitted update occurred before interruption. |
| Signed caller withdrawal | Root-provided public signed catalog with higher sequence, same candidate manifest and exact rc7 entry withdrawn. Actual existing conversation's next update must report withdrawn through real admission; owner/count/bytes unchanged. No fake Kernel receipt is required or added for a pre-dispatch admission rejection. |

Actual Host confirmation evidence is the real pending-sheet/Router audit chain. The official Relay acknowledges awaiting_confirmation before requesting that sheet; the parent does not fabricate or add an acknowledgement to Kernel History. It binds the recorded actual sheet decision to the Kernel call via the official hosttool: prefix, and additionally matches the driver's real pending-request fixture answer by exact tool/arguments. A create plan lacking fixture Once is only a bridge protocol rejection and is not included as a successful Deny scenario.

Signed withdrawal input: it must be issued under the same configured trusted anchor, preserve the frozen candidate manifest, mark only the intended selected release withdrawn, and use a sequence greater than the offered mirror's sequence. The parent copies those exact public bytes only into fixture apps/catalog.json; real App Hub accept_catalog/admission verifies the signature/channel/floor. A malformed signature, unrelated version or rollback fails the scenario. The helper never reads signing keys or makes a signature. If --withdrawal-catalog is omitted, that required case is NOT_TESTED and overall status is PARTIAL/exit 2. Removing or corrupting a catalog is not substituted for signed withdrawal.

Withdrawal runs last. Preserve the original offered catalog as evidence but do not restore its lower sequence or restart with it, since doing so would bypass the tested revocation/floor boundary. Any later restoration needs Root's separately issued valid higher-sequence public catalog. This parent leaves the isolated withdrawn state and original event for inspection; it does not silently erase results.

Outputs: immutable identity and launch PID/commands; original parent requests; wrapper stdout/stderr; original bridge harness stdout/stderr and bridge replies/events in fixture root; actual History per case; actual Router audit and fixture answers; actual owner results/count/store SHA before and after; actual resolved/model logs; restart raw history; result.json with each required case status. Runtime result is PASS only when all five cases actually pass, PARTIAL for missing interruption/withdrawal coverage, FAILED for an assertion/error. A missing terminal reply is result unknown and never prompts automatic redispatch. Error shutdown closes only this wrapper's input, allowing its actual driver deadline/EOF shutdown; no unrelated Kernel or GUI process is killed.

This is five focused actual bridge scenarios, not a repeat of the 25 standalone Relay component tests. Static preparation results belong in L4_BRIDGE_PREP_RESULT.json; actual runtime evidence will exist only after Root runs the command.
