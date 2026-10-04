# A3 synthetic contract maintenance

`PUBLIC_A3_SUMMARY.json` is the compact result. `FIRST_FAILURE_INDEX.json` retains original failed attempts by hashes and relative local paths. No retry erases an earlier failure. Runtime logs, source/bundle copies, states, archives and build targets stay local and are outside the explicit public allowlist.

This directory uses the repository's existing `regression_run` and `runtime_probe` against an explicitly supplied, verified actual CardHost. It introduces no runtime, model service or OS connector. These fixtures inject synthetic completions and do not establish real model semantics or full-chain acceptance.

Generate the independent 306 SDK and 315 application inputs:

```sh
python3 official_muse/rc/memory_model/generate_contract_cases.py --out /tmp/muse-contract-inputs
```

The standalone four contracts are captured from production schema declarations. Date expectations use Python datetime; schema expectations follow required/types/length/unknown-field rules. Generated input hashes are identical to the original tested inputs. Split the application JSON into batches of at most80 cases, each named `app-cases.json`, to fit the existing25second fixture runner deadline. Put disposable batch directories under this owned test directory; do not publish them.

Run the actual SDK schema module through the Rust unit driver:

```sh
cargo run --locked --offline --manifest-path official_muse/rc/memory_model/overnight-native-schema/Cargo.toml -- /tmp/muse-contract-inputs/wire-cases.json /tmp/muse-schema-result.json
```

The driver imports the current repository `schema.rs`, avoiding a copied SDK module. Keep the reported SDK module hash with results. An offline dependency cache is required.

Run a batch with the existing CardHost harness:

```sh
python3 official_muse/rc/memory_model/run_contract_probe.py --bundle <verified-production-bundle> --host <verified-card-host> --out <new-owned-run-name> --probes contract_app_cases --data <owned-batch-directory>/app-cases.json
```

The runner uses8510 only, refuses an occupied port, copies the supplied bundle to a disposable directory and records source/Host/input hashes. Use one process at a time. Do not treat boolean-summary counts as the number of individual cases: read `total`, `passed_cases` and `failed_cases`.

`PUBLIC_NEGATIVE_EXPECTATIONS.json` records the twelve original independent preservation expectations. The V6 result additionally compared the complete candidate, metadata and zero candidate-model callbacks; the original frozen V5 failed11updates and1append. The scope first-attempt budget failure remains unresolved in the group result.

The three corrupted-file cases and three freshprocess recoveries nowPASS onV8/new4KiBCard; bindingsareinPUBLIC_A3_SUMMARY.json. `generate_corrupt_fixtures.py` requires an explicitly supplied synthetic64claim/65source seed and writes three disposable directories. Never supply production user storage. Run `corrupt_preserve_rc7` separately for each directory; supply its four JSON files through `--data`. For the write-failure case add `--corrupt-preserve-write-blocker`: it fills the existing256entry jail cap with empty synthetic files; the native preservation write is rejected, then one empty filler is removed solely to save the report. No budget is raised. Original primary, backup and settings bytes must remain unchanged. A valid-backup recovery must preserve the90,000byte raw primary at `memory.json.corrupt-<raw SHA256>`.

Historical large-seed/runtime failures require their locally retained source/Host/seed bindings in addition to the hashes in the failure index. They are not claimed reproducible from only the current public checkout. The detailed historical raw material is deliberately excluded from Git staging.

Aftereachpreservationcase, usecorrupt_recovery_new_process_rc8 withitsretainedoriginalinputsandpreservedfile (ifpresent) inafreshCardHostprocess; expectedstateis64claimreadyforvalidbackup,stoppedforbothbad/writefailure. Priorfailedattemptsremaininthefailureindex.


V10 indexdelta is PARTIAL: newboot indexguard13whole attemptsPASS,17tombcontrol semantic7true butrendererERROR; scope/canonicalguard/singlecorrect budgeterrors remain. See PUBLIC_A3_SUMMARY and FIRST_FAILURE_INDEX. `large_boot_index_rc10.splash` adds explicit pending emptyretrieval/deniedwrites/privateimmutable-snapshot checks. `scope_cache_single_check_rc10_fill12.splash` splits first22 assertions into separatecallbacks while keepingoriginal270inputs/12percallback; saturation only96completed beforebudgeterror. Originalscopefailedattempt is retained. No repeat removes a failure. Supply all required syntheticcorrection inputfiles; the omittedinputfirstattempt is recorded as an orchestration mistake.


V13bchat delta remainsPARTIAL: actualasync11cases77savedsemanticchecks true andallnativefileinvariantsPASS; whole9PASS2rendererERROR. Old/newfull10casesPASS; badproposalrefsyncbudgeterror andsmallercomparison sourceprep failure retained. `chat_boot_guard_rc13.splash` exercisesproductionasyncfunctions; `--chat-boot-continuation --count-storage-writes` replacesonlylaterboot_load continuationwithprobecontinuation andcountsproductionwrites in copiedprefix. `chat_validator_diff_rc13.splash` containsbyteboundoldV12validator renamedonly; sharedrefs/numberhelpersverifiedunchanged. NeitherfixtureprovesfullShellboot,modelorOSactions. Rawstates/bundles/logs excluded.


FinalV14reuse isread-only: `RC5V14_SHARED_FUNCTION_REUSE_PROOF.json` records187exactbodyhashpairs(sharedchat76/core40/gm71),41prefixedletlines identical, V13b b4ac3453 and V14 201d2cc1. NoV14runtime rerun orupgradeofV13bPARTIAL. Twoasyncnative rendererERROR, onewholevalidatorcomparisonbudgetFAIL andone reducedcomparisonpre-probe sourceprepFAIL retained withprecisephase distinctions.


V15twoempty-tombhelpers firstsmallfixture28/28PASS. `empty_tombs_delta_rc15.splash` containsverifiedV14controls withonlynamesrenamed and28independentexpectedcases. `RC5V15_EMPTY_TOMBS_STATIC_PROOF.json` verifies onlyaddedemptytombguard andbadvaluecheckbeforeit, nonemptybody/deps unchanged. Optional `--minimal-bundle-copy` copiesonlyscript/manifest/listing/icon, no media, about0.75MiB observed. ThissmallPASS doesnotupgrade historicalV13bPARTIAL orprovefullUI/performance/fullchain.


Calendar clarification review: CHANGES_REQUIRED. ActualCard first43checks40true; 过几天/改天 explicit followups still rejected. Third ref mutation failure retained; independent JSON revision2/ref1 diagnostic rejects correctly, raw false observation runner misclassification retained. No runtime error, no real model orsend_chat callback; dateoverride inference unverified. Details CLARIFICATION_REVIEW_FINAL_REPORT.md; source binding/status JSON. Port8510free, noGit/product edits.


Root clarification delta2 SHA9fefe620 static review: no new blocker found; reverse only helper/predicate/prompt delta restores33d5d2entire source exactly. Scope/ref/revision/source/expiry/forget/2400guards byte unchanged. Latest explicitdate clearsolder ambiguity byinspection; newer ambiguity retains refusal. A3 no newCard/model run; A2Card andRootM3 pending, previous failures retained. See CLARIFICATION_DELTA2_REVIEW.md andSTATIC_PROOF.json.


Finalclarificationreview boundreadable b154f497: onlydate_known OR existingtemporalregex routingdelta versus9fefe620; reversefullsourceSHAproof exact. Scope/expiredrefs/revision/source/forget/2400guards unchanged. A3noCard/modelrun onfinalSHA; finalrealmodel/dateguardPASS unclaimed. Old33d5/9fefereviews andfailuresretained. CLARIFICATION_FINAL_REVIEW.md + FINAL_SOURCE_BINDING.json.


RC6Settingslabelonly reuse: SHA47c56065ab8be64c48734c4c2b1afdb96de1a6fb391dd360e5dd20a4b5b60966; reversingrc6→rc5label restoresb154entire fileSHA exactly. Allbusiness functions unchanged; no repeatreview orA3Card/modelrun. Rootreported prior9fefefive modelstepsPASS; raw notverified byA3. FinalpuredateM3/restartpending, no finalPASSclaim. SeeCLARIFICATION_RC6_LABEL_REUSE_PROOF.json.
