"""Fail-closed accounting for the explicitly authorized MiniMax-only runner.

Reads only isolated ledger/trace and provider fields. No HTTP client, keys,
profile cloning, Host quota writes or actual-bill claims. Root initializes one
shared cost table and uses it for all paid diagnostics and acceptance runs.
"""
import datetime
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import time
from urllib.parse import urlsplit

KIND = 'AUTHORIZED_MODEL_ONLY_SYNTHETIC'
LIMIT_MICRO_CNY = 30_000_000
ORIGINAL_INPUT_MAX = 65536
REPAIR_OUTPUT_MAX = 16384
INPUT_PER_ATTEMPT = 262144
OUTPUT_PER_ATTEMPT = 1_000_000
ATTEMPTS = 2
RESERVE_TOKENS = ATTEMPTS * (INPUT_PER_ATTEMPT + OUTPUT_PER_ATTEMPT)


class PaidPause(RuntimeError):
    """Stop before any further UI send; keep an uncertain reservation."""


def number(value):
    if type(value) is not int or value < 0:
        raise PaidPause('Invalid nonnegative usage counter')
    return value


def upper_micro(tokens):
    # All input+output at the higher standard short-context output price.
    return (number(tokens)*84+9)//10


def request_reserve_micro():
    # MiniMax official standard M3 pricing (2026-10-03): <=512k INPUT
    # tokens uses CNY2.10/M input and CNY8.40/M output. The reviewed byte
    # guard bounds each attempt to 262144 input tokens, including repair.
    # No change to token ceilings, attempts, connection allocations or CNY30.
    if INPUT_PER_ATTEMPT > 512000:
        raise PaidPause('Input reserve no longer fits the verified short-context price')
    return usage_upper_micro(ATTEMPTS*INPUT_PER_ATTEMPT, ATTEMPTS*OUTPUT_PER_ATTEMPT)


def usage_upper_micro(input_tokens, output_tokens):
    return (number(input_tokens)*21+9)//10 + upper_micro(output_tokens)


def request_bounds(original_bytes):
    original_bytes = number(original_bytes)
    if original_bytes > ORIGINAL_INPUT_MAX:
        raise PaidPause('Original request exceeds 65,536-byte pre-send bound; stop before payment')
    repair_bytes = original_bytes + 8 * REPAIR_OUTPUT_MAX + 1024
    if repair_bytes > INPUT_PER_ATTEMPT:
        raise PaidPause('Repair request exceeds 262,144-byte reserve; stop before payment')
    return {'input_byte_upper_bound': original_bytes,
            'original_input_byte_ceiling': ORIGINAL_INPUT_MAX,
            'repair_input_byte_upper_bound': repair_bytes,
            'repair_escape_multiplier': 8, 'repair_output_byte_ceiling': REPAIR_OUTPUT_MAX,
            'repair_framing_bytes': 1024, 'input_token_reserve': INPUT_PER_ATTEMPT}


def input_bound_check(candidate, session, text, host_source, contract):
    """Check the reviewed frozen code and a conservative data superset before send.

    Contract hashes identify inspected code, not a new Host build attestation.
    Root must bind that source directory to the selected frozen Host artifact.
    """
    try:
        source = (candidate / 'bundle/main.splash').read_text()
        for name, digest in contract['app_function_sha256'].items():
            start = source.index('fn '+name+'(')
            end = re.search(r'^fn ', source[start+3:], re.M)
            block = source[start:start+3+end.start()] if end else source[start:]
            if hashlib.sha256(block.encode()).hexdigest() != digest:
                raise ValueError()
        for name, digest in contract['host_file_sha256'].items():
            if hashlib.sha256((host_source / name).read_bytes()).hexdigest() != digest:
                raise ValueError()
        jail = candidate / 'private/apps/muse-goals'
        # The reviewed Splash len() budgets are UTF-8 byte budgets. Whole
        # stored session is a superset, additionally capped by the reviewed
        # 2400 recent + 2600 earlier bytes plus separators/role/header margin.
        history_bytes = min(len(json.dumps(session, ensure_ascii=True).encode()), 5500)
        memory_path = jail / 'memory.json'
        memory = json.loads(memory_path.read_text()) if memory_path.is_file() else {}
        memory_bytes = min(len(json.dumps(memory, ensure_ascii=True).encode()), 2200)
        query_bytes = len(json.dumps(text, ensure_ascii=True).encode())
        # Task focus has a 1600-byte serialized bound even for result counts.
        data_bytes = history_bytes + memory_bytes + query_bytes + 1600
        # Original request only: fixed flat schemas <1024B, task/clock <=2500B,
        # prefixes 2048B and message framing 512B. Repair is bounded separately;
        # Rust Debug escaping of valid JSON property text can exceed 3x.
        overhead = 2500 + 1024 + 2048 + 512
        upper = data_bytes + overhead
        bounds = request_bounds(upper)
        return {'checked_before_send': True, 'data_superset_ascii_json_bytes': data_bytes,
                'history_bytes_upper': history_bytes, 'memory_bytes_upper': memory_bytes,
                'query_ascii_json_bytes': query_bytes, 'task_focus_bytes_upper': 1600,
                'fixed_original_request_overhead_bytes': overhead, **bounds,
                'short_context_ceiling': 512000,
                'basis': 'Reviewed text-only request byte superset; conservative one token per byte plus framing; not an exact tokenizer count'}
    except (OSError, ValueError, KeyError, TypeError):
        raise PaidPause('Frozen input-bound source contract or synthetic data differs; stop before payment') from None


def profile_fields(path):
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
        llm = value['config']['llm']
        primary = llm['primary']
        route = primary['route']
        base = urlsplit(route['base_url'])
        allowed = (primary['family_id'] == 'minimax-cn'
                   and primary['model_id'] == 'MiniMax-M3'
                   and llm.get('fallbacks') == []
                   and route['api_type'] == 'openai'
                   and base.scheme == 'https'
                   and base.hostname in ['api.minimax.cn', 'api.minimaxi.com']
                   and base.port in [None, 443] and base.path.rstrip('/') == '/v1'
                   and not base.username and not base.password
                   and not base.query and not base.fragment)
        if not allowed:
            raise ValueError()
        # Never access/iterate config.env_vars or any key field. Full-file
        # fingerprint detects changes without logging those contents.
        fields = {'family': 'minimax-cn', 'model': 'MiniMax-M3',
                  'base_url': base.geturl(), 'api_type': 'openai'}
        return fields, hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        raise PaidPause('Authorized isolated model profile failed whitelist validation') from None


def timestamp(value):
    if type(value) in [int, float]:
        return float(value)
    try:
        parsed = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed.timestamp()
    except (AttributeError, ValueError, TypeError):
        raise PaidPause('Invalid trace timestamp') from None


def snapshot(ledger_path, activity_path):
    exists = ledger_path.is_file()
    try:
        ledger = json.loads(ledger_path.read_text()) if exists else {
            'day': int(time.time()//86400), 'apps': {}, 'limits': {}}
        app = ledger['apps'].get('muse-goals', {'calls': 0, 'tokens': 0})
        limits = ledger['limits'].get('muse-goals', {})
        tokens_limit = number(limits.get('tokens_per_day', 100000))
        calls_limit = number(limits.get('calls_per_day', 100))
        minute_limit = number(limits.get('per_minute', 6))
        if tokens_limit > 100000 or calls_limit > 100 or minute_limit > 6:
            raise PaidPause('Host quota exceeds its authorized defaults')
        events = json.loads(activity_path.read_text()) if activity_path.is_file() else []
        if not isinstance(events, list):
            raise ValueError()
        model_events = [e for e in events if e.get('kind') == 'model called']
        return {'ledger_exists': exists, 'day': number(ledger['day']),
                'calls': number(app['calls']), 'tokens': number(app['tokens']),
                'tokens_per_day': tokens_limit, 'calls_per_day': calls_limit,
                'per_minute': minute_limit, 'model_event_count': len(model_events)}
    except (OSError, ValueError, KeyError, TypeError):
        raise PaidPause('Isolated Host ledger or activity evidence is unreadable') from None


def usage_evidence(before, after, trace, text, session_id, user_at, is_model, expected_goal_id=''):
    if before['day'] != after['day']:
        raise PaidPause('UTC ledger day changed; usage attribution unknown')
    calls, tokens = after['calls']-before['calls'], after['tokens']-before['tokens']
    events = after['model_event_count']-before['model_event_count']
    if min(calls, tokens, events) < 0:
        raise PaidPause('Ledger or event counters decreased; usage unknown')
    delta = {'calls': calls, 'tokens': tokens, 'model_called_events': events}
    if not is_model:
        if calls or tokens or events:
            raise PaidPause('Local setup/cancellation caused a model increment')
        return {'known_usage': True, 'local_zero_increment': True, 'delta': delta,
                'upper_micro_cny': 0}
    try:
        expected_sha = hashlib.sha256(text.encode()).hexdigest()
        meta, usage, budget = trace['meta'], trace['meta']['usage'], trace['meta']['budget']
        attempts = number(meta['attempts'])
        input_tokens, output_tokens = number(usage['input_tokens']), number(usage['output_tokens'])
        request_at, response_at = timestamp(trace['request_at']), timestamp(trace['response_at'])
        valid = (trace['schema'] == 1 and trace['known_usage'] is True
                 and trace['current'] is True and trace['is_ok'] is True
                 and usage['estimated'] is False and trace['query_sha256'] == expected_sha
                 and trace['session_id'] == session_id and trace['goal_id'] == expected_goal_id
                 and user_at-2 <= request_at <= response_at <= time.time()+2
                 and calls == 1 and events == 1 and 1 <= attempts <= ATTEMPTS
                 and tokens == input_tokens+output_tokens and tokens > 0
                 and input_tokens <= attempts*INPUT_PER_ATTEMPT
                 and output_tokens <= attempts*OUTPUT_PER_ATTEMPT
                 and number(budget['calls_today']) == after['calls']
                 and number(budget['tokens_today']) == after['tokens']
                 and number(budget['tokens_per_day']) <= 100000)
        if not valid:
            raise ValueError()
        return {'known_usage': True, 'delta': delta, 'attempts': attempts,
                'expected_goal_id': expected_goal_id,
                'input_tokens': input_tokens, 'output_tokens': output_tokens,
                'estimated': False, 'query_sha256': expected_sha,
                'request_at': request_at, 'response_at': response_at,
                'upper_micro_cny': usage_upper_micro(input_tokens, output_tokens)}
    except (ValueError, KeyError, TypeError):
        raise PaidPause('Missing, estimated, stale or inconsistent Host usage; cost unknown') from None


class CostTable:
    """One global CNY30 file; never create/reset an absent paid history."""
    def __init__(self, path):
        self.path = Path(path).resolve()
        if not self.path.is_file():
            raise PaidPause('Root must initialize the shared paid cost table first')
        self.change(lambda data: None)

    def change(self, operation):
        with self.path.with_suffix(self.path.suffix+'.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                data = json.loads(self.path.read_text())
                if (data['schema'] != 1 or data['currency'] != 'CNY'
                        or data['budget_id'] != 'minimax-authorized-20261003'
                        or not 0 < number(data['limit_micro_cny']) <= LIMIT_MICRO_CNY
                        or not isinstance(data['entries'], list)):
                    raise ValueError()
                for entry in data['entries']:
                    if entry['status'] not in ['ALLOCATED', 'RESERVED', 'KNOWN_UPPER_BOUND', 'UNKNOWN']:
                        raise ValueError()
                    number(entry['upper_micro_cny'])
                allocations = sum(e['upper_micro_cny'] for e in data['entries']
                                  if e['id'] == 'official-connection-reserve' and e['status'] == 'ALLOCATED')
                if allocations < 2_300_000:
                    raise PaidPause('Root must retain the CNY2.30 official-connection allocation')
                result = operation(data)
                tmp = self.path.with_suffix(self.path.suffix+'.tmp')
                tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
                os.replace(tmp, self.path)
                return result
            except (OSError, ValueError, KeyError, TypeError):
                raise PaidPause('Global paid accounting table invalid; never reset it') from None
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def reserve(self, run_id, case_id):
        def operation(data):
            if any(e['status'] in ['RESERVED', 'UNKNOWN'] for e in data['entries']):
                raise PaidPause('Outstanding/unknown paid request; stop all further paid sends')
            amount = request_reserve_micro()
            if sum(e['upper_micro_cny'] for e in data['entries'])+amount > data['limit_micro_cny']:
                raise PaidPause('Global CNY30 cap cannot cover the next worst-case reservation')
            key = run_id+':'+case_id
            if any(e['id'] == key for e in data['entries']):
                raise PaidPause('Paid case already accounted; do not replay it')
            data['entries'].append({'id': key, 'run_id': run_id, 'case_id': case_id,
                                    'status': 'RESERVED', 'upper_micro_cny': amount,
                                    'reserve_tokens': RESERVE_TOKENS, 'at': time.time()})
            return key
        return self.change(operation)

    def settle(self, key, proof=None, reason=None):
        def operation(data):
            entry = next(e for e in data['entries'] if e['id'] == key)
            if entry['status'] != 'RESERVED':
                raise PaidPause('Reservation is not pending; cannot settle twice')
            if proof is not None and (proof.get('known_usage') is not True or number(proof['upper_micro_cny']) > entry['upper_micro_cny']):
                raise PaidPause('Usage proof cannot exceed or invalidate its reservation')
            if proof is None:
                entry['status'] = 'UNKNOWN'
                entry['reason'] = reason or 'No reliable usage proof'
            else:
                entry['status'] = 'KNOWN_UPPER_BOUND'
                entry['upper_micro_cny'] = number(proof['upper_micro_cny'])
                entry['usage_proof'] = proof
            entry['settled_at'] = time.time()
            return dict(entry)
        return self.change(operation)


class PaidGuard:
    def __init__(self, candidate, cost_path, run_id):
        self.candidate, self.run_id = Path(candidate), run_id
        self.profile = self.candidate / 'private/home/octos-home/.octos/profiles/_main.json'
        self.fields, self.profile_sha = profile_fields(self.profile)
        self.ledger = self.candidate / 'private/apps/.host/model/ledger.json'
        self.jail = self.candidate / 'private/apps/muse-goals'
        if any((self.candidate / ('private/apps/.host/'+name)).exists() for name in ['mail', 'calendar']):
            raise PaidPause('Authorized candidate must have no Mail/Calendar account state')
        self.table, self.pending = CostTable(cost_path), None
        self.last_observation = None

    def check_profile(self):
        _, digest = profile_fields(self.profile)
        if digest != self.profile_sha:
            raise PaidPause('Model profile changed during acceptance; stop immediately')

    def begin(self, case_id):
        self.last_observation = None
        self.check_profile()
        before = snapshot(self.ledger, self.jail / 'activity.json')
        if before['tokens'] >= before['tokens_per_day'] or before['calls'] >= before['calls_per_day']:
            raise PaidPause('Default Host daily quota exhausted; do not raise it')
        self.pending = self.table.reserve(self.run_id, case_id)
        return before

    def finish(self, before, text, session_id, user_at, is_model, expected_goal_id=''):
        self.check_profile()
        after = snapshot(self.ledger, self.jail / 'activity.json')
        self.last_observation = {'before': before, 'after': after, 'known_usage': False}
        trace_path = self.jail / 'model-last-response.json'
        try:
            trace = json.loads(trace_path.read_text()) if is_model else None
        except (OSError, ValueError):
            raise PaidPause('Official callback trace missing or unreadable; cost unknown') from None
        self.last_observation['trace'] = trace
        proof = usage_evidence(before, after, trace, text, session_id, user_at, is_model, expected_goal_id)
        accounting = self.table.settle(self.pending, proof)
        self.pending = None
        return {'before': before, 'after': after, 'trace': trace,
                'usage_proof': proof, 'global_accounting': accounting,
                'billing_note': 'Conservative tokens upper bound, not an actual invoice'}

    def unknown(self):
        if self.pending is not None:
            self.table.settle(self.pending, reason='Interrupted or unreliable evidence; actual cost unknown')
            self.pending = None
