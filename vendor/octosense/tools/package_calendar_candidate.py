#!/usr/bin/env python3
"""Package the isolated Calendar Shell candidate for local macOS testing."""

import argparse
import hashlib
import plistlib
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEPAD_WIDGETS = ROOT.parent / "makepad-splash-budget/widgets/resources"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--output", type=Path, help="New isolated .app path")
    options = parser.parse_args()
    profile = "release" if options.release else "debug"
    binary = ROOT / f"target/{profile}/octosense"
    base_plist = ROOT / f"target/{profile}/Info.plist"
    bundle = options.output or ROOT / "target/muse-calendar-test" / (
        "OctoSense Calendar Release Candidate.app" if options.release
        else "OctoSense Calendar Candidate.app"
    )
    if not binary.is_file() or not base_plist.is_file():
        raise SystemExit("Build the isolated octosense binary first")
    shell_resources = ROOT / "crates/shell/resources"
    hub_resources = ROOT / ".sources/app-hub/crates/app-hub-app/resources"
    if not MAKEPAD_WIDGETS.is_dir() or not shell_resources.is_dir() or not hub_resources.is_dir():
        raise SystemExit("Locked Makepad widgets, OctoSense Shell or App Hub resources are missing")
    if bundle.exists():
        raise SystemExit(f"Candidate already exists: {bundle}")

    macos = bundle / "Contents/MacOS"
    macos.mkdir(parents=True)
    executable = macos / "octosense"
    shutil.copy2(binary, executable)
    resources = bundle / "Contents/Resources"
    for crate, source in (
        ("makepad_widgets", MAKEPAD_WIDGETS),
        ("octosense_shell", shell_resources),
        ("octosense_app_hub_app", hub_resources),
    ):
        shutil.copytree(source, resources / crate / "resources")
        # This candidate is a normal Cargo binary: Makepad also searches
        # beside the executable unless compiled with apple_bundle.
        (macos / crate).symlink_to(Path("../Resources") / crate, target_is_directory=True)
    with base_plist.open("rb") as source:
        info = plistlib.load(source)
    info.update(
        {
            "CFBundleIdentifier": (
                "dev.makepad.octosense.musecalendar.release.local" if options.release
                else "dev.makepad.octosense.musecalendar.local"
            ),
            "CFBundleExecutable": "octosense",
            "CFBundlePackageType": "APPL",
            "CFBundleVersion": "1",
            "CFBundleShortVersionString": "0.1.0",
            "NSCalendarsFullAccessUsageDescription": (
                "Muse 在你确认后读取、创建或修改系统日历事件，并读回结果。"
            ),
        }
    )
    with (bundle / "Contents/Info.plist").open("wb") as destination:
        plistlib.dump(info, destination)
    subprocess.run(["codesign", "--force", "--sign", "-", str(bundle)], check=True)
    subprocess.run(["codesign", "--verify", "--verbose=1", str(bundle)], check=True)
    print(f"candidate: {bundle}")
    print(f"binary_sha256: {hashlib.sha256(binary.read_bytes()).hexdigest()}")
    print(f"signed_executable_sha256: {hashlib.sha256(executable.read_bytes()).hexdigest()}")
    print("resource_roots: makepad_widgets, octosense_shell, octosense_app_hub_app")


if __name__ == "__main__":
    main()
