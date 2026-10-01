#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OFFICIAL_ROOT="${OCTOSENSE_OFFICIAL_ROOT:-/Users/mima0000/Documents/Codex/2026-09-24/gosim-agentic-app-2026-git-gosim-2/work/official}"
LOG_PATH="${G01_EVIDENCE_LOG:-$ROOT_DIR/evidence/g01-capability-tests.log}"
mkdir -p "$(dirname "$LOG_PATH")"

{
  echo "G-01 bounded capability tests"
  date -u '+started_at_utc=%Y-%m-%dT%H:%M:%SZ'
  echo "project_root=$ROOT_DIR"
  echo "official_root=$OFFICIAL_ROOT"
  for repo in octosense octoscript robrix2 makepad; do
    if [[ -d "$OFFICIAL_ROOT/$repo" ]] && git -C "$OFFICIAL_ROOT/$repo" rev-parse --git-dir >/dev/null 2>&1; then
      echo "$repo=$(git -C "$OFFICIAL_ROOT/$repo" rev-parse HEAD)"
    else
      echo "$repo=NOT_FOUND"
    fi
  done

  PYTHONPATH="$ROOT_DIR/app" python3 -m py_compile "$ROOT_DIR/app/g01_capabilities.py"
  echo "python_compile=PASS"
  PYTHONPATH="$ROOT_DIR/app" python3 -m unittest discover \
    -s "$ROOT_DIR/app" -p 'test_g01_capabilities.py' -v
  echo "local_adapter_unit_tests=PASS"

  test -f "$OFFICIAL_ROOT/octoscript/crates/octoscript-capabilities/src/fixed_file_catalog.rs"
  test -f "$OFFICIAL_ROOT/octoscript/crates/octoscript-protocol/src/lib.rs"
  test -f "$OFFICIAL_ROOT/octoscript/crates/octoscript-worker/src/lib.rs"
  test -f "$OFFICIAL_ROOT/octosense/apps/appcard/src/lib.rs"
  test -f "$OFFICIAL_ROOT/robrix2/src/agent_chat/ops/protocol.rs"
  rg -q 'pub struct CapabilityGrant' "$OFFICIAL_ROOT/octoscript/crates/octoscript-protocol/src/lib.rs"
  rg -q 'pub struct OperationDispatchRequest' "$OFFICIAL_ROOT/octoscript/crates/octoscript-protocol/src/lib.rs"
  rg -q 'pub struct FixedFileCatalog' "$OFFICIAL_ROOT/octoscript/crates/octoscript-capabilities/src/fixed_file_catalog.rs"
  rg -q 'pub struct WorkerSession' "$OFFICIAL_ROOT/octoscript/crates/octoscript-worker/src/lib.rs"
  rg -q 'fn execute\(' "$OFFICIAL_ROOT/octosense/apps/appcard/src/lib.rs"
  rg -q 'pub fn available' "$OFFICIAL_ROOT/robrix2/src/agent_chat/ops/mod.rs"
  echo "official_source_contract_presence=PASS"
  echo "official_runtime_targeted_unit_tests=NOT_RUN (see cargo evidence separately)"
  echo "official_runtime_live_test=NOT_TESTED (no external host session)"
  date -u '+finished_at_utc=%Y-%m-%dT%H:%M:%SZ'
} 2>&1 | tee "$LOG_PATH"
