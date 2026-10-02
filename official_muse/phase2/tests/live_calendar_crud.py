"""Authorized synthetic EventKit CRUD in the final visible Shell; no fixture."""

import argparse
import json
import time
from pathlib import Path

from remote import Remote


def reach(remote, key):
    area = remote.find("calendar_editor")["r"]
    remote.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), -5000)
    for _ in range(70):
        try:
            item = remote.find(key)
            minimum = {"TextInput": 28, "Button": 24}.get(item.get("ty"), 2)
            rect = item["r"]
            # Shell's Dock overlays the bottom of the app viewport. A full
            # widget rectangle there can still route input to a Dock app.
            if (rect[2] >= 2 and rect[3] >= minimum
                    and rect[1] >= area[1] + 24
                    and rect[1] + rect[3] <= area[1] + area[3] - 96):
                return item
        except AssertionError:
            pass
        remote.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), 80)
    raise AssertionError(f"unreachable Calendar control: {key}")


def click(remote, key):
    reach(remote, key)
    remote.click(key)


def text(remote, key, value):
    reach(remote, key)
    remote.set_text(key, value)


def select_test_event(remote, title):
    reach(remote, title)
    widgets = remote.widgets()
    title_index = next(i for i, w in enumerate(widgets) if w.get("t") == title)
    button = next(w for w in widgets[title_index + 1:]
                  if w.get("t") == "选中此系统事件")
    area = remote.find("calendar_editor")["r"]
    rect = button["r"]
    assert (rect[3] >= 24 and rect[1] >= area[1]
            and rect[1] + rect[3] <= area[1] + area[3] - 96), "test event selection is clipped"
    remote.request("/click", x=int(rect[0] + rect[2] / 2),
                   y=int(rect[1] + rect[3] / 2), wait=1)


def wait_receipt(args, service):
    deadline = time.monotonic() + 35
    while time.monotonic() < deadline:
        file = args.jail / "calendar-state.json"
        if file.exists():
            state = json.loads(file.read_text())
            matches = [r for r in state["receipts"] if r["service"] == service
                       and args.test_id in json.loads(r["payload_json"]).get("title", "")]
            if service == "calendar.delete":
                matches = [r for r in state["receipts"] if r["service"] == service
                           and r["event_id"] == args.event_id]
            if matches and matches[-1]["status"] == "verified":
                return matches[-1]
        time.sleep(0.2)
    raise TimeoutError(f"no verified receipt for {service}; inspect visible error")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("jail", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--test-id", required=True)
    parser.add_argument("--calendar", required=True)
    parser.add_argument("--stage", choices=["create", "update", "delete"], required=True)
    parser.add_argument("--prepare-only", action="store_true", help="stop before the real confirmation button")
    args = parser.parse_args()
    assert args.test_id.startswith(("MUSE-PHASE2-", "MUSE-CALENDAR-TEST-", "MUSE-CALENDAR-FINAL-")), "synthetic test ID required"
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    remote.click("日历")
    area = remote.find("calendar_editor")["r"]
    remote.scroll(int(area[0] + area[2] - 4), int(area[1] + area[3] / 2), -5000)
    label = None
    for _ in range(50):
        labels = [w["t"] for w in remote.widgets() if w.get("t", "").startswith(args.calendar + " · ")
                  and w["t"].endswith(" · 可写")]
        if labels:
            label = labels[0]
            break
        time.sleep(0.1)
    assert label, "actual writable Calendar not returned"
    click(remote, label)
    text(remote, "calendar_range_start", "2026-10-03T00:00:00+08:00")
    text(remote, "calendar_range_end", "2026-10-04T00:00:00+08:00")
    click(remote, "查询选中日历与范围")
    time.sleep(1)
    if args.stage != "create":
        select_test_event(remote, args.test_id + ("-UPDATED" if args.stage == "delete" else ""))
        prior = json.loads((args.output / "create.json").read_text())
        args.event_id = prior["event_id"]
    click(remote, {"create": "新建", "update": "修改所选", "delete": "删除所选"}[args.stage])
    if args.stage != "delete":
        text(remote, "calendar_title", args.test_id + ("-UPDATED" if args.stage == "update" else ""))
        text(remote, "calendar_start", "2026-10-03T14:45:00+08:00" if args.stage == "update" else "2026-10-03T14:00:00+08:00")
        text(remote, "calendar_end", "2026-10-03T15:15:00+08:00" if args.stage == "update" else "2026-10-03T14:30:00+08:00")
        text(remote, "calendar_timezone", "Asia/Shanghai")
        text(remote, "calendar_location", "Muse synthetic acceptance")
        click(remote, "查询当前候选冲突")
        time.sleep(1)
    else:
        text(remote, "calendar_delete_id", args.test_id)
    click(remote, "预览精确日历操作")
    reach(remote, "单独确认系统日历操作 · " + {"create": "新建", "update": "修改", "delete": "删除"}[args.stage])
    reach(remote, "确认执行这项系统日历操作")
    if args.stage != "create":
        labels = [w.get("t", "") for w in remote.widgets() if w.get("ty") == "Label"]
        assert any(label.startswith("系统事件 ID · " + args.event_id + "  |  ")
                   for label in labels), "confirmation is bound to a different event; stop before mutation"
    remote.shot(args.output / f"{args.stage}-approval.png")
    if args.prepare_only:
        print(json.dumps({"stage":args.stage,"status":"waiting_user","test_id":args.test_id}))
        return
    remote.click("确认执行这项系统日历操作")
    receipt = wait_receipt(args, "calendar." + args.stage)
    (args.output / f"{args.stage}.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    reach(remote, "刷新宿主授权状态")
    remote.shot(args.output / f"{args.stage}-readback.png")
    print(json.dumps({"stage": args.stage, "status": receipt["status"],
                      "event_id": receipt["event_id"], "request_id": receipt["request_id"]}))


if __name__ == "__main__":
    main()
