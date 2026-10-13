#!/bin/sh
set -eu
MUSE_DELIVERY_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
if [ -f "$MUSE_DELIVERY_DIR/.local/runtime-profile.path" ]; then
    MUSE_PROFILE_DIR=$(cat "$MUSE_DELIVERY_DIR/.local/runtime-profile.path")
    case "$MUSE_PROFILE_DIR" in /*) ;; *) exit 2 ;; esac
    exec /usr/bin/open --env "MUSE_INTEGRATED_STATE=$MUSE_PROFILE_DIR" "$MUSE_DELIVERY_DIR/Muse.app"
fi
exec /usr/bin/open "$MUSE_DELIVERY_DIR/Muse.app"
