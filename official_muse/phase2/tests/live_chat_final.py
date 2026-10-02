"""Final visible Shell A/B/C chat test, with synthetic messages and real model calls."""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from remote import Remote


def state(jail):
    return json.loads((jail / "chat-sessions.json").read_text())


def selected(jail):
    data = state(jail)
    return next(s for s in data["sessions"] if s["id"] == data["selected_id"])


def top(remote):
    area = remote.find("page_content")["r"]
    remote.scroll(int(area[0]+area[2]-4), int(area[1]+area[3]/2), -10000)


def turn(remote, jail, text, output, number):
    previous = len(selected(jail)["messages"])
    remote.set_text("goal_input",text)
    remote.click("发送")
    deadline = time.monotonic()+150
    while time.monotonic()<deadline:
        current=selected(jail)
        if len(current["messages"])>=previous+2:
            answer=current["messages"][-1]
            assert answer["state"]=="success", "real model call failed"
            remote.shot(output/f"chat-{number}.png")
            return {"question":text,"answer":answer["text"],"session_id":current["id"]}
        time.sleep(.25)
    raise TimeoutError("real model did not finish")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("port",type=int)
    parser.add_argument("jail",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    remote=Remote(args.port);remote.click("对话");top(remote);remote.click("新对话")
    old_id=selected(args.jail)["id"]
    records=[]
    for number,text in enumerate(["请记住测试代号 MUSE-3147，不要解释。","刚才的测试代号是什么？","不要再重复完整代号，只告诉我其中有几位数字。"],1):
        records.append(turn(remote,args.jail,text,args.output,number))
    top(remote);remote.click("新对话")
    new_id=selected(args.jail)["id"]
    assert new_id!=old_id
    records.append(turn(remote,args.jail,"记住代号 TEST-9082。",args.output,4))
    top(remote)
    data=state(args.jail)
    old=next(s for s in data["sessions"] if s["id"]==old_id)
    # Session titles can repeat within a minute. Render order follows saved order;
    # select the actual button rectangle and verify its persisted session id.
    peers=[s for s in data["sessions"] if s["id"]!=data["selected_id"] and s["title"]==old["title"]]
    index=next(i for i,s in enumerate(peers) if s["id"]==old_id)
    buttons=[w for w in remote.widgets() if w.get("ty")=="Button" and w.get("t","").startswith(old["title"]+" · ")]
    x,y,width,height=buttons[index]["r"]
    assert width>=2 and height>=24
    remote.request("/click",x=int(x+width/2),y=int(y+height/2))
    assert selected(args.jail)["id"]==old_id, "session selector chose another session"
    records.append(turn(remote,args.jail,"刚才的测试代号是什么？",args.output,5))
    data=state(args.jail)
    before={s["id"]:hashlib.sha256(json.dumps(s["messages"],ensure_ascii=False,sort_keys=True).encode()).hexdigest() for s in data["sessions"]}
    answer=records[2]["answer"]
    semantic={"A_recall":"MUSE-3147" in records[1]["answer"],
              "B_four":bool(re.search(r"(?:4|四)\s*(?:位|个)",answer)) or bool(re.fullmatch(r"[\s。.]*(?:4|四)[\s。位个数字.]*",answer)),
              "B_no_repeat":"3147" not in answer and "MUSE-" not in answer,
              "C_isolated":"MUSE-3147" in records[4]["answer"] and "TEST-9082" not in records[4]["answer"]}
    report={"version":"0.2.9","evidence":"LIVE visible packaged Shell; real keyless model; synthetic inputs", "transport":"TRANSPORT_PASS","semantic":"SEMANTIC_PASS" if all(semantic.values()) else "SEMANTIC_LIMITED","checks":semantic,"turns":records,"old_id":old_id,"new_id":new_id,"selected_id":data["selected_id"],"restart_expected_messages":before}
    (args.output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({"transport":report["transport"],"semantic":report["semantic"],"checks":semantic},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
