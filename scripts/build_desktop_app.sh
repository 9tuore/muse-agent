#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DIST=${MUSE_DIST_DIR:-"$ROOT/dist"}
APP="$DIST/GOSIM-Local-Agent.app"
CONTENTS="$APP/Contents"
RESOURCES="$CONTENTS/Resources"
MACOS="$CONTENTS/MacOS"
PYTHON_RUNTIME=${MUSE_PYTHON_RUNTIME:-}
LLAMA_RUNTIME=${MUSE_LLAMA_RUNTIME:-}

if [ -z "$PYTHON_RUNTIME" ] || [ ! -x "$PYTHON_RUNTIME/bin/python3" ]; then
  echo 'MUSE_PYTHON_RUNTIME must point to a relocatable CPython with bin/python3 and lib/pythonX.Y.' >&2
  exit 2
fi
PYTHON_VERSION=$("$PYTHON_RUNTIME/bin/python3" -I -c 'import sys; print("python%d.%d" % sys.version_info[:2])')
[ -d "$PYTHON_RUNTIME/lib/$PYTHON_VERSION" ] || { echo 'Python standard library not found' >&2; exit 2; }
if [ -z "$LLAMA_RUNTIME" ] || [ ! -x "$LLAMA_RUNTIME/llama-server" ] || [ ! -f "$LLAMA_RUNTIME/LICENSE" ]; then
  echo 'MUSE_LLAMA_RUNTIME must point to a licensed llama.cpp runtime containing llama-server.' >&2
  exit 2
fi

rm -rf "$APP"
mkdir -p "$RESOURCES" "$MACOS"
mkdir -p "$RESOURCES/python/bin" "$RESOURCES/python/lib/$PYTHON_VERSION"
cp -p "$PYTHON_RUNTIME/bin/python3" "$RESOURCES/python/bin/python3"
/usr/bin/rsync -a --exclude='site-packages' --exclude='__pycache__' --exclude='test' --exclude='idlelib' --exclude='tkinter' \
  "$PYTHON_RUNTIME/lib/$PYTHON_VERSION/" "$RESOURCES/python/lib/$PYTHON_VERSION/"
[ -f "$RESOURCES/python/lib/$PYTHON_VERSION/LICENSE.txt" ] || { echo 'Python license missing' >&2; exit 2; }
if [ -f "$PYTHON_RUNTIME/lib/libpython${PYTHON_VERSION#python}.dylib" ]; then
  cp -p "$PYTHON_RUNTIME/lib/libpython${PYTHON_VERSION#python}.dylib" "$RESOURCES/python/lib/"
fi
"$RESOURCES/python/bin/python3" -I -B -c 'import sqlite3, ssl, zoneinfo, json'
mkdir -p "$RESOURCES/llama"
/usr/bin/ditto "$LLAMA_RUNTIME" "$RESOURCES/llama"
cp "$ROOT/app/desktop_worker.py" "$RESOURCES/desktop_worker.py"
cp "$ROOT/app/agent_app.py" "$RESOURCES/agent_app.py"
cp "$ROOT/app/memory_store.py" "$RESOURCES/memory_store.py"
cp "$ROOT/app/muse_models.py" "$RESOURCES/muse_models.py"
cp "$ROOT/app/muse_goal_store.py" "$RESOURCES/muse_goal_store.py"
cp "$ROOT/app/muse_goals.py" "$RESOURCES/muse_goals.py"
cp "$ROOT/app/muse_goal_schema.json" "$RESOURCES/muse_goal_schema.json"
cp "$ROOT/app/muse_capabilities.py" "$RESOURCES/muse_capabilities.py"
cp "$ROOT/app/muse_events.py" "$RESOURCES/muse_events.py"
cp "$ROOT/app/muse_plugins.py" "$RESOURCES/muse_plugins.py"
cp "$ROOT/app/muse_plugin_manifest.json" "$RESOURCES/muse_plugin_manifest.json"
cp "$ROOT/app/official_event_adapter.py" "$RESOURCES/official_event_adapter.py"
cp "$ROOT/app/qqmail_imap_bridge.py" "$RESOURCES/qqmail_imap_bridge.py"
for EXTRA in muse_action_bus.py muse_dsl.py muse_memory_schema.json muse_capability_schema.json \
  muse_memory_graph.py muse_capability_catalog.py muse_model_costs.py muse_keychain.py muse_provider_protocols.py \
  muse_app_learning.py muse_ax_adapter.py muse_brief.py muse_browser.py muse_browser_learning.py \
  muse_browser_recipe.py muse_search_policy.py \
  muse_web_search.py muse_official_session.py muse_official_bridge.py muse_calendar.py calendar_selftest.py muse_calendar_intent.py muse_plugin_sdk.py muse_activity.py \
  muse_textedit_recipe.py; do
  if [ ! -f "$ROOT/app/$EXTRA" ]; then
    if [ "${MUSE_ALLOW_INCOMPLETE_BUILD:-0}" = 1 ]; then
      echo "Development build missing $EXTRA" >&2
      continue
    fi
    echo "Required application resource missing: $EXTRA" >&2
    exit 2
  fi
  cp "$ROOT/app/$EXTRA" "$RESOURCES/$EXTRA"
done
mkdir -p "$RESOURCES/plugin_examples"
for MANIFEST in hello-capability.json browser-helper-1.0.json browser-helper-1.1.json; do
  if [ ! -f "$ROOT/app/plugin_examples/$MANIFEST" ]; then
    if [ "${MUSE_ALLOW_INCOMPLETE_BUILD:-0}" = 1 ]; then
      echo "Development build missing plugin manifest $MANIFEST" >&2
      continue
    fi
    echo "Required plugin manifest missing: $MANIFEST" >&2
    exit 2
  fi
  cp "$ROOT/app/plugin_examples/$MANIFEST" "$RESOURCES/plugin_examples/$MANIFEST"
done
if [ -f "$ROOT/app/muse_ax_helper.m" ]; then
  /usr/bin/clang -fobjc-arc -framework AppKit -framework ApplicationServices \
    "$ROOT/app/muse_ax_helper.m" -o "$RESOURCES/muse_ax_helper"
  chmod +x "$RESOURCES/muse_ax_helper"
elif [ "${MUSE_ALLOW_INCOMPLETE_BUILD:-0}" != 1 ]; then
  echo 'Required AX helper source missing: muse_ax_helper.m' >&2
  exit 2
fi
if [ -f "$ROOT/app/muse_calendar_helper.m" ]; then
  /usr/bin/clang -fobjc-arc -framework Foundation -framework EventKit \
    "$ROOT/app/muse_calendar_helper.m" -o "$RESOURCES/muse_calendar_helper"
  chmod +x "$RESOURCES/muse_calendar_helper"
elif [ "${MUSE_ALLOW_INCOMPLETE_BUILD:-0}" != 1 ]; then
  echo 'Required Calendar helper source missing: muse_calendar_helper.m' >&2
  exit 2
fi
if [ -f "$ROOT/app/muse_activity_helper.m" ]; then
  /usr/bin/clang -fobjc-arc -framework AppKit \
    "$ROOT/app/muse_activity_helper.m" -o "$RESOURCES/muse_activity_helper"
  chmod +x "$RESOURCES/muse_activity_helper"
elif [ "${MUSE_ALLOW_INCOMPLETE_BUILD:-0}" != 1 ]; then
  echo 'Required Activity helper source missing: muse_activity_helper.m' >&2
  exit 2
fi
/usr/bin/clang -fobjc-arc -framework Cocoa -framework UserNotifications -framework ApplicationServices -framework Security \
  "$ROOT/app/desktop_app.m" "$ROOT/app/muse_model_manager.m" -o "$MACOS/GOSIM-Local-Agent"
chmod +x "$MACOS/GOSIM-Local-Agent"
"$RESOURCES/python/bin/python3" -I -B - "$ROOT" "$RESOURCES/muse_build_info.json" <<'PY'
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root, output = Path(sys.argv[1]), Path(sys.argv[2])
sources = ("app/agent_app.py", "app/desktop_worker.py", "app/desktop_app.m")
commit = subprocess.check_output(["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
record = {
    "source_commit": commit,
    "built_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sources},
}
output.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY

cat > "$CONTENTS/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDisplayName</key><string>Muse · GOSIM</string>
  <key>CFBundleExecutable</key><string>GOSIM-Local-Agent</string>
  <key>CFBundleIdentifier</key><string>org.gosim.local-agent</string>
  <key>CFBundleName</key><string>Muse · GOSIM</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>0.3.1</string>
  <key>CFBundleVersion</key><string>0.3.1</string>
  <key>LSMinimumSystemVersion</key><string>13.3</string>
  <key>NSCalendarsUsageDescription</key><string>Muse 仅在你选择并批准的日历中核对和管理测试日程。</string>
  <key>NSCalendarsFullAccessUsageDescription</key><string>Muse 仅在你选择并批准的日历中核对和管理测试日程。</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSUIElement</key><false/>
</dict>
</plist>
PLIST

/usr/bin/plutil -lint "$CONTENTS/Info.plist"
for HELPER in muse_ax_helper muse_calendar_helper muse_activity_helper; do
  if [ -f "$RESOURCES/$HELPER" ]; then
    /usr/bin/codesign --force --sign - --identifier "org.gosim.local-agent.$HELPER" "$RESOURCES/$HELPER"
    /usr/bin/codesign --verify --strict "$RESOURCES/$HELPER"
  fi
done
/usr/bin/codesign --force --deep --sign - "$APP"
/usr/bin/codesign --verify --deep --strict "$APP"
rm -f "$DIST/GOSIM-Local-Agent-macOS.zip" "$DIST/GOSIM-Local-Agent-macOS.zip.sha256"
# Ordinary unzip must not materialize AppleDouble files inside the signed app.
/usr/bin/ditto -c -k --norsrc --keepParent "$APP" "$DIST/GOSIM-Local-Agent-macOS.zip"
/usr/bin/shasum -a 256 "$DIST/GOSIM-Local-Agent-macOS.zip" | tee "$DIST/GOSIM-Local-Agent-macOS.zip.sha256"
STAGING="$DIST/.dmg-staging"
rm -rf "$STAGING" "$DIST/GOSIM-Local-Agent-macOS.dmg" "$DIST/GOSIM-Local-Agent-macOS.dmg.sha256"
mkdir -p "$STAGING"
ln -s /Applications "$STAGING/Applications"
/usr/bin/ditto "$APP" "$STAGING/$(basename "$APP")"
/usr/bin/hdiutil create -quiet -volname 'Muse GOSIM' -srcfolder "$STAGING" -format UDZO \
  "$DIST/GOSIM-Local-Agent-macOS.dmg"
rm -rf "$STAGING"
/usr/bin/shasum -a 256 "$DIST/GOSIM-Local-Agent-macOS.dmg" | tee "$DIST/GOSIM-Local-Agent-macOS.dmg.sha256"
/usr/bin/file "$MACOS/GOSIM-Local-Agent" "$DIST/GOSIM-Local-Agent-macOS.zip"
printf '%s\n' "Built $APP" "Built $DIST/GOSIM-Local-Agent-macOS.zip" "Built $DIST/GOSIM-Local-Agent-macOS.dmg"
