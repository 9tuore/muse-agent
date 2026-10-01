#!/usr/bin/env python3
"""Controlled live AX recipe test against a synthetic TextEdit file only."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_app_learning import RecipeStore
from muse_ax_adapter import AXUnavailable, NativeAXAdapter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--helper", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--content", required=True)
    args = parser.parse_args()
    root, document = args.root.resolve(), args.document.resolve()
    if not document.is_file() or root not in document.parents or document.is_symlink():
        raise ValueError("synthetic_document_required")
    if not args.content or len(args.content) > 8192:
        raise ValueError("synthetic_content_required")
    title = document.name
    adapter = NativeAXAdapter(args.helper)
    store = RecipeStore(root, adapter)
    try:
        content = args.content
        inputs = {"window_title": title, "content": content}
        dry = store.dry_run("textedit.synthetic_save", inputs)
        created = dry.get("error") == "recipe_missing"
        if created:
            observed = store.observe("com.apple.TextEdit")
            controls = [node for node in observed["elements"] if node.get("window_title") == title]
            text_areas = [node for node in controls if node["role"] == "AXTextArea" and "set_value" in node["actions"]]
            saves = [node for node in controls if node["role"] == "AXMenuItem" and
                     node["name"] in {"Save", "存储"} and "press" in node["actions"]]
            if len(text_areas) != 1 or len(saves) != 1:
                print(json.dumps({"status": "BLOCKED_CONTROL_MAPPING", "text_areas": len(text_areas),
                                  "save_controls": len(saves)}))
                return 0
            steps = [
                {"role": text_areas[0]["role"], "name": text_areas[0]["name"],
                 "window_title": title, "action": "set_value", "input": "content"},
                {"role": saves[0]["role"], "name": saves[0]["name"],
                 "window_title": title, "action": "press", "input": None},
            ]
            proposal = store.propose("textedit.synthetic_save", "com.apple.TextEdit", steps)
            dry = store.dry_run("textedit.synthetic_save", inputs)
        if dry["status"] != "READY_FOR_APPROVAL":
            print(json.dumps(dry)); return 0
        decision = (store.decide("textedit.synthetic_save", proposal["recipe"]["revision"],
                                 proposal["digest"], approved=True) if created else {"status": "REUSED_APPROVAL"})
        result = store.run("textedit.synthetic_save", inputs, approved=True,
                           allowed_bundle_ids=["com.apple.TextEdit"], allowed_window_titles=[title])
        time.sleep(0.5)
        actual = document.read_text(encoding="utf-8")
        print(json.dumps({"status": result["status"], "proposal_digest": dry["digest"],
                          "recipe_created": created,
                          "dry_run": dry["status"], "decision": decision["status"],
                          "receipt": result, "file_readback_matches": actual == content,
                          "file_sha256": hashlib.sha256(document.read_bytes()).hexdigest(),
                          "document": str(document)}, ensure_ascii=False))
    except AXUnavailable as exc:
        print(json.dumps({"status": exc.result.get("status"), "ax_error": exc.result.get("ax_error")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
