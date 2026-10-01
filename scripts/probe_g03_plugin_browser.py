#!/usr/bin/env python3
"""Source-run reviewed browser-helper with synthetic host approval."""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from muse_capabilities import CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog
from muse_plugin_sdk import DeclarativePluginSDK, PluginAwareExecutor


def main():
    with tempfile.TemporaryDirectory(prefix="muse-g03-plugin-browser-") as tmp:
        workspace = Path(tmp)
        catalog = CapabilityCatalog(workspace)
        register_builtin_catalog(catalog)
        sdk = DeclarativePluginSDK(workspace)
        installed = sdk.install("example.browser-helper", "1.1.0", approved=True)
        enabled = sdk.decide("example.browser-helper", "enable", approved=True)
        executor = PluginAwareExecutor(CapabilityExecutor(workspace, catalog=catalog), sdk)
        call = {"action_id": "g03-plugin-browser-1", "capability": "browser.research",
                "goal_id": "synthetic-g03-plugin-goal", "revision": 1,
                "args": {"query": "Python 3.13", "engine": "python.org", "max_pages": 3}}
        context = {"gui_control_granted": True, "allowed_domains": ["python.org"],
                   "permissions": {"capabilities": ["browser.research"],
                                   "resource_refs": ["app:com.microsoft.edgemac", "site:python.org"]}}
        receipt = executor.execute(call, approved=True, context=context)
        sources = receipt.get("output", {}).get("sources", [])
        print(json.dumps({"test_id": "G03-PLUGIN-BROWSER-LIVE", "phase": "A",
                          "actual_at": datetime.now(timezone.utc).isoformat(),
                          "install_status": installed["status"], "enable_status": enabled["status"],
                          "status": receipt["status"], "error": receipt.get("error"),
                          "plugin": receipt.get("plugin"), "verification": receipt.get("verification"),
                          "sources": [{"rank": item["rank"], "url": item["source_url"],
                                       "sha256": item["content_sha256"],
                                       "click_transport": item["click_transport"]} for item in sources],
                          "approval_type": "synthetic_host_fixture",
                          "workspace": "isolated_temp_removed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
