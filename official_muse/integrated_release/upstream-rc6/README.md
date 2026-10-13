# Muse Intel host compatibility source

English | [简体中文](README.zh-CN.md)

This build uses official OctoSense `desktop-v0.1.0-rc.6`, commit
`f9f6fea90b52182790cb2641fd0145c425af4d84`, and its pinned App Hub
`386359153ed6377b5f047bd9ed2767a6a2ac2bc7`. The resulting Intel binary is a
Muse compatibility build from official source, not an untouched upstream release.
Retain the upstream Apache-2.0 licenses and notices when distributing it.

`sdk.patch` adds exact Calendar readback, unique event IDs, refusal of unreadable
event stores, bounded broker receipts, and explicit sharing of reviewed Calendar tools.
`app-hub.patch` carries the existing authenticated per-app tool ceiling into
the current store. It preserves the new catalog/component implementation,
bundle verification, account scope, user consent and native write approval.
There is no mock or prototype Calendar executor. Mail send claims use the app's declared storage identity: device-scoped apps retain access to explicitly granted mailboxes after reinstall, while account-scoped agents remain bound to their selected account. Removed grants and suspended identities are still refused.

`prepare_official_host.py` requires both exact source revisions and refuses
unrelated local edits. It applies these two patches or verifies an exact
already-applied match. The patch includes the matching lockfile: only the five
App Hub packages change from the pinned Git source to its patched `.sources`
checkout. Calendar also uses the already-locked workspace UUID dependency for
IDs, so deletion and a repeated clock tick cannot reuse an event identity.
Existing event IDs remain readable; no locked dependency version changes.

The SDK patch also stacks the existing `bounded-source-preparation.patch`
on the official Makepad runtime overlay. `prepare_official_host.py` verifies
that baseline and the resulting tree; the builder refuses a missing overlay.
Run the SDK's `python3 tools/setup.py --no-hub` before Muse preparation.
Source bodies above 64 KiB are parsed in 1 KiB frames before executing once.
This fixes the observed 600,409-byte Muse startup timeout without changing
the ordinary 64 ms callback limit. Kernel code and its paired binary do not change.

The SDK checkout must include its official `.cargo` directory. Its desktop
system-app selection embeds Mail, Calendar and the other bundled apps; a
build without it can open a window while containing none of those apps.
The builder checks the configuration identity and records the selection.

`build_official_host.py` has `check`, `host`, `kernel`, `hub`, `tests` and `startup-tests`
phases. It uses upstream packaging flags, strips debug data, remaps build
paths, uses isolated target directories, and records the source/patch/lock
identity, commands, logs and output hashes. The host builds only
`app-hub,octos-core`, which links the real Mail and Calendar services.
The kernel is built from the SDK's own octos pin and checked by upstream's
kernel staging helper. The Hub CLI uses the same patched dependency graph.

The live build receipts and full logs are retained under the chosen build
directory. A successful build is `BUILT_NOT_RUNTIME_VERIFIED`; it is not GUI
or external Mail/Calendar acceptance. The service, broker and authenticated
offer tests use isolated synthetic data. The final Muse bundle must still be
installed and tested through its actual host.
