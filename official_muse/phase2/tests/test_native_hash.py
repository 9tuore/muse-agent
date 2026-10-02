"""LOCAL card-host SHA-256 vectors, using the final patched runtime and a test jail."""
import hashlib
import json
import shutil
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_core_logic import HERE, REPO, launch, quit_host, wait_file


def main():
    port = 8264
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", port)) != 0, "port already owned"
    root = HERE / ".local-state/native-hash-final"
    assert not root.exists(), "keep previous evidence; use a new output root"
    bundle = root / "bundle"
    state = root / "state"
    jail = state / "muse-goals"
    shutil.copytree(REPO / "official_muse/app/bundle", bundle)
    jail.mkdir(parents=True)
    values = ["", "abc", "中文🙂", "a"*55, "a"*56, "a"*64,
              "资料\n"*1000, "a"*4000, "a"*65536]
    for i, value in enumerate(values):
        (jail / f"input-{i}.txt").write_text(value)
    # Read one input per callback; no script or host budget is increased.
    script = '''let index = 0
let hashes = []
fn probe(){
    hashes.push(fs.sha256(fs.read("input-" + index + ".txt")))
    index = index + 1
    if index < 9 { start_timeout(0.02, || probe()) }
    else { fs.write("test-hashes.json", hashes.to_json()) }
}
start_timeout(0.05, || probe())
View{width: Fill height: Fill Label{text: "Native SHA-256 test"}}
'''
    (bundle / "main.splash").write_text(script)
    try:
        launch(bundle, state, port)
        hashes = wait_file(jail / "test-hashes.json")
        expected = [hashlib.sha256(value.encode()).hexdigest() for value in values]
        assert hashes == expected, "native/Python UTF-8 digest mismatch"
    finally:
        quit_host(port)
    (state / "card-host.log").rename(state / "vectors.log")
    (jail / "input-rejected.txt").write_text("a"*65537)
    (bundle / "main.splash").write_text('''fn probe(){
    fs.write("guard-started.json", {started: true}.to_json())
    let digest = fs.sha256(fs.read("input-rejected.txt"))
    fs.write("guard-value.txt", digest)
}
start_timeout(0.05, || probe())
View{width: Fill height: Fill Label{text: "Native hash limit check"}}
''')
    try:
        launch(bundle, state, port)
        wait_file(jail / "guard-started.json")
        time.sleep(.4)
        assert "sha256 requires UTF-8 text of at most 65536 bytes" in (state / "card-host.log").read_text()
        assert not (jail / "guard-value.txt").exists()
    finally:
        quit_host(port)
    report = {"evidence": "LOCAL card-host; exact UTF-8 native/Python vectors",
              "vectors": len(values), "byte_lengths": [len(v.encode()) for v in values],
              "sha256": hashes, "over_64k_rejected": True, "status": "PASS"}
    (root / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
