#!/usr/bin/env python3
"""Drive the OctoSense desktop Shell: install Muse from the local catalog and
run one real task inside the Shell's Card runner.

Talks to Makepad's remote bridge only (GET routes): /snap, /d, /click, /t,
/m?k=scroll, /g. Coordinates are window points.
"""
import json, sys, time, urllib.parse, urllib.request

BASE = f"127.0.0.1:{sys.argv[1]}"
GOAL = "把研究讨论整理成会议要点"
SOURCES = "周五提交演示；负责人小组共同核对"


def get(path, **q):
    url = f"http://{BASE}{path}"
    if q:
        url += "?" + urllib.parse.urlencode(q)
    return urllib.request.urlopen(url, timeout=15).read().decode()


def widgets():
    return json.loads(get("/snap")).get("s", [])


def find(pred, tries=40):
    for _ in range(tries):
        for w in widgets():
            if pred(w):
                return w
        time.sleep(0.25)
    return None


def centre(w):
    r = w["r"]
    return int(r[0] + r[2] / 2), int(r[1] + r[3] / 2)


def click(w):
    x, y = centre(w)
    get("/click", x=x, y=y, wait=1)
    time.sleep(0.6)


def by_text(t):
    return lambda w: w.get("t") == t


def by_id(i):
    return lambda w: w.get("i") == i


def scroll(x, y, dy):
    get("/m", k="scroll", x=x, y=y, dy=dy)
    time.sleep(0.6)


def step(msg):
    print("SHELL:", msg, flush=True)


# --- 1. install from the local catalog -------------------------------------
step("Get")
click(find(by_text("Get") or (lambda w: False)) or exit("no Get button"))
scroll(549, 400, 600)
inst = find(by_text("Install"))
if not inst:
    scroll(549, 400, 600)
    inst = find(by_text("Install"))
if not inst:
    exit("Install button never appeared")
step("Install")
click(inst)
op = find(by_text("Open"))
if not op:
    exit("Open button never appeared — install failed")
step("installed; Open")

# --- 2. launch it in the Shell's Card runner --------------------------------
click(op)
time.sleep(5)
goal = find(by_id("goal_input"))
if not goal:
    exit("Muse window did not open in the Shell")
step(f"Muse running at {goal['r']}")

# --- 3. run one real task ---------------------------------------------------
click(goal)
get("/t", t=GOAL, wait=1)
click(find(by_id("source_input")))
get("/t", t=SOURCES, wait=1)
click(find(by_text("生成计划")))
time.sleep(1.5)
notice = find(by_id("notice"))
step(f"notice: {notice and notice.get('t')}")

ap = find(by_text("批准并执行"), tries=8)
for _ in range(4):
    if ap:
        break
    scroll(579, 640, 300)
    ap = find(by_text("批准并执行"), tries=8)
if not ap:
    exit("批准并执行 unreachable inside the Shell")
step("approve")
click(ap)
time.sleep(2.5)

notice = find(by_id("notice")) or {}
step(f"final notice: {notice.get('t')}")
print("NOTICE=" + str(notice.get("t")))
