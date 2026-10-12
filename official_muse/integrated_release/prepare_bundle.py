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
VERSION = '0.4.0-rc9'


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
    manifest.pop('github', None)
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
    listing['description'] = ('Muse 让对话、记忆和行动连在一起。用中文整理想法，保存和更正重要记忆，'
        '查看来信、起草回复，把邮件里的安排添加到日历。行动链显示事情进行到哪一步，重启后继续处理。')
    listing['release_notes'] = (VERSION + '：精简界面；支持连续撰写邮件；提供明确的回复和添加日历按钮；'
        '优化邮件正文与写信区域的滚动；保留日程与原事项的关联。')
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
