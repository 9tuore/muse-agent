#!/usr/bin/env python3
"""Reversibly wrap the verified rc51 stage without changing product bytes."""
import argparse
import json
import posixpath
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile
import time
import zipfile
from package_lean_portable import inventory, sha, dump, verify_and_extract_zip, ANCHOR, PUBLISHER


def write_payload(stage, destination, expected, preset=9):
    with tarfile.open(destination, 'x:xz', preset=preset, format=tarfile.PAX_FORMAT) as tar:
        rows = {'': dict(kind='dir', mode=stat.S_IMODE(stage.stat().st_mode)), **expected}
        for rel, item in sorted(rows.items()):
            member = tarfile.TarInfo(stage.name + ('/' + rel if rel else ''))
            member.mode = item['mode']
            if item['kind'] == 'dir':
                member.type = tarfile.DIRTYPE
                tar.addfile(member)
            elif item['kind'] == 'symlink':
                member.type = tarfile.SYMTYPE
                member.linkname = item['target']
                tar.addfile(member)
            else:
                member.size = item['bytes']
                with (stage / rel).open('rb') as f:
                    tar.addfile(member, f)


def validate_payload(archive, stage_name, expected):
    seen = set()
    with tarfile.open(archive, 'r:xz') as tar:
        for member in tar:
            name = member.name.rstrip('/')
            if name == stage_name:
                rel = ''
            elif name.startswith(stage_name + '/'):
                rel = name[len(stage_name) + 1:]
            else:
                raise RuntimeError('payload root mismatch')
            if Path(name).is_absolute() or '..' in Path(name).parts or rel in seen:
                raise RuntimeError('unsafe or duplicate payload member')
            if rel == '':
                if not member.isdir(): raise RuntimeError('invalid root type')
            else:
                if rel not in expected: raise RuntimeError('payload allowlist mismatch')
                item = expected[rel]
                if member.mode != item['mode']: raise RuntimeError('payload mode mismatch')
                if item['kind'] == 'dir' and member.isdir(): pass
                elif item['kind'] == 'symlink' and member.issym():
                    resolved = posixpath.normpath(str(Path(rel).parent / member.linkname))
                    if member.linkname != item['target'] or Path(member.linkname).is_absolute() or resolved == '..' or resolved.startswith('../'):
                        raise RuntimeError('payload symlink mismatch')
                elif item['kind'] == 'file' and member.isfile() and member.size == item['bytes']: pass
                else: raise RuntimeError('unsupported payload member')
            seen.add(rel)
    if seen != {''} | set(expected): raise RuntimeError('payload omitted allowed members')


def bootstrap(payload_name, digest, stage_name, app_name):
    for name in (payload_name, stage_name, app_name):
        if any(c in name for c in ('"', '$', '`', '\\', '\n')):
            raise ValueError('unsupported bootstrap filename')
    return '''#!/bin/zsh
set -euo pipefail
cd -- "${0:A:h}"
trap 'print -u2 -- "展开或校验失败；没有启动 Muse。请保留文件夹和错误提示。"' ZERR
[[ "$(/usr/bin/uname -m)" == x86_64 ]] || { print -u2 '需要 Intel Mac'; exit 1; }
os_version=$(/usr/bin/sw_vers -productVersion)
[[ "${os_version%%%%.*}" -ge 14 ]] || { print -u2 '需要 macOS 14 或更新'; exit 1; }
payload="%s"
target="%s"
digest="%s"
[[ ! -L "$target" ]] || { print -u2 '目标目录不能是符号链接'; exit 1; }
print '检查完整压缩档；首次展开可能需要数分钟。'
actual=$(/usr/bin/shasum -a 256 "$payload")
[[ "${actual%%%% *}" == "$digest" ]] || { print -u2 '压缩档 SHA256 不匹配，没有展开或启动'; exit 1; }
if [[ -e "$target" ]]; then
    [[ -d "$target" && -f .muse-unpack-complete && "$(<.muse-unpack-complete)" == "$digest" ]] || { print -u2 '已有未验证的同名目录，请在新的空文件夹解压 ZIP'; exit 1; }
else
    work=$(/usr/bin/mktemp -d "$PWD/.muse-unpack.XXXXXX")
    /usr/bin/tar -xJf "$payload" -C "$work"
    [[ -d "$work/$target" && ! -L "$work/$target" ]] || { print -u2 '完整内容目录缺失'; exit 1; }
    /bin/mv "$work/$target" "$target"
    /bin/rmdir "$work"
fi
app="$target/%s"
/usr/bin/codesign --verify --deep --strict "$app"
"$app/Contents/MacOS/muse-launcher" --check
print -r -- "$digest" > .muse-unpack-complete
if [[ "${1:-}" == --check-only ]]; then
    print '展开与资源检查通过；未打开应用。'
    exit 0
fi
[[ "$#" -eq 0 ]] || { print -u2 '未知参数；没有打开应用'; exit 1; }
/usr/bin/open "$app"
print '已请求 macOS 打开 Muse；实际界面与操作结果请继续核验。'
''' % (payload_name, stage_name, digest, app_name)


def write_stored_zip(stage, archive, expected):
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_STORED, strict_timestamps=False) as z:
        z.write(stage, stage.name + '/')
        for rel in sorted(expected):
            z.write(stage / rel, stage.name + '/' + rel, compress_type=zipfile.ZIP_STORED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=Path, required=True)
    parser.add_argument('--verified-evidence', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    args.evidence.mkdir(parents=True, exist_ok=False)
    result = {'status': 'IN_PROGRESS', 'product': 'PARTIAL', 'native_GUI_started': False,
              'models_mail_Calendar_calls': 0, 'two_receiving_Macs_tested': False,
              'actual_envelope_attempts': 1, 'stages_seconds': {}, 'packaging_tool_sha256': sha(Path(__file__))}
    try:
        stage = args.stage.resolve()
        initial = json.loads((args.verified_evidence / 'package-inventory.json').read_text())
        if inventory(stage) != initial: raise RuntimeError('verified stage has changed')
        identity = json.loads((stage / '包身份与验收.json').read_text())
        source_name = '04-公开源码-' + identity['frozen_public_commit'][:8]
        excluded = source_name + '.tar.xz'
        source_files = json.loads((stage / '公开源码允许清单.json').read_text())['files']
        expected_payload = {r: i for r, i in initial.items() if r != excluded}
        if set(r[len(source_name)+1:] for r, i in expected_payload.items()
               if r.startswith(source_name+'/') and i['kind']=='file') != set(source_files):
            raise RuntimeError('complete frozen source missing')
        if shutil.disk_usage(stage).free < 1_600_000_000 + sum(i.get('bytes', 0) for i in expected_payload.values()):
            raise RuntimeError('insufficient free space for complete envelope verification')
        title = 'Muse-0.3.26-rc51-Intel完整展开包-' + identity['frozen_public_commit'][:8] + '-2026-10-06'
        outer = args.destination / title
        archive = args.destination / (title + '.zip')
        if outer.exists() or archive.exists(): raise RuntimeError('never overwrite envelope')
        outer.mkdir()
        payload = outer / 'Muse完整内容.tar.xz'
        print('Verified stage; compressing all payload with XZ preset9.', flush=True)
        t = time.monotonic()
        write_payload(stage, payload, expected_payload)
        result['stages_seconds']['compression'] = round(time.monotonic()-t, 2)
        print('Payload written; validating exact tar members.', flush=True)
        t = time.monotonic()
        validate_payload(payload, stage.name, expected_payload)
        digest = sha(payload)
        command = outer / '00-展开并启动.command'
        command.write_text(bootstrap(payload.name, digest, stage.name, 'Muse 0.3.26-rc51.app'))
        command.chmod(0o755)
        dump(outer / '完整内容允许清单.json', dict(source_commit=identity['frozen_public_commit'],
             excluded_redundant_source_archive=excluded, files=expected_payload))
        tools = outer / '分发工具源码'; tools.mkdir()
        shutil.copy2(Path(__file__), tools / Path(__file__).name)
        shutil.copy2(Path(__file__).with_name('package_lean_portable.py'), tools / 'package_lean_portable.py')
        (outer / '01-先看这里.txt').write_text('Muse 0.3.26-rc51 · Intel Mac · macOS 14+ · PARTIAL\n\n'
            '双击 ZIP 解压后，双击 00-展开并启动.command。首次使用 macOS 自带 tar 展开完整内容，随后检查原应用签名与资源并请求打开。\n'
            '无需安装 Python、Rust、Git 或第三方解压工具。首次展开可能需要数分钟和额外磁盘空间；错误会明确报告，不假启动。\n'
            '展开后，可直接双击原 Muse 0.3.26-rc51.app；完整源码已展开，不需要旧教程里描述的单独源码 tar.xz。\n'
            '全部原支持资料保留。旧教程的单独源码压缩档说明属于前一分发形式，本包只有完整内容 tar.xz。\n'
            '内置原 Qwen 模型、宿主、签名、配置逻辑和源码字节未改；这是分发封装，不是功能升级。\n'
            '实际 rc51 视频是与 ZIP 同交付的 Muse-0.3.26-rc51-本轮实录.mp4，也在冻结源码里保留。\n'
            '本机解压验签不等于两台 Mac、模型质量、外部整链或原版 Calendar 准入通过。\n')
        result['stages_seconds']['tar_validation'] = round(time.monotonic()-t, 2)
        expected = inventory(outer)
        write_stored_zip(outer, archive, expected)
        result.update(zip_path=str(archive), stage_path=str(outer), zip_bytes=archive.stat().st_size,
                      zip_sha256=sha(archive), payload_bytes=payload.stat().st_size,
                      payload_sha256=digest, source_commit=identity['frozen_public_commit'],
                      source_file_count=len(source_files), source_logical_bytes=sum(i['bytes'] for i in source_files.values()),
                      payload_raw_bytes=sum(i.get('bytes',0) for i in expected_payload.values()),
                      excluded_only_redundant_source_tar=excluded)
        if archive.stat().st_size >= 500000000: raise RuntimeError('envelope ZIP exceeds strict 500MB')
        print('ZIP below500MB; independently extracting and checking original app.', flush=True)
        t = time.monotonic()
        restored = args.evidence / '.local-state/independent-envelope'
        restored.mkdir(parents=True)
        verify_and_extract_zip(archive, outer.name, expected, restored)
        proc = subprocess.run(['/bin/zsh', str(restored / command.name), '--check-only'], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (args.evidence/'bootstrap-check.txt').write_text(proc.stdout)
        if proc.returncode: raise RuntimeError('bootstrap failed; native GUI not started')
        recovered = restored / stage.name
        if inventory(recovered) != expected_payload: raise RuntimeError('restored full inventory mismatch')
        app = recovered / 'Muse 0.3.26-rc51.app'
        hub = recovered / '诊断工具/hub'; resources = app/'Contents/Resources'
        for label, argv in [('hub-verify',[hub,'verify',resources/'mirror/catalog.json','--anchor',ANCHOR]),
                            ('hub-check',[hub,'check',resources/'mirror/artifacts/muse-goals-0.3.26-rc51.bundle','--publisher-key',PUBLISHER]),
                            ('hub-scan',[hub,'scan',resources/'mirror/artifacts/muse-goals-0.3.26-rc51.bundle','--packet',args.evidence/'review-packet.json','--publisher-key',PUBLISHER])]:
            checked=subprocess.run([str(a) for a in argv],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (args.evidence/(label+'.txt')).write_text(checked.stdout)
            if checked.returncode: raise RuntimeError(label+' failed')
        result['stages_seconds']['independent_restore_checks']=round(time.monotonic()-t,2)
        result.update(status='PASS_DISTRIBUTION_ONLY_PRODUCT_PARTIAL', strict_under500MB=True,
                      complete_source_SHA_modes_verified=True, all_payload_SHA_modes_symlinks_verified=True,
                      bootstrap_codesign_launcher_check=True, local_extended_Hub_checks=True,
                      upstream_Calendar_admission=False)
        archive.with_suffix('.sha256.txt').write_text(result['zip_sha256']+'  '+archive.name+'\n')
    except Exception as exc:
        result['status']='FAIL_RETAINED'; result['failure']=str(exc)
        raise
    finally:
        result['elapsed_seconds']=round(time.monotonic()-started,2)
        dump(args.evidence/'RESULT.json',result)
        print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    main()
