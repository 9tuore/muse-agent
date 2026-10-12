#!/usr/bin/env python3
"""Apply Muse's reviewed compatibility patch to an exact official RC6 checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SDK_REV = "f9f6fea90b52182790cb2641fd0145c425af4d84"
HUB_REV = "386359153ed6377b5f047bd9ed2767a6a2ac2bc7"
HERE = Path(__file__).resolve().parent


def run(argv, cwd):
    return subprocess.run(argv, cwd=cwd, text=True, check=True, capture_output=True).stdout


def apply(repo, patch, revision):
    if run(["git", "rev-parse", "HEAD"], repo).strip() != revision:
        raise RuntimeError(f"{repo.name}: expected source revision {revision}")
    wanted = patch.read_bytes()
    current = subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=repo)
    if current != wanted:
        if current:
            raise RuntimeError(f"{repo.name}: preserve existing changes; use an isolated clean checkout")
        run(["git", "apply", "--check", str(patch)], repo)
        run(["git", "apply", str(patch)], repo)
        added = []
        for line in patch.read_text().splitlines():
            if line.startswith("+++ b/"):
                name = line[6:]
                exists = subprocess.run(["git", "cat-file", "-e", f"HEAD:{name}"], cwd=repo,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                if not exists:
                    added.append(name)
        if added:
            run(["git", "add", "-N", "--", *added], repo)
        current = subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=repo)
        if current != wanted:
            raise RuntimeError(f"{repo.name}: applied diff does not match the reviewed patch")
    return {"revision": revision, "patch_sha256": hashlib.sha256(current).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    if run(["git", "rev-parse", "HEAD"], sdk).strip() != SDK_REV:
        raise SystemExit("Use the official desktop-v0.1.0-rc.6 checkout")
    if not (sdk / ".cargo/config.toml").is_file():
        raise SystemExit("Include the official .cargo directory in the SDK checkout before preparing it")
    hub = sdk / ".sources/app-hub"
    if not hub.exists():
        hub.mkdir(parents=True)
        run(["git", "init", "--quiet"], hub)
        run(["git", "fetch", "--no-tags", "--depth=1",
             "https://github.com/OctoSense-org/OctoSense-App-Hub", HUB_REV], hub)
        run(["git", "checkout", "--quiet", "--detach", HUB_REV], hub)
    report = {
        "app_hub": apply(hub, HERE / "upstream-rc6/app-hub.patch", HUB_REV),
        "sdk": apply(sdk, HERE / "upstream-rc6/sdk.patch", SDK_REV),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
