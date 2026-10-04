#!/usr/bin/env python3
"""Read-only telemetry of a visible, fixed Shell candidate and its Mail monitor.

Never submits Chat, approves a card, sends Mail, writes Calendar or grants
permissions. Account and message contents are omitted from the summary.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def signatures(jail):
    return {p.relative_to(jail).as_posix(): {'sha256': sha(p),
        'mtime_ns': p.stat().st_mtime_ns, 'bytes': p.stat().st_size}
        for p in jail.rglob('*') if p.is_file() and 'bundle' not in p.relative_to(jail).parts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=7200)
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--observe-existing-baseline', action='store_true',
                        help='Read-only existing authorized stable window; never final RC proof')
    args = parser.parse_args()
    assert args.port in ((8484,) if args.observe_existing_baseline else (8486, 8487, 8488, 8489)) and 60 <= args.seconds <= 7200
    assert 10 <= args.interval <= 30
    meta = json.loads((args.candidate / 'candidate.json').read_text())
    if args.observe_existing_baseline:
        assert meta['version'] == '0.3.25' and meta['profile_kind'] == 'PRIVATE_AUTHORIZED_CLONE'
    assert meta['profile_kind'] in ('LOCAL_MODEL_ONLY_SYNTHETIC', 'PRIVATE_AUTHORIZED_CLONE')
    private = Path(meta.get('runtime_private_path', str(args.candidate / 'private')))
    jail = private / 'apps/muse-goals'
    assert sha(jail / 'bundle/main.splash') == meta['source_sha256']
    assert sha(Path(meta['host_app_path']) / 'Contents/MacOS/octosense') == meta['host_sha256']
    args.out.mkdir(parents=True, exist_ok=False); args.out.chmod(0o700)
    remote = Remote(args.port); remote.wait_for('goal_input', 20)
    pid = json.loads(remote.request('/s'))['pid']
    ledger = private / 'apps/.host/model/ledger.json'

    def model_usage():
        value = json.loads(ledger.read_text()) if ledger.is_file() else {}
        return {'day': value.get('day'), **value.get('apps', {}).get('muse-goals', {'calls': 0, 'tokens': 0})}

    def records():
        read = lambda name: json.loads((jail / name).read_text()) if (jail / name).is_file() else {}
        watch = read('mail-watch.json')
        assert watch.get('enabled') is True, 'Mail monitor must actually be enabled'
        memory = read('memory.json'); calendar = read('calendar-state.json'); chat = read('chat-sessions.json')
        assert memory.get('claims') and chat.get('sessions'), 'Nonempty Memory and Chat required'
        goals = read('goals.json')
        return {'mail_enabled': True, 'accounts': len(watch.get('accounts', [])),
            'ready_accounts': sum(x.get('ready') is True for x in watch.get('accounts', [])),
            'seen': sum(len(x.get('seen', [])) for x in watch.get('accounts', [])),
            'alerts': len(watch.get('alerts', [])), 'claims': len(memory.get('claims', [])),
            'sources': len(memory.get('sources', [])), 'sessions': len(chat.get('sessions', [])),
            'messages': sum(len(x.get('messages', [])) for x in chat.get('sessions', [])),
            'calendar_links': len(calendar.get('links', [])), 'actions': len(goals.get('actions', []))}

    baseline = signatures(jail); usage = model_usage(); counts = records()
    assert counts['accounts'] and counts['ready_accounts'] and counts['seen'], 'Ready Mail baseline required'
    log_offset = remote.log(300)['n']
    report = {'kind': 'VISIBLE_SHELL_REAL_MAIL_READ_ONLY_SOAK' if meta['profile_kind'] == 'PRIVATE_AUTHORIZED_CLONE'
              else 'VISIBLE_SHELL_SYNTHETIC_ACCOUNT_NO_BACKEND_SOAK',
        'code_commit': meta['commit'], 'version': meta['version'], 'source_sha256': meta['source_sha256'],
        'host_sha256': meta['host_sha256'], 'pid': pid, 'requested_seconds': args.seconds,
        'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'samples': [],
        'model_usage_before': usage, 'baseline_counts': counts, 'status': 'RUNNING',
        'external_write_or_send_performed_by_sampler': False}
    if args.observe_existing_baseline:
        report['kind'] = 'EXISTING_STABLE_REAL_MAIL_READ_ONLY_SOAK_NOT_FINAL_RC'
    report['host_request_count'] = 'NOT_OBSERVABLE_FROM_EXISTING_REMOTE_SURFACE'
    report['calendar_initialization'] = 'Must be verified separately; stored links do not prove system access'
    started = time.monotonic()
    previous = baseline

    def save():
        # Preserve the last complete observation if the disk fills during a save.
        temporary = args.out / 'report.json.pending'
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(args.out / 'report.json')

    save()
    try:
        while True:
            elapsed = time.monotonic() - started
            row = {'elapsed_seconds': elapsed, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            assert json.loads(remote.request('/s'))['pid'] == pid, 'Shell process changed'
            assert remote.find('goal_input')['r'][2] > 80, 'Editable Chat input disappeared'
            resource = subprocess.check_output(['ps', '-p', str(pid), '-o', 'pcpu=,rss='], text=True).split()
            assert len(resource) == 2
            row.update(cpu_percent=float(resource[0]), rss_kib=int(resource[1]))
            row['records'] = records(); row['model_usage'] = model_usage()
            assert row['model_usage'] == usage, 'Unattended monitor triggered model use'
            current = signatures(jail)
            row['content_changes'] = [name for name, value in current.items() if name not in previous or value['sha256'] != previous[name]['sha256']]
            row['unchanged_content_rewrites'] = [name for name, value in current.items()
                if name in previous and value['sha256'] == previous[name]['sha256'] and value['mtime_ns'] != previous[name]['mtime_ns']]
            assert not row['unchanged_content_rewrites'], 'Unchanged state was written again'
            assert row['records']['actions'] == counts['actions'], 'Background external-action record added'
            logs = json.loads(remote.request('/log', since=log_offset)); log_offset = logs['n']
            errors = [x for x in logs['l'] if '[E]' in x or 'budget exceeded' in x or 'no root view' in x]
            row['runtime_error_count'] = len(errors)
            if errors:
                (args.out / 'failure-log.json').write_text(json.dumps(logs, ensure_ascii=False, indent=2))
                raise AssertionError('Runtime error; original private log preserved')
            report['samples'].append(row); save()
            previous = current
            print(json.dumps({'elapsed_seconds': round(elapsed, 1), 'cpu_percent': row['cpu_percent'],
                              'rss_kib': row['rss_kib'], 'alerts': row['records']['alerts']}), flush=True)
            if elapsed >= args.seconds:
                break
            time.sleep(min(args.interval, args.seconds - elapsed))
        report['status'] = 'PASS'; report['actual_seconds'] = time.monotonic() - started
    except Exception:
        report['status'] = 'FAIL'; report['actual_seconds'] = time.monotonic() - started
        (args.out / 'exception.txt').write_text(traceback.format_exc())
        raise
    finally:
        report['model_usage_after'] = model_usage(); save()


if __name__ == '__main__':
    main()
