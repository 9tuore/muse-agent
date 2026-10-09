# Executed policy and Calendar reproductions

Layers: actual original Hub Rust policy; isolated original Calendar pure Rust
logic; four exact original relay methods inside a minimal Catalog container.
No native Shell/Host installation, consent UI, approval click, Agent model turn,
provider or personal calendar is exercised. These are not native PASS receipts.

Use the fixed source URLs/blob/SHA256 inventories in `../upstream-sources.json`,
`../night-policy-sources.json`, `../night-calendar-sources.json` to restore ignored
cache inputs. Policy sources are 25 original files in `.local-state/night-policy`;
Calendar originals are under `.local-state/native-agent-upstream/OctoSense`.
No whole SDK was downloaded. Worktree is the repository root for these commands.
The committed lockfiles record dependency resolutions used by the small harnesses;
copy them to their corresponding ignored harness root if reproducibility requires
those exact resolutions. Build artifacts stay ignored.

```sh
python3 research/native-agent/night-repros/restore_sources.py
python3 research/native-agent/night-repros/prepare_policy.py
cargo test --offline --manifest-path .local-state/night-policy/Cargo.toml -p octosense-app-policy --test muse_namespace --test namespace_portable --jobs 1 -- --nocapture
python3 research/native-agent/night-repros/prepare_calendar.py
CARGO_TARGET_DIR="$PWD/.local-state/night-policy/target" cargo test --offline --manifest-path .local-state/night-calendar/Cargo.toml --jobs 1 -- --nocapture --test-threads=1
python3 research/native-agent/night-repros/prepare_calendar_patch.py
CARGO_TARGET_DIR="$PWD/.local-state/night-policy/target" cargo test --offline --manifest-path .local-state/night-calendar-patched/Cargo.toml --jobs 1 -- --nocapture --test-threads=1
cargo test --offline --manifest-path .local-state/night-policy/Cargo.toml -p octosense-app-policy --test calendar_schema --jobs 1 -- --nocapture
```

Baseline offline Calendar initially stopped because chrono-tz 0.10.4 was missing.
That error log is preserved. Online retry downloaded public crate dependencies;
it did not access any account, model or event service. All compile/test calls used
one job and were serial. Original Rust files in policy/contract were not modified;
only harness Cargo manifests exclude optional GUI resolution. Calendar preparation
removes the Host registration adapter, not the actual owner guard, handler,
mutation or persistence algorithm. `calendar-extraction.json` records the seam.
The four relay methods are byte-extracted, not rewritten. The scaffold implements
no Host/Agent/runtime behavior; consent/approval integration remains untested.

Evidence:

- `namespace.log`: current B fixture, 1 test passed, original policy refusal.
- `namespace-portable.log`: standalone synthetic fixture, 1 test passed; proposed
  upstream regression patch records existing policy and changes no Gate.
- `calendar-baseline.log`: initial missing offline dependency, retained.
- `calendar-baseline-online.log`: 7 original tests + 2 boundary tests passed.
- `calendar-patch.log`: initial 7 + 3 local tests passed; superseded by the final
  patch that includes two of those regression tests inside upstream source.
- `calendar-patch-final.log`: final 9 core tests + 1 relay policy test passed.
- `calendar-schema.log`: one actual original tool policy test passed.
- `patch-check.json`: both patches apply; prepared/tested tools match applied patch.

Proposed patches under `../patches` affect Calendar source/descriptors/tests and
add a namespace regression test only. No Gate edit, production integration,
identity rename, upstream public submission or accepted version is implied.
Root decides whether to post the two prepared English feature-request bodies.
