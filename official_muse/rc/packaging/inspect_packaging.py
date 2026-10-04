#!/usr/bin/env python3
"""Read metadata/public bundle and SDK overlays; write only A4 reports."""
import argparse
import hashlib
import json
import os
import stat
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def metadata(path):
    result = {"files": 0, "directories": 0, "symlinks": 0, "bytes": 0,
              "allocated_bytes": 0, "exists": path.exists() or path.is_symlink()}
    if not result["exists"]:
        return result
    paths = [path]
    while paths:
        current = paths.pop()
        info = current.lstat()
        if stat.S_ISDIR(info.st_mode):
            result["directories"] += 1
            paths.extend(current.iterdir())
        else:
            result["files"] += 1
            result["bytes"] += info.st_size
            result["allocated_bytes"] += info.st_blocks * 512
            if stat.S_ISLNK(info.st_mode):
                result["symlinks"] += 1
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", choices=("before", "after"), default="before")
    args = parser.parse_args()
    report_name = "SIZE_REPORT_" + args.snapshot.upper()
    if (HERE / (report_name + ".json")).exists():
        raise FileExistsError("Preserve existing snapshot; choose a new report before rerunning")
    now = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    tracked = [Path(os.fsdecode(p)) for p in git("ls-files", "-z").split(b"\0") if p]
    source = {"files": 0, "bytes": 0, "allocated_bytes": 0, "symlinks": 0, "missing": []}
    for relative in tracked:
        path = ROOT / relative
        if not (path.exists() or path.is_symlink()):
            source["missing"].append(str(relative))
            continue
        info = path.lstat()
        source["files"] += 1
        source["bytes"] += info.st_size
        source["allocated_bytes"] += info.st_blocks * 512
        source["symlinks"] += int(stat.S_ISLNK(info.st_mode))
    common_git = Path(os.fsdecode(git("rev-parse", "--git-common-dir")).strip())
    if not common_git.is_absolute():
        common_git = ROOT / common_git
    rows = []
    for path in sorted(ROOT.iterdir()):
        if path.name == ".git":
            continue
        category = "public-source-or-docs"
        if path.name in ("vendor", "build", "dist", "runtime"):
            category = "restored-sdk-or-runtime-cache"
        rows.append({"path": path.name, "category": category, **metadata(path)})
    worktree = {key: sum(row[key] for row in rows) for key in
                ("files", "directories", "symlinks", "bytes", "allocated_bytes")}
    bundle = ROOT / "official_muse/app/bundle"
    manifest = json.loads((bundle / "manifest.json").read_text())
    listing = json.loads((bundle / "listing.json").read_text())
    size_report = {"at": now, "head": git("rev-parse", "HEAD").decode().strip(),
        "branch": git("branch", "--show-current").decode().strip(), "root": str(ROOT),
        "worktree_without_git_pointer": worktree, "tracked_source_checkout": source,
        "shared_git": {"path": str(common_git), "shared_not_owned_by_this_task": True, **metadata(common_git)},
        "git_pointer": metadata(ROOT / ".git"), "app_hub_bundle": metadata(bundle),
        "review_draft_directory": metadata(ROOT / "official_muse/prelim/submit_draft"),
        "final_review_packet": {"state": "NOT_SUPPLIED_BY_CONTROLLER", "bytes": None, "files": None},
        "categories": rows, "no_shared_target_or_history_cleanup_performed": True,
        "authorized_own_probe_cleanup": json.loads((HERE / 'PROBE_REMOVAL_PROOF.json').read_text()) if (HERE / 'PROBE_REMOVAL_PROOF.json').exists() else None}
    (HERE / (report_name + ".json")).write_text(json.dumps(size_report, ensure_ascii=False, indent=2) + "\n")
    lines = ["# A4 体积" + ("基线" if args.snapshot == "before" else "后续快照"), "", f"现场时间：{now}；HEAD `{size_report['head']}`。",
        "", "统计只读取文件系统元数据，不打开账号、私人数据或 Secret。逻辑 bytes 与分配空间分别记录；",
        "shared .git 属于所有 worktree，不能归入本工作区或宣称可直接删除。下表口径互相重叠，不求和。",
        "", "| 路径/口径 | files | bytes | MiB | 分类 |", "| --- | ---: | ---: | ---: | --- |"]
    for label, item, category in [
        ("working tree（排除.git指针）", worktree, "当前所有可见文件，包含本轮并行产物"),
        ("tracked source checkout", source, "当前Git索引文件，不含恢复vendor/cache"),
        (str(common_git), size_report["shared_git"], "共享Git历史/对象"),
        ("official_muse/app/bundle", size_report["app_hub_bundle"], "当前RC脚本bundle"),
        ("official_muse/prelim/submit_draft", size_report["review_draft_directory"], "历史评审工具/草稿，非最终packet")]:
        lines.append(f"| {label} | {item['files']} | {item['bytes']} | {item['bytes']/1048576:.3f} | {category} |")
    lines += ["| final review packet | 未提供 | 未提供 | 未提供 | 等总控最终freeze+scan |", "",
        "A4未清理共享target或历史；按单独授权只删自己的重复SDK恢复探针，证据见PROBE_REMOVAL_PROOF.json。SDK恢复与新app构建结果另见实际结果文件；体积变化包含并行任务产物，不能全归为A4瘦身。", "",
        "## 当前工作区顶层分组", "", "| 路径 | files | bytes | category |", "| --- | ---: | ---: | --- |"]
    lines += [f"| {row['path']} | {row['files']} | {row['bytes']} | {row['category']} |" for row in rows]
    (HERE / (report_name + ".md")).write_text("\n".join(lines) + "\n")

    lock = json.loads((ROOT / "dependencies.lock.json").read_text())
    dependencies = []
    errors = []
    for entry in lock["dependencies"]:
        checked = []
        for relative, expected in entry["overlay_files"].items():
            if expected["mode"] == "120000":
                # The bootstrap creates these declared relative internal links.
                target = expected["target"]
                ok = not Path(target).is_absolute() and ".git" not in Path(target).parts
                checked.append({"path": relative, "kind": "declared-link", "target": target, "shape_ok": ok})
            else:
                path = ROOT / "sdk-overlays" / entry["name"] / relative
                ok = path.is_file() and sha(path) == expected["sha256"]
                mode = "100755" if path.exists() and path.stat().st_mode & 0o111 else "100644"
                ok = ok and mode == expected["mode"]
                checked.append({"path": relative, "kind": "file", "hash_and_mode_match": ok})
            if not ok:
                errors.append(entry["name"] + "/" + relative)
        dependencies.append({"name": entry["name"], "repository": entry["repository"],
            "commit": entry["commit"], "expected_tree_sha256": entry["tree_sha256"],
            "expected_restored_files": entry["files"], "declared_overlay_entries": len(checked),
            "checks": checked, "exclude_count": len(entry["delete"])})
    tracked_privacy = [str(p) for p in tracked if "privacy" in str(p).lower()]
    audit = {"at": now, "head": size_report["head"], "version": manifest["version"],
        "main_sha256": sha(bundle / "main.splash"), "manifest_sha256": sha(bundle / "manifest.json"),
        "listing_sha256": sha(bundle / "listing.json"), "integrity": manifest.get("integrity"),
        "sdk_lock_sha256": sha(ROOT / "dependencies.lock.json"), "sdk_overlay_errors": errors,
        "sdk_dependencies": dependencies, "vendor_present": (ROOT / "vendor").exists(),
        "execution_evidence": {
            name: str(HERE / name) if (HERE / name).is_file() else None
            for name in ("SDK_RESTORE_RESULT.json", "CARGO_METADATA_RESULTS.json",
                         "HOST_BUILD_RESULTS.json", "HOST_PACKAGE_RESULT.json",
                         "HUB_BUILD_RESULTS.json", "STORAGE_DELTA_BUILD_RESULTS.json",
                         "STORAGE_CARD_PACKAGE_RESULT.json", "STORAGE_HOST_PACKAGE_RESULT.json")
        }, "privacy_named_tracked_files": tracked_privacy,
        "publisher": listing["publisher"], "privacy_is_placeholder": listing["publisher"]["privacy_policy_url"].startswith("https://example.com"),
        "screenshots": [{"path": p, "exists": (bundle / p).is_file(),
            "sha256": sha(bundle / p) if (bundle / p).is_file() else None} for p in listing["screenshots"]],
        "listing": listing, "capabilities": manifest["capabilities"],
        "status": "MATERIALS_PARTIAL_NOT_RC_READY"}
    audit_name = "PUBLIC_PACKAGE_AUDIT" + ("_AFTER" if args.snapshot == "after" else "")
    (HERE / (audit_name + ".json")).write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"head": size_report["head"], "version": manifest["version"],
        "worktree_bytes": worktree["bytes"], "source_bytes": source["bytes"],
        "git_bytes": size_report["shared_git"]["bytes"], "bundle_bytes": size_report["app_hub_bundle"]["bytes"],
        "overlay_errors": errors, "privacy_placeholder": audit["privacy_is_placeholder"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
