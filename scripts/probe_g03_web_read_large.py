#!/usr/bin/env python3
"""Read the bounded public Python docs page through the real capability."""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_capabilities import CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog


URL = "https://docs.python.org/zh-cn/3.13/whatsnew/3.13.html"


def main():
    with tempfile.TemporaryDirectory(prefix="muse-g03-large-web-") as tmp:
        workspace = Path(tmp)
        catalog = CapabilityCatalog(workspace)
        register_builtin_catalog(catalog)
        receipt = CapabilityExecutor(workspace, catalog=catalog).execute(
            {"action_id": "g03-docs-read-1", "capability": "web.read",
             "goal_id": "synthetic-g03-docs-goal", "revision": 1, "args": {"url": URL}},
            approved=True,
            context={"allowed_domains": ["docs.python.org"],
                     "permissions": {"capabilities": ["web.read"],
                                     "resource_refs": ["site:docs.python.org"]}})
        output = receipt.get("output", {})
        text = output.get("text", "")
        print(json.dumps({"test_id": "G03-LARGE-OFFICIAL-DOC-READ", "phase": "A",
                          "actual_at": datetime.now(timezone.utc).isoformat(),
                          "status": receipt["status"], "error": receipt.get("error"),
                          "source_url": output.get("source_url"), "title": output.get("title"),
                          "text_chars": len(text), "contains_python_3_13": "Python 3.13" in text,
                          "text_truncated": output.get("text_truncated"),
                          "extracted_text_chars": output.get("extracted_text_chars"),
                          "replacement_chars": text.count("\ufffd"),
                          "content_sha256": output.get("content_sha256"),
                          "verification": receipt.get("verification"),
                          "approval_type": "synthetic_host_fixture",
                          "workspace": "isolated_temp_removed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
