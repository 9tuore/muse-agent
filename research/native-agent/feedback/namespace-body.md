Title: Feature request: preserve existing hyphenated app identities when adding app-owned Agent tools

The current app ID contract accepts hyphenated IDs, while the app-owned tool namespace contract requires `[a-z0-9_]{1,24}`. This is an explicitly documented policy difference, not a claim that native admission incorrectly accepts a tool bundle.

An existing app with ID `muse-goals` can therefore remain a valid app, but adding `tools.json` with its own names such as `muse-goals.memory.search` is refused. Renaming an installed app changes an identity used for storage, grants, executor/consent and publisher migration, so a simple app-ID rename is not an equivalent upgrade path.

Verified on App Hub commit `18cd41d91b326db199fbed4129484a9ba1a8c63d`; the `agent.rs` main blob was rechecked and remains `be8253534fa5b2c304b1a18815eb256b1163f9b8` at the audit observation.

Minimal reproduction:

1. Parse a manifest with `id: "muse-goals"` using the actual `AppManifest::parse` implementation: accepted.
2. Parse a minimal read-only tool declaration under that ID using the actual `ToolManifest` implementation.
3. Call `tools.check(&manifest)` with the unchanged ID.
4. Observe the refusal: `the namespace "muse-goals" (a module id, or the last segment of an app id) must be [a-z0-9_]{1,24} to declare tools`.

The local reproduction compiles unmodified official Rust source for the policy/contract crates with a small Cargo harness, and executes one unit test (passed). It is not `hub check`, installation, a Host runtime test or a model-selected tool call. No Gate is patched. Current base app/source identity remains unchanged.

Request: please clarify/support an identity-preserving upgrade path for already installed legal hyphenated IDs that need app-owned tools, or publish the supported migration requirements for data/grants/consent/publisher continuity. If the namespace restriction is intentional and immutable, this should remain a compatibility feature request rather than a bug report. We are not asking a third-party app to claim a reserved/system namespace.

This limitation applies to declaring the app's own tools. It does not establish that an outbound-only Agent, without its own tools file, cannot request another app's shared tools.

Related: the existing Muse submission is App Hub #112; App Hub #172 concerns API/widget admission coverage, not this namespace upgrade path. Targeted searches for `namespace hyphen` found zero results, and `muse-goals` found #112. This is a scoped dedup observation, not proof that no related discussion exists.

No private account data, credentials, emails or production store contents are needed to reproduce.
