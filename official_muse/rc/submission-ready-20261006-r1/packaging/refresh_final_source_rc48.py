#!/usr/bin/env python3
"""One final source/report refresh to Root's explicit 8d9599fd snapshot.

Product 89bfd399, signed Gate, Host, Hub and model stay unchanged. The guide keeps
the actual 89bfd399 launcher data namespace and names the new source separately.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'official_muse/rc/packaging/package_lean_portable.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
SOURCE = '8d9599fd11b6caa44c4194acb685b44aef5c1fd6'
PRODUCT = '89bfd3996b5c2727242b600cd02d075bede24ef4'


def main():
    previous = E / 'rc48-desktop-final-r1'
    d = json.loads((previous / 'DELIVERY.json').read_text())
    archive = Path(d['zip_path'])
    assert b.sha(archive) == d['zip_sha256']
    stage = Path(d['stage_path'])
    before = b.inventory(stage)
    result = E / 'rc48-final-source-r1'
    result.mkdir()
    local = result / '.local-state'
    local.mkdir()
    b.dump(result / 'before-source-delivery.json', d)
    b.dump(result / 'before-source-inventory.json', before)
    app_name = 'Muse 0.3.26-rc48.app'
    resources = stage / app_name / 'Contents/Resources'
    for name in b.BUNDLE_FILES:
        assert b.run(['git', 'rev-parse', SOURCE + ':official_muse/app/bundle/' + name]).strip() == \
               b.run(['git', 'rev-parse', PRODUCT + ':official_muse/app/bundle/' + name]).strip()
    tree = __import__('subprocess').check_output(['git', 'ls-tree', '-rlz', SOURCE], cwd=ROOT)
    allowlist = {}
    for record in tree.split(b'\0'):
        if not record: continue
        meta, encoded = record.split(b'\t', 1)
        mode, kind, oid, length = meta.decode().split()
        name = encoded.decode('utf-8')
        path = b.safe_relative(name)
        assert kind == 'blob' and mode in ('100644', '100755'), name
        assert not set(path.parts) & {'.git', '.local-state', 'private', 'profiles', 'vendor', 'target'}, name
        assert path.suffix.lower() not in ('.db', '.sqlite', '.sqlite3', '.pem', '.key') and not path.name.startswith('.env'), name
        allowlist[name] = dict(git_blob=oid, bytes=int(length), mode=int(mode[-3:], 8))
    old_source = stage / '04-公开源码-89bfd399'
    old_source.rename(local / old_source.name)
    source_name = '04-公开源码-8d9599fd'
    source = stage / source_name
    source.mkdir()
    data = __import__('subprocess').check_output(['git', 'archive', '--format=tar', SOURCE], cwd=ROOT)
    exported = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as tar:
        for member in tar:
            path = b.safe_relative(member.name)
            if member.isdir():
                (source / path).mkdir(parents=True, exist_ok=True)
                continue
            assert member.isfile() and member.name in allowlist, member.name
            payload = tar.extractfile(member).read()
            item = allowlist[member.name]
            assert len(payload) == item['bytes']
            assert hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest() == item['git_blob']
            out = source / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(payload)
            out.chmod(item['mode'])
            item['sha256'] = hashlib.sha256(payload).hexdigest()
            exported.add(member.name)
    assert exported == set(allowlist)
    del data
    b.dump(stage / '公开源码允许清单.json', dict(commit=SOURCE, count=len(allowlist),
        logical_bytes=sum(i['bytes'] for i in allowlist.values()), files=allowlist))
    reports = stage / '07-本轮最终报告与公开证据'
    reports.mkdir()
    prefix = 'official_muse/rc/submission-ready-20261006-r1/'
    names = ['REPORT.md'] + sorted(name[len(prefix):] for name in allowlist
        if name.startswith(prefix + 'RC48_') and '/' not in name[len(prefix):] and name.endswith('.json'))
    for name in names:
        shutil.copy2(source / prefix / name, reports / name)
    guide = b.tutorial(d['version'], PRODUCT, app_name, source_name, 'Muse-0.3.26-rc48-本轮实录.mp4')
    guide = guide.replace('冻结提交 <code>' + PRODUCT + '</code>',
        '公开源码冻结提交 <code>' + SOURCE + '</code>；运行产品提交 <code>' + PRODUCT + '</code>')
    guide = guide.replace('本机 rc45 承载测试中', '本机 rc45、rc48 承载测试中')
    guide = guide.replace('<h2>包内内容与版本依据</h2>',
        '<h2>本轮报告</h2><p><a href="07-本轮最终报告与公开证据/REPORT.md">查看本轮最终报告</a>；'
        '<a href="05-rc48模型与配置验证/FIRST_MODEL_LIVE.json">查看离线模型验证与误答记录</a>。</p>'
        '<h2>包内内容与版本依据</h2>')
    (stage / '01-先看这里-双击教程.html').write_text(guide)
    (resources / 'tutorial.html').write_text(guide)
    identity_file = stage / '包身份与验收.json'
    identity = json.loads(identity_file.read_text())
    identity.update(frozen_public_commit=SOURCE, frozen_product_commit=PRODUCT,
        launcher_state_namespace_commit=PRODUCT[:8], source_file_count=len(allowlist),
        source_and_product_commits_differ_only_by_public_docs_and_evidence=True,
        final_report_directory=reports.name, final_report_files=names)
    b.dump(identity_file, identity)
    b.run(['/usr/bin/codesign', '--force', '--sign', '-', stage / app_name], result / 'outer-sign.txt')
    b.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', stage / app_name], result / 'outer-codesign.txt')
    b.run([stage / app_name / 'Contents/MacOS/muse-launcher', '--check'], result / 'launcher-check.txt')
    expected = b.inventory(stage)
    changes = {'01-先看这里-双击教程.html', '公开源码允许清单.json', '包身份与验收.json',
        app_name + '/Contents/Resources/tutorial.html', app_name + '/Contents/_CodeSignature/CodeResources',
        app_name + '/Contents/MacOS/muse-launcher'}
    for name, item in before.items():
        if name.startswith(old_source.name + '/') or name == old_source.name or name in changes: continue
        assert expected[name] == item, name
    b.dump(result / 'package-inventory.json', expected)
    output = local / archive.name
    b.write_zip(stage, output, expected)
    extracted = local / '解压验证' / stage.name
    extracted.mkdir(parents=True)
    b.verify_and_extract_zip(output, stage.name, expected, extracted)
    app = extracted / app_name
    b.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', app], result / 'extracted-codesign.txt')
    b.run([app / 'Contents/MacOS/muse-launcher', '--check'], result / 'extracted-launcher-check.txt')
    res = app / 'Contents/Resources'
    hub = extracted / '诊断工具/hub'
    b.run([hub, 'verify', res / 'mirror/catalog.json', '--anchor', b.ANCHOR], result / 'hub-verify.txt')
    b.run([hub, 'check', res / 'mirror/artifacts/muse-goals-0.3.26-rc48.bundle',
        '--publisher-key', b.PUBLISHER], result / 'hub-check.txt')
    ditto = local / 'ditto-extraction'
    ditto.mkdir()
    b.run(['/usr/bin/ditto', '-x', '-k', output, ditto], result / 'ditto.txt')
    assert b.inventory(ditto / stage.name) == expected
    digest = b.sha(output)
    os.replace(output, archive)
    archive.with_suffix('.sha256.txt').write_text(digest + '  ' + archive.name + '\n')
    d.update(identity, zip_bytes=archive.stat().st_size, zip_sha256=digest,
        public_source_logical_bytes=sum(i['bytes'] for i in allowlist.values()),
        final_source_refresh_from_explicit_root_freeze=True,
        complete_source_and_reports_verified=True, preserved_gate_host_hub_model_and_prior_evidence=True,
        root_public_reports_copied_exactly_from_frozen_git=True,
        extracted_path=str(extracted), ditto_extracted_path=str(ditto / stage.name))
    shutil.rmtree(extracted)
    shutil.rmtree(ditto)
    d['temporary_extractions_removed_after_validation'] = True
    d['free_bytes_after'] = shutil.disk_usage(stage).free
    b.dump(result / 'DELIVERY.json', d)
    print(json.dumps(d, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
