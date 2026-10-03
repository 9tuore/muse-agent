#!/usr/bin/env python3
"""Four synthetic questions: real card-host config + local Host-wire replay.

This is not a Shell model.complete invocation or final acceptance. The replay
matches the inspected Host wire/system/retry rules, without its ledger/service.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'official_muse/prelim/evidence/ai/protocol-intermediate'
CARD = Path('/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/release/card-host')
PORT = 8486
CASES = [
    ('mail_complete', '请起草一封邮件给self@example.invalid，主题是合成协议诊断，正文是周五进展顺利。只起草，不发送。'),
    ('mail_missing_to', '帮我起草一封邮件，告诉对方我明天再回复，收件人还没确定。不要发送。'),
    ('calendar_complete', '请在日历创建候选：2026年10月10日15:00到16:00，Asia/Shanghai时区，标题合成评审，地点会议室A。只生成候选，不执行。'),
    ('calendar_ambiguous', '请安排一个日程，过几天下午找个时间聊聊，结束时间还没定。'),
]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True)


def check(value, schema, path='$'):
    if schema['type'] == 'object':
        if not isinstance(value, dict):
            return f'{path}: expected an object'
        for key in sorted(schema.get('required', [])):
            if key not in value:
                return f'{path}: missing "{key}"'
        for key in sorted(value):
            if key not in schema['properties']:
                if not schema.get('additionalProperties', True):
                    return f'{path}: unexpected property "{key}"'
            else:
                error = check(value[key], schema['properties'][key], path + '.' + key)
                if error:
                    return error
    elif schema['type'] == 'string':
        if not isinstance(value, str):
            return f'{path}: expected a string'
        if len(value) > schema.get('maxLength', 10**9):
            return f'{path}: longer than maxLength'
    else:
        raise RuntimeError('Unverified schema type in this diagnostic')
    if 'enum' in schema and value not in schema['enum']:
        return f'{path}: not one of the enum values'


def unwrap(text):
    text = text.strip()
    if text.startswith('<think>') and '</think>' in text:
        text = text.split('</think>', 1)[1].strip()
    if text.startswith('```'):
        rest = text[3:]
        if rest.startswith(('json', 'JSON')):
            rest = rest[4:]
        if rest.rstrip().endswith('```'):
            return rest.rstrip()[:-3].strip()
    return text


def accept(text, schema):
    raw = unwrap(text)
    if len(raw.encode()) > 16384:
        return None, 'too_large'
    try:
        value = json.loads(raw)
    except ValueError:
        return None, 'it was not valid JSON'
    error = check(value, schema)
    if error:
        return value, f'it does not match the schema ({error})'
    # These questions contain no URLs; this mirrors Host's ordinary URL veto.
    if any(marker in compact(value).lower() for marker in ['https://', 'http://', 'www.']):
        return value, 'it contains a URL'
    return value, None


def main():
    assert not OUT.exists(), 'Use immutable evidence; do not overwrite an earlier run'
    assert CARD.is_file()
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', PORT)) != 0, 'Diagnostic port is occupied'
    source = (ROOT / 'official_muse/app/bundle/main.splash').read_text()
    start = source.index('fn chat_model_config(message){')
    end = source.index('\nfn send_chat()', start)
    config_fn = source[start:end]
    OUT.mkdir(parents=True)
    bundle, state = OUT / 'bundle', OUT / 'card-state'
    bundle.mkdir()
    manifest = {'schema': 1, 'id': 'ai-protocol-probe', 'version': '0.0.1', 'name': 'AI protocol probe',
                'integrity': {'bundle_blake3': '0'*64}, 'capabilities': ['storage']}
    (bundle / 'manifest.json').write_text(compact(manifest))
    questions = compact([{'id': key, 'question': question} for key, question in CASES])
    script = 'let chat_selected_id = "synthetic"\nfn chat_active_candidate(id){return nil}\nfn chat_edit_request(message){return false}\n'
    script += config_fn + '\nlet cases = ' + json.dumps(questions, ensure_ascii=False) + '.parse_json()\nfn ai_dump(){\nlet result = []\n'
    script += 'for case in cases { let config = chat_model_config(case.question) result.push({id: case.id question: case.question config: config}) }\n'
    script += 'fs.write("configs.json",result.to_json())\n}\nstart_timeout(0.1, || ai_dump())\nView{Label{text:"AI config extraction only"}}\n'
    (bundle / 'main.splash').write_text(script)
    (OUT / 'extracted-chat_model_config.splash').write_text(config_fn)
    env = dict(os.environ, MAKEPAD_REMOTE=str(PORT), MAKEPAD_HIDE_WINDOWS='1')
    env.pop('MAKEPAD_FOCUS', None)
    configs = state / 'ai-protocol-probe/configs.json'
    with (OUT / 'card-host.log').open('w') as log:
        process = subprocess.Popen([str(CARD), '--bundle', str(bundle), '--app-data', str(state),
                                    '--allow-unsigned', '--stamp', '--size', '600x700'],
                                   cwd=CARD.parents[2], env=env, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 25
            while not configs.exists():
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError((OUT / 'card-host.log').read_text()[-6000:])
                time.sleep(.1)
            records = json.loads(configs.read_text())
            assert len(records) == 4
            (OUT / 'configs.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
        finally:
            try:
                urlopen(f'http://127.0.0.1:{PORT}/quit', timeout=2).read()
            except OSError:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
    clock = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    results = []
    for record in records:
        config = record['config']
        task = config['task'] + '\n本轮参考时钟UTC：' + clock + '；默认日期时区Asia/Shanghai（UTC+08:00）。资料有明确日期或时区时遵从资料，缺失必要时间则询问用户。'
        task += '\n本轮没有检索到相关全局记忆。不能凭空生成用户或其项目的事实。一般知识问题仍可正常回答。'
        system = "You are one step inside an app on the person's device. The provided user and assistant turns are a genuine conversation in chronological order. Answer the latest user turn using that conversation and the task. You have no tools, browsing or memory beyond the supplied turns."
        system += '\n\nReply with exactly one JSON value that validates against the JSON Schema below: no prose, no Markdown, no code fences. Do not include any URL or web address.'
        system += '\n\nTask:\n' + task + '\n\nJSON Schema:\n' + compact(config['schema'])
        row = {'id': record['id'], 'question': record['question'], 'schema': config['schema'], 'attempts': []}
        note = None
        for attempt in [1, 2]:
            query = record['question']
            if note:
                query += '\n\nYour previous answer was refused: ' + note + '. Answer again with only one JSON value that validates against the schema.'
            request_body = {'model': 'local-default', 'stream': False,
                            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': query}]}
            t0 = time.monotonic()
            request = Request('http://127.0.0.1:8080/v1/chat/completions', data=compact(request_body).encode(), headers={'Content-Type': 'application/json'})
            with urlopen(request, timeout=125) as response:
                response_body = response.read()
                status = response.status
            parsed = json.loads(response_body)
            text = parsed['choices'][0]['message'].get('content', '')
            value, note = accept(text, config['schema'])
            row['attempts'].append({'attempt': attempt, 'http_status': status, 'seconds': time.monotonic()-t0,
                                    'request': request_body, 'raw_response': parsed, 'raw_content': text,
                                    'parsed_output': value, 'protocol_error': note})
            (OUT / (record['id'] + '.json')).write_text(json.dumps(row, ensure_ascii=False, indent=2)+'\n')
            print(compact({'id': record['id'], 'attempt': attempt, 'protocol_error': note, 'raw_content': text}), flush=True)
            if note is None:
                break
        row['protocol_pass'] = note is None
        results.append(row)
    report = {'scope': 'INTERMEDIATE: actual card-host config; direct 8080 wire replay, not Shell model.complete/ledger/full-chain',
              'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'config_function_sha256': hashlib.sha256(config_fn.encode()).hexdigest(),
              'card_host_sha256': hashlib.sha256(CARD.read_bytes()).hexdigest(),
              'reference_clock': clock, 'question_count': 4, 'backend_request_count': sum(len(r['attempts']) for r in results),
              'protocol_pass_count': sum(r['protocol_pass'] for r in results), 'results': results,
              'external_actions': 0, 'agent_kernel_started': False, 'paid_requests': 0,
              'validator': 'Python replay of inspected Host object/string/enum subset; not actual Rust service invocation',
              'minimal_prompt_or_schema_variant_tested': False}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(compact({k:report[k] for k in ['source_sha256','question_count','backend_request_count','protocol_pass_count']}), flush=True)


if __name__ == '__main__':
    main()
