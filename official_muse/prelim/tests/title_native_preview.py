#!/usr/bin/env python3
"""Isolated native title preview. No production boot, model, mail or calendar.

The list and Nav styling are copied from an immutable production snapshot.
Callbacks below are preview instrumentation, not production behavior evidence.
The proposed patch is never applied to the shared main.splash.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import time
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "official_muse/phase2/tests"))
from remote import Remote

OLD_ROW = '''                        View{width: Fill height: Fit flow: Right spacing: 4
                            Nav{width: Fill text: session.title draw_bg.color: row_color on_click: || chat_select_session(session.id)}
                            Nav{width: 46 text: "删除" on_click: || chat_request_delete(session.id)}
                        }'''
NEW_ROW = '''                        View{width: Fill height: 54 flow: Right spacing: 4 align: Align{x: 0 y: 0.5}
                            Nav{width: Fill height: Fill text: session.title draw_bg.color: row_color
                                flow: Right{wrap: true} align: Align{x: 0 y: 0.5}
                                label_walk: Walk{width: Fill height: Fit}
                                draw_text.max_lines: 2 draw_text.text_overflow: Ellipsis
                                on_click: || chat_select_session(session.id)}
                            Nav{width: 46 text: "删除" on_click: || chat_request_delete(session.id)}
                        }'''

CASES = [
    ("short", "短标题"),
    ("two_lines", "安排个人会面时间"),
    ("long_zh", "这是一个超长中文会话标题用于检查第二行结尾自动省略并保留完整原始内容"),
    ("long_word", "SupercalifragilisticexpialidociousLongUnbrokenSessionTitle0123456789"),
    ("mixed", "项目 Muse 下周安排 follow-up 日程和邮件回复"),
    ("emoji", "🗓️ 讨论安排 👩‍💻 项目进展 🚀 下一轮回复与确认 ✅ 更多内容"),
]


def block(source, marker):
    start = source.index(marker)
    opening = source.index("{", start)
    depth, quoted, escaped = 1, False, False
    pos = opening + 1
    while depth:
        char = source[pos]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        pos += 1
    return source[start:pos]


def renderer_source(source):
    sessions = [dict(id=key, title=title, updated_at=1) for key, title in reversed(CASES)]
    style_start = source.index("let ink = #")
    style_end = source.index("SolidView{width: Fill height: Fill flow: Right container_id:", style_start)
    sidebar = block(source, "sidebar := SolidView{")
    rail = block(source, "left_rail := View{")
    return '''let chat_sessions = SEED
let chat_selected_id = "short"
let chat_delete_pending = ""
let sidebar_open = true
fn chat_history_group(updated){ return "今天" }
fn chat_select_session(id){ chat_selected_id = id fs.write("selection.json",id.to_json()) redraw() }
fn chat_request_delete(id){ chat_delete_pending = id fs.write("delete-target.json",id.to_json()) redraw() }
fn chat_new_session(){ fs.write("new-click.json","true") }
fn set_page(next){ fs.write("page-click.json",next.to_json()) }
fn sidebar_toggle(){ sidebar_open = !sidebar_open redraw() }
fn redraw(){
    ui.sidebar.set_visible(sidebar_open)
    ui.left_rail.set_visible(!sidebar_open)
    ui.history_list.render()
    ui.preview.render()
}
start_timeout(0.05,|| redraw())
STYLE
SolidView{width: Fill height: Fill flow: Right draw_bg.color: paper
RAIL
SIDEBAR
    preview := View{width: Fill height: Fill flow: Down padding: 12 spacing: 8 on_render: || {
        Label{width: Fill text: "独立原生标题预览 · 合成数据" draw_text.color: ink}
        Label{width: Fill text: "选择：" + chat_selected_id draw_text.color: ink}
        Label{width: Fill text: "删除目标：" + chat_delete_pending draw_text.color: ink}
    }}
}
'''.replace("SEED", json.dumps(sessions, ensure_ascii=False)).replace("STYLE", source[style_start:style_end]).replace("SIDEBAR", sidebar).replace("RAIL", rail)


def capture_title(remote, path, rect, requested_width):
    # /snap text can precede the first visible glyph frame in a cold renderer.
    # Observe pixels; preserve every capture instead of equating hitboxes to ink.
    for attempt in range(1, 6):
        capture = path.with_name(path.stem + "-attempt-" + str(attempt) + ".png")
        remote.shot(capture)
        with Image.open(capture) as picture:
            scale = picture.width / requested_width
            x, y, width, height = rect
            crop = picture.convert("RGB").crop(tuple(round(v * scale) for v in
                  (x + 3, y + 1, x + width - 3, y + height - 1)))
            visible = sum(min(pixel) > 160 for pixel in crop.getdata()) > 20
        if visible:
            shutil.copyfile(capture, path)
            return attempt
        time.sleep(0.3)
    raise AssertionError("Title ink remains absent; inspect preserved capture attempts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "official_muse/app/bundle/main.splash")
    parser.add_argument("--host", type=Path, default=Path(os.environ.get("MUSE_CARD_HOST", "/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense-App-Hub/target/release/card-host")))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8497)
    parser.add_argument("--size", default="990x539")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--cases", nargs="+", choices=[key for key, _ in CASES])
    parser.add_argument("--skip-sidebar-checks", action="store_true")
    args = parser.parse_args()
    args.source = args.source.resolve()
    args.host = args.host.resolve()
    args.out = args.out.resolve()
    selected_cases = [(key, title) for key, title in CASES if args.cases is None or key in args.cases]
    args.out.mkdir(parents=True, exist_ok=False)
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", args.port)) == 0:
            raise RuntimeError("Port occupied; existing process untouched")
    source = args.source.read_text()
    if source.count(OLD_ROW) != 1:
        raise RuntimeError("Expected unmodified list row missing or ambiguous")
    candidate = source.replace(OLD_ROW, NEW_ROW, 1)
    (args.out / "production-before.splash").write_text(source)
    (args.out / "production-proposal.splash").write_text(candidate)
    (args.out / "proposal.patch").write_text("".join(difflib.unified_diff(source.splitlines(True), candidate.splitlines(True), fromfile="a/official_muse/app/bundle/main.splash", tofile="b/official_muse/app/bundle/main.splash", n=3)))
    bundle = args.out / "bundle"
    shutil.copytree(args.source.parent, bundle)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["integrity"].pop("signature", None)
    manifest["capabilities"] = ["storage"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (bundle / "main.splash").write_text(renderer_source(source if args.baseline else candidate))
    state = args.out / "state"
    env = dict(os.environ, MAKEPAD_REMOTE=str(args.port), MAKEPAD_NO_FOCUS="1")
    env.pop("MAKEPAD_HIDE_WINDOWS", None)
    env.pop("MAKEPAD_FOCUS", None)
    report = dict(test_kind="VISIBLE_NATIVE_RENDERER_PREVIEW", baseline=args.baseline,
                  source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  proposal_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
                  renderer_sha256=hashlib.sha256((bundle / "main.splash").read_bytes()).hexdigest(),
                  host_path=str(args.host), host_sha256=hashlib.sha256(args.host.read_bytes()).hexdigest(),
                  requested_size=args.size, production_callbacks=False,
                  final_candidate=False, real_model=False, real_mail=False, real_calendar=False,
                  cases={}, checks={})
    with (args.out / "runtime.log").open("w") as log:
        proc = subprocess.Popen([str(args.host), "--bundle", str(bundle), "--app-data", str(state),
                                 "--allow-unsigned", "--stamp", "--size", args.size],
                                env=env, cwd=args.host.parents[2], stdout=log, stderr=log)
        remote = Remote(args.port)
        try:
            deadline = time.monotonic() + 20
            while True:
                try:
                    remote.find("history_list")
                    break
                except (OSError, AssertionError):
                    if proc.poll() is not None or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.2)
            time.sleep(0.4)
            remote.shot(args.out / "initial.png")
            report["actual_pixels"] = list(struct.unpack(">II", (args.out / "initial.png").read_bytes()[16:24]))
            for key, title in selected_cases:
                remote.click_scroll(title, "history_list", attempts=18)
                # /snap reports the clipped visible rectangle. Bring the whole
                # row inside the pane before using its height as evidence.
                for _ in range(4):
                    rect = remote.find(title)["r"]
                    pane = remote.find("history_list")["r"]
                    expected = 34 if args.baseline else 48
                    if rect[3] >= expected - 0.01:
                        break
                    delta = int(rect[1] + rect[3] / 2 - pane[1] - pane[3] / 2)
                    remote.scroll(int(pane[0] + pane[2] / 2), int(pane[1] + pane[3] / 2), delta)
                # The input is delivered only through this newly launched process's remote.
                assert json.loads((state / "muse-goals/selection.json").read_text()) == key
                widget = remote.find(title)
                report["cases"][key] = dict(raw_title=title, rect=widget["r"], selection_callback=True,
                                            snapshot_full_title=widget["t"] == title)
                report["cases"][key]["visible_ink_capture_attempt"] = capture_title(
                    remote, args.out / (key + ".png"), widget["r"], int(args.size.split("x")[0]))
                (args.out / (key + ".snap.json")).write_text(json.dumps(remote.widgets(), ensure_ascii=False, indent=2) + "\n")
            # A Delete button on the same visible row must keep its own hit target.
            title_rect = remote.find(selected_cases[-1][1])["r"]
            buttons = [w for w in remote.widgets() if w.get("t") == "删除" and w["r"][2] > 2
                       and abs(w["r"][1] + w["r"][3] / 2 - title_rect[1] - title_rect[3] / 2) < 2]
            assert len(buttons) == 1, buttons
            x, y, width, height = buttons[0]["r"]
            pane = remote.find("history_list")["r"]
            report["delete_button_rect"] = buttons[0]["r"]
            report["history_list_rect"] = pane
            report["sidebar_rect"] = remote.find("sidebar")["r"]
            report["checks"]["delete_button_fully_visible"] = (width >= 44 and height >= 32
                and x >= pane[0] and y >= pane[1]
                and x + width <= pane[0] + pane[2] and y + height <= pane[1] + pane[3])
            report["checks"]["delete_button_does_not_overlap_title"] = x >= title_rect[0] + title_rect[2]
            remote.request("/click", x=int(x + width / 2), y=int(y + height / 2), wait=1)
            report["checks"]["delete_hit_target_retained"] = json.loads((state / "muse-goals/delete-target.json").read_text()) == selected_cases[-1][0]
            remote.shot(args.out / "delete-target.png")
            if not args.skip_sidebar_checks:
                remote.click("‹")
                report["checks"]["sidebar_collapsed"] = remote.find("☰")["r"][2] > 2
                remote.shot(args.out / "collapsed.png")
                remote.click("☰")
                report["checks"]["sidebar_reexpanded"] = remote.find("history_list")["r"][2] > 2
                remote.shot(args.out / "reexpanded.png")
            heights = [case["rect"][3] for case in report["cases"].values()]
            report["checks"]["title_buttons_equal_height"] = max(heights) - min(heights) < 0.01
            report["checks"]["full_titles_retained_in_renderer"] = all(case["snapshot_full_title"] for case in report["cases"].values())
            report["checks"]["all_tested_titles_have_visible_ink"] = all(case.get("visible_ink_capture_attempt") for case in report["cases"].values())
            report["status"] = "PASS_PREVIEW" if all(report["checks"].values()) else "FAIL_PREVIEW"
        except Exception as error:
            report.update(status="ERROR", error=str(error))
            try:
                (args.out / "failure.snap.json").write_text(json.dumps(remote.widgets(), ensure_ascii=False, indent=2) + "\n")
                remote.shot(args.out / "failure.png")
            except Exception:
                pass
        finally:
            try:
                remote.request("/quit")
            except OSError:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    report["runtime_errors"] = [line for line in (args.out / "runtime.log").read_text().splitlines() if "[E]" in line]
    if report["runtime_errors"]:
        report["status"] = "ERROR"
    (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "requested_size", "checks", "runtime_errors")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS_PREVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
