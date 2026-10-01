#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Keep the detached entry point and the Finder-facing entry point on exactly
# the same launch path.  The app bundle owns its lifetime after `open` returns.
exec "$ROOT_DIR/scripts/open_octosense_appcard.sh" "$@"
