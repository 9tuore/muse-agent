import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from muse_ax_adapter import AXUnavailable, NativeAXAdapter


class NativeAXAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        helper = Path(temp.name) / "muse_ax_helper"
        helper.write_bytes(b"fixture")
        self.adapter = NativeAXAdapter(helper)

    def test_permission_denial_preserves_native_status(self):
        native = {"status": "BLOCKED_PERMISSION", "permission": "accessibility", "trusted": False}
        with patch("muse_ax_adapter.subprocess.run", return_value=CompletedProcess([], 0, json.dumps(native), "")):
            with self.assertRaises(AXUnavailable) as caught:
                self.adapter.snapshot("com.apple.TextEdit")
        self.assertEqual(caught.exception.result, native)

    def test_action_uses_argv_without_shell_and_returns_receipt(self):
        native = {"status": "COMPLETED", "ax_error": 0}
        with patch("muse_ax_adapter.subprocess.run", return_value=CompletedProcess([], 0, json.dumps(native), "")) as run:
            result = self.adapter.act("com.apple.TextEdit", {"role": "AXTextArea", "name": "Document"},
                                      "set_value", "hello; $(touch /tmp/should-not-run)")
        self.assertEqual(result, native)
        self.assertFalse(run.call_args.kwargs.get("shell", False))
        self.assertEqual(run.call_args.args[0][1:3], ["act", "com.apple.TextEdit"])

    def test_focus_document_passes_exact_url_as_argv(self):
        native = {"status": "COMPLETED", "ax_frontmost": True}
        url = "file:///private/tmp/Muse-Test-Focus.txt"
        with patch("muse_ax_adapter.subprocess.run", return_value=CompletedProcess([], 0, json.dumps(native), "")) as run:
            result = self.adapter.focus_document("com.apple.TextEdit", "Muse-Test-Focus.txt", url)
        self.assertEqual(result, native)
        self.assertFalse(run.call_args.kwargs.get("shell", False))
        self.assertEqual(run.call_args.args[0][1:], ["focus", "com.apple.TextEdit", "Muse-Test-Focus.txt", url])


if __name__ == "__main__":
    unittest.main()
