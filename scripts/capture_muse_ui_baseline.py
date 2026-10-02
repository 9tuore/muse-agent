#!/usr/bin/env python3
"""Capture the installed native Muse UI with isolated application data."""
import argparse
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from test_muse_desktop_package import ax, wait_for, window_ready

WINDOWS = r'''
#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>
int main(int argc, char **argv) {
    int pid = atoi(argv[1]);
    CFArrayRef list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID);
    for (NSDictionary *item in (__bridge NSArray *)list) {
        if ([item[(id)kCGWindowOwnerPID] intValue] != pid) continue;
        CGRect rect = CGRectZero;
        CGRectMakeWithDictionaryRepresentation((__bridge CFDictionaryRef)item[(id)kCGWindowBounds], &rect);
        if (rect.size.width < 250 || rect.size.height < 150) continue;
        printf("%u\n", [item[(id)kCGWindowNumber] unsignedIntValue]);
    }
    CFRelease(list);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="muse-ui-baseline-") as temp:
        root = Path(temp)
        app = root / "Muse-Baseline.app"
        shutil.copytree(args.app.resolve(strict=True), app, symlinks=True)
        subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)
        window_id = root / "window_id"
        window_source = root / "windows.m"
        window_source.write_text(WINDOWS)
        subprocess.run(["clang", "-fobjc-arc", "-framework", "Cocoa", "-framework", "CoreGraphics",
                        str(window_source), "-o", str(window_id)], check=True)
        workspace = root / "workspace"
        workspace.mkdir()
        env = dict(os.environ, AGENT_WORKSPACE=str(workspace), GOSIM_LOCAL_INBOX="0",
                   GOSIM_SKIP_ONBOARDING="1", PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPYCACHEPREFIX=str(root / "pycache"))
        with (root / "native.stdout").open("w") as stdout, (root / "native.stderr").open("w") as stderr:
            process = subprocess.Popen([str(app / "Contents/MacOS/GOSIM-Local-Agent"),
                                        "-QQMailAddress", ""], env=env, stdout=stdout,
                                       stderr=stderr, start_new_session=True)
            try:
                wait_for("native Muse window", lambda: window_ready(process.pid))
                def capture(name):
                    time.sleep(0.7)
                    windows = subprocess.check_output([str(window_id), str(process.pid)], text=True).split()
                    for index, wid in enumerate(windows):
                        subprocess.run(["screencapture", "-x", "-l", wid,
                                        str(output / f"{name}-{index}.png")], check=True)
                capture("chat-empty")
                for name, button in (("goals", "长期目标"), ("memory", "记忆"),
                                     ("activity", "活动记录"), ("capabilities", "查看技能位")):
                    ax(process.pid, f'click button "{button}" of group 1 of window "Muse · GOSIM"')
                    capture(name)
                    if name == "memory":
                        ax(process.pid, 'click button "关闭" of window 1')
                ax(process.pid, 'click button "对话" of group 1 of window "Muse · GOSIM"')
                ax(process.pid, 'click radio button 2 of radio group 1 of window "Muse · GOSIM"')
                capture("result-empty")
                ax(process.pid, 'click button "设置与首启" of group 1 of window "Muse · GOSIM"')
                time.sleep(0.8)
                capture("settings")
                ax(process.pid, 'click button "模型与预算" of window 1')
                capture("model-budget")
            finally:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)


if __name__ == "__main__":
    main()
