"""Synthetic-only checks: no real profile, UI, network or paid inference."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

from ai_paid_guard import (CostTable, PaidGuard, PaidPause, RESERVE_TOKENS,
                           profile_fields, snapshot, upper_micro, usage_evidence, input_bound_check,
                           request_bounds, INPUT_PER_ATTEMPT)
from ai_paid_guard import request_reserve_micro, usage_upper_micro


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def table_seed():
    return {'schema': 1, 'currency': 'CNY', 'budget_id': 'minimax-authorized-20261003',
            'limit_micro_cny': 30_000_000, 'entries': [
                {'id': 'official-connection-reserve', 'status': 'ALLOCATED',
                 'upper_micro_cny': 2_300_000, 'purpose': 'Conservative allocation, not actual billing'}]}


class PaidOffline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.root/'private/home/octos-home/.octos/profiles/_main.json'
        self.profile_data = {'config': {'llm': {'primary': {
            'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3',
            'route': {'base_url': 'https://api.minimax.cn/v1', 'api_type': 'openai'}},
            'fallbacks': []}, 'env_vars': {'FAKE_OFFLINE_ONLY': 'opaque-fixture-sentinel'}}}
        write(self.profile, self.profile_data)
        self.table = self.root/'costs.json'
        write(self.table, table_seed())
        self.now = time.time()
        self.before = {'day': 20729, 'calls': 0, 'tokens': 0, 'model_event_count': 0}
        self.after = {'day': 20729, 'calls': 1, 'tokens': 30, 'model_event_count': 1}
        self.text = '合成离线题'
        self.trace = {'schema': 1, 'request_at': self.now-1, 'response_at': self.now,
                      'query_sha256': hashlib.sha256(self.text.encode()).hexdigest(),
                      'session_id': 'synthetic', 'goal_id': '', 'current': True,
                      'is_ok': True, 'known_usage': True, 'meta': {
                          'class': 'strong', 'requested': 'fast', 'attempts': 1,
                          'usage': {'input_tokens': 10, 'output_tokens': 20, 'estimated': False},
                          'budget': {'calls_today': 1, 'tokens_today': 30, 'tokens_per_day': 100000}}}

    def proof(self, trace=None, after=None):
        return usage_evidence(self.before, after or self.after,
                              trace or self.trace, self.text, 'synthetic', self.now-2, True)

    def test_explicit_goal_binding_does_not_accept_another_task(self):
        trace = copy.deepcopy(self.trace)
        trace['goal_id'] = 'synthetic-goal-a'
        with self.assertRaises(PaidPause):
            self.proof(trace)
        proof = usage_evidence(self.before, self.after, trace, self.text,
                               'synthetic', self.now-2, True, 'synthetic-goal-a')
        self.assertEqual(proof['expected_goal_id'], 'synthetic-goal-a')
        with self.assertRaises(PaidPause):
            usage_evidence(self.before, self.after, trace, self.text,
                           'synthetic', self.now-2, True, 'synthetic-goal-b')

    def test_official_whitelist_and_opaque_env(self):
        fields, digest = profile_fields(self.profile)
        self.assertEqual(fields['model'], 'MiniMax-M3')
        self.assertEqual(len(digest), 64)
        self.assertNotIn('opaque-fixture-sentinel', json.dumps(fields))

    def test_wrong_routes_fallback_model_and_missing_fallback_refused(self):
        for base in ['http://api.minimax.cn/v1', 'https://api.minimax.cn.evil/v1',
                     'https://user:fixture@api.minimax.cn/v1', 'https://api.minimax.cn/v1?key=fixture',
                     'https://127.0.0.1/v1', 'https://api.minimax.cn:8080/v1']:
            value = copy.deepcopy(self.profile_data)
            value['config']['llm']['primary']['route']['base_url'] = base
            write(self.profile, value)
            with self.subTest(base=base), self.assertRaises(PaidPause):
                profile_fields(self.profile)
        for mutate in ['model', 'fallback', 'missing']:
            value = copy.deepcopy(self.profile_data)
            if mutate == 'model': value['config']['llm']['primary']['model_id'] = 'local-default'
            if mutate == 'fallback': value['config']['llm']['fallbacks'] = [{}]
            if mutate == 'missing': del value['config']['llm']['fallbacks']
            write(self.profile, value)
            with self.subTest(mutate=mutate), self.assertRaises(PaidPause):
                profile_fields(self.profile)

    def test_reliable_usage_matches_independent_counters(self):
        proof = self.proof()
        self.assertTrue(proof['known_usage'])
        self.assertEqual(proof['upper_micro_cny'], 189)

    def test_separate_role_pricing_keeps_worst_usage_within_reserve(self):
        self.assertEqual(usage_upper_micro(524288, 2000000), request_reserve_micro())
        self.assertEqual(usage_upper_micro(1, 1), 12)
        with self.assertRaises(PaidPause): usage_upper_micro(-1, 10)

    def test_unknown_estimated_stale_mismatch_and_day_roll_stop(self):
        variants = []
        for key, value in [('known_usage', False), ('current', False), ('is_ok', False),
                           ('query_sha256', 'bad'), ('session_id', 'wrong'), ('request_at', self.now-50)]:
            trace = copy.deepcopy(self.trace); trace[key] = value; variants.append(trace)
        trace = copy.deepcopy(self.trace); trace['meta']['usage']['estimated'] = True; variants.append(trace)
        trace = copy.deepcopy(self.trace); del trace['meta']; variants.append(trace)
        trace = copy.deepcopy(self.trace); trace['meta']['budget']['tokens_today'] = 31; variants.append(trace)
        trace = copy.deepcopy(self.trace); trace['meta']['usage']['input_tokens'] = True; variants.append(trace)
        for trace in variants:
            with self.subTest(trace_variant=list(trace)), self.assertRaises(PaidPause): self.proof(trace)
        for field, value in [('day', 20730), ('calls', 2), ('tokens', 31), ('model_event_count', 0)]:
            after = dict(self.after); after[field] = value
            with self.subTest(counter=field), self.assertRaises(PaidPause): self.proof(after=after)

    def test_local_mechanisms_require_zero_increment(self):
        proof = usage_evidence(self.before, self.before, None, self.text, 'synthetic', self.now, False)
        self.assertEqual(proof['upper_micro_cny'], 0)
        with self.assertRaises(PaidPause):
            usage_evidence(self.before, self.after, None, self.text, 'synthetic', self.now, False)

    def test_global_reserve_known_settlement_and_no_duplicate(self):
        table = CostTable(self.table)
        key = table.reserve('run', 'S01')
        data = json.loads(self.table.read_text())
        self.assertEqual(data['entries'][-1]['upper_micro_cny'], request_reserve_micro())
        with self.assertRaises(PaidPause): table.reserve('other', 'D01')
        table.settle(key, self.proof())
        with self.assertRaises(PaidPause): table.reserve('run', 'S01')
        self.assertEqual(json.loads(self.table.read_text())['entries'][0]['upper_micro_cny'], 2_300_000)

    def test_unknown_retains_reservation_and_blocks_all_runs(self):
        table = CostTable(self.table); key = table.reserve('run', 'S01'); table.settle(key)
        entry = json.loads(self.table.read_text())['entries'][-1]
        self.assertEqual(entry['status'], 'UNKNOWN')
        self.assertEqual(entry['upper_micro_cny'], request_reserve_micro())
        with self.assertRaises(PaidPause): CostTable(self.table).reserve('new-run', 'E02')

    def test_cap_missing_history_and_connection_allocation(self):
        data = table_seed(); data['entries'].append({'id': 'other-budget', 'status': 'ALLOCATED', 'upper_micro_cny': 26_000_000})
        write(self.table, data)
        with self.assertRaises(PaidPause): CostTable(self.table).reserve('run', 'S01')
        with self.assertRaises(PaidPause): CostTable(self.root/'missing.json')
        data = table_seed(); data['entries'] = []; write(self.table, data)
        with self.assertRaises(PaidPause): CostTable(self.table)

    def test_profile_changes_and_account_state_refused(self):
        guard = PaidGuard(self.root, self.table, 'run')
        value = copy.deepcopy(self.profile_data); value['name'] = 'changed'
        write(self.profile, value)
        with self.assertRaises(PaidPause): guard.check_profile()
        write(self.profile, self.profile_data)
        (self.root/'private/apps/.host/mail').mkdir(parents=True)
        with self.assertRaises(PaidPause): PaidGuard(self.root, self.table, 'run')

    def test_context_reserve_and_pre_send_byte_guard(self):
        self.assertEqual(RESERVE_TOKENS, 2_524_288)
        self.assertEqual(upper_micro(RESERVE_TOKENS), 21_204_020)
        self.assertEqual(request_reserve_micro(), 17_901_005)
        source = 'fn synthetic(){ return "fixture" }\n'
        bundle = self.root/'bundle/main.splash'
        bundle.parent.mkdir(); bundle.write_text(source)
        host = self.root/'sdk'; host.mkdir(); (host/'fixture.rs').write_text('offline source fixture')
        contract = {'app_function_sha256': {'synthetic': hashlib.sha256(source.encode()).hexdigest()},
                    'host_file_sha256': {'fixture.rs': hashlib.sha256((host/'fixture.rs').read_bytes()).hexdigest()}}
        proof = input_bound_check(self.root, {'messages': []}, self.text, host, contract)
        self.assertLessEqual(proof['input_byte_upper_bound'], 65536)
        self.assertLessEqual(proof['repair_input_byte_upper_bound'], INPUT_PER_ATTEMPT)
        with self.assertRaises(PaidPause):
            input_bound_check(self.root, {'messages': ['x'*24000]}, 'x'*65536, host, contract)
        (host/'fixture.rs').write_text('changed')
        with self.assertRaises(PaidPause):
            input_bound_check(self.root, {'messages': []}, self.text, host, contract)

    def test_settlement_cannot_increase_reserved_cost(self):
        table = CostTable(self.table); key = table.reserve('run', 'S01')
        with self.assertRaises(PaidPause):
            table.settle(key, {'known_usage': True, 'upper_micro_cny': request_reserve_micro()+1})
        with self.assertRaises(PaidPause):
            table.settle(key, {'known_usage': False, 'upper_micro_cny': 0})
        self.assertEqual(json.loads(self.table.read_text())['entries'][-1]['status'], 'RESERVED')

    def test_control_character_fixture_and_separate_repair_ceiling(self):
        # Synthetic reviewed escaping example, not a claim of executing Rust.
        # DEL is legal unescaped JSON text but its Debug representation is longer.
        for character, escaped in [('\x7f', '\\u{7f}'), ('\u200b', '\\u{200b}')]:
            key = character * 2000
            raw = json.dumps({key: 'fixture'}, ensure_ascii=False)
            self.assertIn(key, json.loads(raw))
            fixture_debug_bytes = len((escaped * 2000).encode())
            if character == '\x7f':
                self.assertGreater(fixture_debug_bytes, 3 * len(raw.encode()))
            proof = request_bounds(65536)
            self.assertEqual(proof['repair_input_byte_upper_bound'], 197632)
            self.assertLess(fixture_debug_bytes, 8 * proof['repair_output_byte_ceiling'])
            self.assertLessEqual(proof['repair_input_byte_upper_bound'], 262144)
        with self.assertRaises(PaidPause): request_bounds(65537)
        with self.assertRaises(PaidPause): request_bounds(-1)
        with self.assertRaises(PaidPause): request_bounds(True)

    def test_default_quota_not_raised(self):
        ledger, activity = self.root/'ledger.json', self.root/'activity.json'
        write(ledger, {'day': 20729, 'apps': {'muse-goals': {'calls': 1, 'tokens': 30}}, 'limits': {}})
        write(activity, [{'kind': 'model called'}])
        self.assertEqual(snapshot(ledger, activity)['tokens_per_day'], 100000)
        write(ledger, {'day': 20729, 'apps': {}, 'limits': {'muse-goals': {'tokens_per_day': 100001}}})
        with self.assertRaises(PaidPause): snapshot(ledger, activity)


if __name__ == '__main__':
    unittest.main(verbosity=2)
