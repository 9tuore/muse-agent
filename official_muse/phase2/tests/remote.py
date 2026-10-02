"""Small driver for the real Makepad remote surface of a visible test window.

This module only sends UI input. It does not mock host services or confirm an
external action. Tests must choose an isolated app-data directory and decide
which buttons a person has authorized them to click.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


class Remote:
    def __init__(self, port: int):
        self.base = f"http://127.0.0.1:{port}"

    def request(self, path: str, **params):
        url = self.base + path
        if params:
            url += "?" + urlencode(params)
        with urlopen(url, timeout=15) as response:
            return response.read()

    def widgets(self):
        return json.loads(self.request("/snap"))["s"]

    def find(self, key: str):
        for widget in self.widgets():
            if widget.get("i") == key or widget.get("t") == key:
                return widget
        raise AssertionError(f"visible widget missing: {key}")

    def wait_for(self, key: str, seconds: float = 10):
        deadline = time.monotonic() + seconds
        while True:
            try:
                return self.find(key)
            except AssertionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.2)

    def click(self, key: str):
        for attempt in range(4):
            rect = self.wait_for(key)["r"]
            for _ in range(12):
                time.sleep(0.05)
                current = self.find(key)["r"]
                if current == rect:
                    break
                rect = current
            x, y, width, height = rect
            if width < 2 or height < 2:
                raise AssertionError(f"{key} is clipped to {width}x{height}")
            try:
                answer = json.loads(self.request("/click", x=int(x + width / 2), y=int(y + height / 2), wait=1))
                assert "err" not in answer, answer
                return
            except HTTPError as error:
                body = error.read()
                if error.code == 404 and b"timeout (app busy or not running its event loop)" in body:
                    # Input may have arrived; caller must inspect state. Never
                    # repeat an approval simply because its frame wait timed out.
                    return
                if error.code == 404 and b"requested input frame could not be submitted; retry" in body and attempt < 3:
                    time.sleep(0.15)
                    continue
                raise RuntimeError(f"click HTTP {error.code}: {body.decode(errors='replace')}") from error

    def click_scroll(self, key: str, area: str, attempts: int = 12):
        """Scroll only within a real visible pane until the control is reachable."""
        for _ in range(attempts):
            try:
                widget = self.find(key)
                rect = widget["r"]
            except AssertionError:
                pass
            else:
                if rect[2] >= 2 and rect[3] >= (24 if widget.get("ty") == "Button" else 2):
                    return self.click(key)
            x, y, width, height = self.find(area)["r"]
            self.scroll(int(x + width / 2), int(y + height / 2), 80)
        raise AssertionError(f"visible widget missing after scroll: {key}")

    def set_text(self, key: str, value: str):
        """Clear actual input before typing; never append to an old test value."""
        widget = self.find(key)
        stable = 0
        for _ in range(20):
            time.sleep(0.05)
            current = self.find(key)
            stable = stable + 1 if current["r"] == widget["r"] else 0
            widget = current
            if stable >= 3:
                break
        else:
            raise AssertionError(f"input geometry did not settle: {key}")
        if widget.get("ty") != "TextInput" or "val" not in widget:
            raise AssertionError(f"{key} is not an inspectable TextInput")
        x, y, width, height = widget["r"]
        if width < 2 or height < 2:
            raise AssertionError(f"{key} is clipped to {width}x{height}")
        # Focus and key-down may change no pixels. The remote's wait=1 then
        # times out waiting for a new frame despite delivering the input.
        self.request("/click", x=int(x + width / 2), y=int(y + height / 2))
        if widget["val"]:
            # This remote surface does not deliver Cmd+A to Splash TextInput.
            # Individual key-downs do reach the focused field.
            # Focusing the middle of an existing value puts the caret there.
            # Move to its end before backspacing the whole observed value.
            self.request("/k", k="down", c="End")
            for _ in widget["val"]:
                self.request("/k", k="down", c="Backspace")
        self._wait_value(key, "")
        if value:
            self.request("/t", t=value)
        self._wait_value(key, value)

    def _wait_value(self, key: str, expected: str):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.find(key).get("val") == expected:
                return
            time.sleep(0.05)
        raise AssertionError(f"input readback differs for {key}")

    def scroll(self, x: int, y: int, dy: int):
        for attempt in range(4):
            try:
                self.request("/m", k="scroll", x=x, y=y, dy=dy, precise=1, wait=1)
                return
            except HTTPError as error:
                body = error.read()
                # At an edge input may produce no new frame; inspect the next
                # snapshot. Retry only an explicitly unsubmitted scroll frame.
                if error.code == 404 and b"timeout (app busy or not running its event loop)" in body:
                    return
                if error.code == 404 and b"requested input frame could not be submitted; retry" in body and attempt < 3:
                    time.sleep(0.15)
                    continue
                raise RuntimeError(f"scroll HTTP {error.code}: {body.decode(errors='replace')}") from error

    def shot(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.request("/g", raw=1))

    def log(self, count: int = 100):
        return json.loads(self.request("/log", n=count))
