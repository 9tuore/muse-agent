import subprocess
import tempfile
import unittest
from pathlib import Path

from muse_keychain import get_password, set_password


class KeychainTests(unittest.TestCase):
    def test_isolated_macos_keychain_add_update_read(self):
        with tempfile.TemporaryDirectory(prefix="g01-keychain-test-") as directory:
            keychain = Path(directory) / "fixture.keychain-db"
            # Synthetic keychain password only; no product or user credential.
            created = subprocess.run(
                ["/usr/bin/security", "create-keychain", "-p", "fixture-keychain", str(keychain)],
                capture_output=True, timeout=10)
            self.assertEqual(created.returncode, 0)
            unlocked = subprocess.run(
                ["/usr/bin/security", "unlock-keychain", "-p", "fixture-keychain", str(keychain)],
                capture_output=True, timeout=10)
            self.assertEqual(unlocked.returncode, 0)
            self.assertIsNone(get_password("g01.fixture", "one", keychain_path=keychain))
            set_password("g01.fixture", "one", "first synthetic", keychain_path=keychain)
            self.assertEqual(get_password("g01.fixture", "one", keychain_path=keychain), "first synthetic")
            set_password("g01.fixture", "one", "second synthetic", keychain_path=keychain)
            self.assertEqual(get_password("g01.fixture", "one", keychain_path=keychain), "second synthetic")


if __name__ == "__main__":
    unittest.main()
