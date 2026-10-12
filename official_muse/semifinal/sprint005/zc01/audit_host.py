#!/usr/bin/env python3
"""Read only public application binaries/resources; never read runtime state.

The pack extractor follows App Hub's Pack JSON serialization. It reports
manifest identity and script hashes, never script/provider/account contents.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def embedded_packs(binary):
    rows = []
    for match in re.finditer(re.escape(b'{"schema":1,"files":{'), binary):
        try:
            text = binary[match.start():match.start() + 16 * 1024 * 1024].decode("utf-8", errors="replace")
            pack, end = json.JSONDecoder().raw_decode(text)
            files = pack["files"]
            manifest = json.loads(base64.b64decode(files["manifest.json"], validate=True))
            script = base64.b64decode(files.get("main.splash", ""), validate=True)
            rows.append({
                "offset": match.start(), "pack_json_bytes": len(text[:end].encode()),
                "id": manifest.get("id"), "name": manifest.get("name"),
                "file_count": len(files), "script_bytes": len(script),
                "script_sha256": sha(script),
                "has_run_test": b"fn run_test" in script,
                "has_llm_test": b"llm.test" in script,
            })
        except (ValueError, KeyError, TypeError):
            continue
    return rows


def runtime_inventory(bundle):
    root = bundle / "Contents/Resources/host-runtime"
    if not root.is_dir() or root.is_symlink():
        raise ValueError("expected a public Muse.app host-runtime directory")
    rows = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("runtime symlinks are not accepted")
        if path.is_file():
            data = path.read_bytes()
            rows[path.relative_to(root).as_posix()] = {"bytes": len(data), "sha256": sha(data)}
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--compare-bundle", type=Path)
    parser.add_argument("--ai-script", type=Path)
    args = parser.parse_args()
    if args.bundle.name != "Muse.app":
        parser.error("bundle must be named Muse.app; no state/profile input is supported")
    inventory = runtime_inventory(args.bundle)
    host = args.bundle / "Contents/Resources/host-runtime/muse-host"
    data = host.read_bytes()
    packs = embedded_packs(data)
    result = {"audit_kind": "public_binary_resource_read_only", "host": inventory["muse-host"],
              "embedded_packs": packs, "runtime_file_count": len(inventory),
              "runtime_inventory": inventory, "gui_actions": 0, "model_calls": 0,
              "production_state_read": False}
    if args.compare_bundle:
        other = runtime_inventory(args.compare_bundle)
        result["comparison"] = {
            "other_runtime_file_count": len(other), "identical": inventory == other,
            "different_paths": sorted(k for k in set(inventory) | set(other) if inventory.get(k) != other.get(k)),
        }
    if args.ai_script:
        source = args.ai_script.read_bytes()
        providers = [p for p in packs if p["id"] == "os.ai-providers"]
        result["ai_provider_source"] = {"sha256": sha(source), "bytes": len(source),
                                      "matches_embedded": len(providers) == 1 and providers[0]["script_sha256"] == sha(source)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
