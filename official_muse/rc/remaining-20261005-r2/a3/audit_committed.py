"""Read Git blobs only; emit classes/counts/blob and path hashes, never matches.

Usage: python3 audit_committed.py COMMIT OUTPUT [BASE_COMMIT] [--history]
No network, credentials, worktree contents, index changes, or Git mutations.
This is a bounded heuristic audit, not a proof that publication is safe.
"""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def sha(data):
    return hashlib.sha256(data).hexdigest()


commit = git("rev-parse", sys.argv[1] + "^{commit}").decode().strip()
base = git("rev-parse", sys.argv[3] + "^{commit}").decode().strip() if len(sys.argv) > 3 else None
history = "--history" in sys.argv[4:]
selected = None
if base:
    selected = set(git("diff", "--name-only", "--diff-filter=ACMRT", "-z", base, commit).split(b"\0"))

patterns = {
    "PRIVATE_KEY_MARKER": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "PROVIDER_TOKEN_SHAPE": re.compile(r"\bsk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{20,}\b"),
    "GITHUB_TOKEN_SHAPE": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "AWS_ACCESS_ID_SHAPE": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "JWT_SHAPE": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{15,}\b"),
    "CREDENTIAL_LITERAL_REVIEW": re.compile(r'''(?i)["']?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|client[_-]?secret|secret[_-]?key)["']?\s*[:=]\s*["']([^"'\r\n]{8,})["']'''),
    "BEARER_LITERAL_REVIEW": re.compile(r"\bBearer\s+[A-Za-z0-9_.-]{16,}"),
    "HOME_ABSOLUTE_PATH": re.compile(r"/(?:Users|home)/[^/\s\"'<>]+"),
    "TEMP_ABSOLUTE_PATH": re.compile(r"/(?:private/)?(?:tmp|var/folders)/[^\s\"'<>]+"),
    "NONEXAMPLE_EMAIL_REVIEW": re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})"),
    "AUTHENTICATED_URL_REVIEW": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@"),
}
placeholder = re.compile(r"(?i)(?:^sk-(?:test|ant-test)-|^<|^\$|^\{|^your[_ -]|^example|^placeholder|^synthetic|^dummy|^REDACTED|^\*+$|^…)")
summary = collections.Counter()
findings = []
inventory = []
rawtree = git("ls-tree", "-rlz", commit)
if history:
    assert base is not None
    selected = None
    new_objects = set(git("rev-list", "--objects", "--no-object-names", base + ".." + commit).splitlines())
    entries = {}
    for revision in git("rev-list", base + ".." + commit).splitlines():
        for row in git("ls-tree", "-rlz", revision.decode()).split(b"\0"):
            if not row:
                continue
            meta, path = row.split(b"\t", 1)
            oid = meta.split()[2]
            if oid in new_objects and oid not in entries:
                entries[oid] = row
    rawtree = b"\0".join(entries.values())
proc = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
for entry in rawtree.split(b"\0"):
    if not entry:
        continue
    meta, rawpath = entry.split(b"\t", 1)
    mode, kind, oid, size = meta.split()
    if selected is not None and rawpath not in selected:
        continue
    path = rawpath.decode("utf-8", "surrogateescape")
    identity = {"path_sha256": sha(rawpath), "git_object": oid.decode(), "mode": mode.decode(), "size": None if size == b"-" else int(size)}
    classes = collections.Counter()
    summary["entries"] += 1
    if kind != b"blob":
        classes["NON_BLOB_ENTRY"] += 1
    elif re.search(r"(?i)(?:^|/)(?:\.env(?:\..+)?|credentials?(?:\..+)?|id_rsa|id_ed25519|vault\.(?:json|db)|keychain\.(?:json|db)|profile\.json)$", path) or re.search(r"(?i)\.(?:sqlite3?|db|p12|pfx|key|pem|gguf|safetensors)$", path):
        classes["SENSITIVE_NAMED_FILE_SKIPPED"] += 1
    else:
        proc.stdin.write(oid + b"\n")
        proc.stdin.flush()
        header = proc.stdout.readline().split()
        data = proc.stdout.read(int(header[2]))
        assert proc.stdout.read(1) == b"\n"
        identity["content_sha256"] = sha(data)
        summary["scanned_bytes"] += len(data)
        if mode == b"120000":
            classes["SYMLINK_TARGET_REVIEW"] += 1
        try:
            text = data.decode("utf-8")
            if "\0" in text:
                raise UnicodeError()
        except UnicodeError:
            classes["BINARY_VISUAL_OR_CONTENT_REVIEW"] += 1
            summary["binary_files"] += 1
        else:
            summary["text_files"] += 1
            for name, pattern in patterns.items():
                for match in pattern.finditer(text):
                    value = match.group(1) if name == "CREDENTIAL_LITERAL_REVIEW" else match.group()
                    if name == "NONEXAMPLE_EMAIL_REVIEW":
                        host = match.group(1).lower()
                        if host in ("example.com", "example.org", "example.net", "test.com", "localhost.localdomain") or host.endswith((".example", ".invalid", ".test", ".local", ".example.com", ".example.org", ".example.net")):
                            continue
                    if name in ("PROVIDER_TOKEN_SHAPE", "CREDENTIAL_LITERAL_REVIEW") and placeholder.search(value):
                        classes["EXPLICIT_PLACEHOLDER_LITERAL"] += 1
                        continue
                    classes[name] += 1
    inventory.append(identity)
    if classes:
        findings.append({**identity, "classes": dict(classes)})
        for name, count in classes.items():
            summary[name + "_files"] += 1
            summary[name + "_matches"] += count
proc.stdin.close()
assert proc.wait() == 0
result = {
    "schema_version": 1, "commit": commit, "base_commit": base,
    "scope": "all newly reachable unique file objects in commit range" if history else ("changed final-tree blobs" if base else "entire committed final tree; remote baseline unconfirmed"),
    "verdict": "REVIEW_REQUIRED_NOT_PUBLICATION_CLEARANCE",
    "limitations": ["Heuristic patterns can miss or falsely flag secrets.", "Binary pixels and embedded content were not inspected.", "Credential-like named files are classified without reading them.", "Git commit messages and tree entry names are not content-scanned.", "Untracked and dirty worktree data were not read or approved."] + ([] if history else ["Deleted and intermediate-history blobs are not covered by this final-tree pass."]),
    "summary": dict(summary), "findings": findings,
    "inventory_sha256": sha(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()),
    "script_sha256": sha(Path(__file__).read_bytes()),
}
dest = Path(sys.argv[2])
with dest.open("x") as output:
    json.dump(result, output, ensure_ascii=False, indent=2)
    output.write("\n")
print(json.dumps({"report_sha256": sha(dest.read_bytes()), "summary": result["summary"], "base_commit": base}, sort_keys=True))
