#!/usr/bin/env python3
"""Promote the verified rc48 NO_PROFILE preview with explicit synthetic evidence.

The frozen public source and Host/model bytes remain intact. Only the outer guide,
video index and the allowlisted model-validation evidence are added. The video
itself remains a separately verified attachment supplied by Root later.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'official_muse/rc/packaging/package_lean_portable.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def main():
    pre = E / 'rc48-prepackage-r1'
    d = json.loads((pre / 'DELIVERY.json').read_text())
    assert d['version'] == '0.3.26-rc48'
    assert d['frozen_public_commit'] == '89bfd3996b5c2727242b600cd02d075bede24ef4'
    archive = Path(d['zip_path'])
    assert b.sha(archive) == d['zip_sha256']
    stage = Path(d['stage_path'])
    result = E / 'rc48-desktop-final-r1'
    result.mkdir()
    local = result / '.local-state'
    local.mkdir()
    before = b.inventory(stage)
    b.dump(result / 'before-additions-inventory.json', before)
    b.dump(result / 'before-additions-delivery.json', d)
    native = E / 'rc48-first-model-live-r1'
    evidence = stage / '05-rc48模型与配置验证'
    evidence.mkdir()
    names = ('CARRIER.json', 'FIRST_MODEL_LIVE.json', 'REOPEN_MODELS.json',
             'model-call-1.json', 'model-call-2.json', 'SCREENSHOTS.json')
    for name in names:
        shutil.copy2(native / name, evidence / name)
    # Three representative current-version images fit without omitting any source.
    images = ('first-model-reply-1.png', 'first-model-reply-2.png',
              'models-rc48-empty-first-model-r1.png')
    for name in images:
        shutil.copy2(native / '.local-state/screenshots' / name, evidence / name)
    (evidence / '先读说明.txt').write_text(
        '本目录为同一rc48候选在8492空白隔离配置的本机验证。自动配置、真实model.complete两次调用、'
        'usage/ledger、重开、官方设置及退出清理通过。回答准确率0/2，误答“晴朗”“7”，整体PARTIAL。'
        '不是强模型、接收机或官方full-chain通过证明。SCREENSHOTS.json记录打包机保留的所有原图；'
        '此目录附三张代表性当前版本截图。无账号、生产profile、邮件或日历资料导出。\n')
    app_name = 'Muse 0.3.26-rc48.app'
    resources = stage / app_name / 'Contents/Resources'
    video_name = 'Muse-0.3.26-rc48-本轮实录.mp4'
    source_name = next(p.name for p in stage.iterdir() if p.is_dir() and p.name.startswith('04-公开源码'))
    guide = b.tutorial(d['version'], d['frozen_public_commit'], app_name, source_name, video_name)
    guide = guide.replace('本机 rc45 承载测试中', '本机 rc45、rc48 承载测试中')
    guide = guide.replace('同一模型时这两个基础问题回答正确。',
        '同一模型时这两个基础问题回答正确。rc48本机两次模型调用分别耗时约47秒、11秒；CPU负载会影响等待时间。')
    guide = guide.replace('点击打开本轮实录视频', '点击打开独立交付的本轮实录视频')
    (stage / '01-先看这里-双击教程.html').write_text(guide)
    (resources / 'tutorial.html').write_text(guide)
    (stage / '06-本轮视频附件说明.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>本轮视频附件</title><style>body{font:18px/1.8 -apple-system,sans-serif;max-width:850px;margin:40px auto;padding:25px}</style>
<h1>本轮实录视频单独交付</h1><p>视频不装入ZIP，以保持ZIP严格小于500,000,000字节。
最终交付的同名视频应放在本解压文件夹旁，与ZIP一并复制到另一台Mac。</p>
<p><a href="../%s">打开 Muse rc48 本轮实录视频</a></p>
<p>本说明生成时视频附件尚待Root完成。请以最终交接中列出的实际视频文件、字节数和SHA256为准。
视频使用的实际模型与验收范围请看视频说明；基础离线模型有误答限制，接收机仍需实际测试。</p></html>''' % video_name)
    identity_path = stage / '包身份与验收.json'
    identity = json.loads(identity_path.read_text())
    identity.update(model_validation_report='05-rc48模型与配置验证/FIRST_MODEL_LIVE.json',
        isolated_rc48_model_complete_status='PASS', isolated_rc48_answer_quality_status='FAIL (0/2)',
        external_video=dict(name=video_name, status='pending separately supplied Root attachment', included_in_zip=False),
        native_gui_smoke='separate rc48 isolated carrier: actual App Hub install, six hashes and 2 real model calls; accuracy 0/2',
        native_smoke_passed=False)
    b.dump(identity_path, identity)
    app = stage / app_name
    b.run(['/usr/bin/codesign', '--force', '--sign', '-', app], result / 'outer-sign.txt')
    b.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', app], result / 'outer-codesign.txt')
    b.run([app / 'Contents/MacOS/muse-launcher', '--check'], result / 'staged-launcher-check.txt')
    expected = b.inventory(stage)
    changed = {'01-先看这里-双击教程.html', '包身份与验收.json',
        app_name + '/Contents/Resources/tutorial.html', app_name + '/Contents/_CodeSignature/CodeResources',
        app_name + '/Contents/MacOS/muse-launcher'}
    for name, item in before.items():
        if name not in changed:
            assert expected[name] == item, name
    b.dump(result / 'package-inventory.json', expected)
    new_zip = local / (stage.name + '.zip')
    b.write_zip(stage, new_zip, expected)
    extracted = local / '解压验证' / stage.name
    extracted.mkdir(parents=True)
    b.verify_and_extract_zip(new_zip, stage.name, expected, extracted)
    extracted_app = extracted / app_name
    b.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', extracted_app], result / 'extracted-codesign.txt')
    b.run([extracted_app / 'Contents/MacOS/muse-launcher', '--check'], result / 'extracted-launcher-check.txt')
    res = extracted_app / 'Contents/Resources'
    hub = extracted / '诊断工具/hub'
    b.run([hub, 'verify', res / 'mirror/catalog.json', '--anchor', b.ANCHOR], result / 'extracted-hub-verify.txt')
    b.run([hub, 'check', res / 'mirror/artifacts/muse-goals-0.3.26-rc48.bundle',
           '--publisher-key', b.PUBLISHER], result / 'extracted-hub-check.txt')
    # The macOS extractor is checked as well as our member/permission reader.
    ditto = local / 'ditto-extraction'
    ditto.mkdir()
    b.run(['/usr/bin/ditto', '-x', '-k', new_zip, ditto], result / 'ditto.txt')
    assert b.inventory(ditto / stage.name) == expected
    for name in ('02-运行环境检查.command', '04-打开官方模型设置.command'):
        b.run(['/bin/zsh', '-n', extracted / name], result / (name + '.syntax.txt'))
    desktop = Path.home() / 'Desktop'
    destination = desktop / stage.name
    output = desktop / (stage.name + '.zip')
    assert not destination.exists() and not output.exists()
    digest = b.sha(new_zip)
    stage.rename(destination)
    new_zip.rename(output)
    output.with_suffix('.sha256.txt').write_text(digest + '  ' + output.name + '\n')
    d.update(identity, stage_path=str(destination), zip_path=str(output), zip_bytes=output.stat().st_size,
        zip_sha256=digest, extracted_path=str(extracted), ditto_extracted_path=str(ditto / stage.name),
        final_frozen_rc48_desktop_delivery=True, full_prior_frozen_source_and_runtime_preserved=True,
        outer_model_evidence_and_guide_added=True, ditto_inventory_exact=True,
        current_zip_model_calls_performed=False,
        model_live_scope='same rc48 isolated carrier; archive integrity verified independently',
        video_attachment_pending=True)
    b.dump(result / 'DELIVERY.json', d)
    # Remove only our now-superseded preview and verified temporary extractions.
    archive.unlink()
    preview_sha = archive.with_suffix('.sha256.txt')
    if preview_sha.exists(): preview_sha.unlink()
    shutil.rmtree(Path(json.loads((pre / 'DELIVERY.json').read_text())['extracted_path']))
    shutil.rmtree(extracted)
    shutil.rmtree(ditto)
    d['temporary_extractions_removed_after_validation'] = True
    d['free_bytes_after'] = shutil.disk_usage(desktop).free
    b.dump(result / 'DELIVERY.json', d)
    print(json.dumps(d, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
