#!/usr/bin/env python3
"""Read scoped TextEdit process health without shell or process arguments."""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_capabilities import CapabilityExecutor, register_builtin_catalog
from muse_capability_catalog import CapabilityCatalog


def main():
    with tempfile.TemporaryDirectory(prefix="muse-g03-app-health-") as tmp:
        workspace = Path(tmp)
        catalog = CapabilityCatalog(workspace)
        register_builtin_catalog(catalog)
        receipt = CapabilityExecutor(workspace, catalog=catalog).execute(
            {"action_id": "g03-app-health-1", "goal_id": "synthetic-g03-app-health-goal",
             "revision": 1, "capability": "system.app_health",
             "args": {"bundle_id": "com.apple.TextEdit"}}, approved=True,
            context={"permissions": {"capabilities": ["system.app_health"],
                                     "resource_refs": ["app:com.apple.TextEdit"]}})
        print(json.dumps({"test_id": "G03-RESTRICTED-APP-HEALTH", "phase": "A",
                          "actual_at": datetime.now(timezone.utc).isoformat(),
                          "status": receipt["status"], "error": receipt.get("error"),
                          "output": receipt.get("output"), "verification": receipt.get("verification"),
                          "approval_type": "synthetic_host_fixture",
                          "workspace": "isolated_temp_removed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
