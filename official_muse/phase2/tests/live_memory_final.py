"""Edit only synthetic final-test Memory through the actual visible Shell."""
import argparse
import hashlib
import json
from pathlib import Path
from remote import Remote


def read(jail):
    return json.loads((jail / "memory.json").read_text())


def claim(data, subject):
    return next(c for c in data["claims"] if c["document"]["payload"]["subject_id"] == subject)


def select(remote, subject):
    remote.set_text("memory_search", subject)
    area = remote.find("page_content")["r"]
    remote.scroll(int(area[0]+area[2]-4),int(area[1]+area[3]/2),-10000)
    remote.click_scroll("查看/更正", "page_content", 40)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("jail", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    goals = json.loads((args.jail / "goals.json").read_text())["goals"]
    ids = [next(g["id"] for g in goals if g["goal"] == f"MUSE-FINAL-029 目标 {n}") for n in (1,2)]
    before = read(args.jail)
    original = claim(before, ids[0])["document"]
    assert not original["payload"]["deleted"]
    assert not claim(before, ids[1])["pinned"]
    args.output.mkdir(parents=True, exist_ok=True)
    remote = Remote(args.port)
    remote.click("记忆")
    select(remote, ids[0])
    correction = "MUSE-FINAL-029 更正记录，仅作合成验收。"
    remote.set_text("memory_correction", correction)
    remote.click("保存更正")
    corrected = claim(read(args.jail), ids[0])
    assert corrected["document"]["revision"] == original["revision"]+1
    assert corrected["document"]["created_at"] == original["created_at"]
    assert corrected["document"]["payload"]["value"] == correction
    assert corrected["source_history"], "original source lineage missing"
    source_id = corrected["document"]["payload"]["source_ids"][0]
    source = next(s for s in read(args.jail)["sources"] if s["source_id"] == source_id)
    assert source["content_sha256"] == hashlib.sha256(correction.encode()).hexdigest()
    remote.set_text("memory_search", "更正记录")
    remote.shot(args.output / "corrected.png")
    remote.click("删除记忆")
    deleted = claim(read(args.jail), ids[0])
    assert deleted["document"]["payload"]["deleted"]
    assert not deleted["document"]["payload"]["value"]
    assert not deleted["document"]["payload"]["source_ids"]
    tombstones = [t for t in read(args.jail)["forget"] if t["subject_id"] == ids[0]]
    assert len(tombstones) == 2 and all(t["content_sha256"] for t in tombstones)
    remote.shot(args.output / "deleted-empty.png")
    select(remote, ids[1])
    remote.click("固定/取消")
    assert claim(read(args.jail), ids[1])["pinned"]
    remote.shot(args.output / "pinned.png")
    remote.set_text("memory_search", "")
    report = {"evidence":"LIVE final visible Shell; synthetic app jail only",
              "status":"PASS", "corrected_claim_id":corrected["document"]["id"],
              "pinned_claim_id":claim(read(args.jail),ids[1])["document"]["id"],
              "correction_sha256":source["content_sha256"], "tombstones":len(tombstones),
              "source_history_preserved":True, "created_at_preserved":True}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
