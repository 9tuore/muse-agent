#!/usr/bin/env python3
"""Build one local Intel reproduction archive from an explicit public Git commit.

Only the given frozen Git tree, public Gate mirror, and pinned Host/Hub enter it.
The public local model and its required Intel runner are verified from an explicit
input manifest. No publication, profile export, download, or cleanup is performed.
"""
import argparse
import base64
import hashlib
import html
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import tarfile
import time
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HOST = ROOT / 'official_muse/rc/packaging/.local-state/desktop-workarea-20261005-r1/Muse Host.app'
HUB = ROOT / 'official_muse/rc/packaging/.local-state/qq-login-20261005-r1/hub'
HOST_SHA = '1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3'
HUB_SHA = '24db5e559582c44936e3023b2bd6e276f9390531d94f77682d45760db9a6b64d'
ANCHOR = '3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840'
PUBLISHER = 'muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5'
BUNDLE_FILES = ('assets/icon.svg', 'listing.json', 'main.splash', 'manifest.json',
                'screenshots/01-main.png', 'screenshots/02-global-memory.png')
MAX_ZIP_BYTES = 500_000_000
MODEL_EVIDENCE = ROOT / 'official_muse/rc/submission-ready-20261006-r1/packaging'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def run(args, log=None):
    result = subprocess.run([str(a) for a in args], cwd=ROOT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        log.write_text(result.stdout)
    if result.returncode:
        raise RuntimeError('command failed (%s): %s\n%s' %
                           (result.returncode, args[0], result.stdout[-4000:]))
    return result.stdout


def safe_relative(name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('unsafe relative path: ' + name)
    return p


def inventory(root):
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            p = Path(base) / name
            rel = p.relative_to(root).as_posix()
            s = p.lstat()
            mode = stat.S_IMODE(s.st_mode)
            if p.is_symlink():
                target = os.readlink(p)
                if Path(target).is_absolute():
                    raise ValueError('external symlink: ' + rel)
                try:
                    (p.parent / target).resolve().relative_to(root.resolve())
                except ValueError:
                    raise ValueError('escaping symlink: ' + rel)
                if not p.exists():
                    raise ValueError('broken symlink: ' + rel)
                result[rel] = dict(kind='symlink', mode=mode, target=target,
                                   sha256=hashlib.sha256(os.fsencode(target)).hexdigest())
            elif p.is_dir():
                result[rel] = dict(kind='dir', mode=mode)
            elif p.is_file():
                result[rel] = dict(kind='file', mode=mode, bytes=s.st_size, sha256=sha(p))
            else:
                raise ValueError('unsupported filesystem entry: ' + rel)
    return result


def write_zip(stage, destination, expected):
    prefix = stage.name + '/'
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as z:
        root = zipfile.ZipInfo(prefix)
        root.create_system = 3
        root.external_attr = (stat.S_IFDIR | 0o755) << 16 | 0x10
        z.writestr(root, b'')
        for rel, item in sorted(expected.items()):
            name = prefix + rel + ('/' if item['kind'] == 'dir' else '')
            zi = zipfile.ZipInfo(name)
            zi.create_system = 3
            kind = {'dir': stat.S_IFDIR, 'file': stat.S_IFREG, 'symlink': stat.S_IFLNK}[item['kind']]
            zi.external_attr = (kind | item['mode']) << 16
            if item['kind'] == 'dir':
                zi.external_attr |= 0x10
                z.writestr(zi, b'')
            elif item['kind'] == 'symlink':
                z.writestr(zi, os.fsencode(item['target']))
            else:
                zi.compress_type = zipfile.ZIP_DEFLATED
                with (stage / rel).open('rb') as source, z.open(zi, 'w') as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
    if destination.stat().st_size >= MAX_ZIP_BYTES:
        raise RuntimeError('ZIP exceeds strict 500,000,000-byte limit')


def verify_and_extract_zip(archive, stage_name, expected, extract_dir):
    prefix = stage_name + '/'
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        names = [m.filename for m in members]
        wanted = {prefix} | {prefix + rel + ('/' if i['kind'] == 'dir' else '')
                              for rel, i in expected.items()}
        if len(names) != len(set(names)) or set(names) != wanted:
            raise RuntimeError('ZIP member allowlist mismatch')
        for member in members:
            rel = member.filename[len(prefix):].rstrip('/')
            if not rel:
                continue
            p = extract_dir / safe_relative(rel)
            item = expected[rel]
            mode = (member.external_attr >> 16) & 0o7777
            if mode != item['mode']:
                raise RuntimeError('ZIP mode mismatch: ' + rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            if item['kind'] == 'dir':
                p.mkdir(exist_ok=True)
                p.chmod(mode)
            elif item['kind'] == 'symlink':
                data = z.read(member)
                if hashlib.sha256(data).hexdigest() != item['sha256']:
                    raise RuntimeError('ZIP symlink mismatch: ' + rel)
                p.symlink_to(os.fsdecode(data))
            else:
                h = hashlib.sha256()
                with z.open(member) as source, p.open('xb') as output:
                    for block in iter(lambda: source.read(1024 * 1024), b''):
                        h.update(block)
                        output.write(block)
                p.chmod(mode)
                if h.hexdigest() != item['sha256'] or p.stat().st_size != item['bytes']:
                    raise RuntimeError('ZIP file mismatch: ' + rel)
    if inventory(extract_dir) != expected:
        raise RuntimeError('extracted inventory differs from packaged tree')


def tutorial(version, commit, app_name, source_name, external_video=None):
    video_block = ''
    if external_video:
        video_block = ('<h2>本轮实录视频</h2><p>视频与 ZIP 分开交付，以保持 ZIP 严格小于 500,000,000 字节。'
            '需要观看时，将视频与 ZIP 一起复制到另一台 Mac，并放在解压后的文件夹旁。'
            '<a href="../%s">点击打开本轮实录视频</a>。视频说明的是实录时实际使用的模型和验收范围，'
            '不代表基础离线模型具有同样能力。</p>') % quote(external_video)
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Muse 双机复现教程</title>
<style>body{font:17px/1.75 -apple-system,BlinkMacSystemFont,sans-serif;color:#19212d;background:#f2f5fa;margin:0}main{max-width:880px;margin:40px auto;padding:32px;background:white;border-radius:18px}h1{line-height:1.25}h2{margin-top:36px}a{color:#1858b5}code{background:#edf1f7;padding:2px 5px;overflow-wrap:anywhere}li{margin:9px 0}.pill{background:#edf4ff;padding:12px 18px;border-radius:10px}.links a{display:inline-block;margin:8px 12px 8px 0;padding:10px 16px;border:1px solid #bacbea;border-radius:8px}table{border-collapse:collapse;width:100%%}td,th{border:1px solid #dce2ea;text-align:left;padding:10px}</style>
<main><p class="pill">Intel Mac · macOS 14 或更新 · 本地开发复现包 · %(version)s</p>
<h1>Muse 双机复现教程</h1><p>把整个 ZIP 复制到另一台 Mac，双击解压。先读此教程，再在 Finder 中双击 <strong>%(app)s</strong>。应用、宿主和基础离线模型已打包，无需安装 Python、Rust、Git 或开发工具。首次启动会自动建立本机独立配置并启动内置模型，无需下载模型或填写 API Key。</p>
<nav class="links"><a href="%(app_url)s">查看应用</a><a href="02-运行环境检查.command">运行环境检查</a><a href="03-双机测试记录.html">双机测试记录</a><a href="%(source_url)s/README.md">公开源码 README</a><a href="包身份与验收.json">包身份与验收</a></nav>
<p>浏览器可能将应用或 .command 链接作为下载处理；这种情况下回到解压后的 Finder 文件夹，双击对应文件即可。教程本身不联网。</p>
%(video_block)s
<h2>1. 检查电脑并打开应用</h2><ol><li>苹果菜单 → 关于本机：芯片为 Intel，macOS 至少为 14。两台电脑各自解压一份，运行与数据彼此独立。</li><li>可先双击「02-运行环境检查.command」，它只检查文件、版本与签名，不配置账号、不打开宿主。</li><li>在 Finder 双击「%(app)s」。若系统提示开发者无法验证，使用 macOS 的右键 → 打开，或在「系统设置 → 隐私与安全性」按系统提示允许本次打开。本包为本地 ad hoc 签名开发候选，未公证。</li><li>启动器打开 OctoSense App Hub。在 Muse 一行点击「获取」，阅读权限页，向下滚动到底部点击「安装」。切到「已安装」，点击 Muse 的「打开」。首次加载后稍等几秒，确认对话输入框已出现。包中当前运行版本为 <strong>%(version)s</strong>；运行制品只保留这一版。</li></ol>
<h2>2. 直接测试离线对话，按需更换模型</h2><p>内置 Qwen3-0.6B Q4_K_S（纯四位量化） 是基础离线模型，由官方 Apache 2.0 权重经 llama.cpp 重新量化得到，能力和精度有限。适合基础对话、格式与离线运行检查；不是强模型，不能据此保证复杂推理、工具规划或全部闭环成功。运行器为 Intel CPU 版，首次加载请等候数秒。模型仅监听本机回环地址，启动器退出时关闭自己的模型进程。</p>
<p>本机 rc45 承载测试中，自动配置与两次真实模型调用成功，但天空颜色和 7+5 两个问题均误答；直接连接同一模型时这两个基础问题回答正确。内置模型与 Muse 的请求上下文组合仍有准确性限制。实际任务复现请在官方模型设置中换用可靠服务，按真实回答逐项记录结果。</p>
<p>首次启动自动配置内置模型。以后若需更强模型，先用 ⌘Q 退出宿主，再在 Finder 双击「04-打开官方模型设置.command」，在官方 AI 模型页面配置本人授权的服务。启动器保留已配置的其他模型和记录，不覆盖它们。设置保存后退出宿主，再正常打开复现应用。云端服务可能计费；包中没有账号、API Key、邮箱密码或旧机聊天资料。</p>
<p>打开 Muse 后测试：「请用两句话介绍你能做什么」，再发送一个内容不同的追问，确认第二次答案对应新问题。不要把窗口出现、按钮出现或编译通过当作实际动作成功。</p>
<h2>3. 一次性任务与记忆</h2><p>先使用虚构内容测试：创建一个无外部操作的整理任务，修改任务描述，再取消；在全局记忆中保存一个虚构偏好，重新打开查看，再测试更正与遗忘。逐项记录实际结果和失败提示，不写入真实联系人资料。</p>
<h2>4. 邮箱和系统日历按需授权</h2><p>邮件、日历功能依赖宿主能力及你自己的账号或系统权限。只在本人授权后配置邮箱，读取自己允许的内容；发送邮件或更改事件前检查候选内容并逐项确认，完成后从邮箱或日历独立读回。第一轮可跳过这些实际动作。</p>
<p>Calendar 使用本包中的最小本地 EventKit 宿主扩展；它<strong>尚未获得原版 OctoSense 官方接纳</strong>。本地扩展 Hub 检查通过也不能替代官方 full-chain 验收。当前整体状态为 <strong>PARTIAL</strong>，没有宣称 20/20 完成。Hub 的 review packet 已生成，但尚无独立发布者审查；签名列表内隐私链接为占位链接，正式发布材料仍待补齐。</p>
<h2>5. 退出、重开与定位问题</h2><p>在 OctoSense 中按 ⌘Q 正常退出。再打开复现应用会继续使用这台电脑的独立数据。数据目录：<code>~/Library/Application Support/Muse Reproduction %(version)s %(short)s/</code>；启动日志：该目录的 <code>logs/host.log</code>，离线模型日志为 <code>logs/model.log</code>。这份包不包含旧机器的生产配置。模型启动失败时保留错误提示和日志；无需手工安装运行器。反馈失败时记录系统版本、版本号、步骤与可见提示；日志中若包含本人配置，先去掉私密信息。</p>
<h2>包内内容与版本依据</h2><table><tr><th>内容</th><th>说明</th></tr><tr><td>运行应用</td><td>一个实际 Muse Host、当前签名 catalog、当前 bundle 与 pack、原生启动器，以及基础离线模型和必需的 llama.cpp 库</td></tr><tr><td>公开源码</td><td>冻结提交 <code>%(commit)s</code> 的完整公开 Git 文件，包括已有失败证据、SDK 引导和 overlay；不含 .git、未跟踪目录或私人资料。源码里的旧版说明和验收结果保留为历史记录。</td></tr><tr><td>模型来源和许可</td><td>包内「离线模型来源与许可.json」记录权重来源、量化方法和 SHA256；Apache 2.0 与 MIT 完整许可随运行资源提供。</td></tr><tr><td>历史目录</td><td>签名 catalog 的历史元数据保持原样以维持签名，仅打包当前运行制品。源码中的历史证据也保留。</td></tr><tr><td>不含</td><td>账号、密钥、生产资料、私有 Mail/Calendar 数据、编译缓存</td></tr></table>
<p>本机打包检查与接收电脑的实际复现结果请分别记录。启动器资源检查及解压验签通过不等于聊天、投递邮件或日历 CRUD 通过。</p></main></html>''' % dict(version=html.escape(version), commit=commit, short=commit[:8],
        app=html.escape(app_name), app_url=quote(app_name), source_url=quote(source_name), video_block=video_block)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--gate', required=True, type=Path)
    p.add_argument('--evidence', required=True, type=Path)
    p.add_argument('--model-root', type=Path, default=MODEL_EVIDENCE / '.local-state/local-model')
    p.add_argument('--external-video', type=Path, help='Approved public MP4, copied beside the ZIP and linked in the tutorial')
    p.add_argument('--date', default='2026-10-05')
    args = p.parse_args()
    video = None
    if args.external_video:
        args.external_video = args.external_video.resolve(strict=True)
        if not args.external_video.is_file() or args.external_video.suffix.lower() != '.mp4':
            raise ValueError('expected an existing approved MP4 file')
        video = dict(name='Muse-' + args.version + '-本轮实录.mp4', bytes=args.external_video.stat().st_size,
                     sha256=sha(args.external_video), included_in_zip=False)
    started = time.monotonic()
    commit = run(['git', 'rev-parse', args.commit]).strip()
    if len(commit) != 40 or not all(c in '0123456789abcdef' for c in commit):
        raise ValueError('expected full frozen Git commit')
    if not args.version.startswith('0.3.26-rc') or not args.version[9:].isdigit():
        raise ValueError('unexpected candidate version')
    evidence = args.evidence.resolve()
    allowed_evidence = ROOT / 'official_muse/rc/packaging'
    if not evidence.is_relative_to(allowed_evidence):
        evidence.relative_to(MODEL_EVIDENCE)
    evidence.mkdir(parents=True, exist_ok=False)
    local = evidence / '.local-state'
    local.mkdir()
    if shutil.disk_usage(ROOT).free < 2 * 1024 * 1024 * 1024:
        raise RuntimeError('need at least 2 GiB free for staging, ZIP and extraction; no cleanup performed')
    if sha(HOST / 'Contents/MacOS/octosense') != HOST_SHA or sha(HUB) != HUB_SHA:
        raise RuntimeError('pinned runtime input hash mismatch')
    if run(['/usr/bin/lipo', '-archs', HOST / 'Contents/MacOS/octosense']).strip() != 'x86_64':
        raise RuntimeError('expected Intel Host')
    run(['/usr/bin/codesign', '--verify', '--deep', '--strict', HOST], evidence / 'host-input-codesign.txt')
    host_inventory = inventory(HOST)
    model_root = args.model_root.resolve()
    model_plan = json.loads((MODEL_EVIDENCE / 'MODEL_INPUTS.json').read_text())
    model_inventory = inventory(model_root)
    actual_files = {r: i for r, i in model_inventory.items() if i['kind'] == 'file'}
    if set(actual_files) != set(model_plan['files']):
        raise RuntimeError('model runtime file allowlist mismatch')
    for name, item in actual_files.items():
        if item['sha256'] != model_plan['files'][name]['sha256'] or item['bytes'] != model_plan['files'][name]['bytes']:
            raise RuntimeError('model input identity mismatch: ' + name)
    run([model_root / 'llama/llama-server', '--version'], evidence / 'model-runner-version.txt')
    if run(['/usr/bin/lipo', '-archs', model_root / 'llama/llama-server']).strip() != 'x86_64':
        raise RuntimeError('expected Intel model runner')
    gate = args.gate.resolve()
    candidate = json.loads((gate / 'candidate.json').read_text())
    catalog = gate / 'mirror/catalog.json'
    catalog_data = json.loads(catalog.read_text())
    entry = next(e for e in catalog_data['entries'] if e['manifest']['version'] == args.version)
    bundle_name = 'muse-goals-' + args.version + '.bundle'
    bundle = gate / 'mirror/artifacts' / bundle_name
    pack = bundle.with_name(bundle_name + '.pack.json')
    packed_files = json.loads(pack.read_text())['files']
    if set(packed_files) != set(BUNDLE_FILES) or candidate['version'] != args.version:
        raise RuntimeError('Gate version/file mismatch')
    comparisons = {}
    for name in BUNDLE_FILES:
        public = subprocess.check_output(['git', 'show', commit + ':official_muse/app/bundle/' + name], cwd=ROOT)
        actual = (bundle / name).read_bytes()
        if public != actual or public != base64.b64decode(packed_files[name]):
            raise RuntimeError('frozen Git/Gate/pack mismatch: ' + name)
        comparisons[name] = hashlib.sha256(public).hexdigest()
    readable = subprocess.check_output(['git', 'show', commit + ':official_muse/app/source/main.splash'], cwd=ROOT)
    readable_sha = hashlib.sha256(readable).hexdigest()
    manifest = json.loads((bundle / 'manifest.json').read_text())
    if manifest != candidate['manifest'] or manifest != entry['manifest']:
        raise RuntimeError('Gate/candidate/catalog manifest mismatch')
    run([HUB, 'verify', catalog, '--anchor', ANCHOR], evidence / 'input-hub-verify.txt')
    # --catalog applies publication policy and refuses this already listed version.
    # Verify the signed catalog separately; this check validates the current bundle.
    run([HUB, 'check', bundle, '--publisher-key', PUBLISHER], evidence / 'input-hub-check.txt')
    run([HUB, 'scan', bundle, '--packet', evidence / 'input-review-packet.json', '--publisher-key', PUBLISHER],
        evidence / 'input-hub-scan.txt')

    tree = subprocess.check_output(['git', 'ls-tree', '-rlz', commit], cwd=ROOT)
    allowlist = {}
    for record in tree.split(b'\0'):
        if not record:
            continue
        meta, name_bytes = record.split(b'\t', 1)
        mode, kind, oid, length = meta.decode().split()
        name = name_bytes.decode('utf-8')
        path = safe_relative(name)
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise RuntimeError('unsupported source entry: ' + name)
        if set(path.parts) & {'.git', '.local-state', 'private', 'profiles', 'vendor', 'target'}:
            raise RuntimeError('private/cache source path: ' + name)
        if path.suffix.lower() in ('.db', '.sqlite', '.sqlite3', '.pem', '.key') or path.name.startswith('.env'):
            raise RuntimeError('credential/database source path: ' + name)
        allowlist[name] = dict(git_blob=oid, bytes=int(length), mode=int(mode[-3:], 8))
    title = 'Muse-%s-Intel精简运行与源码-%s-%s' % (args.version, commit[:8], args.date)
    stage = Path.home() / 'Desktop' / title
    archive = stage.with_name(title + '.zip')
    if stage.exists() or archive.exists():
        raise RuntimeError('new delivery path already exists; never overwrite')
    stage.mkdir()
    source_name = '04-公开源码-' + commit[:8]
    source = stage / source_name
    source.mkdir()
    archived = subprocess.check_output(['git', 'archive', '--format=tar', commit], cwd=ROOT)
    exported = set()
    with tarfile.open(fileobj=io.BytesIO(archived), mode='r:') as tar:
        for member in tar:
            path = safe_relative(member.name)
            if member.isdir():
                (source / path).mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile() or member.name not in allowlist:
                raise RuntimeError('Git archive differs from explicit allowlist: ' + member.name)
            data = tar.extractfile(member).read()
            item = allowlist[member.name]
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if blob != item['git_blob'] or len(data) != item['bytes']:
                raise RuntimeError('source content mismatch: ' + member.name)
            out = source / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            out.chmod(item['mode'])
            item['sha256'] = hashlib.sha256(data).hexdigest()
            exported.add(member.name)
    if exported != set(allowlist):
        raise RuntimeError('Git archive omitted frozen public files')
    del archived
    dump(stage / '公开源码允许清单.json', dict(commit=commit, count=len(allowlist),
         logical_bytes=sum(i['bytes'] for i in allowlist.values()), files=allowlist))

    app_name = 'Muse ' + args.version + '.app'
    app = stage / app_name
    contents = app / 'Contents'
    resources = contents / 'Resources'
    (contents / 'MacOS').mkdir(parents=True)
    resources.mkdir()
    shutil.copytree(HOST, resources / 'OctoSense Host.app', symlinks=True)
    mirror = resources / 'mirror'
    (mirror / 'artifacts').mkdir(parents=True)
    shutil.copy2(catalog, mirror / 'catalog.json')
    shutil.copytree(bundle, mirror / 'artifacts' / bundle_name)
    shutil.copy2(pack, mirror / 'artifacts' / pack.name)
    shutil.copytree(model_root, resources / 'local-model', symlinks=True)
    if inventory(resources / 'local-model') != model_inventory:
        raise RuntimeError('packaged model runtime differs from verified inputs')
    dump(stage / '离线模型来源与许可.json', model_plan)
    guide = tutorial(args.version, commit, app_name, source_name, video['name'] if video else None)
    (stage / '01-先看这里-双击教程.html').write_text(guide)
    (resources / 'tutorial.html').write_text(guide)
    launcher_source = (ROOT / 'official_muse/rc/packaging/portable_launcher.m').read_text()
    launcher_source = launcher_source.replace('0.3.26-rc5', args.version).replace('b48618ac', commit[:8])
    owned_launcher = evidence / 'portable_launcher.m'
    owned_launcher.write_text(launcher_source)
    run(['/usr/bin/clang', '-fobjc-arc', '-mmacosx-version-min=14.0', '-framework', 'AppKit',
         owned_launcher, '-o', contents / 'MacOS/muse-launcher'], evidence / 'launcher-build.txt')
    plist = dict(CFBundleIdentifier='org.xinghai.muse.reproduction.' + commit[:8],
                 CFBundleExecutable='muse-launcher', CFBundleName='Muse ' + args.version,
                 CFBundleDisplayName='Muse ' + args.version, CFBundlePackageType='APPL',
                 CFBundleShortVersionString='0.3.26', CFBundleVersion=args.version.split('rc')[-1],
                 CFBundleDevelopmentRegion='zh_CN', LSMinimumSystemVersion='14.0', LSUIElement=True)
    (contents / 'Info.plist').write_bytes(plistlib.dumps(plist))
    tools = stage / '诊断工具'
    tools.mkdir()
    shutil.copy2(HUB, tools / 'hub')
    checks = '''#!/bin/zsh
set -eu
cd -- "${0:A:h}"
print 'Muse Intel 环境与包文件检查（不配置账号、不打开宿主）'
[[ "$(/usr/bin/uname -m)" == x86_64 ]] || { print '需要 Intel Mac'; exit 1; }
os_version=$(/usr/bin/sw_vers -productVersion)
[[ "${os_version%%%%.*}" -ge 14 ]] || { print '需要 macOS 14 或更新'; exit 1; }
print "macOS: $os_version"
app='./%s'
/usr/bin/codesign --verify --deep --strict "$app"
"$app/Contents/MacOS/muse-launcher" --check
./诊断工具/hub verify "$app/Contents/Resources/mirror/catalog.json" --anchor '%s'
./诊断工具/hub check "$app/Contents/Resources/mirror/artifacts/%s" --publisher-key '%s'
print '文件、版本、签名检查通过；真实对话与外部动作仍需实际测试。'
read -r '?按回车关闭窗口：'
''' % (app_name, ANCHOR, bundle_name, PUBLISHER)
    (stage / '02-运行环境检查.command').write_text(checks)
    (stage / '02-运行环境检查.command').chmod(0o755)
    (stage / '04-打开官方模型设置.command').write_text('''#!/bin/zsh
set -eu
cd -- "${0:A:h}"
print '先用 ⌘Q 退出已经打开的复现宿主。此入口打开同一复现环境的官方 AI 模型设置。'
exec './%s/Contents/MacOS/muse-launcher' --models
''' % app_name)
    (stage / '04-打开官方模型设置.command').chmod(0o755)
    (stage / '03-双机测试记录.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>双机测试记录</title><style>body{font:16px/1.7 -apple-system,sans-serif;max-width:1000px;margin:40px auto;padding:20px}table{border-collapse:collapse;width:100%%}td,th{border:1px solid #bbc4d1;padding:12px}textarea{width:95%%;min-height:60px}</style><h1>Muse %s 双机测试记录</h1><p>在浏览器填写后可打印为 PDF 保存。默认不自动保存、不联网。未测试填「未测试」，失败保留实际提示。</p><p>电脑/系统版本：<textarea></textarea></p><table><tr><th>步骤</th><th>实际结果与提示</th></tr>%s</table><p>Calendar 属于本地宿主扩展；整体验收 PARTIAL。本表不是官方 full-chain 通过证明。</p></html>''' %
        (html.escape(args.version), ''.join('<tr><td>%s</td><td><textarea></textarea></td></tr>' % s for s in
         ['解压与环境检查', '启动 App Hub 并安装当前 Muse', '自动配置基础离线模型，发送两次不同问题',
          '虚构一次性任务：创建、更正、取消', '虚构记忆：保存、重开、修改、遗忘',
          '重启后恢复', '邮箱本人授权后测试；投递独立读回', 'Calendar 本人授权后测试；系统独立读回'])))
    identity = dict(version=args.version, frozen_public_commit=commit,
        external_video=video,
        gate_source_commit=entry['source']['commit'], gate_candidate_commit=candidate['commit'],
        gate_commit_differs_from_frozen=entry['source']['commit'] != commit,
        frozen_bundle_equals_gate_and_pack=True, bundle_file_sha256=comparisons,
        readable_source_sha256=readable_sha, payload_sha256=comparisons['main.splash'],
        host_executable_sha256=HOST_SHA, hub_cli_sha256=HUB_SHA,
        supported_arch='x86_64', minimum_macos='14.0', signature='local ad hoc; not notarized',
        overall_acceptance='PARTIAL', upstream_calendar_acceptance=False,
        independent_publisher_review=False, model_weights_included=True,
        local_model='Qwen3-0.6B-Q4_K_S-pure-offline', local_model_quality='basic offline fallback; not strong',
        model_first_configuration='automatic in recipient isolated profile; existing custom providers preserved',
        model_input_sha256=model_plan['files']['Qwen3-0.6B-Q4_K_S-pure.gguf']['sha256'],
        credentials_or_profiles_included=False, source_file_count=len(allowlist),
        signed_catalog_preserved=True, signed_catalog_entries=len(catalog_data['entries']),
        runtime_artifact_versions=[args.version], recipient_machine_tested=False,
        native_gui_smoke='not performed by archive builder; see external delivery evidence for separate smoke',
        limitations=['First launch configures a basic offline model; complex work requires a more capable provider.',
                     'Calendar is the minimal local Host extension, not upstream official admission.',
                     'Historical signed catalog metadata and public source evidence are retained.',
                     'Static checks do not establish paid model, Mail, Calendar or official full-chain success.'])
    dump(stage / '包身份与验收.json', identity)
    run(['/usr/bin/codesign', '--force', '--sign', '-', app], evidence / 'outer-sign.txt')
    run(['/usr/bin/codesign', '--verify', '--deep', '--strict', app], evidence / 'outer-codesign.txt')
    if inventory(resources / 'OctoSense Host.app') != host_inventory:
        raise RuntimeError('nested Host changed')
    run([contents / 'MacOS/muse-launcher', '--check'], evidence / 'staged-launcher-check.txt')
    expected = inventory(stage)
    dump(evidence / 'package-inventory.json', expected)
    write_zip(stage, archive, expected)
    extracted = local / '解压验证' / title
    extracted.mkdir(parents=True)
    verify_and_extract_zip(archive, title, expected, extracted)
    extracted_app = extracted / app_name
    run(['/usr/bin/codesign', '--verify', '--deep', '--strict', extracted_app], evidence / 'extracted-codesign.txt')
    run([extracted_app / 'Contents/MacOS/muse-launcher', '--check'], evidence / 'extracted-launcher-check.txt')
    e_res = extracted_app / 'Contents/Resources'
    e_hub = extracted / '诊断工具/hub'
    run([e_hub, 'verify', e_res / 'mirror/catalog.json', '--anchor', ANCHOR], evidence / 'extracted-hub-verify.txt')
    run([e_hub, 'check', e_res / 'mirror/artifacts' / bundle_name,
         '--publisher-key', PUBLISHER], evidence / 'extracted-hub-check.txt')
    run([e_hub, 'scan', e_res / 'mirror/artifacts' / bundle_name, '--packet', evidence / 'extracted-review-packet.json',
         '--publisher-key', PUBLISHER],
        evidence / 'extracted-hub-scan.txt')
    digest = sha(archive)
    archive.with_suffix('.sha256.txt').write_text(digest + '  ' + archive.name + '\n')
    external_video_path = None
    if video:
        external_video_path = archive.parent / video['name']
        if external_video_path.exists():
            if sha(external_video_path) != video['sha256']:
                raise RuntimeError('different video already exists at delivery destination')
        else:
            shutil.copy2(args.external_video, external_video_path)
        if sha(external_video_path) != video['sha256'] or external_video_path.stat().st_size != video['bytes']:
            raise RuntimeError('external delivery video differs from approved input')
    delivery = dict(identity, zip_path=str(archive), zip_bytes=archive.stat().st_size, zip_sha256=digest,
        external_video_path=str(external_video_path) if external_video_path else None,
        stage_path=str(stage), extracted_path=str(extracted),
        public_source_logical_bytes=sum(i['bytes'] for i in allowlist.values()),
        strict_size_limit=MAX_ZIP_BYTES, zip_below_limit=True,
        zip_member_allowlist_sha256_modes_and_symlinks_verified=True,
        extracted_inventory_exact=True, extracted_codesign_and_hub_checks_passed=True,
        launcher_resource_check_passed=True, native_smoke_passed=False,
        elapsed_seconds=round(time.monotonic() - started, 2))
    dump(evidence / 'DELIVERY.json', delivery)
    print(json.dumps(delivery, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
