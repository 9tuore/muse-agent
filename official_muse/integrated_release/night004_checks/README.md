# NIGHT-004 check sources

These are the reviewed GPT05 build helpers moved into Git source. `SOURCE_MIGRATION.json` records original/new SHA256 values. Original build evidence is retained. No Launcher, package, Muse source, SDK or Cargo target is modified.

Run from the repository root:

```sh
python3 official_muse/integrated_release/night004_checks/prepare_probes.py
python3 official_muse/integrated_release/night004_checks/coldstart.py --help
python3 official_muse/integrated_release/night004_checks/read_mail_counts.py --help
```

Preparation compiles exactly `signature_probe.c` with Security/CoreFoundation and `owned_main_window_id.c` with ApplicationServices, using system clang. Commands, source/binary hashes and exits are saved in ignored `local-evidence/probes`. Generated binaries and Python cache are ignored; commit only sources and the preparation summary.

Coldstart requires `--candidate-app --state-root --out --port --expected-source-identities`; `--prepare-only` validates without launching. Freeze every required launcher/runtime/catalog file plus the installed formal Muse manifest/main. STATE must already exist under repo `build/night-004`, with both STATE and `apps/.host` carrying `FIXTURE_ONLY`. Use the confirmed outer `.app` Launcher via `open -n`; state persists without reinstalling, profile copies or approval creation. Owner/guardian identity, exact Host executable and three dynamic Security return statuses 0 are required. `/quit` targets only the checked owner; no force kill occurs.

The real open route remains AppsMenu → `apphub` → Library → exact Muse row’s installed Open. Get/Update/Install/Unavailable or ambiguous controls fail. Chat requires formal sidebar/central_main/title/goal_input; Memory navigation uses Muse `shortcuts` and requires actual Memory controls. Prototype/Host chrome cannot pass. Native screenshots use the owned CGWindow probe; remote `/g` is not used to classify black screens. Resource metrics are sampled CPU/RSS maxima from ready discovery, not absolute peaks. Successful 20 iterations remain `MUSE_20_STARTUP_INTERACTION_CHECKS_PASS_NATIVE_REVIEW_PENDING` with `muse_20_pass=false`; central must inspect actual native images and confirm Calendar/Mail count coverage. T18 remains separate.

`read_mail_counts.py STATE` fits the existing `--side-effect-reader` adapter. Freeze its SHA in `helper_files.side_effect_reader`, then obtain the real baseline for `expected_side_effect_counts.supplied_counts`. It reads only committed official schema-1 `STATE/apps/.host/mail/drafts-SHA256(account)/*.json` records and emits numeric aggregates. Draft/composer/accepted/all-attempt/submission-claim counts remain distinct: awaiting approval and cancelled attempts are not SMTP calls, and a saved sending claim precedes transport. Empty/missing storage returns zero with observed-record flags 0; SMTP and recipient-delivery observations are always 0. Accounts, cached inbox, contacts, secrets, `.tmp`, receiver data, service recovery and business writes are excluded. A manually supplied `--mail-host-root` must be absolute, under the same fixture base and independently marked; alternate-store binding is explicit. Count equality cannot exclude transient create/delete cycles or replace business recovery/authorization tests. The original marked-sample CLI suite passed 16 checks; the copied suite is preserved as `check_reader_fixtures.py`.

Central’s actual integrated rc7 App Hub/Chat/Memory single preflight passed startup/interactivity checks with signature statuses 0, Calendar count 0 and graceful exit. It was one run, not Muse 20 PASS. Migration validation compiled two C probes, compiled Python, passed four help calls, checked repository path imports and ran `prepare-only` once against that explicit package/state. No new Host, GUI, dynamic-PID probe, Mail baseline or cold start was executed in this migration. `PREPARATION.json` records results; final source freeze and unified Git commit belong to central.
