#!/usr/bin/env python3
"""Clean JSON-line facade over the test-only actual Rust service helper."""
import argparse, json, os, subprocess, sys, threading
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--binary', type=Path, required=True)
p.add_argument('--root', type=Path, required=True)
a = p.parse_args()
owned_build = Path(__file__).resolve().parents[5] / 'build'
state = a.root.resolve()
state.relative_to(owned_build)
assert state != owned_build
env = dict(os.environ, NIGHT004_TMP_ROOT=str(owned_build), NIGHT004_L3_ROOT=str(state),
           NIGHT004_RECEIVER_SCRIPT=str(Path(__file__).with_name('receiver.py')))
child = subprocess.Popen([str(a.binary.resolve(strict=True)), '--exact',
    'night004_l2::l3_protocol_driver', '--ignored', '--nocapture', '--test-threads=1'],
    env=env, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
def forward_input():
    try:
        for line in sys.stdin:
            child.stdin.write(line); child.stdin.flush()
            if json.loads(line).get('method') == 'fixture.quit': break
    finally:
        child.stdin.close()
thread = threading.Thread(target=forward_input, daemon=True)
thread.start()
try:
    for line in child.stdout:
        start = line.find('{')
        if start >= 0:
            response = json.loads(line[start:])
            print(json.dumps(response), flush=True)
        else: sys.stderr.write(line)
    raise SystemExit(child.wait())
finally:
    if child.poll() is None: child.terminate(); child.wait(timeout=10)
