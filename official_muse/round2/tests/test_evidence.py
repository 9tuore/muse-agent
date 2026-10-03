import importlib.util
import io
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('evidence', Path(__file__).parents[1] / 'evidence.py')
evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evidence)


class EvidenceTest(unittest.TestCase):
    def test_stale_claim_cannot_pass(self):
        candidate = dict(muse_commit='a'*40, bundle_version='0.2.14', octosense_commit=None,
                         octosense_source_sha256='c'*64, apphub_commit='b'*40,
                         host_extension_commit='d'*40, bundle_blake3='e'*64, host_executable_sha256='f'*64)
        entry = dict(candidate, id='sample', feature='C06', test_time='2026-10-02T16:00:00+08:00',
                     environment='synthetic', test_kind='UNIT', result='PASS', evidence_files=['proof.json'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'proof.json').write_text('{}')
            self.assertEqual(evidence.evaluate(entry, candidate, root), 'PASS')
            for field in evidence.IDENTITY + ('octosense_source_sha256', 'bundle_blake3', 'host_executable_sha256'):
                changed = dict(entry, **{field: 'older'})
                self.assertEqual(evidence.evaluate(changed, candidate, root), 'STALE_EVIDENCE', field)
            self.assertEqual(evidence.evaluate(dict(entry, bundle_version='0.2.8'), candidate, root), 'STALE_EVIDENCE')
            self.assertEqual(evidence.evaluate(dict(entry, test_kind='LIVE'), candidate, root), 'INVALID_EVIDENCE')
            self.assertEqual(evidence.evaluate(dict(entry, evidence_files=['absent']), candidate, root), 'MISSING_EVIDENCE')

    def test_changed_product_bytes_are_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root/'official_muse/app/bundle'
            bundle.mkdir(parents=True)
            manifest = {'version':'0.2.15','integrity':{'bundle_blake3':'abc'},'capabilities':['storage']}
            (bundle/'manifest.json').write_text(json.dumps(manifest))
            (bundle/'main.splash').write_text('original')
            candidate = {'bundle_version':'0.2.15','bundle_blake3':'abc',
                         'bundle_files_sha256':{'main.splash':hashlib.sha256(b'original').hexdigest()},
                         'manifest_semantic_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
            self.assertTrue(evidence.candidate_matches_files(candidate,root))
            (bundle/'unexpected.splash').write_text('extra')
            self.assertFalse(evidence.candidate_matches_files(candidate,root))
            (bundle/'unexpected.splash').unlink()
            (bundle/'main.splash').write_text('modified')
            self.assertFalse(evidence.candidate_matches_files(candidate,root))
            (bundle/'main.splash').write_text('original')
            manifest['capabilities'].append('mail')
            (bundle/'manifest.json').write_text(json.dumps(manifest))
            self.assertFalse(evidence.candidate_matches_files(candidate,root))

    def test_missing_or_corrupt_manifest_does_not_match(self):
        candidate = {'bundle_version': '0.2.16', 'bundle_blake3': 'abc'}
        cases = (None, b'{', b'\xff', b'null', b'[]', b'{}',
                 b'{"version":"0.2.16"}',
                 b'{"version":"0.2.16","integrity":null}',
                 b'{"version":"0.2.16","integrity":[]}',
                 b'{"version":"0.2.16","integrity":{}}')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / 'official_muse/app/bundle'
            bundle.mkdir(parents=True)
            for content in cases:
                with self.subTest(content=content):
                    if content is not None:
                        (bundle / 'manifest.json').write_bytes(content)
                    self.assertFalse(evidence.candidate_matches_files(candidate, root))

    def test_main_missing_id_is_invalid_even_when_candidate_is_stale(self):
        entry = {field: 'synthetic' for field in evidence.FIELDS - {'id'}}
        entry.update(test_kind='UNIT', result='PASS', evidence_files=['proof.json'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_file = root / 'candidate.json'
            index_file = root / 'index.json'
            candidate_file.write_text('{}')
            index_file.write_text(json.dumps({'entries': [entry]}))
            argv = ['evidence.py', str(index_file), '--candidate', str(candidate_file), '--root', str(root)]
            for product_current in (True, False):
                with self.subTest(product_current=product_current), \
                     patch('sys.argv', argv), \
                     patch.object(evidence, 'candidate_matches_files', return_value=product_current), \
                     patch('sys.stdout', new_callable=io.StringIO) as output:
                    self.assertEqual(evidence.main(), 1)
                    self.assertEqual(json.loads(output.getvalue()), [
                        {'id': None, 'declared': 'PASS', 'effective': 'INVALID_EVIDENCE'}])

    def test_previous_016_candidate_is_stale_for_017_cli(self):
        candidate = dict(muse_commit='72e37240d53c045b57570d6b9178ff9980a83c8e',
                         bundle_version='0.2.17', bundle_blake3='synthetic-current',
                         octosense_commit='c'*40, apphub_commit='b'*40, host_extension_commit='d'*40)
        entry = dict(candidate, id='current', feature='C06', test_time='2026-10-02T17:00:00+08:00',
                     environment='synthetic', test_kind='UNIT', result='PASS', evidence_files=['proof.json'])
        old = dict(muse_commit='ce17b9ece3ecdc3a4aa318d4abd7ba16b8c4420d',
                   bundle_version='0.2.16', bundle_blake3='synthetic-previous')
        entries = [entry, dict(entry, id='previous', **old)]
        entries.extend(dict(entry, id=field, **{field: value}) for field, value in old.items())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / 'official_muse/app/bundle'
            bundle.mkdir(parents=True)
            manifest = {'version': candidate['bundle_version'],
                        'integrity': {'bundle_blake3': candidate['bundle_blake3']}}
            (bundle / 'manifest.json').write_text(json.dumps(manifest))
            (bundle / 'main.splash').write_text('synthetic')
            candidate['bundle_files_sha256'] = {'main.splash': hashlib.sha256(b'synthetic').hexdigest()}
            candidate['manifest_semantic_sha256'] = hashlib.sha256(
                json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            (root / 'proof.json').write_text('{}')
            candidate_file = root / 'candidate.json'
            index_file = root / 'index.json'
            candidate_file.write_text(json.dumps(candidate))
            index_file.write_text(json.dumps({'entries': entries}))
            argv = ['evidence.py', str(index_file), '--candidate', str(candidate_file), '--root', str(root)]
            with patch('sys.argv', argv), patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(evidence.main(), 0)
            results = json.loads(output.getvalue())
            self.assertEqual([r['declared'] for r in results], ['PASS']*5)
            self.assertEqual([r['effective'] for r in results], ['PASS'] + ['STALE_EVIDENCE']*4)


if __name__ == '__main__':
    unittest.main()
