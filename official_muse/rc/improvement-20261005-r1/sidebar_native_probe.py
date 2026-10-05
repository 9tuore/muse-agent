#!/usr/bin/env python3
"""Visible native clicks with 16 synthetic chats; preview and cancel only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "official_muse/ui_memory/tests"))
import visual_capture as capture


original_columns = capture.column_checks


def native_columns(remote, out, size):
    state = out / "state/muse-goals/chat-sessions.json"
    before = json.loads(state.read_text())
    checks = []
    for bottom in (False, True):
        x, y, width, height = remote.find("history_list")["r"]
        remote.scroll(int(x + width / 2), int(y + height / 2), 10000 if bottom else -10000)
        visible = [w for w in remote.widgets() if w.get("ty") == "Button"
                   and w.get("t") == "删除" and w["r"][3] >= 34
                   and y <= w["r"][1] and w["r"][1] + 34 <= y + height]
        assert visible, "No fully visible delete button"
        button = visible[-1] if bottom else visible[0]
        bx, by, bw, bh = button["r"]
        assert bx + bw <= x + width - 12, "Delete button overlaps the scrollbar lane"
        remote.request("/click", x=int(bx + bw / 2), y=int(by + bh / 2))
        remote.wait_for("delete_chat_cancel")
        assert any(w.get("t") == "删除对话？" for w in remote.widgets()), "Delete preview not visible"
        capture.shot(remote, out / ("oldest-delete-preview.png" if bottom else "newest-delete-preview.png"))
        remote.click("delete_chat_cancel")
        assert not any(w.get("i") == "delete_chat_confirm" for w in remote.widgets()), "Cancel left deletion active"
        titles = [w for w in remote.widgets() if w.get("ty") == "Button"
                  and w.get("t", "").startswith("合成长标题") and w["r"][3] >= 40
                  and y <= w["r"][1] and w["r"][1] + w["r"][3] <= y + height]
        assert titles, "No fully visible native title button"
        title = titles[-1] if bottom else titles[0]
        tx, ty, tw, th = title["r"]
        remote.request("/click", x=int(tx + tw / 2), y=int(ty + th / 2))
        after = json.loads(state.read_text())
        assert after["selected_id"] != "", "Native title click did not select a chat"
        selected = next(s for s in after["sessions"] if s["id"] == after["selected_id"])
        assert selected["title"].startswith(title["t"].rstrip("…")), "Native click selected a different title"
        checks.append({"end": "oldest" if bottom else "newest", "delete_rect": button["r"],
                       "scrollbar_clearance": x + width - bx - bw,
                       "title_rect": [tx, ty, tw, th], "preview_and_cancel": True})
    after = json.loads(state.read_text())
    # Existing chat_save also stamps the selected chat on every save.
    # Assert every history field apart from that timestamp is preserved.
    def histories(document):
        return [{k: v for k, v in session.items() if k != "updated_at"}
                for session in document["sessions"]]
    assert histories(before) == histories(after), "Preview/cancel/select changed history content"
    assert len(after["sessions"]) == 16, "Preview/cancel removed a chat"
    result = {"native_clicks": checks, "histories_preserved": True, "session_count": 16,
              "confirmed_deletion_clicked": False, "external_actions": False}
    (out / "native-sidebar-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    result["columns"] = original_columns(remote, out, size)
    return result


capture.column_checks = native_columns
if __name__ == "__main__":
    capture.main()
