"""Match real role/hash wire observations to the synthetic final chat report."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("wire", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    turns = report["turns"]
    wire = [json.loads(line)["messages"] for line in args.wire.read_text().splitlines()]
    expected = []
    for n, indices in enumerate(([], [0], [0,1], [], [0,1,2])):
        pairs = []
        for i in indices:
            pairs.extend([("user",digest(turns[i]["question"])), ("assistant",digest(turns[i]["answer"]))])
        pairs.append(("user",digest(turns[n]["question"])))
        expected.append(pairs)
    first = [i for i, messages in enumerate(wire) if [(m["role"],m["sha256"]) for m in messages[1:]] == expected[0]]
    assert first
    matched = [first[-1]]
    for pairs in expected[1:]:
        matches = [i for i,messages in enumerate(wire) if i > matched[-1]
                   and [(m["role"],m["sha256"]) for m in messages[1:]] == pairs]
        assert matches, "actual role/history hash mismatch"
        matched.append(matches[0])
    assert all(wire[i][0]["role"] == "system" for i in matched)
    assert len({wire[i][0]["sha256"] for i in matched}) == 1
    assert turns[0]["session_id"] == turns[4]["session_id"] != turns[3]["session_id"]
    result = {"status":"TRANSPORT_PASS", "matched_wire_indices":matched,
              "chronological_roles_and_exact_history_hashes":True,
              "latest_user_once":True,"system_hash_constant":True,"sessions_isolated":True,
              "report_sha256":digest(args.report.read_text()),"wire_sha256":digest(args.wire.read_text()),
              "semantic":report["semantic"]}
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
