#!/usr/bin/env python3
"""Prepare one Muse integration candidate without changing the stable bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.4.0-rc6'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    output.relative_to(ROOT / 'build')
    output.mkdir(parents=True, exist_ok=False)
    readable = output / 'readable-bundle'
    shutil.copytree(ROOT / 'bundle', readable)
    source = (ROOT / 'official_muse/app/source/main.splash').read_text()
    assert source.count('Muse · 0.3.27-rc18') == 1
    source = source.replace('Muse · 0.3.27-rc18', 'Muse · ' + VERSION)
    (readable / 'main.splash').write_text(source)
    manifest = json.loads((readable / 'manifest.json').read_text())
    assert manifest['id'] == 'muse-goals' and manifest['agent'] is None
    manifest['version'] = VERSION
    manifest['integrity'] = {'bundle_blake3': ''}
    manifest['capabilities'] = ['storage', 'model', 'mail', 'glance', 'runtime',
        'octos.session.open', 'octos.session.history', 'octos.turn.start', 'octos.turn.interrupt']
    manifest['requires'] = ['host-api-v1']
    manifest['host_api'] = {'required': {method: 1 for method in
        ('runtime.list', 'mail.compose', 'mail.compose_status', 'mail.review_send')}}
    manifest['agent'] = {'profile': 'read-only', 'instructions': 'AGENT.md',
        'tools': ['ask_user_question', 'calendar.events', 'calendar.get_event',
            'calendar.add_event', 'calendar.update_event', 'calendar.remove_event', 'calendar.notify'], 'model': {'tier': 'standard',
        'needs': ['tool_calling'], 'local_only': False},
        'token_budget': None, 'max_iterations': None}
    (readable / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    shutil.copyfile(Path(__file__).with_name('AGENT.md'), readable / 'AGENT.md')
    listing = json.loads((readable / 'listing.json').read_text())
    listing['description'] = ('Muse 将中文对话、全局记忆、长期事务和行动链整合在同一界面。'
        '邮件使用配套 OctoSense 原生登录、起草、审阅和状态接口；发送需要本人批准。'
        '全局记忆支持来源、范围、更正和遗忘。官方助手申请内置日历查询、回读、新建、更新、删除和通知，'
        '使用前需要宿主本人启用；更新与删除仍需 Host 本人批准；真实调动须经过同身份验收。'
        '本候选保留历史记录并明确显示能力状态。配套宿主基于官方源码，包含待审修复。')
    listing['release_notes'] = (VERSION + '：统一应用入口、宿主、锁定内核、界面和本地模型启动器。'
        '移植有界源码准备，保留 64ms 脚本限额；新增官方 Agent 声明，首次使用仍需宿主本人授权。'
        '日历工具和真实邮件全链仍需同身份验收，候选状态不代表正式公开发布。')
    (readable / 'listing.json').write_text(json.dumps(listing, ensure_ascii=False, indent=2) + '\n')
    compact = subprocess.run([sys.executable, str(ROOT / 'official_muse/ui_memory/compact_bundle.py'),
        '--source', str(readable), '--out', str(output / 'bundle')], check=True,
        capture_output=True, text=True)
    identity = {'version': VERSION, 'transform': json.loads(compact.stdout),
        'upstream_source_sha256': hashlib.sha256((ROOT / 'official_muse/app/source/main.splash').read_bytes()).hexdigest(),
        'status': 'PREPARED_NOT_ADMITTED', 'calendar_grant_added': False,
        'production_data_included': False}
    (output / 'bundle-identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    print(json.dumps(identity))


if __name__ == '__main__':
    main()
