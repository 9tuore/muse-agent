import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]


def inspect_official(bundle):
    source = '\n'.join(p.read_text() for p in bundle.rglob('*.splash'))
    for forbidden in ('qqmail_imap_bridge', 'SMTP outbox', 'smtp_outbox', 'smtplib', 'qqmail-bridge'):
        if forbidden in source:
            raise AssertionError('legacy mail path reintroduced: ' + forbidden)
    assert 'host.request("mail.send",' in source
    assert 'mail' in json.loads((bundle / 'manifest.json').read_text())['capabilities']
    assert 'core_begin_action(' in source and 'UNKNOWN' in source
    return 'LEGACY_PATH_RETIRE_PASS'


class LegacyBoundaryTest(unittest.TestCase):
    def test_current_official_only_uses_host(self):
        self.assertEqual(inspect_official(ROOT/'official_muse/app/bundle'), 'LEGACY_PATH_RETIRE_PASS')

    def test_accidental_fallback_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'main.splash').write_text('host.request("mail.send", {}) qqmail_imap_bridge')
            with self.assertRaisesRegex(AssertionError, 'legacy'):
                inspect_official(p)


if __name__ == '__main__':
    unittest.main()
