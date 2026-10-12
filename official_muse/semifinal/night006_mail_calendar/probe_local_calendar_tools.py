#!/usr/bin/env python3
"""Inspect genuine bundled Qwen tool output; never executes a Calendar tool."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resources', required=True, type=Path)
    parser.add_argument('--tools', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--jinja', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False, mode=0o700)
    runner = args.resources / 'local-model/llama/llama-server'
    weight = args.resources / 'local-model/qwen2.5-0.5b-instruct-q4_0.gguf'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    alias = 'Qwen2.5-0.5B-Instruct-Q4_0-offline'
    command = [str(runner), '--model', str(weight), '--host', '127.0.0.1', '--port', str(port),
               '--alias', alias, '--ctx-size', '4096', '--parallel', '1', '--threads', '4',
               '--gpu-layers', '0', '--offline', '--no-webui', '--temp', '0.2', '--reasoning', 'off']
    if args.jinja:
        command.append('--jinja')
    declared = json.loads(args.tools.read_text())['tools']
    tools = [{'type': 'function', 'function': {'name': item['name'].replace('.', '_'),
              'description': item['description'], 'parameters': item['input_schema']}} for item in declared]
    request = {'model': alias, 'stream': False, 'max_tokens': 200, 'temperature': 0.2,
               'messages': [
                   {'role': 'system', 'content': 'You are a calendar assistant. Today is 2026-10-13 in Asia/Shanghai. Use the supplied Calendar tools for actual results; do not invent events.'},
                   {'role': 'user', 'content': '查询2026年10月13日的日程，按开始时间列出。请调用calendar_events，不要直接编造结果。'}],
               'tools': tools}
    (args.out / 'request.json').write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
    report = {'level': 'REAL_LOCAL_MODEL_HTTP_TOOLS_NO_TOOL_EXECUTION', 'status': 'RUNNING',
              'command': command, 'runner_sha256': sha(runner), 'weight_sha256': sha(weight),
              'tool_manifest_sha256': sha(args.tools), 'jinja': args.jinja,
              'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    process = None
    try:
        with (args.out / 'llama-server.txt').open('wb') as log:
            process = subprocess.Popen(command, cwd=args.out, stdout=log, stderr=subprocess.STDOUT,
                env={'PATH': '/usr/bin:/bin', 'HOME': str(args.out.resolve()), 'TMPDIR': '/tmp'})
            base = f'http://127.0.0.1:{port}'
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f'Local runner exited: {process.returncode}')
                try:
                    with urlopen(base + '/health', timeout=1) as response:
                        report['health'] = json.load(response)
                    break
                except Exception:
                    time.sleep(.2)
            else:
                raise TimeoutError('Local runner readiness timeout')
            start = time.monotonic()
            http = Request(base + '/v1/chat/completions', data=json.dumps(request).encode(),
                           headers={'Content-Type': 'application/json'}, method='POST')
            try:
                with urlopen(http, timeout=90) as response:
                    body = json.load(response)
                    report['http_status'] = response.status
            except HTTPError as error:
                body = json.loads(error.read())
                report['http_status'] = error.code
            (args.out / 'response.json').write_text(json.dumps(body, ensure_ascii=False, indent=2) + '\n')
            report['request_seconds'] = round(time.monotonic() - start, 3)
            if report['http_status'] == 200:
                choice = body['choices'][0]
                calls = choice['message'].get('tool_calls') or []
                report['tool_call_names'] = [call['function']['name'] for call in calls]
                report['status'] = 'TOOL_CALL_RETURNED' if 'calendar_events' in report['tool_call_names'] else 'NO_EXPECTED_TOOL_CALL'
                selected = [call for call in calls if call['function']['name'] == 'calendar_events']
                if len(selected) == 1:
                    arguments = json.loads(selected[0]['function']['arguments'])
                    report['arguments'] = arguments
                    report['requested_day_matched'] = str(arguments.get('from', '')).startswith('2026-10-13') and (
                        str(arguments.get('to', '')).startswith('2026-10-14') or
                        str(arguments.get('to', '')).startswith('2026-10-13T23:59'))
                    if not report['requested_day_matched']:
                        report['status'] = 'TOOL_CALL_SEMANTICS_FAIL'
                report['finish_reason'] = choice.get('finish_reason')
                report['usage'] = body.get('usage')
            else:
                report['status'] = 'HTTP_TOOLS_REJECTED'
                report['error'] = body
    except Exception as error:
        report.update(status='ERROR', error=str(error))
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['status'] == 'TOOL_CALL_RETURNED' and report.get('requested_day_matched') else 1


if __name__ == '__main__':
    raise SystemExit(main())
