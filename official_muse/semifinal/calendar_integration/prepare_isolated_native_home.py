#!/usr/bin/env python3
"""Prepare fresh isolation directories/child environment. Never launches a process."""
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    root = Path(tempfile.mkdtemp(prefix="native-prototype-home-", dir=HERE))
    leaves = {
        "OCTOSENSE_HOME": "shell",
        "OCTOSENSE_APP_DATA": "apps",
        # Explicit kernel dir skips legacy provider-profile migration (kernel/dirs.rs).
        "OCTOS_APP_CORE_DIR": "kernel/.octos",
        "RINX_DATA_DIR": "rinx",
        "ROBRIX_DATA_DIR": "rinx",
        "XDG_CONFIG_HOME": "config",
        "XDG_DATA_HOME": "data",
        "XDG_CACHE_HOME": "cache",
    }
    env = {}
    for key, leaf in leaves.items():
        path = root / leaf
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(path, 0o700)
        env[key] = str(path)
    env["OCTOSENSE_DEV_MODE"] = "0"
    receipt = {
        "state": "FRESH_HOME_PREPARED_NOT_LAUNCHED",
        "id": "muse-native-prototype", "root": str(root), "child_environment": env,
        "consent_written": False, "settings_copied": False, "calendar_seeded": False,
        "process_launched": False,
        "launch_boundary": "Central owner must supply the reviewed Shell with app-muse-native-prototype and its reviewed kernel artifact; no --dev-grant-all or developer-profile. Assert runtime Host layout/approval/core paths match these directories. Configure the provider through authorized Host settings. Existing system events are not copied.",
    }
    output = HERE / "NATIVE_PROTOTYPE_HOME.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"state": receipt["state"], "root": str(root)}, indent=2))


if __name__ == "__main__":
    main()
