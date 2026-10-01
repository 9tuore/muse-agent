"""Resize the actual Muse WM client through supported Command mouse drags."""

import argparse
import json
import time
from pathlib import Path

from remote import Remote


def settle(remote):
    last = None
    same = 0
    for _ in range(40):
        time.sleep(0.1)
        rect = remote.find("card")["r"]
        same = same + 1 if rect == last else 0
        if same >= 3:
            return rect
        last = rect
    raise AssertionError("WM geometry did not settle")


def drag(remote, x, y, dx, dy, button):
    remote.request("/m", k="down", x=int(x), y=int(y), b=button, cmd=1)
    remote.request("/m", k="move", x=int(x + dx), y=int(y + dy), b=button, cmd=1)
    remote.request("/m", k="up", x=int(x + dx), y=int(y + dy), b=button, cmd=1)
    return settle(remote)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("output", type=Path)
    parser.add_argument("--jail", type=Path, help="opt in to one synthetic real model send per size")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    remote.click("对话")
    native = json.loads(remote.request("/s"))
    if native["w"][0]["sz"][1] < 900:
        remote.request("/w", k="maximize")
    x, y, width, height = settle(remote)
    native = json.loads(remote.request("/s"))
    drag(remote, x + width / 2, y + 50, 20 - x, 70 - y, 0)
    if args.jail:
        area = remote.find("page_content")["r"]
        remote.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), -10000)
        remote.click("新对话")
    results = []
    for width, height in ((990, 539), (990, 400), (990, 300), (412, 892), (1280, 800)):
        x, y, old_width, old_height = settle(remote)
        rect = drag(remote, x + old_width - 24, y + old_height * 0.65,
                    width - old_width, height - old_height, 1)
        expected_height = min(height, native["w"][0]["sz"][1] - rect[1] - 12)
        assert abs(rect[2] - width) <= 2, (width, rect)
        assert abs(rect[3] - expected_height) <= 2, (height, rect, expected_height)
        input_rect = remote.find("goal_input")["r"]
        content_rect = remote.find("page_content")["r"]
        assert input_rect[2] > 80 and input_rect[3] >= 28, input_rect
        assert content_rect[2] > 80 and content_rect[3] >= 80, content_rect
        send_rect = remote.find("发送")["r"]
        # The current OctoSense style's shelf starts 88pt above the native
        # bottom (verified in crates/shell/src/desktop.rs). A widget rect alone
        # is not proof it is reachable through that floating shelf.
        dock_top = native["w"][0]["sz"][1] - 88
        assert input_rect[1] + input_rect[3] <= dock_top, (input_rect, dock_top)
        assert send_rect[1] + send_rect[3] <= dock_top, (send_rect, dock_top)
        sent = False
        if args.jail:
            file = args.jail / "chat-sessions.json"
            state = json.loads(file.read_text())
            current = next(s for s in state["sessions"] if s["id"] == state["selected_id"])
            count = len(current["messages"])
            remote.set_text("goal_input", f"合成窗口测试 {width}x{height}，请简短确认。")
            remote.click("发送")
            deadline = time.monotonic() + 150
            while time.monotonic() < deadline:
                state = json.loads(file.read_text())
                current = next(s for s in state["sessions"] if s["id"] == state["selected_id"])
                if len(current["messages"]) >= count + 2:
                    assert current["messages"][-1]["state"] == "success"
                    sent = True
                    break
                time.sleep(0.2)
            assert sent, "the real send button did not complete a model turn"
        remote.shot(args.output / f"shell-{width}x{height}.png")
        results.append({"requested": [width, height], "client_rect": rect,
                        "input": input_rect, "content": content_rect, "send": send_rect,
                        "above_dock": True, "real_model_send": sent})
    assert remote.find("right_column")["r"][2] >= 240
    remote.shot(args.output / "shell-wide-three-columns.png")
    (args.output / "report.json").write_text(json.dumps({
        "evidence": "LIVE final packed Shell; normal WM drags",
        "native": json.loads(remote.request("/s")), "sizes": results,
        "note": "requested tall size can be clamped by the physical desktop"}, indent=2))
    print(json.dumps(results))


if __name__ == "__main__":
    main()
