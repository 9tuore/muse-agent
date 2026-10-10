"""Portable parser unit tests. All inputs here are SYNTHETIC, not live evidence."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from check_host_log import analyze
from check_failure_artifacts import check

class LogChecks(unittest.TestCase):
    def classify(self, source, log, report=None):
        return analyze(source, [('test', log)], report)['cases'][0]['classifications']

    def test_synthetic_refusal_does_not_claim_loaded_artifact(self):
        result = self.classify(b'SYNTHETIC candidate payload',
            '[SPLASH] eval: 717 bytes preserve=false view=true')
        self.assertIn('PAYLOAD_NOT_OBSERVED', result)
        self.assertNotIn('SCRIPT_TIME_BUDGET_EXCEEDED', result)
        # Old Host does not log the reason; do not invent compatibility certainty.
        self.assertNotIn('COMPATIBILITY_REFUSAL', result)

    def test_synthetic_time_budget_failure(self):
        result = self.classify(b'abc',
            'splash: script time budget exceeded\n'
            '[SPLASH] eval: 3 bytes preserve=false view=false')
        self.assertIn('SCRIPT_TIME_BUDGET_EXCEEDED', result)
        self.assertIn('PAYLOAD_EVALUATED_WITHOUT_VIEW', result)

    def test_explicit_missing_api(self):
        self.assertIn('COMPATIBILITY_REFUSAL', self.classify(b'abc',
            'card-host refused this bundle: this host does not implement required APIs: mail.compose@1'))

    def test_equal_size_different_sha(self):
        report = {'source_sha256': hashlib.sha256(b'xyz').hexdigest()}
        self.assertIn('ARTIFACT_SHA_MISMATCH', self.classify(b'abc',
            '[SPLASH] eval: 3 bytes preserve=false view=true', report))

    def test_window_and_admission_only(self):
        self.assertIn('PAYLOAD_NOT_OBSERVED', self.classify(b'abc',
            'card-host: window sized 1100x740\ncard-host: rc18 admitted'))

    def test_other_error_even_with_view(self):
        self.assertIn('OTHER_RUNTIME_ERROR', self.classify(b'abc',
            '[SPLASH] eval: 3 bytes preserve=false view=true\n[E] bad script'))

    def test_empty_harness_checks(self):
        report = {'source_sha256': hashlib.sha256(b'abc').hexdigest(), 'cases': [{'checks': {}}]}
        self.assertIn('HARNESS_CASE_INCOMPLETE_OR_FAILED', self.classify(b'abc',
            '[SPLASH] eval: 3 bytes preserve=false view=true', report))

    def test_matching_eval_is_only_log_observation(self):
        result = analyze(b'abc', [('test', '[SPLASH] eval: 3 bytes preserve=false view=true')])
        self.assertEqual(result['cases'][0]['classifications'], ['PAYLOAD_BYTES_AND_VIEW_OBSERVED'])
        self.assertIsNone(result['report_source_sha_matches'])
        self.assertIn('no Mail delivery', result['boundary'])

    def test_missing_artifacts_are_not_tested(self):
        with tempfile.TemporaryDirectory() as directory:
            result, code = check(Path(directory), 'refusal')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'NOT_TESTED')
        self.assertEqual(len(result['missing_evidence']), 2)

    def test_synthetic_artifact_without_expected_failure_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'bundle').mkdir()
            (root / 'bundle/main.splash').write_bytes(b'abc')
            (root / 'runtime-0.log').write_text('[SPLASH] eval: 3 bytes preserve=false view=true')
            result, code = check(root, 'timeout')
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'FAIL_EXPECTED_FAILURE_NOT_FOUND')


if __name__ == '__main__':
    unittest.main()
