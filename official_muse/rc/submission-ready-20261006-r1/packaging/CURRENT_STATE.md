# Portable packaging state — 2026-10-06

## Current rc48 artifact, held for Root's rc49 approval-card fix

Desktop ZIP: `Muse-0.3.26-rc48-Intel精简运行与源码-89bfd399-2026-10-06.zip`.
Actual size **496,332,297 bytes**, SHA256
`ce5bd4aba86426bc5bf98818c22258be337e5264c67875fdd45cd45a04a1d789`.
Product is frozen **89bfd399**; the complete public source is Root's explicit
**8d9599fd** snapshot (1568 files, 88,571,469 logical bytes). The Gate, Host,
Hub and model identities match. Only the guide's outer app signature changed.

`rc48-first-model-live-r1/`: fresh profile, real App Hub installation, six SHA
matches, two actual `model.complete` calls, 1188 tokens in the real ledger,
official model UI, reopen/history preservation and custom-provider byte
preservation PASS. Basic answer quality remains **0/2**, no tuning changed.
This is a local candidate test; the final ZIP itself was checked independently
for complete member content, modes, links, two extraction methods, strict
codesign, launcher and signed Hub identities. Both receiver Macs remain untested.

`rc48-final-source-r1/DELIVERY.json` is authoritative; earlier rc48 hashes are
preserved as history. The ZIP includes the latest Root public report and safe
frozen RC48 JSON, the local-model error report and three current screenshots.
The tutorial links the independently supplied video. Video attachment is still
pending; it is never added to the hard-limited ZIP.

Old Desktop rc45 binaries/ZIP and the duplicate isolated test app were removed
after no-open-file checks; all source, notes and raw evidence remain. The final
cleanup measured about 6.1 GB free. Production profiles and all model state
records are preserved. Source and success/failure history have not been cut.

Root subsequently found the Chat plan-card approval regression and requested
holding this rc48 artifact while making the minimal rc49 fix. Do not present
rc48 as the final full-chain release or rebuild it for later media-only changes.
Wait for the explicit rc49 product/source/Gate freeze before the next packaging
pass. Model weights and automatic configuration stay unchanged.

The section below records the earlier model-feasibility phase.

Status: **PARTIAL**. First configuration and the real Host model path work; this
small model is not a strong model and did not answer the two Muse accuracy checks
correctly. No new final Desktop archive has been produced in this round.

The selected input is Qwen3-0.6B, derived from the official Q8_0 GGUF using
llama.cpp b11178 `--allow-requantize --pure Q4_K_S`, with all tensors retained.
Weights: 341,454,496 bytes, SHA256
`f755be04e46e7f768edb977e1ffa2ba25295941b69ca943dfb0388cfba4ee71b`.
Apache 2.0 weights, MIT runner, full licenses and a derivative notice are included.
All runner libraries are Intel x86_64, minimum macOS 13.3; the complete Muse
package continues to require macOS 14.0. Existing Host/Hub inputs are unchanged.

The native launcher starts its own loopback CPU server, waits for readiness and
creates only the recipient's isolated `_main` profile. Reopen updates this
bundled-model route and preserves history and other configured providers.
`--models` opens official `launch-ai-providers`; `--check` opens no window or
account. Host exit or launcher termination cleans up its own runner.

Verified on prior frozen **rc45 d306d3c0**, not the new product candidate:

- `FIRST_MODEL_LIVE.json`: empty profile, App Hub installation and six bundle
  identities match; two real `model.complete` calls, distinct replies, actual
  usage and ledger (2 calls / 1188 tokens), orderly runner cleanup. Accuracy
  **0/2**: sky color → “晴朗”; 7+5 → “7”. Overall PARTIAL.
- `REOPEN_MODELS.json`: official settings display this exact model, profile
  creation time and chat bytes preserved; synthetic custom provider bytes
  unchanged and bundled runner not started for that custom profile. PASS.
- `DIRECT_MODEL_DIAGNOSIS.json`: both this Q4 model and original Q8 answer the
  same basic questions correctly through direct HTTP. This does not establish
  Muse request accuracy. A bounded-thinking experiment also misanswered both
  Muse questions, took longer and was rejected. Evidence is retained.
- `SIZE_FEASIBILITY.json`: actual private ZIP **471,005,179 bytes**, ordinary
  deflate level 6, headroom **28,994,821 bytes**. Prior non-app source/report
  members and every new app member/permission/link were retained and verified.
  This temporary feasibility ZIP was removed after verification to save space.
- Final selected launcher compiles with `-Wall`; app strict deep codesign and
  launcher `--check` pass. Python syntax and builder `--help` pass.

Current runtime cache is `.local-state/local-model/`. It contains only the
approved public model and the recursive server dependency closure, plus licenses.
`MODEL_INPUTS.json` is the regular-file identity manifest. The final builder
checks every file and copies full public frozen Git source, current Gate, Host,
Hub and model. It enforces a strict ZIP limit below 500,000,000 bytes.

Root supplies the next frozen commit/Gate and approved video. rc46 was observed
but subsequently rejected by Root's live intent-routing check; rc47 is pending.
Do not final-package rc46 or imply 20/20. A 30–60 MB video should be delivered
beside the ZIP via `--external-video`; the tutorial links it and explains that
the video must also be transferred. Final size is checked again after the new
source/report inputs enter. No SDK/Host/product source, production profile,
credentials, Mail/Calendar operation, port 8493, tag, push or publication changed.

Before the first packaging commit, new duplicate/experimental raw screenshots
were consolidated under `.local-state/historical-test-images/`, with every file
hash and original path in `HISTORICAL_IMAGE_ARCHIVE.json`. All original images
remain locally available. Five canonical live screenshots and all success/failure
JSON and logs remain public. No prior frozen Git source or evidence was removed.
New public packaging evidence contributes about 15 MB to the next source ZIP;
the final complete frozen-source size must still be measured again.
