import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

import audit
import observe_owned


class ToolsTests(unittest.TestCase):
    def test_actual_owner_path_is_not_truncated_ps_comm(self):
        row = observe_owned.read_pid(os.getpid())
        self.assertTrue(Path(row['executable']).is_file())
        self.assertGreater(len(row['executable']), 16)
        self.assertTrue(row['started'])

    def test_exit_is_not_zero_usage_or_success(self):
        with patch('observe_owned.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', '')):
            self.assertIsNone(observe_owned.read_pid(12345))

    def test_negative_usage_is_rejected(self):
        with self.assertRaises(AssertionError):
            observe_owned.summarize([dict(rss_kib=-1, cpu_percent_ps=0, elapsed_seconds=0)])

    def test_pending_startup_cannot_pass_twenty(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / 'result.json').write_text(json.dumps(dict(launches=[], requested_repetitions=20)))
            with self.assertRaises(AssertionError):
                audit.startup(directory)

    def test_stamped_source_is_distinct_and_tamper_is_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            source = directory / 'source.splash'
            source.write_text('Label{text: "Muse · 0.3.27-rc18"}\n')
            candidate = directory / 'candidate'
            readable = candidate / 'readable-bundle'
            bundle = candidate / 'bundle'
            legacy = directory / 'legacy'
            for p in [readable, bundle, legacy]: p.mkdir(parents=True)
            (readable / 'main.splash').write_text('Label{text: "Muse · 0.4.0-rc7"}\n')
            (bundle / 'main.splash').write_text('// synthetic signed layer\nLabel{text: "Muse · 0.4.0-rc7"}\n')
            (bundle / 'manifest.json').write_text(json.dumps(dict(version='0.4.0-rc7')))
            (legacy / 'main.splash').write_text('legacy fixture')
            (legacy / 'manifest.json').write_text(json.dumps(dict(version='0.3.27-rc17')))
            (candidate / 'bundle-identity.json').write_text(json.dumps(dict(version='0.4.0-rc7',
                upstream_source_sha256=audit.SHA(source), transform=dict(source_sha256=audit.SHA(readable / 'main.splash'),
                artifact_sha256=audit.SHA(bundle / 'main.splash')))))
            self.assertEqual(audit.identities(source, candidate, legacy)['status'], 'PASS')
            (bundle / 'main.splash').write_text('tampered fixture')
            self.assertEqual(audit.identities(source, candidate, legacy)['status'], 'FAIL')

    def test_actual_passive_sampler_on_only_this_test_process(self):
        owner = observe_owned.read_pid(os.getpid())
        self.assertIsNotNone(owner)
        executable = Path(owner['executable']).resolve()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'observation.json'
            deadline = (datetime.now(timezone.utc) + timedelta(seconds=20)).isoformat()
            result = subprocess.run(['python3', '-B', str(Path(observe_owned.__file__)), '--pid', str(os.getpid()),
                '--executable', str(executable), '--sha256', hashlib.sha256(executable.read_bytes()).hexdigest(),
                '--duration', '2', '--interval', '1', '--deadline', deadline, '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            self.assertEqual(data['status'], 'OBSERVED_NOT_FUNCTIONAL_SOAK')
            self.assertGreaterEqual(data['summary']['samples'], 2)
            self.assertEqual(data['owner_pid'], os.getpid())

    def test_lost_owner_verification_is_preserved_as_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executable = directory / 'synthetic-executable'
            executable.write_bytes(b'not an executed program')
            out = directory / 'observation.json'
            owner = dict(executable=str(executable), started='fixture birth', cpu_percent_ps=0, rss_kib=1)
            args = ['observe_owned.py', '--pid', '12345', '--executable', str(executable),
                    '--sha256', hashlib.sha256(executable.read_bytes()).hexdigest(), '--duration', '2',
                    '--interval', '1', '--deadline', (datetime.now(timezone.utc)+timedelta(seconds=20)).isoformat(),
                    '--out', str(out)]
            with patch.object(sys, 'argv', args), patch('observe_owned.read_pid', side_effect=[owner, RuntimeError('fixture')]):
                self.assertEqual(observe_owned.main(), 1)
            self.assertEqual(json.loads(out.read_text())['status'], 'OWNER_UNVERIFIABLE')
            self.assertIsNone(json.loads(out.read_text())['summary'])


if __name__ == '__main__':
    unittest.main()
