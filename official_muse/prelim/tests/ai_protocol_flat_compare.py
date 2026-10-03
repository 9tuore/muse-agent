#!/usr/bin/env python3
"""Three original synthetic questions, one flat-schema variant, direct 8080.

No product changes, Shell/model.complete service, card-host or external actions.
The imported replay helpers do not execute the original diagnostic's main.
"""
import datetime
import hashlib
import json
import time
from urllib.request import Request, urlopen

from ai_protocol_diagnose import CASES, ROOT, accept, compact


OUT = ROOT / 'official_muse/prelim/evidence/ai/protocol-flat-variant'
BASE = ROOT / 'official_muse/prelim/evidence/ai/protocol-intermediate'
SELECTED = ['mail_complete', 'calendar_complete', 'mail_missing_to']


def main():
    assert not OUT.exists(), 'Do not overwrite evidence'
    baseline = json.loads((BASE / 'report.json').read_text())
    main_source = (ROOT / 'official_muse/app/bundle/main.splash').read_text()
    assert 'fn mail_model_draft(){' in main_source
    assert 'fn calendar_model_candidate(' in main_source
    # Calendar limits match its existing flat schema. Existing mail_model_draft
    # has subject/body only; to is added for this expressly requested variant,
    # using the verified chat schema's existing to limit.
    mail_schema = {'type': 'object', 'properties': {
        'to': {'type': 'string', 'maxLength': 200},
        'subject': {'type': 'string', 'maxLength': 180},
        'body': {'type': 'string', 'maxLength': 1800}},
        'required': ['to', 'subject', 'body'], 'additionalProperties': False}
    calendar_schema = {'type': 'object', 'properties': {
        'title': {'type': 'string', 'maxLength': 160},
        'start': {'type': 'string', 'maxLength': 40},
        'end': {'type': 'string', 'maxLength': 40},
        'time_zone': {'type': 'string', 'maxLength': 80},
        'location': {'type': 'string', 'maxLength': 160}},
        'required': ['title', 'start', 'end', 'time_zone', 'location'],
        'additionalProperties': False}
    questions = dict(CASES)
    OUT.mkdir(parents=True)
    records = []
    for key in SELECTED:
        old = next(row for row in baseline['results'] if row['id'] == key)
        assert questions[key] == old['question'], 'Keep original questions'
        schema = calendar_schema if key.startswith('calendar') else mail_schema
        kind = '日历候选' if key.startswith('calendar') else '邮件草稿候选'
        task = ('只形成' + kind + '，不执行，不声称已发送或创建。缺失字段留空字符串，不猜。'
                '保留用户正文意图，不增加未提供的事实或承诺。'
                '日期需完整ISO8601偏移；模糊时间不猜。只输出schema规定的平面字段。')
        # Retain original non-task system instructions and the reference-clock/
        # no-retrieved-memory suffix so the comparison changes only task/schema.
        old_system = old['attempts'][0]['request']['messages'][0]['content']
        prefix, rest = old_system.split('\n\nTask:\n', 1)
        old_task = rest.split('\n\nJSON Schema:\n', 1)[0]
        suffix = old_task[old_task.index('\n本轮参考时钟UTC：'):]
        system = prefix + '\n\nTask:\n' + task + suffix
        system += '\n\nJSON Schema:\n' + compact(schema)
        row = {'id': key, 'question': questions[key], 'task': task,
               'schema': schema, 'attempts': []}
        note = None
        for attempt in [1, 2]:
            query = questions[key]
            if note:
                query += ('\n\nYour previous answer was refused: ' + note +
                          '. Answer again with only one JSON value that validates against the schema.')
            wire = {'model': 'local-default', 'stream': False, 'messages': [
                {'role': 'system', 'content': system}, {'role': 'user', 'content': query}]}
            request = Request('http://127.0.0.1:8080/v1/chat/completions',
                              data=compact(wire).encode(),
                              headers={'Content-Type': 'application/json'})
            before = time.monotonic()
            with urlopen(request, timeout=125) as response:
                raw = response.read()
                status = response.status
            parsed = json.loads(raw)
            text = parsed['choices'][0]['message'].get('content', '')
            value, note = accept(text, schema)
            row['attempts'].append({'attempt': attempt, 'http_status': status,
                                    'seconds': time.monotonic()-before,
                                    'request': wire, 'raw_response': parsed,
                                    'raw_content': text, 'parsed_output': value,
                                    'protocol_error': note})
            (OUT / (key + '.json')).write_text(json.dumps(row, ensure_ascii=False, indent=2)+'\n')
            print(compact({'id': key, 'attempt': attempt, 'http_status': status,
                           'protocol_error': note, 'raw_content': text}), flush=True)
            if note is None:
                break
        row['protocol_pass'] = note is None
        records.append(row)
    report = {'scope': 'INTERMEDIATE_DIRECT_8080_HOST_WIRE_REPLAY; not model.complete service or full-chain',
              'recorded_at': datetime.datetime.now().astimezone().isoformat(),
              'variant': 'One flat candidate schema and short task; unchanged original questions, wire settings, system prefix and reference context',
              'main_sha256_at_variant': hashlib.sha256(main_source.encode()).hexdigest(),
              'baseline_main_sha256': baseline['source_sha256'],
              'baseline_function_sha256': baseline['config_function_sha256'],
              'reference_clock': baseline['reference_clock'],
              'mail_schema_provenance': 'Existing function is mail_model_draft (subject/body only); explicitly requested variant adds to from verified chat field. Not an exact existing API invocation.',
              'calendar_schema_provenance': 'Existing calendar_model_candidate flat field types/limits',
              'question_count': 3, 'backend_request_count': sum(len(r['attempts']) for r in records),
              'protocol_pass_count': sum(r['protocol_pass'] for r in records),
              'baseline_selected_protocol_pass_count': sum(row['protocol_pass'] for row in baseline['results'] if row['id'] in SELECTED),
              'semantic_grading': 'Pending separate review of raw content; protocol acceptance does not imply correct fields',
              'results': records, 'external_actions': 0, 'paid_requests': 0,
              'agent_kernel_started': False, 'product_or_host_modified': False,
              'holdout_used': False, 'validator': 'Same inspected Python schema subset replay as baseline'}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(compact({k: report[k] for k in ['question_count', 'backend_request_count', 'protocol_pass_count']}), flush=True)


if __name__ == '__main__':
    main()
