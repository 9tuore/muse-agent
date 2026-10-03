#!/bin/bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
matched_root="${repo_root}/official_muse/app/build/ui-memory-20261003/mail-host-033/OctoSense"
candidate_target="${repo_root}/official_muse/app/build/ui-memory-20261003/prelim-host/target"
cd "$matched_root"
cargo build -j 2 --locked --offline --release --manifest-path "$matched_root/Cargo.toml" --target-dir "$candidate_target" -p octosense --bin octosense --no-default-features --features app-hub
