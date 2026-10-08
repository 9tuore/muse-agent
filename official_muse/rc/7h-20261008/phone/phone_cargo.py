#!/usr/bin/env python3
"""Own packager workaround: decode its file-URL pkgid before path use."""
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote

real = Path(__file__).resolve().parent / ".local-state/tools/rustup/toolchains/stable-x86_64-apple-darwin/bin/cargo"
args = sys.argv[1:]
if args and args[0] == "pkgid":
    result = subprocess.run([str(real), *args], stdout=subprocess.PIPE)
    value = result.stdout.decode("utf-8")
    if value.startswith(("path+file://", "file://")):
        value = unquote(value)
    sys.stdout.write(value)
    raise SystemExit(result.returncode)
os.execv(real, [str(real), *args])
