#!/usr/bin/env python3
"""Read-only static launch preflight. No subprocess, GUI, profile or secret reads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REVISION = "b0759a57719fd35b3a2da1c5d969bc67538ed516"
KERNEL_SHA = "9c3d4b947a9f90f19acfabad0f90cc891525751d418cb333e6e1d83220c4fb0a"


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as file:
        for data in iter(lambda: file.read(1024 * 1024), b""):
            value.update(data)
    return value.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def within(path, parent):
    return path == parent or parent in path.parents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--home-receipt", type=Path, default=HERE / "NATIVE_PROTOTYPE_HOME.json")
    parser.add_argument("--shell-binary", type=Path)
    args = parser.parse_args()
    result = {"state": "STATIC_PREFLIGHT_PENDING", "process_launched": False,
              "profile_read": False, "consent_verified": False, "Relay_verified": False}
    try:
        sdk = args.sdk.resolve()
        candidate = sdk.parent
        artifacts, metadata = args.artifacts.resolve(), args.metadata.resolve()
        require(within(artifacts, candidate) and within(metadata, candidate), "Inputs must belong to this isolated candidate")
        record = json.loads((artifacts / "octos-kernel.json").read_text())
        require(record.get("revision") == REVISION and record.get("sha256") == KERNEL_SHA, "Kernel receipt differs from reviewed pin/SHA")
        kernel = artifacts / "octos-kernel"
        require(within(kernel.resolve(), candidate), "Kernel symlink leaves candidate")
        require(digest(kernel) == KERNEL_SHA and os.access(kernel, os.X_OK), "Kernel bytes/executable do not match receipt")
        lock = (sdk / "Cargo.lock").read_text()
        revisions = []
        for name in ["octos-cli", "octos-core"]:
            found = set()
            for block in lock.split("[[package]]"):
                if re.search(r'^name = "' + name + '"$', block, re.M):
                    match = re.search(r'^source = "git\+https://github.com/octos-org/octos.git\?rev=([a-f0-9]{40})#', block, re.M)
                    if match:
                        found.add(match.group(1))
            if found:
                require(len(found) == 1, "Ambiguous lock pin")
                revisions = sorted(found)
                break
        require(revisions == [REVISION], "Kernel build.rs lock-derived revision mismatch")
        graph = json.loads(metadata.read_text())
        ids = {p["id"] for p in graph["packages"] if p["name"] == "octosense-shell"}
        nodes = [node for node in graph["resolve"]["nodes"] if node["id"] in ids]
        require(len(nodes) == 1, "Metadata does not contain exactly one Shell")
        required = {"app-hub", "octos-core", "app-muse-native-prototype"}
        require(required.issubset(nodes[0]["features"]), "Metadata lacks required features")
        toolfile = sdk / "apps/calendar/bundle/tools.json"
        tool = next(t for t in json.loads(toolfile.read_text())["tools"] if t["name"] == "calendar.events")
        require(tool["risk"] == "read" and tool["shareable"] is True, "Calendar read/shareable contract differs")
        require(set(tool["input_schema"]["properties"]) == {"from", "to", "limit"}, "Calendar read input fields changed")
        home = json.loads(args.home_receipt.read_text())
        root = Path(home["root"]).resolve()
        require(root.parent == HERE and root.name.startswith("native-prototype-home-"), "Home is not this task's isolated root")
        require(not any(p.is_file() or p.is_symlink() for p in root.rglob("*")), "Home is no longer fresh/empty; use a new receipt")
        env = home["child_environment"]
        for key, value in env.items():
            if key != "OCTOSENSE_DEV_MODE":
                require(within(Path(value).resolve(), root), "Home environment escapes isolation")
        require(env.get("OCTOSENSE_DEV_MODE") == "0", "Developer grant override enabled")
        result.update(state="STATIC_PREREQUISITES_PASS_BINARY_NOT_CHECKED",
                      kernel_sha256=KERNEL_SHA, kernel_revision=REVISION,
                      metadata_sha256=digest(metadata), lock_sha256=digest(sdk / "Cargo.lock"),
                      metadata_features=sorted(required), metadata_package_count=len(graph["packages"]),
                      isolated_root=str(root), child_environment=env,
                      child_unset=["OCTOS_APP_CORE_BIN", "OCTOSENSE_KERNEL_ANY_REVISION", "OCTOSENSE_CONTAINED_APPS", "MAKEPAD_HIDE_WINDOWS", "MAKEPAD_NO_FOCUS"],
                      launch_argv_optional=["--remote"], calendar_read_args={"limit": 10},
                      runtime_boundary="Metadata/receipt/source checks do not prove built executable features, compile-time revision, consent, model selection or Relay execution")
        if args.shell_binary:
            binary = args.shell_binary.resolve()
            require(within(binary, candidate), "Shell executable leaves candidate")
            require(binary.is_file() and os.access(binary, os.X_OK), "Shell executable absent")
            # Match the actual macOS packaged candidates, never an env override.
            choices = [binary.parent / "octos-kernel"]
            if binary.parent.name == "MacOS" and binary.parent.parent.name == "Contents":
                choices.append(binary.parent.parent / "Resources/octos-kernel")
            packaged = next((p for p in choices if p.is_file()), None)
            require(packaged is not None, "Reviewed kernel not yet beside executable/Resources")
            require(within(packaged.resolve(), candidate), "Packaged kernel leaves candidate")
            receipts = [packaged.with_name("octos-kernel.json")]
            if binary.parent.name == "MacOS":
                receipts.append(binary.parent.parent / "Resources/octos-kernel.json")
            receipt = next((p for p in receipts if p.is_file()), None)
            require(receipt is not None and json.loads(receipt.read_text()) == record, "Packaged receipt absent/differs")
            require(digest(packaged) == KERNEL_SHA, "Packaged kernel SHA mismatch")
            result.update(state="STATIC_PACKAGE_PREFLIGHT_PASS_NOT_LAUNCHED", shell_sha256=digest(binary))
    except (OSError, ValueError, KeyError, StopIteration, TypeError) as error:
        result.update(state="STATIC_PREFLIGHT_FAILED", error=str(error))
    (HERE / "NATIVE_LAUNCH_PREFLIGHT_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["state", "process_launched", "profile_read"]}, indent=2))
    return 1 if result["state"] == "STATIC_PREFLIGHT_FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
