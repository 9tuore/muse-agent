#!/usr/bin/env python3
"""One-shot real GUI input and evidence. Product PASS is a reviewed observation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
SAFE_FIELDS = {
    'goal_input', 'source_input', 'session_focus_project', 'session_focus_owner',
    'chat_title_edit', 'memory_search', 'memory_correction', 'memory_new_key',
    'memory_new_value', 'memory_project', 'memory_owner', 'memory_import_text',
    'mail_to', 'mail_subject', 'mail_body', 'mail_intent', 'mail_reply_intent',
    'mail_reply_body', 'calendar_agent_input', 'schedule_clarification',
}
STATES = {'PASS', 'SIMULATION_PASS', 'FAIL', 'BLOCKED', 'HUMAN_REQUIRED', 'NOT_IMPLEMENTED'}
LEVELS = {'GUI_ONLY', 'LOCAL_REAL_STORAGE', 'REAL_OWNER_SYNTHETIC_MODEL',
          'FIXTURE_TRANSPORT', 'REAL_EXTERNAL', 'NONE'}


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def masked(value):
    value = re.sub(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[email]', str(value))
    value = re.sub(r'(?i)(bearer|password|api[_ -]?key|token|authorization)\s*[:=]\s*[^\s,;]+', r'\1=[redacted]', value)
    return value[:1200]


def inside(rect, parent):
    x, y, w, h = rect
    a, b, c, d = parent
    return w >= 2 and h >= 2 and x >= a and y >= b and x + w <= a + c and y + h <= b + d


def validate_matrix(path):
    matrix = json.loads(Path(path).read_text())
    ids = [f['test_id'] for f in matrix['features']]
    require(len(ids) == len(set(ids)), 'Duplicate case IDs')
    for f in matrix['features']:
        require([r['round'] for r in f['rounds']] == [1, 2, 3], 'Three distinct rounds required')
        require(f['priority'] in ('P0', 'P1', 'P2'), 'Unknown priority')
        for r in f['rounds']:
            require(r['status'] in STATES | {'NOT_TESTED'}, 'Unknown status')
    return {'features': len(ids), 'result_cells': len(ids) * 3,
            'pass_cells': sum(r['status'] in ('PASS', 'SIMULATION_PASS') for f in matrix['features'] for r in f['rounds'])}


class GUI:
    def __init__(self, config, case, round_id, attempt, live=True):
        self.cfg = json.loads(Path(config).read_text())
        c = self.cfg
        require(c.get('permission') == 'GUI_OWNERSHIP_GRANTED' and c.get('gui_owner') == 'ZC-05',
                'Root has not granted this GUI to ZC-05')
        require(c.get('stage') == 'FINAL_FROZEN', 'Formal rounds require a frozen candidate')
        require(c.get('isolated_test_data') is True, 'This driver is restricted to isolated test data')
        data = Path(c['data_root']).resolve(strict=True)
        for forbidden in c.get('production_data_dirs', []):
            p = Path(forbidden).resolve()
            require(data != p and data not in p.parents and p not in data.parents, 'Test data overlaps production')
        matrix = json.loads((HERE / 'acceptance-matrix.json').read_text())
        rows = [f for f in matrix['features'] if f['test_id'] == case]
        require(len(rows) == 1, 'Unknown case')
        self.feature = rows[0]
        require(round_id in (1, 2, 3) and attempt > 0, 'Invalid round or attempt')
        self.path = HERE / f'round-{round_id:02}' / case / f'attempt-{attempt:02}'
        self.path.mkdir(parents=True, exist_ok=True)
        require(not (self.path / 'result.json').exists(), 'Finished attempt is immutable; use a new attempt')
        frozen = c['frozen_files']
        for key in ('main', 'manifest', 'host', 'kernel', 'launcher'):
            require(key in frozen, f'Missing frozen {key}')
        for key, item in frozen.items():
            require(digest(item['path']) == item['sha256'], f'Frozen {key} changed')
        require(Path(frozen['host']['path']).resolve() == Path(c['executable']).resolve(), 'Wrong Host identity')
        static = {k: c[k] for k in ('git_commit', 'version', 'octosense_revision', 'frozen_files')}
        candidate_fields = dict(static, frozen_files={key: item['sha256'] for key, item in frozen.items()})
        candidate = hashlib.sha256(json.dumps(candidate_fields, sort_keys=True).encode()).hexdigest()
        identity = dict(static, candidate_key=candidate, pid=c['pid'], port=c['port'], remote_window=c['window'],
                        native_window_id=c['native_window_id'], data_root=str(data), test_id=case, round=round_id)
        identity_path = self.path / 'identity.json'
        if identity_path.exists():
            prior = json.loads(identity_path.read_text())
            require(prior['candidate_key'] == candidate, 'Candidate changed within attempt')
            require(prior['data_root'] == str(data), 'Data root changed within attempt')
        else:
            save(identity_path, identity)
        if live:
            self.check_process()

    def request(self, route, **params):
        if route in ('/snap', '/click', '/k', '/t', '/m', '/g'):
            params['w'] = self.cfg['window']
        url = f"http://127.0.0.1:{self.cfg['port']}{route}"
        if params:
            url += '?' + urlencode(params)
        with urlopen(url, timeout=20) as response:
            return response.read()

    def log(self, kind, **data):
        with (self.path / 'ui-actions.jsonl').open('a') as f:
            f.write(json.dumps(dict(time=now(), kind=kind, pid=self.cfg['pid'], remote_window=self.cfg['window'], **data), ensure_ascii=False) + '\n')

    def check_process(self):
        pid = self.cfg['pid']
        owner = subprocess.check_output(['/usr/sbin/lsof', '-nP', '-t', '-iTCP:' + str(self.cfg['port']), '-sTCP:LISTEN'], text=True).split()
        require(owner == [str(pid)], 'Remote port is not exclusively owned by expected Host')
        executable = subprocess.check_output(['/bin/ps', '-p', str(pid), '-o', 'comm='], text=True).strip()
        require(Path(executable).resolve() == Path(self.cfg['executable']).resolve(), 'Unexpected running executable')
        status = json.loads(self.request('/s'))
        require(status.get('pid') == pid, 'Remote PID mismatch')
        require(any(w['i'] == self.cfg['window'] for w in status.get('w', [])), 'Expected remote window missing')

    def widgets(self):
        self.check_process()
        rows = json.loads(self.request('/snap'))['s']
        # Never persist Splash program text or input values from a full snapshot.
        mains = [w.get('t', '') for w in rows if w.get('ty') == 'Splash']
        if mains:
            require(any(hashlib.sha256(m.encode()).hexdigest() == self.cfg['frozen_files']['main']['sha256'] for m in mains),
                    'Running Splash is not the frozen main')
        return rows

    def observe(self):
        observed = []
        for w in self.widgets():
            if w.get('ty') in ('Splash', 'TextInput'):
                if w.get('ty') == 'TextInput':
                    observed.append({'i': w.get('i'), 'ty': 'TextInput', 'r': w.get('r'), 'value': '[not recorded]'})
                continue
            row = {k: w[k] for k in ('i', 'ty', 'r', 'visible', 'enabled') if k in w}
            if w.get('t'):
                row['t'] = masked(w['t'])
            if row.get('t') or row.get('i'):
                observed.append(row)
        p = self.path / ('observation-' + str(time.time_ns()) + '.json')
        save(p, observed)
        self.log('observe', file=p.name)
        return {'file': str(p), 'widgets': observed}

    def target(self, key, pane):
        rows = self.widgets()
        found = [w for w in rows if w.get('i') == key or w.get('t') == key]
        require(len(found) == 1, 'Control is missing or ambiguous; inspect current GUI')
        target = found[0]
        require(target.get('enabled') is not False and target.get('visible') is not False, 'Disabled or hidden control')
        require(inside(target['r'], self.cfg['window_rect']), 'Control clipped outside window')
        if pane:
            parents = [w for w in rows if w.get('i') == pane]
            require(len(parents) == 1 and inside(target['r'], parents[0]['r']), 'Control clipped outside pane')
        return target

    def click(self, key, pane):
        w = self.target(key, pane)
        require(not re.search(r'(?i)^(approve(?:\s*&\s*send)?|allow(?: once| always)?|grant|confirm action)$', str(w.get('t', '')).strip()),
                'Native trusted approval requires a person; do not synthesize it')
        x, y, width, height = w['r']
        self.log('click_sent_once', key=masked(key), rect=w['r'])
        self.request('/click', x=int(x + width / 2), y=int(y + height / 2))
        return {'input_delivered_once': True, 'result_observation_required': True}

    def type_text(self, key, text, pane):
        require(key in SAFE_FIELDS, 'Only non-secret Muse fields are allowed')
        w = self.target(key, pane)
        require(w.get('ty') == 'TextInput', 'Target is not a TextInput')
        old = w.get('val', '')
        require(len(old) <= 20000, 'Input too large for controlled replacement')
        x, y, width, height = w['r']
        self.request('/click', x=int(x + width / 2), y=int(y + height / 2))
        self.request('/k', k='down', c='End')
        for _ in old:
            self.request('/k', k='down', c='Backspace')
        self.wait_value(key, '', pane)
        self.log('type', key=key, characters=len(text), text_sha256=hashlib.sha256(text.encode()).hexdigest())
        self.request('/t', t=text)
        self.wait_value(key, text, pane)
        return {'typed_characters': len(text), 'readback_matches': True}

    def wait_value(self, key, text, pane):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.target(key, pane).get('val', '') == text:
                return
            time.sleep(0.05)
        raise RuntimeError('Input readback did not match; stop without repeating input')

    def scroll(self, pane, dy):
        w = self.target(pane, None)
        x, y, width, height = w['r']
        self.log('scroll', pane=pane, dy=dy)
        self.request('/m', k='scroll', x=int(x + width / 2), y=int(y + height / 2), dy=dy, precise=1)
        return {'scroll_delivered': True}

    def capture(self, label):
        require(re.fullmatch(r'[a-zA-Z0-9_-]+', label), 'Use a simple image label')
        self.check_process()
        c = self.cfg
        ids = subprocess.check_output([c['window_id_tool'], str(c['pid'])], text=True).split()
        require(str(c['native_window_id']) in ids, 'Native window does not belong to expected Host')
        path = self.path / (label + '.png')
        require(not path.exists(), 'Never overwrite screenshot evidence')
        subprocess.run(['/usr/sbin/screencapture', '-x', '-o', '-l', str(c['native_window_id']), str(path)], check=True)
        require(path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), 'Native capture failed')
        self.log('native_capture', file=path.name, sha256=digest(path), requires_visual_inspection=True)
        return {'path': str(path), 'sha256': digest(path), 'next': 'View the actual image before reporting any result.'}

    def record(self, result_path):
        result = json.loads(Path(result_path).read_text())
        require(result.get('status') in STATES and result.get('execution_level') in LEVELS, 'Invalid result classification')
        require(result.get('expected') and result.get('actual') and result.get('started_at') and result.get('ended_at'), 'Observation or time missing')
        require(result.get('screenshots'), 'Every actual outcome needs independent GUI evidence')
        for shot in result['screenshots']:
            p = (self.path / shot['path']).resolve()
            require(self.path.resolve() in p.parents and digest(p) == shot['sha256'], 'Screenshot identity mismatch')
            require(shot.get('viewed_at') and shot.get('observation'), 'Screenshot must be actually viewed')
        if result['status'] in ('PASS', 'SIMULATION_PASS'):
            require((self.path / 'ui-actions.jsonl').is_file(), 'No GUI execution evidence')
            if self.feature['readback_required']:
                require(result.get('independent_readback'), 'Persistent result requires independent readback')
            if result['execution_level'] in ('FIXTURE_TRANSPORT', 'REAL_OWNER_SYNTHETIC_MODEL'):
                require(result['status'] == 'SIMULATION_PASS', 'Do not present simulation as real service PASS')
        for name in result.get('independent_readback', []):
            p = (self.path / name).resolve()
            require(self.path.resolve() in p.parents and p.is_file(), 'Missing independent readback artifact')
        save(self.path / 'result.json', result)
        manifest(self.path)
        matrix = json.loads((HERE / 'acceptance-matrix.json').read_text())
        identity = json.loads((self.path / 'identity.json').read_text())
        current = matrix.get('candidate')
        require(current is None or current['candidate_key'] == identity['candidate_key'],
                'New candidate must have its own acceptance matrix; do not combine candidate results')
        if current is None:
            matrix['candidate'] = {key: identity[key] for key in ('candidate_key', 'git_commit', 'version', 'octosense_revision')}
        feature = next(f for f in matrix['features'] if f['test_id'] == identity['test_id'])
        cell = feature['rounds'][identity['round'] - 1]
        cell['attempts'].append(str((self.path / 'result.json').relative_to(HERE)))
        cell['status'] = result['status']
        cell['execution_level'] = result['execution_level']
        feature['discovery'] = 'GUI_OBSERVED'
        if result['status'] != 'NOT_IMPLEMENTED':
            feature['applicability'] = 'APPLICABLE'
        else:
            feature['applicability'] = 'NOT_IMPLEMENTED'
        matrix['stage'] = 'IN_PROGRESS'
        save(HERE / 'acceptance-matrix.json', matrix)
        return {'recorded': str(self.path / 'result.json'), 'status': result['status']}


def manifest(directory):
    directory = Path(directory).resolve()
    records = [{'path': str(p.relative_to(directory)), 'sha256': digest(p), 'bytes': p.stat().st_size}
               for p in sorted(directory.rglob('*')) if p.is_file() and p.name != 'evidence-manifest.json' and '__pycache__' not in p.parts]
    save(directory / 'evidence-manifest.json', {'generated_at': now(), 'files': records})
    return {'files': len(records)}


def summary():
    matrix = json.loads((HERE / 'acceptance-matrix.json').read_text())
    features = matrix['features']
    applicable = [f for f in features if f['applicability'] != 'NOT_IMPLEMENTED']
    cells = [r for f in features for r in f['rounds']]
    complete = sum(all(r['status'] != 'NOT_TESTED' for r in f['rounds']) for f in applicable)
    full = sum(all(r['status'] in ('PASS', 'SIMULATION_PASS') for r in f['rounds']) for f in applicable)
    counts = {s: sum(r['status'] == s for r in cells) for s in sorted(STATES | {'NOT_TESTED'})}
    evidence_complete = True
    prior_failures = 0
    for cell in cells:
        for relative in cell['attempts']:
            result_path = HERE / relative
            try:
                result = json.loads(result_path.read_text())
                identity = json.loads((result_path.parent / 'identity.json').read_text())
                proof = json.loads((result_path.parent / 'evidence-manifest.json').read_text())
                evidence_complete &= identity['candidate_key'] == matrix['candidate']['candidate_key']
                evidence_complete &= all(digest(result_path.parent / f['path']) == f['sha256'] for f in proof['files'])
                prior_failures += result['status'] == 'FAIL'
            except (OSError, KeyError, TypeError, ValueError):
                evidence_complete = False
    state = 'FULL_3_ROUND_PASS' if (applicable and full == len(applicable)
            and all(f['discovery'] == 'GUI_OBSERVED' for f in features)
            and evidence_complete and not prior_failures and not matrix.get('unresolved_bugs')) else 'PARTIAL_3_ROUND_ACCEPTANCE'
    matrix['status'] = state
    matrix['discovered_gui_features'] = sum(f['discovery'] == 'GUI_OBSERVED' for f in features)
    save(HERE / 'acceptance-matrix.json', matrix)
    lines = ['# Muse 独立三轮用户验收', '', '**' + state + '**', '',
             '候选：' + json.dumps(matrix.get('candidate'), ensure_ascii=False), '',
             f'计划覆盖 {len(features)} 项；实际 GUI 发现 {matrix["discovered_gui_features"]} 项；完成三轮 {complete} 项；三轮通过 {full} 项。', '',
             '结果格数量：' + json.dumps(counts, ensure_ascii=False), '',
             f'证据清单完整：{evidence_complete}；同候选保留失败尝试：{prior_failures}。', '',
             'REAL_OWNER_SYNTHETIC_MODEL 和 FIXTURE_TRANSPORT 的通过仅计 SIMULATION_PASS，不能视作真实模型、生产账号或真实外部发送验收。', '',
             '| 用例 | 功能 | 第一轮 | 第二轮 | 第三轮 |', '| --- | --- | --- | --- | --- |']
    for f in features:
        results = []
        for r in f['rounds']:
            results.append('[' + r['status'] + '](' + r['attempts'][-1] + ')' if r['attempts'] else r['status'])
        lines.append('| ' + ' | '.join([f['test_id'], f['feature']] + results) + ' |')
    (HERE / 'MUSE_USER_ACCEPTANCE_3ROUNDS_REPORT.md').write_text('\n'.join(lines) + '\n')
    return {'status': state, 'features': len(features), 'completed_three_rounds': complete,
            'passed_three_rounds': full, 'result_counts': counts, 'evidence_complete': evidence_complete,
            'retained_failed_attempts': prior_failures}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--handoff', type=Path)
    p.add_argument('--case')
    p.add_argument('--round', type=int, dest='round_id')
    p.add_argument('--attempt', type=int, default=1)
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('observe',):
        sub.add_parser(name)
    q = sub.add_parser('click'); q.add_argument('key'); q.add_argument('--pane')
    q = sub.add_parser('type'); q.add_argument('key'); q.add_argument('text'); q.add_argument('--pane')
    q = sub.add_parser('scroll'); q.add_argument('pane'); q.add_argument('dy', type=int)
    q = sub.add_parser('capture'); q.add_argument('label')
    q = sub.add_parser('record'); q.add_argument('result_file', type=Path)
    q = sub.add_parser('manifest'); q.add_argument('directory', type=Path)
    q = sub.add_parser('validate-matrix'); q.add_argument('matrix', type=Path)
    sub.add_parser('summary')
    a = p.parse_args()
    if a.command == 'manifest':
        answer = manifest(a.directory)
    elif a.command == 'validate-matrix':
        answer = validate_matrix(a.matrix)
    elif a.command == 'summary':
        answer = summary()
    else:
        require(a.handoff and a.case and a.round_id, 'GUI calls require handoff, case and round')
        gui = GUI(a.handoff, a.case, a.round_id, a.attempt, live=a.command != 'record')
        if a.command == 'observe': answer = gui.observe()
        elif a.command == 'click': answer = gui.click(a.key, a.pane)
        elif a.command == 'type': answer = gui.type_text(a.key, a.text, a.pane)
        elif a.command == 'scroll': answer = gui.scroll(a.pane, a.dy)
        elif a.command == 'capture': answer = gui.capture(a.label)
        else: answer = gui.record(a.result_file)
    print(json.dumps(answer, ensure_ascii=False))


if __name__ == '__main__':
    main()
