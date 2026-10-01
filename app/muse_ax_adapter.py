"""Accessibility transport for the reviewed native helper.

The helper checks existing Accessibility trust without requesting a TCC prompt.
Its process identity must be verified again in the packaged product.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class AXUnavailable(ValueError):
    def __init__(self, result: dict):
        self.result = result
        super().__init__(result.get("status", "ax_unavailable") + ":" + str(result.get("ax_error", "")))


class NativeAXAdapter:
    def __init__(self, helper_path: Path, *, window_title: str | None = None):
        self.helper_path = Path(helper_path)
        if not self.helper_path.is_file():
            raise ValueError("ax_helper_missing")
        self.window_title = window_title

    def _call(self, *args: str) -> dict:
        completed = subprocess.run([str(self.helper_path), *args], capture_output=True,
                                   text=True, timeout=8, check=False)
        if completed.returncode not in (0, 2) or len(completed.stdout) > 262_144:
            raise AXUnavailable({"status": "AX_HELPER_FAILED"})
        try:
            result = json.loads(completed.stdout)
        except (ValueError, TypeError):
            raise AXUnavailable({"status": "AX_HELPER_INVALID_RESPONSE"}) from None
        if not isinstance(result, dict):
            raise AXUnavailable({"status": "AX_HELPER_INVALID_RESPONSE"})
        return result

    def snapshot(self, bundle_id: str) -> dict:
        result = self._call("snapshot", bundle_id, self.window_title) if self.window_title else self._call("snapshot", bundle_id)
        if result.get("status") != "COMPLETED":
            raise AXUnavailable(result)
        return result

    def status(self) -> dict:
        """Read trust for this helper's own process identity without a prompt."""
        return self._call("status")

    def document_url(self, bundle_id: str, window_title: str) -> dict:
        return self._call("document", bundle_id, window_title)

    def focus_document(self, bundle_id: str, window_title: str, document_url: str) -> dict:
        """Bring one already-verified document window forward without a permission prompt."""
        return self._call("focus", bundle_id, window_title, document_url)

    def act(self, bundle_id: str, selector: dict, action: str, value: str | None) -> dict:
        if action not in {"press", "set_value"} or not isinstance(selector, dict):
            return {"status": "INVALID_CALL"}
        encoded = json.dumps(selector, ensure_ascii=False, separators=(",", ":"))
        if len(encoded) > 1024:
            return {"status": "INVALID_CALL"}
        return self._call("act", bundle_id, encoded, action, value or "")
