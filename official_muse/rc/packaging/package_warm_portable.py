#!/usr/bin/env python3
"""Build the frozen Intel reproduction package from explicit public inputs."""
import argparse
import io
import tarfile
import base64
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--commit', required=True, help='Latest source snapshot commit')
parser.add_argument('--application-commit', required=True, help='Signed application bundle and catalog source commit')
parser.add_argument('--runtime-sdk-commit', required=True, help='SDK source commit used to compile the Host (b486 for Host938)')
parser.add_argument('--mirror', required=True, type=Path)
parser.add_argument('--host', required=True, type=Path)
parser.add_argument('--host-report', required=True, type=Path)
args = parser.parse_args()
COMMIT = args.commit
APPLICATION_COMMIT = args.application_commit
RUNTIME_SDK_COMMIT = args.runtime_sdk_commit
for commit in [COMMIT, APPLICATION_COMMIT, RUNTIME_SDK_COMMIT]:
    assert len(commit) == 40 and int(commit, 16) >= 0
APPLICATION_MANIFEST = json.loads(subprocess.check_output(['git', 'show', f'{APPLICATION_COMMIT}:official_muse/app/bundle/manifest.json'], cwd=ROOT))
VERSION = APPLICATION_MANIFEST['version']
assert APPLICATION_MANIFEST['id'] == 'muse-goals' and isinstance(VERSION, str) and VERSION
assert '/' not in VERSION and '\\' not in VERSION
ANCHOR = '3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'
PUBLISHER = 'muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5'
STATE = HERE / ('.local-state/portable-warm-' + COMMIT[:8])
STAGE = STATE / f'Muse-{VERSION}-Intel复现与源码-2026-10-05'
APP = STAGE / f'Muse {VERSION}.app'
RES = APP / 'Contents/Resources'
MIRROR = args.mirror.resolve()
WARM = HERE / '.local-state/chunk-delta-r2'
HOST = args.host.resolve()
HOST_REPORT = json.loads(args.host_report.read_text())
CARD = WARM / 'Muse Chunk RC Card Host.app'
HUB = HERE / '.local-state/tools/hub'
HOST_SHA = HOST_REPORT['signed_executable_sha256']
CARD_SHA = '52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
BUNDLE = f'artifacts/muse-goals-{VERSION}.bundle'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(args, cwd=ROOT):
    result = subprocess.run([str(v) for v in args], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{args[0]} exited {result.returncode}: {result.stderr[-2500:]}')
    return {'command': [str(v) for v in args], 'exit_code': result.returncode,
            'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}


def inventory(root):
    rows = []
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root).as_posix()
        mode = stat.S_IMODE(p.lstat().st_mode)
        if p.is_symlink():
            assert p.resolve().is_relative_to(root.resolve()), f'external link: {rel}'
            rows.append({'path': rel, 'kind': 'symlink', 'target': os.readlink(p), 'mode': oct(mode)})
        elif p.is_file():
            rows.append({'path': rel, 'kind': 'file', 'bytes': p.stat().st_size,
                         'sha256': sha(p), 'mode': oct(mode)})
    return rows


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def validate_frozen_inputs(entry):
    runtime_lock = subprocess.check_output(['git', 'show', f'{RUNTIME_SDK_COMMIT}:dependencies.lock.json'], cwd=ROOT)
    assert HOST_REPORT['sdk_lock_sha256'] == hashlib.sha256(runtime_lock).hexdigest(), 'Host SDK does not match the explicitly selected runtime SDK commit'
    assert entry['artifact'] == BUNDLE and entry['source']['commit'] == APPLICATION_COMMIT, 'Catalog source does not match the application commit'
    manifest = json.loads(subprocess.check_output(['git', 'show', f'{APPLICATION_COMMIT}:official_muse/app/bundle/manifest.json'], cwd=ROOT))
    assert entry['manifest'] == manifest, 'Catalog manifest does not match the frozen application manifest'
    assert manifest['id'] == 'muse-goals' and manifest['version'] == VERSION
    assert manifest['integrity']['bundle_blake3'], 'Signed application digest is missing'
    bundle_paths = ['assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
                    'screenshots/01-main.png', 'screenshots/02-global-memory.png']
    pack = json.loads((MIRROR / (BUNDLE + '.pack.json')).read_text())
    assert sorted(pack['files']) == sorted(bundle_paths)
    for rel in bundle_paths:
        frozen = subprocess.check_output(['git', 'show', f'{APPLICATION_COMMIT}:official_muse/app/bundle/{rel}'], cwd=ROOT)
        assert (MIRROR / BUNDLE / rel).read_bytes() == frozen, 'Mirror bytes do not match the application commit: ' + rel
        assert frozen == subprocess.check_output(['git', 'show', f'{COMMIT}:official_muse/app/bundle/{rel}'], cwd=ROOT), 'Source snapshot does not include the selected application bytes: ' + rel
        assert base64.b64decode(pack['files'][rel], validate=True) == frozen
    return bundle_paths


def main():
    assert Path.cwd().resolve() == ROOT, 'Run from the specified RC checkout'
    assert not STAGE.exists(), 'Preserve existing output; use a new owned stage'
    assert shutil.disk_usage(ROOT).free > 600 * 1024**2, 'Insufficient space for the warm package'
    checks = []
    inputs = []
    host_input = inventory(HOST); card_input = inventory(CARD)
    assert sha(HOST / 'Contents/MacOS/octosense') == HOST_SHA
    assert sha(CARD / 'Contents/MacOS/card-host') == CARD_SHA
    for original in [HOST, CARD]:
        checks.append(run(['codesign', '--verify', '--deep', '--strict', original]))
    checks.append(run([HUB, 'verify', MIRROR / 'catalog.json', '--anchor', ANCHOR]))
    catalog = json.loads((MIRROR / 'catalog.json').read_text())
    selected = [e for e in catalog['entries'] if e['manifest']['id'] == 'muse-goals'
                and e['manifest']['version'] == VERSION]
    assert len(selected) == 1
    entry = selected[0]
    bundle_paths = validate_frozen_inputs(entry)
    checks.append(run([HUB, 'check', MIRROR / BUNDLE, '--publisher-key', PUBLISHER]))
    before = shutil.disk_usage(ROOT).free
    (APP / 'Contents/MacOS').mkdir(parents=True)
    RES.mkdir()
    (STAGE / '03-诊断工具').mkdir()
    for src, dst, expected in [(HOST, RES / 'OctoSense Host.app', host_input),
                               (CARD, STAGE / '03-诊断工具' / CARD.name, card_input)]:
        run(['/bin/cp', '-cR', src, dst])
        assert inventory(dst) == expected
        inputs.append({'source': str(src), 'destination': str(dst.relative_to(STAGE)),
                       'entries': expected})
    for rel in ['catalog.json', BUNDLE + '.pack.json'] + [BUNDLE + '/' + v for v in bundle_paths]:
        src = MIRROR / rel; dst = RES / 'mirror' / rel
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
        inputs.append({'source': 'public_final_mirror/' + rel, 'destination': dst.relative_to(STAGE).as_posix(),
                       'bytes': src.stat().st_size, 'sha256': sha(src)})
    shutil.copy2(HUB, STAGE / '03-诊断工具/hub')
    assert sha(STAGE / '03-诊断工具/hub') == 'de6840e5aa85c73c915434488da2cd4ec8f633bde7f2f69f6259e17993318e6f'
    tutorial = (HERE / 'portable_tutorial.html').read_text().replace('__SOURCE_COMMIT__', COMMIT).replace('__APPLICATION_COMMIT__', APPLICATION_COMMIT).replace('Muse Reproduction 0.3.26-rc5 b48618ac', 'Muse Reproduction 0.3.26-rc5 ' + COMMIT[:8]).replace('0.3.26-rc5', VERSION).replace('0.3.26-RC5', VERSION.upper())
    (STAGE / '00-先看这里.html').write_text(tutorial)
    (RES / 'tutorial.html').write_text(tutorial)
    # The exact tracked-file list is the source allowlist, fixed before copying.
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '-l', '-z', COMMIT], cwd=ROOT)
    source_rows = []
    for row in tree.split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, blob, length = meta.decode().split()
        rel = name.decode('utf8')
        assert mode in ['100644', '100755'] and kind == 'blob'
        assert not any(v in rel for v in ['/private/', '/profiles/', '/vendor/', '/target/', '/cargo-home/'])
        source_rows.append({'path': rel, 'git_blob': blob, 'bytes': int(length), 'git_mode': mode})
    source_map = {r['path']: r for r in source_rows}
    assert len(source_map) == len(source_rows)
    write_json(HERE / ('SOURCE_ALLOWLIST_' + COMMIT[:8] + '.json'),
               {'source_commit': COMMIT, 'include_rule': 'Exact Git tracked public regular files only; no working-tree directory import.',
                'files': source_rows})
    tar = subprocess.check_output(['git', 'archive', '--format=tar', COMMIT], cwd=ROOT)
    copied = set()
    with tarfile.open(fileobj=io.BytesIO(tar)) as archive:
        for item in archive:
            if item.isdir():
                continue
            assert item.isfile() and item.name in source_map and '..' not in Path(item.name).parts
            row = source_map[item.name]
            data = archive.extractfile(item).read()
            assert len(data) == row['bytes']
            assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob']
            dst = STAGE / '04-最新源码' / item.name
            dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
            dst.chmod(0o755 if row['git_mode'] == '100755' else 0o644)
            row['sha256'] = sha(dst)
            inputs.append({'source_commit': COMMIT, 'source': item.name,
                           'destination': dst.relative_to(STAGE).as_posix(), **row})
            copied.add(item.name)
    assert copied == set(source_map)
    write_json(HERE / ('SOURCE_ALLOWLIST_' + COMMIT[:8] + '.json'),
               {'source_commit': COMMIT, 'file_count': len(source_rows),
                'include_rule': 'Exact frozen Git paths and verified blob/SHA256/mode; no private or untracked input.',
                'files': source_rows})
    write_json(STAGE / '源码允许清单.json', {'source_commit': COMMIT, 'files': source_rows})
    (STAGE / '05-打包入口源码').mkdir()
    for name in ['portable_launcher.m', 'portable_tutorial.html', 'package_warm_portable.py']:
        source = (HERE / name).read_text()
        if name == 'portable_launcher.m':
            source = source.replace('b48618ac', COMMIT[:8]).replace('0.3.26-rc5', VERSION)
        elif name == 'portable_tutorial.html':
            source = tutorial
        (STAGE / '05-打包入口源码' / name).write_text(source)
    for name in ['clean_room.py', 'package_clean_host.py']:
        shutil.copy2(HERE / name, STAGE / '05-打包入口源码' / name)
    launcher_source = STAGE / '05-打包入口源码/portable_launcher.m'
    executable = APP / 'Contents/MacOS/muse-launcher'
    checks.append(run(['/usr/bin/clang', '-fobjc-arc', '-mmacosx-version-min=13.3',
                       '-framework', 'AppKit', launcher_source, '-o', executable]))
    info = {'CFBundleIdentifier': 'org.xinghai.muse.reproduction.' + COMMIT[:8],
            'CFBundleExecutable': 'muse-launcher', 'CFBundleName': 'Muse ' + VERSION,
            'CFBundleDisplayName': 'Muse ' + VERSION, 'CFBundlePackageType': 'APPL',
            'CFBundleVersion': VERSION.split('-')[0], 'CFBundleShortVersionString': VERSION.split('-')[0],
            'CFBundleDevelopmentRegion': 'zh_CN', 'CFBundleLocalizations': ['zh_CN'],
            'LSMinimumSystemVersion': '13.3', 'LSUIElement': True,
            'NSCalendarsFullAccessUsageDescription': '在你授权和确认后，Muse 读取或操作本机测试日历并核对结果。'}
    (APP / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    checks.append(run(['codesign', '--force', '--sign', '-', APP]))
    checks.append(run(['codesign', '--verify', '--deep', '--strict', APP]))
    assert inventory(RES / 'OctoSense Host.app') == host_input, 'Nested host was changed'
    assert inventory(STAGE / '03-诊断工具' / CARD.name) == card_input
    checks.append(run([executable, '--check']))
    checks.append(run([STAGE / '03-诊断工具/hub', 'verify', RES / 'mirror/catalog.json', '--anchor', ANCHOR]))
    checks.append(run([STAGE / '03-诊断工具/hub', 'check', RES / 'mirror' / BUNDLE, '--publisher-key', PUBLISHER]))
    checks.append(run([STAGE / '03-诊断工具' / CARD.name / 'Contents/MacOS/card-host', '--help']))
    for binary in [executable, RES / 'OctoSense Host.app/Contents/MacOS/octosense',
                   STAGE / '03-诊断工具' / CARD.name / 'Contents/MacOS/card-host']:
        assert run(['lipo', '-archs', binary])['stdout'] == 'x86_64'
    system_check = '''#!/bin/bash
set -u
base="$(cd "$(dirname "$0")" && pwd)"
report="$base/系统检查结果-$(date +%Y%m%d-%H%M%S).txt"
app="$base/Muse 0.3.26-rc5.app"
resources="$app/Contents/Resources"
status=0
{
  printf 'Muse 0.3.26-rc5 Intel 包检查（不读取账号配置）\\n'
  sw_vers
  uname -m
  df -h "$base"
  "$app/Contents/MacOS/muse-launcher" --check || status=1
  codesign --verify --deep --strict "$app" || status=1
  codesign --verify --deep --strict "$base/03-诊断工具/Muse Chunk RC Card Host.app" || status=1
  "$base/03-诊断工具/hub" verify "$resources/mirror/catalog.json" --anchor ANCHOR_VALUE || status=1
  "$base/03-诊断工具/hub" check "$resources/mirror/artifacts/muse-goals-0.3.26-rc5.bundle" --publisher-key PUBLISHER_VALUE || status=1
  printf '\\n检查退出状态：%s（0 表示上述文件检查通过，真实业务需另测）\\n' "$status"
} > "$report" 2>&1
printf '结果已保存：%s\\n' "$report"
open -t "$report"
exit "$status"
'''.replace('ANCHOR_VALUE', ANCHOR).replace('PUBLISHER_VALUE', PUBLISHER).replace('0.3.26-rc5', VERSION)
    command = STAGE / '02-系统检查.command'; command.write_text(system_check); command.chmod(0o755)
    checks.append(run(['/bin/bash', '-n', command]))
    record = f'''Muse Intel 双机复现记录 · {VERSION} / {COMMIT}
本包没有模型权重，请先在宿主配置并测试相同模型。

分别填 Mac A 与 Mac B，每项记录 PASS / FAIL / 未测，不用空白代替通过。

Mac：A / B
日期：
型号 / Intel 芯片：
macOS 版本：
剩余磁盘 / 内存：
模型提供方 / 模型名 / 线路：
包校验与签名检查结果：
首次启动、安装、版本：
连续两条问答（输入、原始输出、耗时）：
跨对话合成记忆召回（代号蓝鲸17、来源）：
更正为银杏23：
遗忘后再次询问：
一次性本地测试任务、批准与实际结果：
退出后重新打开：
电脑重启后恢复：
本人授权的邮箱 / 日历选测：
故障提示与必要日志片段：

注意：窗口或卡片出现不等于模型 / 邮件 / 日历动作成功。
请勿将密钥、邮箱授权码、真实个人资料写入要分享的记录。
'''
    (STAGE / '01-复现测试记录.txt').write_text(record)
    (STAGE / '本机验证说明.txt').write_text(f'''Muse {VERSION} / {COMMIT}
交付类型：冻结应用源码 + 已构建 Intel 宿主的开发复现包。
已执行：目录签名、公钥应用签名、载荷与 frozen Git 逐字节比较、pack 解码逐文件比较、宿主资源与符号链接完整比较、ad hoc 严格验签、x86_64 架构检查、启动器 --check、Card Host --help、系统检查脚本语法检查、ZIP 逐文件哈希 / 链接 / 权限读回。
未执行：A4 打包任务没有启动 GUI、连接模型或账号、发送邮件、操作 EventKit、接收两台 Mac 上的复现或电脑重启。
源码92b1/新SDK da756dde已修Calendar桥；本包运行Host938/旧SDK3f未含该修复，truncated仍可返回数字0，完整Calendar/T18未通过。
独立便携启动器GUI smoke：NOT_OBSERVED；只有--check资源检查已执行，不能代替窗口实测。
总控原V15/b486应用+938Host的70次启动与持续运行证据仅作旧候选支持；不计新应用或新日历桥通过。
严格全新目录编译：BLOCKED_CAPACITY；中断证据保留。此包不是从零构建通过的证明。
整体业务验收：PARTIAL；主线最终矩阵和持续运行结果另有对应报告，本说明不代报结果。
不含模型权重 / 凭据 / 私人历史 / 生产数据库。两台 Mac 各自配置模型和账号。
Apple Silicon 未验证；启动器最低 macOS 13.3。
宿主签名：ad hoc、未 Apple 公证；内部已验证宿主未重签或修改。
''')
    (STAGE / '04-最新源码/本包源码说明.txt').write_text(f'''源码快照来自 frozen Git {COMMIT}；签名应用来源 {APPLICATION_COMMIT}；宿主SDK来源 {RUNTIME_SDK_COMMIT}。
源码包含92b1日历桥修复，新SDK锁da756dde，Calendar truncated布尔序列化已在源码修复。
运行Host仍938ba58a/旧SDK3f1bbb4e，未重编译该修复。两者不得声称同一修复状态。
普通使用只需打开上级目录的 Muse.app，不需要开发工具。
开发恢复：在本目录运行 python3 scripts/bootstrap_sdk.py，再运行 python3 scripts/bootstrap_sdk.py --verify。
首次恢复需联网取得 dependencies.lock.json 指定的官方源码；本地差异在 sdk-overlays 中。
此步骤需自行安装 Python 3 / Rust / Apple Command Line Tools，不属于普通运行要求。
上级05-打包入口源码的clean_room.py与package_clean_host.py是A4维护副本；本目录不包含 Git 历史；包含冻结提交的全部{len(source_rows)}个tracked允许文件及测试。
没有 publisher 私钥，不能直接重签新的应用载荷。
''')
    metadata = {'schema': 1, 'version': VERSION, 'status': 'DEVELOPMENT_PARTIAL', 'latest_source_commit': COMMIT, 'application_source_commit': APPLICATION_COMMIT, 'runtime_sdk_source_commit': RUNTIME_SDK_COMMIT,
                'bundle_blake3': entry['manifest']['integrity']['bundle_blake3'],
                'bundle_main_sha256': sha(RES / 'mirror' / BUNDLE / 'main.splash'),
                'latest_source_sdk_lock_sha256': sha(STAGE / '04-最新源码/dependencies.lock.json'),
                'host_sdk_lock_at_build': HOST_REPORT['sdk_lock_sha256'],
                'source_and_host_same_sdk_revision': False,
                'calendar_truncated_boolean_fix_in_source': True,
                'calendar_truncated_boolean_fix_in_runtime_host': False,
                'calendar_full_chain_T18': 'NOT_PASSED',
                'independent_portable_gui_smoke': 'NOT_OBSERVED_BY_A4',
                'tutorial_browser_visual_qa': 'NOT_OBSERVED_LOCAL_FILE_PROTOCOL_BLOCKED',
                'host_executable_sha256': HOST_SHA, 'card_executable_sha256': CARD_SHA,
                'card_sdk_lock_at_build': '3f1bbb4e4486dd418bb7692d250c567ecfbe8fb6665a9fc5c1c2cd335f48f71e',
                'catalog_sha256': sha(RES / 'mirror/catalog.json'), 'catalog_anchor_public_key': ANCHOR,
                'architecture': 'x86_64', 'minimum_macos': '13.3',
                'signature': 'ad hoc; strict verification passed; not notarized',
                'models_included': False, 'account_data_included': False,
                'clean_build_status': 'BLOCKED_CAPACITY', 'business_acceptance': 'DEVELOPMENT_PARTIAL',
                'receiver_two_mac_validation': 'NOT_RUN', 'arm_validation': 'NOT_RUN',
                'packager_gui_or_external_actions': 'NOT_RUN',
                'root_old_host_70_startups': 'COORDINATOR_REPORTED_PASS_b486_APPLICATION_AND_938_HOST_SUPPORT_ONLY',
                'root_old_host_two_hour_soak': 'OLD_V15_CANDIDATE_EVIDENCE_ONLY_SEE_ROOT_REPORT',
                'formal_publication': 'NOT_PUBLISHED'}
    write_json(STAGE / '版本与校验.json', metadata)
    manifest = {'schema': 1, 'include_rule': 'Only these exact files and relative symlinks, plus this manifest itself.',
                'self_manifest_excluded_from_own_hash': True, 'files': inventory(STAGE)}
    write_json(STAGE / '文件校验清单.json', manifest)
    final_rows = inventory(STAGE)
    assert not any('/private/' in r['path'] or '/profiles/' in r['path'] or '/cargo-home/' in r['path']
                   or '/target/' in r['path'] or '/vendor/' in r['path'] or '.gguf' in r['path'] for r in final_rows)
    write_json(HERE / ('WARM_PORTABLE_ALLOWLIST_' + COMMIT[:8] + '.json'),
               {'schema': 1, 'status': 'LOCAL_REPRODUCTION_PACKAGE_NOT_PUBLISHED', 'metadata': metadata,
                'files': final_rows, 'input_provenance': inputs})
    archive = STATE / (STAGE.name + '.zip')
    checks.append(run(['/usr/bin/ditto', '--norsrc', '--noextattr', '--noacl', '-c', '-k',
                       '--keepParent', STAGE, archive]))
    expected = {r['path']: r for r in final_rows}
    found = {}
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            name = item.filename
            if not item.flag_bits & 0x800:
                try: name = name.encode('cp437').decode('utf8')
                except UnicodeError: pass
            prefix = STAGE.name + '/'
            assert name.startswith(prefix) and '..' not in Path(name).parts
            rel = name[len(prefix):]; assert rel not in found
            row = expected[rel]; data = z.read(item)
            mode = (item.external_attr >> 16) & 0o7777
            assert mode == int(row['mode'], 8), f'mode changed: {rel}'
            if row['kind'] == 'symlink':
                assert stat.S_ISLNK(item.external_attr >> 16)
                assert data.decode() == row['target']
            else:
                assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], rel
            found[rel] = True
    assert set(found) == set(expected), 'ZIP differs from the explicit allowlist'
    result = {'metadata': metadata, 'stage': str(STAGE), 'archive': str(archive),
              'archive_bytes': archive.stat().st_size, 'archive_sha256': sha(archive),
              'entry_count': len(found), 'stage_file_bytes': sum(r.get('bytes', 0) for r in final_rows),
              'free_bytes_before': before, 'free_bytes_after': shutil.disk_usage(ROOT).free,
              'checks': checks, 'zip_exact_allowlist_match': True,
              'nested_host_unchanged': True, 'warm_card_unchanged': True,
              'pack_decoded_bytes_match_frozen_git': True, 'gui_launched': False}
    report = HERE / ('WARM_PORTABLE_RESULT_' + COMMIT[:8] + '.json'); write_json(report, result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks', 'metadata']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
