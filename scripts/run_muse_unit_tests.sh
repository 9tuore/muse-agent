#!/usr/bin/env bash
# Run the Muse Python unit-test suite without corrupting a signed .app bundle.
#
# Why this exists
# ---------------
# The bundled interpreter lives inside the sealed bundle
# (Contents/Resources/python/bin/python3). Any Python process that imports a
# module writes __pycache__ unless bytecode writing is disabled, and `python3 -B`
# only protects the single process it is passed to. Test-spawned child processes
# therefore kept writing bytecode into the sealed bundle and invalidated its
# signature.
#
# This runner:
#   1. resolves an interpreter (default: the installed app's bundled Python),
#   2. optionally works on a throwaway copy of the bundle (MUSE_TEST_APP_COPY=1),
#   3. exports PYTHONDONTWRITEBYTECODE=1 and PYTHONPYCACHEPREFIX to a temp dir so
#      EVERY child process inherits the guard, not just the top-level process,
#   4. snapshots the bundle signature and full file inventory before/after and
#      fails the run if anything under the bundle changed.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

APP_PATH="${MUSE_TEST_APP:-/Applications/GOSIM-Local-Agent.app}"
START_DIR="${MUSE_TEST_START_DIR:-$ROOT_DIR/app}"
PATTERN="${MUSE_TEST_PATTERN:-test_*.py}"
COPY_APP="${MUSE_TEST_APP_COPY:-0}"
EVIDENCE="${MUSE_TEST_EVIDENCE:-}"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/muse-unit-tests.XXXXXX")"
CACHE_DIR="$WORK_DIR/pycache"
mkdir -p "$CACHE_DIR"
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT INT TERM

# Optionally run against a throwaway copy so the real bundle can never change.
EFFECTIVE_APP="$APP_PATH"
if [[ "$COPY_APP" == "1" ]]; then
  EFFECTIVE_APP="$WORK_DIR/GOSIM-Local-Agent.app"
  echo "copying bundle: $APP_PATH -> $EFFECTIVE_APP"
  /usr/bin/ditto "$APP_PATH" "$EFFECTIVE_APP"
fi

if [[ -n "${MUSE_TEST_PYTHON:-}" ]]; then
  PYTHON_BIN="$MUSE_TEST_PYTHON"
else
  PYTHON_BIN="$EFFECTIVE_APP/Contents/Resources/python/bin/python3"
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "test interpreter not executable: $PYTHON_BIN" >&2
  exit 2
fi

# Any bundle that physically contains the interpreter must keep a valid seal.
BUNDLE_ROOT=""
case "$PYTHON_BIN" in
  */Contents/Resources/*) BUNDLE_ROOT="${PYTHON_BIN%%/Contents/Resources/*}" ;;
esac

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$CACHE_DIR"
export PYTHONPATH="$START_DIR${PYTHONPATH:+:$PYTHONPATH}"

snapshot() {
  local out="$1"
  : >"$out"
  [[ -n "$BUNDLE_ROOT" ]] || return 0
  if /usr/bin/codesign --verify --deep --strict "$BUNDLE_ROOT" >/dev/null 2>>"$out"; then
    echo "signature=OK" >>"$out"
  else
    echo "signature=FAIL" >>"$out"
  fi
  ( cd "$BUNDLE_ROOT" && find . -type f -print | LC_ALL=C sort ) >>"$out"
}

BEFORE="$WORK_DIR/before.txt"
AFTER="$WORK_DIR/after.txt"
snapshot "$BEFORE"

echo "interpreter=$PYTHON_BIN"
echo "start_dir=$START_DIR"
echo "pattern=$PATTERN"
echo "bytecode_guard=PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=$CACHE_DIR"

set +e
"$PYTHON_BIN" -B -m unittest discover -s "$START_DIR" -p "$PATTERN" -q
STATUS=$?
set -e

snapshot "$AFTER"

REPORT="$WORK_DIR/report.txt"
{
  echo "date_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "repo=$ROOT_DIR"
  echo "interpreter=$PYTHON_BIN"
  if [[ -n "$BUNDLE_ROOT" ]]; then echo "bundle=$BUNDLE_ROOT"; else echo "bundle=NONE"; fi
  echo "tests_exit=$STATUS"
} >"$REPORT"

if [[ -n "$BUNDLE_ROOT" ]]; then
  if diff -q "$BEFORE" "$AFTER" >/dev/null; then
    echo "bundle_integrity=PASS" >>"$REPORT"
    echo "bundle unchanged and signature verified: $BUNDLE_ROOT"
  else
    echo "bundle_integrity=FAIL" >>"$REPORT"
    echo "!! bundle changed during tests: $BUNDLE_ROOT" >&2
    diff -u "$BEFORE" "$AFTER" | head -40 >&2 || true
    STATUS=1
  fi
else
  echo "bundle_integrity=N/A" >>"$REPORT"
fi

if [[ -n "$EVIDENCE" ]]; then
  mkdir -p "$(dirname "$EVIDENCE")"
  { echo "# Muse safe unit-test run"; cat "$REPORT"; } >"$EVIDENCE"
fi
cat "$REPORT"

if [[ $STATUS -eq 0 ]]; then echo "RESULT=PASS"; else echo "RESULT=FAIL(exit=$STATUS)"; fi
exit $STATUS
