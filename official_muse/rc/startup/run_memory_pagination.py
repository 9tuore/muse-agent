#!/usr/bin/env python3
"""Verify every synthetic Memory record is reachable in the visible Shell."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate, shot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    assert args.port in (8486, 8488)
    meta = json.loads((args.candidate / 'candidate.json').read_text())
    assert meta['profile_kind'] == 'LOCAL_MODEL_ONLY_SYNTHETIC'
    jail = args.candidate / 'private/apps/muse-goals'
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest(jail / 'bundle/main.splash') == meta['source_sha256']
    memory = json.loads((jail / 'memory.json').read_text())
    values = {entry['document']['payload']['value'] for entry in memory['claims']}
    assert len(values) == 64 and not memory['forget'], 'Use the complete synthetic stability seed'
    args.out.mkdir(parents=True, exist_ok=False)
    before = digest(jail / 'memory.json')
    remote = Remote(args.port)
    log_offset = remote.log(400)['n']
    report = {'status': 'RUNNING', 'source_sha256': meta['source_sha256'],
              'host_sha256': meta['host_sha256'], 'pages': [], 'external_actions': False}

    def save():
        (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def scroll(amount):
        x, y, width, height = remote.find('memory_body')['r']
        remote.scroll(int(x + width - 4), int(y + height / 2), amount)

    try:
        navigate(remote, '记忆')
        found = set()
        for page in range(8):
            scroll(-10000)
            visible = set()
            for step in range(24):
                labels = {widget.get('t', '') for widget in remote.widgets() if widget.get('ty') == 'Label'}
                visible |= labels & values
                if len(visible) == 8:
                    break
                scroll(220)
            assert len(visible) == 8 and not found & visible, (page + 1, len(visible))
            found |= visible
            report['pages'].append({'page': page + 1, 'records': len(visible), 'scroll_steps': step})
            save()
            if page in (0, 7):
                shot(remote, args.out / f'page-{page + 1}.png')
            scroll(-10000)
            if page < 7:
                remote.click('下一页')
        assert found == values
        assert not any(widget.get('t') == '下一页' for widget in remote.widgets())
        remote.click('上一页')
        remote.set_text('memory_search', '汇报先给结论')
        assert any(widget.get('t', '').startswith('汇报先给结论') for widget in remote.widgets())
        assert not any(widget.get('t') in ('上一页', '下一页') for widget in remote.widgets())
        remote.set_text('memory_search', '')
        remote.wait_for('下一页', 5)
        assert digest(jail / 'memory.json') == before
        log = json.loads(remote.request('/log', since=log_offset))
        (args.out / 'log.json').write_text(json.dumps(log, ensure_ascii=False))
        assert not any('[E]' in line for line in log['l']), 'Runtime error retained in log.json'
        report.update(status='PASS', all64_reachable=True, search_reset=True, memory_sha256_unchanged=True)
        navigate(remote, '对话')
    except Exception:
        report['status'] = 'FAIL'
        (args.out / 'exception.txt').write_text(traceback.format_exc())
        (args.out / 'failure-log.json').write_bytes(remote.request('/log', n=400))
        raise
    finally:
        save()
    print(json.dumps({key: value for key, value in report.items() if key != 'pages'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
