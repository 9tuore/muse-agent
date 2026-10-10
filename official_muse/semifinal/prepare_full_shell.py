#!/usr/bin/env python3
"""Prepare an isolated complete RC2 Shell; never build, grant or run it.

Copies tracked SDK source, applies the reviewed host proposals and redirects
the five Hub packages to one patched checkout. The normal Shell services and
system-app packaging remain intact. This is not an accepted upstream release.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SDK_HEAD = "4ccf8e068399b1da139771a9ed94cef05fa6ae60"
HUB_HEAD = "95e4831afca7227b640f075b252c04355bb63865"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_manifest(root):
    """Fingerprint the actual inputs, independently of a claimed revision."""
    import os
    files = {}
    for directory, folders, names in os.walk(root):
        folders[:] = sorted(name for name in folders if name not in (".git", "target", "build", "__pycache__"))
        for name in sorted(names):
            path = Path(directory) / name
            if path.is_file():
                files[str(path.relative_to(root))] = digest(path)
    return files


def apply(root, patch):
    subprocess.run(["git", "apply", "--check", str(patch)], cwd=root, check=True)
    subprocess.run(["git", "apply", str(patch)], cwd=root, check=True)


def prepare(out, native_prototype=False, calendar_review=False, qq_login_review=False):
    out = out.resolve()
    if not out.is_relative_to(ROOT / "build"):
        raise ValueError("Complete Shell candidates belong in this worktree build/")
    sdk = ROOT / ".local-state/official-rc2-source"
    hub = ROOT / ".local-state/hub-contract-sdk/app-hub"
    if subprocess.check_output(["git", "-C", str(sdk), "rev-parse", "HEAD"], text=True).strip() != SDK_HEAD:
        raise ValueError("Unexpected SDK revision")
    if subprocess.check_output(["git", "-C", str(sdk), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        raise ValueError("SDK tracked source differs from the fixed revision")
    identity = json.loads((hub.parent / "identity.json").read_text())
    if identity["app_hub"] != HUB_HEAD:
        raise ValueError("Unexpected Hub identity")
    out.mkdir(parents=True, exist_ok=False)
    host = out / "sdk"
    host.mkdir()
    tracked = subprocess.check_output(["git", "-C", str(sdk), "ls-files", "-z"]).decode().split("\0")
    for name in filter(None, tracked):
        source, target = sdk / name, host / name
        if not source.is_file():
            raise ValueError("Missing tracked source: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # The pinned, prepared frameworks are read-only inputs to this build.
    (host / ".sources").symlink_to(sdk / ".sources", target_is_directory=True)
    patched_hub = out / "hub"
    shutil.copytree(hub, patched_hub, ignore=shutil.ignore_patterns(".git", "target", "build", "__pycache__"))
    wiring = ROOT / "official_muse/semifinal/calendar_integration"
    patches = {"hub": wiring / "hub-shared-host-wiring.patch",
               "desktop": wiring / "desktop-shared-host-wiring.patch"}
    apply(patched_hub, patches["hub"])
    apply(host, patches["desktop"])
    if native_prototype:
        # Frozen proposal sequence: never regenerate a patch over its baseline.
        # Each step keeps the official admission, consent and trigger checks.
        for key, target, name in (
            ("native_sdk", host, "native-prototype-sdk.patch"),
            ("native_reserved_id", patched_hub, "native-prototype-hub-reserved.patch"),
            ("native_owner_preparation", host, "native-granted-owner-preparation.patch"),
            ("native_read_schema", host, "native-prototype-readonly-schema.patch"),
            ("native_chinese", host, "native-prototype-chinese-label.patch"),
            ("native_history", host, "native-prototype-history-evidence-r2.patch"),
            ("native_scroll", host / "apps/muse-native-prototype", "native-prototype-scroll.patch"),
        ):
            patches[key] = wiring / name
            apply(target, patches[key])
        module = host / "apps/muse-native-prototype"
        for name in ("Cargo.toml", "src/lib.rs", "src/history.rs"):
            if (module / name).read_bytes() != (wiring / "native-prototype" / name).read_bytes():
                raise ValueError("Native proposal sequence differs from reviewed source: " + name)
    if calendar_review:
        for key, relative, expected in (
            ("calendar_review", "evidence/pivot-builtin-20261010/calendar-review.patch",
             "f40635f6373dd68ea295f5c1c0bf964c1f044ce14dc268df0931be8a809c2ad8"),
            ("calendar_tool_contract_test", "evidence/native-full-shell-r1/calendar-tool-contract-test-r2.patch",
             "3adfe5c450ea71f8587c37bd041773b839b72ecc4241f05fd97045f5b560f4f8"),
            ("calendar_private_data", "evidence/native-full-shell-r1/calendar-get-private-data.patch",
             "60a6ba798ee6059bf1f12c712f9fb1b149b4e5caa483b58295c9a5014f622313"),
        ):
            patches[key] = ROOT / "official_muse/semifinal" / relative
            if digest(patches[key]) != expected:
                raise ValueError("Reviewed Calendar patch changed: " + key)
            apply(host, patches[key])
    if qq_login_review:
        patches["qq_login_review"] = ROOT / "official_muse/semifinal/mail_integration/qq-login-ui-review.patch"
        if digest(patches["qq_login_review"]) != "0415463dc87bba93b8867d1476f12260ac366eaf7be9a2c9380640d8437d5b25":
            raise ValueError("Reviewed QQ login patch changed")
        apply(host, patches["qq_login_review"])
    # Consumer [patch] tables, not a second registry/service implementation.
    cargo = (host / "Cargo.toml").read_text()
    contract_pin = ('octosense-app-contract = { git = "https://github.com/OctoSense-org/OctoSense-App-Hub", '
                    'rev = "' + HUB_HEAD + '" }')
    if cargo.count(contract_pin) != 1:
        raise ValueError("Unexpected contract patch")
    cargo = cargo.replace(contract_pin, 'octosense-app-contract = { path = "../hub/crates/app-contract" }')
    cargo += '\n[patch."https://github.com/OctoSense-org/OctoSense-App-Hub"]\n'
    for package in ("app-contract", "app-policy", "app-hub", "appstore", "app-hub-app"):
        cargo += 'octosense-' + package + ' = { path = "../hub/crates/' + package + '" }\n'
    (host / "Cargo.toml").write_text(cargo)
    # The Hub's own workspace references prepared sibling frameworks. Point
    # them at the same canonical inputs as the consumer SDK, without edits.
    hub_cargo = (patched_hub / "Cargo.toml").read_text()
    hub_cargo = re.sub(r'path = "(\.\./(makepad|octoscript|octoscript-makepad)/[^"]+)"',
                       lambda m: 'path = ' + json.dumps(str((sdk / ".sources" / m[1][3:]).resolve())), hub_cargo)
    (patched_hub / "Cargo.toml").write_text(hub_cargo)
    inputs = {"sdk": {name: digest(sdk / name) for name in filter(None, tracked)},
              "hub": file_manifest(hub),
              "frameworks": {name: file_manifest(sdk / ".sources" / name)
                             for name in ("makepad", "octoscript", "octoscript-makepad")}}
    (out / "source-inputs.json").write_text(json.dumps(inputs, sort_keys=True, indent=2) + "\n")
    record = {"status": "PREPARED_NOT_BUILT", "sdk_commit": SDK_HEAD, "hub_commit": HUB_HEAD,
              "source_inputs_sha256": digest(out / "source-inputs.json"),
              "provenance": "SDK tracked source checked clean; Hub identity names its pin, while actual Hub/framework bytes are independently fingerprinted. Frameworks remain shared build inputs and must be rechecked before freezing.",
              "host_cargo_sha256": digest(host / "Cargo.toml"),
              "input_lock_sha256": digest(sdk / "Cargo.lock"),
              "patches": {key: digest(value) for key, value in patches.items()},
              "features": ["app-hub", "octos-core"] + (["app-muse-native-prototype"] if native_prototype else []),
              "system_apps_sha256": digest(host / "desktop/system-apps.json"),
              "default_agent_offers": "EMPTY", "grants_written": False,
              "native_prototype": native_prototype,
              "calendar_review_proposal": calendar_review,
              "qq_login_review_proposal": qq_login_review,
              "native_registry_read_grants": ["os.calendar/calendar.events"] if native_prototype else [],
              "kernel": "Locked official binary and receipt still required separately",
              "boundary": "Host proposal only; not upstream accepted, not installed, not runtime or admission evidence"}
    (out / "preparation.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native-prototype", action="store_true",
                        help="Include the reviewed independent, read-only Native proposal; never grants consent")
    parser.add_argument("--calendar-review", action="store_true",
                        help="Include the companion Calendar proposal and metadata tests; not upstream acceptance or a grant")
    parser.add_argument("--qq-login-review", action="store_true",
                        help="Include the Chinese QQ login UI proposal; keeps the Mail protocol and credential boundary")
    args = parser.parse_args()
    prepare(args.out, native_prototype=args.native_prototype, calendar_review=args.calendar_review,
            qq_login_review=args.qq_login_review)
