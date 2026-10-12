# Fresh local AI startup — 2026-10-13

The isolated launcher patch makes a genuinely new hybrid installation start its bundled Qwen, create a credential-free Native local primary, and hand off to Host only after file readback. It never replaces an existing profile or adds a provider to an existing cloud configuration. Existing exact Qwen routes retain their loopback port; a real occupied port gives an actionable error and preserves the profile. No user profile, credential, real Host window, or Calendar store was changed by this work.

Apply `fresh-local-launcher.patch` to the integration worktree. It changes only `official_muse/integrated_release/muse_launcher.m`; SHA identities are in `fresh-local-launcher-identity.json`. `fresh-local-launcher-test-compat.patch` updates the old test which intentionally expected fresh hybrid startup to skip Qwen. The 16-case executable fixture is `test_fresh_local_launcher.py`.

- Baseline launcher SHA-256: `86243b58a0a5a613426e972722d1065d866a8977bf0bfeb09080656f2a8dfcd1`.
- Patched launcher SHA-256: `8c87f3c8e9ca49117308ba52ff1a8d93956d117bc7c05bb48be8b17ea7747465`.
- Latest SDK source HEAD inspected: `f9f6fea90b52182790cb2641fd0145c425af4d84` (desktop-v0.1.0-rc.6). Its Calendar and Relay contain separately owned Muse adaptations; exact source hashes and modified paths are recorded in `ai-sdk-source-identity.json`.

## Root causes and minimal behavior

Previously, missing cloud primary forced `models=YES`, which skipped Qwen. Even an existing exact Qwen selection started on a newly allocated random port while Native retained its old route. The patch allows fresh or already-configured local primary, reuses its registered loopback endpoint, and creates a new profile only after Qwen health is ready. A temporary 0600 file is fsynced and atomically hard-linked to the final name; `link` cannot replace a file created meanwhile. The final bytes are independently read back. The compiled helper test confirms a second creation returns EEXIST and leaves the first bytes intact.

The first executable regression exposed TIME_WAIT sockets being mistaken for a live listener immediately after exit. SO_REUSEADDR on the availability probe fixes restart while the occupied-listener test still refuses correctly. That failed run remains under `launcher-fresh-first-fix`.

The official Native registry (`apps/ai-providers/config/src/registry.rs:91`) supports `local` without a key, with OpenAI-compatible transport. The current model name is `Qwen2.5-0.5B-Instruct-Q4_0-offline`. Official `config/src/profile.rs` requires the `_main` envelope (id, name, enabled, created_at, updated_at); the launcher follows that schema. Octos `config` is read-only, `profile` provides QR/decode, and `init` writes standalone config.json rather than this Native `_main` profile. There is no matching CLI that only initializes the required keyless Native profile. Native `llm.*` writes remain its own app/sheet operations; the launcher does not call or impersonate them.

## Executed evidence

| Evidence directory | Actual execution and result |
| --- | --- |
| `evidence/launcher-fresh-baseline` | Compiled old launcher, 16 isolated stub-Host/health cases, **7 FAIL**. |
| `evidence/launcher-fresh-first-fix` | First compiled fix, 16 cases, **1 FAIL**: immediate restart falsely saw TIME_WAIT as occupied. |
| `evidence/launcher-fresh-final` | Same final source as patch, all **16 PASS**: fresh/default/explicit hybrid, restart, existing local, cloud with/without local, empty/corrupt/symlink profile preservation, real occupied port, remote route refusal, GPT and Models behavior. |
| `evidence/launcher-create-only-final` | Actual compiled production helpers: create-only EEXIST preservation, Native metadata readback, mode 0600 and eight route-validation inputs PASS. The earlier wrapper compile error (Unicode include-path escaping) is preserved in `launcher-create-only`. |
| `evidence/ai-open-box-20261013` | Actual packaged Qwen, two Chinese HTTP turns. Connectivity/Chinese-output checks PASS; the first unconstrained greeting repeated itself to the 100-token cap, so this is **not** a general conversation quality pass. |
| `evidence/ai-muse-wire-20261013` | Actual Qwen, two Chinese turns plus two requests using the current extracted Muse chat task and Native wire shape. Reply JSON schema passed for `你好` and `请只回复一个字：好`. This does not execute Native ModelHost. |
| `evidence/launcher-real-qwen` | Final compiled launcher + actual bundled runner/weights + signed stub Host, two clean process starts. Initial ready 3.865 s / reply 2.768 s; restart ready 3.728 s / reply 2.873 s. Both returned `你好`, reused identical profile/port and stopped the owned model on Host exit. |

Launcher flow fixtures isolate only duplicate-Host process discovery and the per-user mutex filename, so the running user Host cannot be interrupted. The complete profile/health/port code is the production code. Stub health responses never count as inference; real Qwen tests retain original HTTP responses and runner logs. These tests are **not GUI or Native Host/Kernel full-chain acceptance**. No screenshot is claimed. SHA-256 manifests retain successes and failures.

## Calendar read-only boundary

The manifest's `read-only` is the agent workspace permission profile (`.sources/app-hub/crates/app-contract/src/manifest.rs:270`, `app-policy/src/containers.rs:132`). Cross-app Calendar operations travel separately through installed `agent.tools` grants (`crates/shell/src/host_tools/script_apps.rs:163`) and the real Relay (`relay.rs:657`): the Relay verifies caller identity, admitted bundle, consent, account, schema and granted owner/tool. The Calendar host service itself accepts only `os.calendar` (`apps/calendar/host-service/src/lib.rs:279`).

In the actual adapted SDK inspected, events/get are read; add_event is act with its granted/consented route; update/remove are destructive with `confirm:host` and `auto_approvable:false`. The kernel HostRoutedTool and Host approval router retain that approval. Raising the generic profile to full access is neither necessary nor a replacement for approval. This is source-level boundary verification; no Calendar mutation or approval was exercised in this unit.

## Remaining integration boundary

Root must package this launcher with the newly built Host and run Native ModelHost/GUI against the fresh profile. `package_app.py` currently emits `profile_modified_by_launcher:false`; it should distinguish existing-profile preservation from new-profile initialization. The latest SDK catalog still has no entry classifying this exact Qwen alias as fast, so cloud-primary plus local-fallback configuration does not by itself prove task-dependent local/cloud collaboration. Existing cloud profiles are deliberately preserved byte for byte; Native Models remains the provider setup path. Qwen 0.5B is a basic local fallback, and its weak conversational output is retained as evidence rather than hidden.
