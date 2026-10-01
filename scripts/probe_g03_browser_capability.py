#!/usr/bin/env python3
"""Run the real browser.research capability with synthetic host approval."""

import json
import argparse
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_capabilities import CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="packaging")
    parser.add_argument("--max-pages", type=int, default=3)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="muse-g03-browser-capability-") as tmp:
        workspace = Path(tmp)
        catalog = CapabilityCatalog(workspace)
        register_builtin_catalog(catalog)
        executor = CapabilityExecutor(workspace, catalog=catalog)
        call = {"action_id": "g03-browser-capability-live-1", "capability": "browser.research",
                "goal_id": "synthetic-g03-browser-goal", "revision": 1,
                "args": {"query": args.query, "engine": "python.org", "max_pages": args.max_pages}}
        context = {"gui_control_granted": True,
                   "permissions": {"capabilities": ["browser.research"],
                                   "resource_refs": ["app:com.microsoft.edgemac", "site:python.org"]},
                   "allowed_domains": ["python.org"]}
        receipt = executor.execute(call, approved=True, context=context)
        sources = receipt.get("output", {}).get("sources", [])
        print(json.dumps({"test_id": "G03-BROWSER-CAPABILITY-LIVE", "phase": "A",
                          "actual_at": datetime.now(timezone.utc).isoformat(),
                          "goal_id": call["goal_id"], "revision": 1, "action_id": call["action_id"],
                          "status": receipt["status"], "error": receipt.get("error"),
                          "verification": receipt["verification"],
                          "sources": [{"rank": item["rank"], "title": item["title"],
                                       "source_url": item["source_url"],
                                       "retrieved_at": item["retrieved_at"],
                                       "content_sha256": item["content_sha256"],
                                       "click_transport": item["click_transport"],
                                       "text_chars": len(item["text"])} for item in sources],
                          "approval_type": "synthetic_host_fixture",
                          "workspace": "isolated_temp_removed"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
