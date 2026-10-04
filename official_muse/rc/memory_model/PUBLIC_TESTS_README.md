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
