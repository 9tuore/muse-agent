#!/bin/sh
# Muse in the official OctoSense card-host: one real end-to-end task.
#
# Runs the real bundle in the official card-host, drives the real UI through
# Makepad's remote-control bridge, and verifies the app's own readback.
#
# NOTE: a visible window, not --hidden. On this runtime build
# (Octoscript-Makepad b33f494b / card-host from the Shell-locked App Hub),
# MAKEPAD_HIDE_WINDOWS=1 lays out the widgets but renders no glyphs, so a
# screenshot taken that way is not product evidence. See
# evidence/official-migration-v2/README.md.
#
# Usage:  MUSE_OFFICIAL_WS=<workspace> sh run-official-smoke.sh [port]
# Exits 0 only when the whole task (plan -> approve -> write -> readback)
# really happened and the app's own result file confirms it.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
APP_DIR="$HERE/app"
BUNDLE="$HERE/../bundle"
WS="${MUSE_OFFICIAL_WS:-$HOME/.codex/worktrees/muse-official-migration/official-ws}"
PORT="${1:-8241}"

FLOW="$WS/OctoScript-App-Design-Flow"
OCTO="$FLOW/tools/octo"
export OCTOSENSE_APP_HUB="${OCTOSENSE_APP_HUB:-$WS/OctoSense-App-Hub}"
export OCTO_HUB="${OCTO_HUB:-$WS/target/release/hub}"
export OCTO_CARD_HOST="${OCTO_CARD_HOST:-$WS/target/release/card-host}"

STATE="$APP_DIR/.local-state/smoke-$PORT"
P="127.0.0.1:$PORT"
GOAL="把访谈笔记整理成清单"
SOURCES="会议时间周六；地点图书馆"

fail() { echo "SMOKE: FAIL — $*"; exit 1; }
[ -x "$OCTO_CARD_HOST" ] || fail "card-host not found at $OCTO_CARD_HOST"
[ -x "$OCTO_HUB" ] || fail "hub not found at $OCTO_HUB"
[ -d "$BUNDLE" ] || fail "bundle not found at $BUNDLE"

cleanup() { curl -s -m 5 "$P/quit" >/dev/null 2>&1; sleep 1; }
trap cleanup EXIT INT TERM

cleanup   # never leave a stray instance on this port
rm -rf "$STATE"; mkdir -p "$STATE"

echo "SMOKE: doctor"
(cd "$FLOW" && /usr/bin/python3 "$OCTO" doctor) | grep -q "\[ok\]   card-host" \
  || fail "tools/octo doctor did not find card-host"

echo "SMOKE: run $BUNDLE (visible window, port $PORT)"
(cd "$FLOW" && /usr/bin/python3 "$OCTO" run "$BUNDLE" --port "$PORT" --detach --app-data "$STATE") \
  >"$STATE/run.out" 2>&1 || { cat "$STATE/run.out"; fail "card-host refused to run"; }
grep -q "first frame drawn" "$STATE/run.out" || fail "no first frame"
grep -q "admitted" "$STATE/run.out" || fail "bundle was not admitted"
sleep 2

# ui.py talks to the remote bridge: find a widget by its visible text or id,
# click its centre, type into it. Coordinates are window points, y down.
cat >"$STATE/ui.py" <<'PY'
import json, sys, urllib.parse, urllib.request

BASE = sys.argv[1]

def get(path, **q):
    url = f"http://{BASE}{path}"
    if q:
        url += "?" + urllib.parse.urlencode(q)
    return urllib.request.urlopen(url, timeout=10).read().decode()

def widgets():
    return json.loads(get("/snap")).get("s", [])

def find(key):
    for w in widgets():
        if w.get("i") == key or w.get("t") == key:
            return w
    return None

def click(w):
    r = w["r"]
    x, y = r[0] + r[2] / 2, r[1] + r[3] / 2
    get("/click", x=int(x), y=int(y), wait=1)

def wait_for(key, tries=60):
    for _ in range(tries):
        w = find(key)
        if w:
            return w
        import time; time.sleep(0.25)
    return None

cmd = sys.argv[2]
if cmd == "click":
    w = wait_for(sys.argv[3])
    if not w:
        print("MISSING:" + sys.argv[3]); sys.exit(3)
    click(w); print("CLICKED:" + sys.argv[3])
elif cmd == "type":
    w = wait_for(sys.argv[3])
    if not w:
        print("MISSING:" + sys.argv[3]); sys.exit(3)
    click(w)
    get("/t", t=sys.argv[4], wait=1)
    print("TYPED:" + sys.argv[3])
elif cmd == "click_scroll":
    for _ in range(12):
        w = find(sys.argv[3])
        if w:
            click(w); print("CLICKED:" + sys.argv[3]); break
        area = find("detail_view")
        if not area:
            print("MISSING:detail_view"); sys.exit(3)
        x, y, width, height = area["r"]
        get("/m", k="scroll", x=int(x + width / 2), y=int(y + height / 2), dy=80, precise=1, wait=1)
    else:
        print("MISSING:" + sys.argv[3]); sys.exit(3)
elif cmd == "text":
    w = wait_for(sys.argv[3], tries=20)
    print((w or {}).get("t", ""))
elif cmd == "buttons":
    print(" | ".join(str(w.get("t")) for w in widgets() if "Button" in str(w.get("ty"))))
PY

ui() { /usr/bin/python3 "$STATE/ui.py" "$P" "$@"; }

echo "SMOKE: type goal and sources"
ui type goal_input "$GOAL"   || fail "goal input unreachable"
ui click "设为目标" || fail "goal composer unreachable"
ui type source_input "$SOURCES" || fail "source input unreachable"

echo "SMOKE: generate plan"
ui click "生成计划" || fail "生成计划 button unreachable"
sleep 1
[ "$(ui text notice)" = "计划已生成。核对目标和能力范围后再批准。" ] \
  || fail "plan was not generated (notice: $(ui text notice))"

echo "SMOKE: approve (the button that was previously clipped out of the layout)"
ui click_scroll "批准并执行" || fail "批准并执行 button unreachable — layout regression"
sleep 2

echo "SMOKE: app's own readback"
[ "$(ui text notice)" = "已保存并重新读取核对结果。" ] \
  || fail "app did not report a matching readback (notice: $(ui text notice))"

RESULT=$(ls "$STATE"/muse-goals/results/result-*.json 2>/dev/null | head -1)
[ -n "$RESULT" ] || fail "no result file in the app jail"
grep -q "会议时间周六" "$RESULT" || fail "result file is missing the first source"
grep -q "地点图书馆" "$RESULT" || fail "result file is missing the second source"

/usr/bin/python3 "$OCTO" shot "$PORT" "$STATE/smoke.png" >/dev/null 2>&1 || true
echo "SMOKE: result file   $RESULT"
echo "SMOKE: sha256        $(/usr/bin/shasum -a 256 "$RESULT" | cut -d' ' -f1)"
echo "SMOKE: screenshot    $STATE/smoke.png"
echo "SMOKE: PASS"
