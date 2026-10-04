#!/usr/bin/env python3
"""Generate bounded, reproducible synthetic history in a fresh candidate jail.

No production input is read. This seed proves storage/boot behavior, not Mail
connectivity or OS Calendar actions. Existing files are never replaced.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jail', type=Path, required=True)
    args = parser.parse_args()
    jail = args.jail.resolve()
    root = Path(__file__).resolve().parents[3]
    assert jail.is_relative_to(root / 'official_muse/app/build/ui-memory-20261003')
    assert (jail / 'bundle/main.splash').is_file()
    assert not any(p.name != 'bundle' for p in jail.iterdir()), 'Fresh synthetic jail required'
    now = '2026-10-05T00:00:00Z'
    user = 'user:synthetic:stability-rc5'
    scope = {'project': 'muse-goals', 'account': 'local', 'visibility': 'personal',
             'user_id': user, 'project_id': '', 'owner_id': ''}
    memory = {'schema': 1, 'claims': [], 'sources': [], 'forget': []}
    for i in range(65):
        sid = f'source:user:stability:{i:02d}'
        value = '汇报先给结论，再列三项重点' if i == 0 else f'合成偏好{i:02d}：' + 'bounded-fixture-content-' * 32
        memory['sources'].append({'source_id': sid, 'kind': 'user',
            'locator': f'conversation:synthetic-{i:02d}',
            'content_sha256': hashlib.sha256(value.encode()).hexdigest(),
            'observed_at': now, 'updated_at': now, 'support_excerpt': value[:120], 'scope': scope})
        if i == 64:
            continue
        doc = {'schema_version': 'muse.dsl/1', 'kind': 'memory',
            'id': f'memory:stability:{i:02d}', 'revision': 1, 'created_at': now, 'updated_at': now,
            'origin': {'type': 'user', 'ref': f'synthetic-{i:02d}'}, 'scope': scope,
            'payload': {'subject_id': '用户', 'predicate': '汇报偏好' if i == 0 else f'合成偏好{i:02d}',
                'value': value, 'epistemic_type': 'user_statement', 'source_ids': [sid],
                'observed_at': now, 'valid_from': None, 'valid_until': None,
                'relations': [], 'deleted': False}}
        memory['claims'].append({'document': doc, 'pinned': False, 'source_history': [sid],
            'memory_type': 'preference', 'conversation_id': f'synthetic-{i:02d}', 'history': []})
    sessions = []
    for i in range(16):
        messages = [{'role': 'user' if j % 2 == 0 else 'assistant',
            'text': f'合成历史 {i:02d}/{j:02d}。' + 'history-content-' * 206,
            'state': 'success', 'at': 1791158400 + i * 16 + j,
            'project': '合成验收项目', 'owner': '个人'} for j in range(16)]
        sessions.append({'id': f'stability-session-{i:02d}', 'title': f'合成验收对话 {i + 1}',
            'created_at': 1791158400 + i, 'updated_at': 1791158400 + i,
            'focus_project': '合成验收项目', 'focus_owner': '个人', 'goal_id': '',
            'proposals': [], 'messages': messages})
    chat = {'schema': 1, 'selected_id': sessions[-1]['id'], 'sessions': sessions}
    values = {'memory.json': memory, 'memory.backup.json': memory,
        'global-memory-settings.json': {'schema': 1, 'enabled': True, 'user_id': user, 'forget_pending': False},
        'chat-sessions.json': chat, 'chat-sessions.backup.json': chat,
        'calendar-state.json': {'schema': 1, 'links': [], 'receipts': [], 'local_states': []},
        'goals.json': {'schema': 2, 'goals': [], 'runs': [], 'actions': [], 'selected_id': ''},
        'mail-watch.json': {'schema': 1, 'enabled': False,
            'accounts': [{'id': 'synthetic-unconnected-account', 'ready': True,
                          'seen': [f'synthetic-message-{i}' for i in range(64)]}], 'alerts': []}}
    for name, value in values.items():
        raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
        assert len(raw) <= 1048576
        with (jail / name).open('xb') as file:
            file.write(raw)
    print(json.dumps({'kind': 'SYNTHETIC_BOOT_STRESS_NOT_LIVE_SERVICE',
        'sessions': 16, 'messages': 256, 'claims': 64, 'sources': 65,
        'files': {name: {'bytes': (jail/name).stat().st_size,
            'sha256': hashlib.sha256((jail/name).read_bytes()).hexdigest()} for name in values}}, indent=2))


if __name__ == '__main__':
    main()
