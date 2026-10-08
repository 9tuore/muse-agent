#!/usr/bin/env python3
"""Create only this task's isolated Android emulator, using installed tools."""
from pathlib import Path
import os
import subprocess
p = Path(__file__).resolve().parent
t = p / ".local-state/tools"
sdk = t / "android-sdk"
env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR") if k in os.environ}
env.update(LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8", ANDROID_HOME=str(sdk),
    ANDROID_SDK_ROOT=str(sdk), ANDROID_USER_HOME=str(p / ".local-state/android-user"),
    ANDROID_AVD_HOME=str(p / ".local-state/avd"))
cmd = [str(t / "jdk-17.0.2.jdk/Contents/Home/bin/java"),
    "-Dcom.android.sdkmanager.toolsdir=" + str(sdk / "cmdline-tools/17.0"),
    "-classpath", str(sdk / "cmdline-tools/17.0/lib/avdmanager-classpath.jar"),
    "com.android.sdklib.tool.AvdManagerCli", "create", "avd",
    "--name", "MusePhoneAPI35", "--package", "system-images;android-35;default;x86_64",
    "--device", "pixel_2", "--path", str(p / ".local-state/avd/MusePhoneAPI35.avd")]
with (p / "evidence/emulator-create-r4.log").open("w") as f:
    result = subprocess.run(cmd, input="no\n", text=True, env=env, stdout=f, stderr=subprocess.STDOUT)
raise SystemExit(result.returncode)
