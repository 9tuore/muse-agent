"""Three real model turns via visible Muse; only synthetic test text is recorded."""

import argparse
import json
import re
import time
from pathlib import Path

from remote import Remote


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("jail", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    remote.click("对话")
    x, y, width, height = remote.find("page_content")["r"]
    remote.scroll(int(x + width - 4), int(y + height / 2), -10000)
    remote.click("新对话")
    questions = ["记住验证码 MUSE-8427，只用于这次测试。", "刚才的验证码是什么？",
                 "不要再重复验证码，告诉我它有几位数字。"]
    replies = []
    for index, question in enumerate(questions, 1):
        state = json.loads((args.jail / "chat-sessions.json").read_text())
        current = next(s for s in state["sessions"] if s["id"] == state["selected_id"])
        previous = len(current["messages"])
        remote.set_text("goal_input", question)
        remote.click("发送")
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            state = json.loads((args.jail / "chat-sessions.json").read_text())
            current = next(s for s in state["sessions"] if s["id"] == state["selected_id"])
            if len(current["messages"]) >= previous + 2:
                reply = current["messages"][-1]
                break
            time.sleep(0.3)
        else:
            raise TimeoutError(f"turn {index} model did not finish")
        replies.append({"question": question, "reply": reply})
        remote.shot(args.output / f"chat-round-{index}.png")
        print(json.dumps(replies[-1], ensure_ascii=False), flush=True)
    answer2 = replies[1]["reply"]["text"]
    answer3 = replies[2]["reply"]["text"]
    report = {"evidence": "LIVE visible Shell model.complete; synthetic inputs",
              "session_id": current["id"], "turns": replies,
              "round2_recall": "MUSE-8427" in answer2,
              "round3_four": bool(re.search(r"(?:4|四)\s*(?:位|个)", answer3)),
              "round3_no_code": "8427" not in answer3 and "MUSE-" not in answer3,
              "all_model_success": all(t["reply"]["state"] == "success" for t in replies)}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
