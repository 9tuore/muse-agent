#!/usr/bin/env python3
"""Ask the running OctoSense Shell for a real one-shot model call from Muse.

Drives the Shell over Makepad's remote bridge: open Muse from App Hub, enter a
Chinese goal and sources, generate the plan, then press 「请模型给建议」 and
report exactly what came back. A transport error is reported verbatim — this
script never manufactures a model answer.

    python3 shell-model-e2e.py <bridge-port>
"""
import json, sys, time, urllib.parse, urllib.request

BASE = f"127.0.0.1:{sys.argv[1]}"
GOAL = "把研究讨论整理成会议要点"
SOURCES = "讨论 A：降低成本；讨论 B：周四演讲；讨论 C：需要整理资料"


def get(path, **q):
    url = f"http://{BASE}{path}"
    if q:
        url += "?" + urllib.parse.urlencode(q)
    return urllib.request.urlopen(url, timeout=20).read().decode()


def widgets():
    return json.loads(get("/snap")).get("s", [])


def find(pred, tries=40):
    for _ in range(tries):
        for w in widgets():
            if pred(w):
                return w
        time.sleep(0.25)
    return None


def click(w):
    r = w["r"]
    get("/click", x=int(r[0] + r[2] / 2), y=int(r[1] + r[3] / 2), wait=1)
    time.sleep(0.6)


def by_text(t):
    return lambda w: w.get("t") == t


def by_id(i):
    return lambda w: w.get("i") == i


def step(m):
    print("MODEL:", m, flush=True)


op = find(by_text("Open"))
if not op:
    exit("Muse is not installed in this Shell (no Open button)")
click(op)
time.sleep(5)

goal = find(by_id("goal_input"))
if not goal:
    exit("Muse window did not open")
click(goal)
get("/t", t=GOAL, wait=1)
click(find(by_id("source_input")))
get("/t", t=SOURCES, wait=1)
click(find(by_text("生成计划")))
time.sleep(1.5)
step("plan: " + str((find(by_id("notice")) or {}).get("t")))

btn = find(by_text("请模型给建议"))
if not btn:
    exit("the model button is not on screen")
step("pressing 请模型给建议")
click(btn)

# The host may take a while: a local model, or a provider error.
final = None
for _ in range(120):
    n = find(by_id("notice"), tries=1) or {}
    t = str(n.get("t") or "")
    if "正在请求" not in t and t:
        final = t
        break
    time.sleep(0.5)

step("notice after the call: " + str(final))
model_line = find(lambda w: str(w.get("t") or "").startswith("模型建议"))
print("MODEL_LINE=" + (str(model_line.get("t")) if model_line else ""))
print("NOTICE=" + str(final))
