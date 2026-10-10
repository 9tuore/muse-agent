#!/usr/bin/env python3
"""Generate review patches inside this directory; never mutate the SDK/Hub.

Uses the observed official generator in an isolated manifest-only staging root.
No Cargo, Git, GUI, runtime or Calendar operation is executed.
"""
import argparse
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
APP_ID = "muse-native-prototype"
MODULE_PATH = "apps/muse-native-prototype"
GENERATED = (
    "Cargo.toml", "crates/shell/Cargo.toml", "crates/process-apps/Cargo.toml",
    "desktop/Cargo.toml", "phone/Cargo.toml", "crates/shell/src/native_apps.rs",
    "crates/ai-host/src/native_agents.rs",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one anchor: {old!r}")
    return text.replace(old, new, 1)


def diff(path, old, new):
    lines = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}" if old else "/dev/null", tofile=f"b/{path}",
    )
    return "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                   for line in lines)


def create_output(path):
    output = path.resolve()
    if output.parent != HERE:
        raise ValueError("Output must be a new direct child directory of calendar_integration")
    output.mkdir(exist_ok=False)
    return output


def module_files(root):
    files = [root / "Cargo.toml", *sorted((root / "src").rglob("*.rs"))]
    if root / "src/lib.rs" not in files:
        raise ValueError("Prototype src/lib.rs is missing")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", required=True, type=Path)
    parser.add_argument("--hub", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="New directory directly under calendar_integration; existing paths are refused")
    args = parser.parse_args()
    output = create_output(args.output_dir)
    sdk, hub = args.sdk.resolve(), args.hub.resolve()
    generator = sdk / "tools/native_apps.py"
    # Loading definitions is read-only; ROOT is replaced explicitly for each call.
    spec = importlib.util.spec_from_file_location("official_native_apps", generator)
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    entry = {
        "id": APP_ID, "crate": APP_ID, "source": {"path": MODULE_PATH},
        "module": "muse_native_prototype::MUSE_NATIVE_PROTOTYPE_MODULE", "bin": None,
        "default_features": False, "crate_features": [], "implies": ["octos-core"],
        "hosting": {target: "module" for target in native.TARGETS},
        "shells": {"desktop": "opt-in", "phone": "off"}, "native_mobile": "feature",
        "sandbox": {"network": "none", "processes": False},
        "storage": {"accounts": False, "agent_workspace": "none", "external": []},
        "agent": {
            "octos": ["octos.session.open", "octos.session.history", "octos.turn.start", "octos.turn.interrupt"],
            "tools": None, "own_tools": [], "generic_tools": [],
            "grants": [{"app": "os.calendar", "tool": "calendar.events"}],
        },
    }
    old_manifest = (sdk / "native-apps.json").read_text()
    manifest = json.loads(old_manifest)
    if any(app["id"] == APP_ID for app in manifest["apps"]):
        raise ValueError("Prototype ID already registered in input")
    manifest["apps"].append(entry)
    native.validate(manifest)  # exact official id/grant/hosting schema
    if any(app["id"] == "muse-goals" for app in manifest["apps"]):
        raise ValueError("Unsafe same-ID Muse registration in input")
    # Preserve all existing manifest bytes; add only the new row.
    at = old_manifest.rindex("\n  ]")
    new_manifest = old_manifest[:at].rstrip() + ",\n" + "\n".join(
        "    " + line for line in json.dumps(entry, indent=2, ensure_ascii=False).splitlines()
    ) + old_manifest[at:]
    if json.loads(new_manifest) != manifest:
        raise ValueError("Manifest insertion changed existing entries")

    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=output))
    copied = (*GENERATED, "desktop/config/apps.json")
    baseline = {}
    for rel in copied:
        source = sdk / rel
        data = source.read_bytes()
        baseline[rel] = sha(data)
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (stage / "native-apps.json").write_text(new_manifest)
    cargo = stage / "Cargo.toml"
    cargo.write_text(replace_once(cargo.read_text(), '    "apps/reference",',
                                 '    "apps/reference",\n    "apps/muse-native-prototype",'))
    # Official generator, verified --no-lock: no cargo metadata/update.
    if native.main(["--no-lock"], root=stage) != 0:
        raise ValueError("Official generation/catalog validation failed")
    if native.main(["--check", "--no-lock"], root=stage) != 0:
        raise ValueError("Official generated output check failed")

    paths = ["native-apps.json", *GENERATED]
    desktop_patch = "".join(diff(rel, (sdk / rel).read_text(), (stage / rel).read_text()) for rel in paths)
    module_hashes = {}
    module_root = HERE / "native-prototype"
    for source in module_files(module_root):
        rel = source.relative_to(module_root).as_posix()
        text = source.read_text()
        module_hashes[rel] = sha(source.read_bytes())
        target = stage / MODULE_PATH / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        desktop_patch += diff(f"{MODULE_PATH}/{rel}", "", text)
    (output / "native-prototype-sdk.patch").write_text(desktop_patch)

    rel = "crates/app-contract/src/manifest.rs"
    reserved = (hub / rel).read_text()
    new_reserved = replace_once(reserved, '    "reference", "reminders",',
                               '    "muse-native-prototype", "reference", "reminders",')
    contract_patch = diff(rel, reserved, new_reserved)
    (output / "native-prototype-hub-reserved.patch").write_text(contract_patch)
    (output / "NATIVE_PROTOTYPE_ENTRY.json").write_text(json.dumps(entry, indent=2) + "\n")
    result = {
        "state": "GENERATED_NOT_APPLIED_NOT_COMPILED",
        "id": APP_ID, "stage": str(stage), "sdk_input": str(sdk), "hub_input": str(hub),
        "official_generator_sha256": sha(generator.read_bytes()),
        "sdk_input_sha256": {"native-apps.json": sha(old_manifest.encode()), **baseline},
        "hub_reserved_input_sha256": sha(reserved.encode()),
        "sdk_patch_sha256": sha(desktop_patch.encode()),
        "hub_patch_sha256": sha(contract_patch.encode()), "module_sha256": module_hashes,
        "official_generator_no_lock_exit": 0, "official_generated_check_exit": 0,
        "only_grant": entry["agent"]["grants"], "default_features_changed": False,
        "build_executed": False, "gui_executed": False, "relay_verified": False,
        "calendar_executed": False, "consent_granted": False,
        "boundary": "Reviewed Shell integration only; RESERVED_NAMES addition blocks script impersonation and requires Hub contract coordination. Not a script Store release.",
    }
    (output / "NATIVE_PROTOTYPE_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"state": result["state"], "stage": str(stage),
                      "sdk_patch_sha256": result["sdk_patch_sha256"],
                      "hub_patch_sha256": result["hub_patch_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
