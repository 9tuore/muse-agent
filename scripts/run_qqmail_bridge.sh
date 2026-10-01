#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORKSPACE=${AGENT_WORKSPACE:-$HOME/Library/Application Support/GOSIM Local Agent/workspace}
exec /usr/bin/python3 "$ROOT/app/qqmail_imap_bridge.py" --workspace "$WORKSPACE" "$@"
