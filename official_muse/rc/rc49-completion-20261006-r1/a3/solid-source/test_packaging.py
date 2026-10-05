#!/usr/bin/env python3
"""Small synthetic archive tests; never invokes packer main or native app."""
from pathlib import Path
import importlib.util
import json
import os
import stat
import subprocess
import tarfile
import time
import zipfile
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
PACKER = ROOT / 'official_muse/rc/packaging/package_lean_portable.py'
spec = importlib.util.spec_from_file_location('portable_packer', PACKER)
packer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packer)


def main():
    local = OUT / '.local-state' / ('synthetic-' + str(time.time_ns()))
    local.mkdir(parents=True)
    result = {'kind': 'SYNTHETIC_ARCHIVE_ONLY', 'python': '3.9', 'real_delivery_built': False,
              'native_app_model_or_external_calls': 0, 'cases': [], 'expected_rejections': []}
    try:
        for solid in (False, True):
            work = local / ('solid' if solid else 'normal')
            stage = work / 'Muse-合成测试'; stage.mkdir(parents=True)
            source = stage / '04-公开源码-合成'; source.mkdir()
            (source / '中文 资料').mkdir()
            (source / '中文 资料/记忆.txt').write_text('这是合成记忆，不含用户资料。\n' * 80)
            (source / '运行.sh').write_text('#!/bin/sh\nprintf "synthetic only\\n"\n')
            (source / '运行.sh').chmod(0o755)
            (source / 'README.md').write_text('# 合成源码\n' + 'Same bounded archive test.\n' * 16000)
            (source / '历史失败.json').write_text('{"status":"FAIL","synthetic":true}\n')
            files = {r: i for r, i in packer.inventory(source).items() if i['kind'] == 'file'}
            allowlist = {r: {k: v for k, v in i.items() if k != 'kind'} for r, i in files.items()}
            (stage / '公开源码允许清单.json').write_text(json.dumps({'files': allowlist}, ensure_ascii=False))
            (stage / 'runtime').mkdir()
            (stage / 'runtime/launcher').write_bytes(b'synthetic launcher only\n' * 40)
            (stage / 'runtime/launcher').chmod(0o755)
            os.utime(stage / 'runtime/launcher', (0, 0))
            (stage / 'runtime/alias').symlink_to('launcher')
            solid_expected = None
            if solid:
                solid_expected = packer.write_solid_source(source, stage / (source.name + '.tar.xz'), allowlist)
            guide = packer.tutorial('0.3.26-rc51', 'a' * 40, 'Muse.app', source.name, solid_source=solid)
            (stage / '教程.html').write_text(guide)
            assert ('/usr/bin/tar -xJf' in guide) == solid
            full_expected = packer.inventory(stage)
            zip_expected = {r: i for r, i in full_expected.items() if not solid or (r != source.name and not r.startswith(source.name + '/'))}
            archive = work / 'delivery.zip'
            public_write = zipfile.ZipFile.write
            levels = []
            def observed_write(z, filename, arcname=None, compress_type=None, compresslevel=None):
                levels.append(compresslevel)
                return public_write(z, filename, arcname, compress_type, compresslevel)
            with patch.object(zipfile.ZipFile, 'write', observed_write):
                packer.write_zip(stage, archive, zip_expected)
            assert levels and all(level == 9 for level in levels)
            with zipfile.ZipFile(archive) as z:
                assert z.testzip() is None
                assert z.getinfo(stage.name + '/runtime/launcher').date_time[0] == 1980
                assert all(i.compress_type == zipfile.ZIP_DEFLATED for i in z.infolist() if stat.S_ISREG(i.external_attr >> 16))
                assert (any(n.startswith(stage.name + '/' + source.name + '/') for n in z.namelist())) == (not solid)
            extracted = work / 'restored'; extracted.mkdir()
            packer.verify_and_extract_zip(archive, stage.name, zip_expected, extracted)
            if solid:
                assert not (extracted / source.name).exists()
                read_allowlist = json.loads((extracted / '公开源码允许清单.json').read_text())['files']
                packer.verify_and_extract_solid_source(extracted / (source.name + '.tar.xz'), source.name,
                                                     read_allowlist, solid_expected, extracted)
                native = work / 'system-tar'; native.mkdir()
                subprocess.run(['/usr/bin/tar', '-xJf', str(stage / (source.name + '.tar.xz')),
                                '-C', str(native)], check=True, capture_output=True)
                assert packer.inventory(native / source.name) == packer.inventory(source)
            assert packer.inventory(extracted) == full_expected
            assert {r: i for r, i in packer.inventory(source).items() if i['kind'] == 'file'} == files
            assert (extracted / source.name / '运行.sh').stat().st_mode & 0o777 == 0o755
            assert os.readlink(extracted / 'runtime/alias') == 'launcher'
            assert source.is_dir() and len(files) == 4
            result['cases'].append({'mode': 'solid' if solid else 'normal', 'status': 'PASS',
                'source_file_count': len(files), 'ZIP_bytes': archive.stat().st_size,
                'ZIP_sha256': packer.sha(archive), 'CRC': 'PASS', 'allowlist_SHA_modes_symlinks': 'PASS',
                'source_tar_reconstruction': 'PASS' if solid else 'NOT_APPLICABLE',
                'independent_macos_system_tar': 'PASS' if solid else 'NOT_APPLICABLE',
                'pre_1980_timestamp_clamped': True,
                'all_regular_files_public_write_compresslevel_9': True, 'expanded_stage_preserved': True})
            if solid:
                def reject(label, action):
                    try: action()
                    except (RuntimeError, ValueError) as e:
                        result['expected_rejections'].append({'case': label, 'status': 'PASS_REJECTED', 'error_type': type(e).__name__})
                    else: raise AssertionError('Failed to reject ' + label)
                wrong = dict(zip_expected)
                wrong['runtime/launcher'] = {**wrong['runtime/launcher'], 'sha256': '0' * 64}
                bad = work / 'wrong-SHA'; bad.mkdir()
                reject('ZIP SHA mismatch', lambda: packer.verify_and_extract_zip(archive, stage.name, wrong, bad))
                wrong = dict(zip_expected)
                wrong['runtime/launcher'] = {**wrong['runtime/launcher'], 'mode': 0o600}
                bad = work / 'wrong-mode'; bad.mkdir()
                reject('ZIP mode mismatch', lambda: packer.verify_and_extract_zip(archive, stage.name, wrong, bad))
                bad = work / 'omitted-allowlist'; bad.mkdir()
                omit = {r: i for r, i in allowlist.items() if r != '运行.sh'}
                reject('source allowlist missing file', lambda: packer.verify_and_extract_solid_source(stage / (source.name + '.tar.xz'), source.name, omit, solid_expected, bad))
                for label, name, type_, link in [('tar traversal', source.name + '/../escape', tarfile.REGTYPE, ''),
                                               ('tar symlink', source.name + '/运行.sh', tarfile.SYMTYPE, '../../escape')]:
                    malicious = work / (label.replace(' ', '-') + '.tar.xz')
                    with tarfile.open(malicious, 'x:xz') as t:
                        member = tarfile.TarInfo(name); member.type = type_; member.mode = 0o755; member.linkname = link
                        t.addfile(member)
                    bad = work / (label.replace(' ', '-') + '-out'); bad.mkdir()
                    reject(label, lambda m=malicious, b=bad: packer.verify_and_extract_solid_source(m, source.name, allowlist, solid_expected, b))
        result['status'] = 'PASS_SYNTHETIC_ONLY'
    except Exception as e:
        result['status'] = 'FAIL_RETAINED'
        result['failure_type'] = type(e).__name__
        raise
    finally:
        result['packer_sha256'] = packer.sha(PACKER)
        result['run_id'] = local.name
        (OUT / ('RESULT-' + local.name + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
