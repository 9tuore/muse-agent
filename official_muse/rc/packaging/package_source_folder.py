#!/usr/bin/env python3
"""Export verified frozen Muse source into a new folder, without a runtime or mirror."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RESERVE = 64 * 1024**2
METADATA_MARGIN = 4 * 1024**2
MANIFEST = 'official_muse/app/bundle/manifest.json'
PRODUCT_FILES = [
    'official_muse/app/bundle/' + path for path in (
        'assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
        'screenshots/01-main.png', 'screenshots/02-global-memory.png')
] + ['official_muse/app/source/main.splash']
FORBIDDEN = {'private', 'profile', 'profiles', 'vendor', 'target',
             '.local-state', 'cargo-home'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.PIPE)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def prepare(repo, commit, application_commit):
    for value in (commit, application_commit):
        require(bool(re.fullmatch(r'[0-9a-f]{40}', value)), 'Use full 40-hex commits')
        require(git(repo, 'rev-parse', value + '^{commit}').decode().strip() == value,
                'Input is not the specified commit')
    rows = {}
    for line in git(repo, 'ls-tree', '-r', '-l', '-z', commit).split(b'\0'):
        if not line:
            continue
        meta, name = line.split(b'\t', 1)
        mode, kind, blob, length = meta.decode().split()
        path = name.decode('utf8')
        parts = path.split('/')
        require(kind == 'blob' and mode in ('100644', '100755'),
                'Only ordinary Git files are allowed: ' + path)
        require(not PurePosixPath(path).is_absolute()
                and not any(part in ('', '.', '..') for part in parts)
                and not {part.lower() for part in parts} & FORBIDDEN
                and not path.lower().endswith('.gguf'),
                'Excluded source path: ' + path)
        rows[path] = {'git_blob': blob, 'bytes': int(length), 'mode': int(mode, 8) & 0o777}
    require('SOURCE_MANIFEST.json' in rows, 'SOURCE_MANIFEST.json is missing')
    manifest = json.loads(git(repo, 'show', commit + ':' + MANIFEST))
    require(manifest.get('id') == 'muse-goals', 'Unexpected application identity')
    version = manifest.get('version')
    require(isinstance(version, str) and version and '/' not in version
            and '\\' not in version, 'Invalid application version')
    for path in PRODUCT_FILES:
        require(path in rows, 'Product source file is missing: ' + path)
        require(git(repo, 'show', commit + ':' + path)
                == git(repo, 'show', application_commit + ':' + path),
                'Application/source commit mismatch: ' + path)
    inventory = json.loads(git(repo, 'show', commit + ':SOURCE_MANIFEST.json'))
    require(inventory.get('version') == version, 'SOURCE_MANIFEST version is stale')
    require(inventory.get('product_source_head') == application_commit,
            'SOURCE_MANIFEST application is stale')
    hashes = inventory.get('files')
    require(isinstance(hashes, dict)
            and set(hashes) == set(rows) - {'SOURCE_MANIFEST.json'},
            'SOURCE_MANIFEST inventory is stale')
    require(all(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
                for value in hashes.values()), 'Invalid SOURCE_MANIFEST SHA256')
    return manifest, rows, hashes


def matching_working_file(repo, path, row, sha):
    source = repo / path
    for part in (source, *source.parents):
        if part == repo:
            break
        if part.is_symlink():
            return False
    try:
        before = source.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_size != row['bytes']
                or stat.S_IMODE(before.st_mode) != row['mode']):
            return False
        if file_digest(source) != sha:
            return False
        after = source.lstat()
        return (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                before.st_ctime_ns) == (
                    after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                    after.st_ctime_ns)
    except OSError:
        return False


def tutorial(metadata):
    version = html.escape(metadata['version'])
    source = metadata['source_export_commit']
    application = metadata['application_commit']
    sdk = metadata['source_sdk_lock_sha256']
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Muse {version} 纯源码文件夹</title>
<style>body{{font:17px/1.7 system-ui,sans-serif;background:#f5f7fa;color:#192337;margin:0}}
main{{max-width:850px;margin:40px auto;padding:28px;background:white;border-radius:16px}}
code{{overflow-wrap:anywhere}}.note{{padding:16px;background:#fff2d5;border-radius:10px}}
td,th{{text-align:left;vertical-align:top;padding:9px;border-bottom:1px solid #dde3eb}}</style>
</head><body><main><h1>Muse {version} · 纯源码文件夹</h1>
<p class="note"><b>交付状态：PARTIAL。这里只交付冻结源码，不能双击直接运行 Muse。</b>
没有额外打包 Intel Host、启动器、模型权重、账号或 App Hub mirror。
本工具只做 Git 内容与文件校验，未执行签名 Gate、编译、GUI、模型或外部服务验收。</p>
<h2>打开与查看</h2><p>双击本文件即可离线阅读。打开 <a href="01-源码/">01-源码/</a>
查看完整冻结的公开 Git 文件；开发说明和测试报告在源码中，不含 Git 历史、vendor、构建缓存、
原始运行环境或私人资料。
接收 Mac 的运行、模型、邮箱、日历和电脑重启结果，以对应产品身份的实际报告为准。</p>
<table><tr><th>文件</th><th>用途</th></tr>
<tr><td>01-源码/</td><td>冻结 Git 普通文件，保留文件内容和可执行权限。</td></tr>
<tr><td><a href="版本与交付边界.json">版本与交付边界.json</a></td><td>源码、应用与 SDK 身份和明确欠项。</td></tr>
<tr><td><a href="文件校验清单.json">文件校验清单.json</a></td><td>文件长度、SHA256、权限；排除清单自身哈希。</td></tr></table>
<h2>代码身份</h2><p>版本来自冻结源码的应用 manifest：<b>{version}</b>。
源码导出提交 F：<code>{source}</code>；产品应用提交 A：<code>{application}</code>。
二者分别绑定源码快照和产品载荷，不能互换。</p>
<p>本次源码 dependencies.lock.json 的 SHA256：<code>{sdk}</code>。</p>
<h2>旧运行包与 SDK 范围</h2><p>此前的
<code>Muse-0.3.26-rc5-Intel复现与源码-0876314b-2026-10-05.zip</code>
是旧087运行包，其入口仍运行 rc5，不会自动变成本文件夹所列版本。
旧 Host938 来自 b486 / runtime SDK lock3f1bbb4e；它未包含源码 SDK da756dde
所记录的 Calendar92b1桥修复。源码锁与旧程序的实际编译输入不同，不能将源码修补记作旧Host已集成。</p>
<p>本文件夹没有新的 runtime 或已验证接收机入口。完整构建、Calendar/T18、
两台接收Mac和正式Hub发布的通过情况必须查询各自实际报告，本教程不代报成功。</p>
</main></body></html>
"""


def export_source(repo, commit, application_commit, destination):
    repo = Path(repo).resolve()
    destination = Path(os.path.abspath(destination))
    pending = destination.with_name(destination.name + '.incomplete')
    require(not os.path.lexists(destination) and not os.path.lexists(pending),
            'Preserve existing destination or pending output')
    require(destination.parent.is_dir(), 'Destination parent must already exist')
    manifest, rows, hashes = prepare(repo, commit, application_commit)
    source_bytes = sum(row['bytes'] for row in rows.values())
    require(shutil.disk_usage(destination.parent).free
            > source_bytes + RESERVE + METADATA_MARGIN,
            'Pure source capacity guard failed')
    pending.mkdir(mode=0o755)
    expected = {}
    verified = {}
    cp_c_files = 0
    git_blob_files = 0

    def reserve(length):
        require(shutil.disk_usage(pending).free > RESERVE + length,
                'Live 64MiB source export reserve failed')

    def add(path, data, mode=0o644):
        target = pending / path
        target.parent.mkdir(parents=True, exist_ok=True)
        reserve(len(data))
        with target.open('xb') as stream:
            stream.write(data)
        target.chmod(mode)
        reserve(0)
        expected[path] = {'bytes': len(data), 'sha256': digest(data), 'mode': mode}

    for path, row in rows.items():
        data = git(repo, 'show', commit + ':' + path)
        sha = digest(data)
        require(len(data) == row['bytes']
                and hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == row['git_blob'], 'Frozen Git blob mismatch: ' + path)
        require(path == 'SOURCE_MANIFEST.json' or sha == hashes[path],
                'SOURCE_MANIFEST SHA mismatch: ' + path)
        target = pending / '01-源码' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        reserve(len(data))
        if sys.platform == 'darwin' and matching_working_file(repo, path, row, sha):
            subprocess.run(['/bin/cp', '-c', str(repo / path), str(target)],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            require(not target.samefile(repo / path), 'Editable source must not be hardlinked')
            cp_c_files += 1
        else:
            with target.open('xb') as stream:
                stream.write(data)
            git_blob_files += 1
        target.chmod(row['mode'])
        require(target.stat().st_size == len(data) and file_digest(target) == sha,
                'Copied source differs from frozen Git: ' + path)
        reserve(0)
        verified[path] = sha
        expected['01-源码/' + path] = {'bytes': len(data), 'sha256': sha, 'mode': row['mode']}
    require('dependencies.lock.json' in verified, 'Source SDK lock is missing')
    metadata = {
        'version': manifest['version'], 'status': 'PARTIAL_PURE_SOURCE_NOT_RUNNABLE',
        'source_export_commit': commit, 'application_commit': application_commit,
        'source_file_count': len(rows), 'source_file_bytes': source_bytes,
        'source_sdk_lock_sha256': verified['dependencies.lock.json'],
        'readable_source_sha256': verified['official_muse/app/source/main.splash'],
        'payload_sha256': verified['official_muse/app/bundle/main.splash'],
        'application_manifest_matches_frozen_source': True,
        'host_included': False, 'launcher_included': False, 'models_included': False,
        'extra_apphub_mirror_included': False, 'signature_gate_run': False,
        'build_or_runtime_validation': 'NOT_RUN_BY_SOURCE_EXPORTER',
        'receiver_two_mac_validation': 'NOT_RUN_BY_SOURCE_EXPORTER',
        'historical_old087_application_version': '0.3.26-rc5',
        'historical_old087_zip_sha256': '127a3ffe0a5343165f659978ec450cecaeeea201467687724e56ec66e521cf17',
        'historical_old087_runtime_sdk_commit': 'b48618acef0ff291ad3dc23b09946b0b15fa4f2f',
        'historical_old087_runtime_sdk_lock_sha256': '3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e',
        'calendar_bridge_fix_in_old087_host': False,
        'cp_c_verified_copy_files': cp_c_files, 'frozen_git_blob_copy_files': git_blob_files,
        'copy_scope': 'Exact frozen Git regular files; working files used only after hash/mode match',
        'cp_c_scope': 'macOS cp -c may fallback to copyfile; no hardlinks and no physical reclaim claim',
        'reserve_bytes': RESERVE, 'metadata_margin_bytes': METADATA_MARGIN,
    }
    add('00-先看这里.html', tutorial(metadata).encode())
    add('版本与交付边界.json', (json.dumps(metadata, ensure_ascii=False, indent=2) + '\n').encode())
    checks = (json.dumps({'self_excluded_from_own_hash': True, 'files': expected},
                         ensure_ascii=False, indent=2) + '\n').encode()
    add('文件校验清单.json', checks)
    found = set()
    for current, directories, files in os.walk(pending, followlinks=False):
        for name in directories:
            require(not (Path(current) / name).is_symlink(), 'Symlink in output')
        for name in files:
            target = Path(current) / name
            rel = target.relative_to(pending).as_posix()
            require(not target.is_symlink() and target.is_file()
                    and rel in expected and rel not in found, 'Unexpected output file')
            row = expected[rel]
            require(target.stat().st_size == row['bytes']
                    and file_digest(target) == row['sha256']
                    and stat.S_IMODE(target.stat().st_mode) == row['mode'],
                    'Final output verification failed: ' + rel)
            found.add(rel)
    require(found == set(expected), 'Final output file inventory mismatch')
    reserve(0)
    require(not os.path.lexists(destination), 'Destination appeared during export')
    pending.rename(destination)
    return {'status': 'PURE_SOURCE_FOLDER_VERIFIED_PARTIAL_NOT_RUNNABLE',
            'destination': str(destination), 'version': manifest['version'],
            'source_export_commit': commit, 'application_commit': application_commit,
            'source_files': len(rows), 'files_verified': len(expected),
            'source_bytes': source_bytes, 'cp_c_verified_copy_files': cp_c_files,
            'frozen_git_blob_copy_files': git_blob_files,
            'free_bytes_after': shutil.disk_usage(destination).free}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True, help='Root-declared frozen source export commit F')
    parser.add_argument('--application-commit', required=True, help='Product application commit A')
    parser.add_argument('--destination', required=True, type=Path, help='New folder in an existing parent')
    args = parser.parse_args()
    try:
        result = export_source(ROOT, args.commit, args.application_commit, args.destination)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'FAILED_NO_SUCCESS', 'error': str(error),
                          'pending_output_preserved_if_created': True}, ensure_ascii=False),
              file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
