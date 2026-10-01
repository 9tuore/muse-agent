#!/usr/bin/env python3
"""One isolated Edge search with three actual result clicks and source readbacks."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_browser import BrowserError, IsolatedEdgeSession


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--engine", choices=("python.org",), default="python.org")
    args = parser.parse_args()
    record = {"query": args.query, "engine": args.engine, "sources": []}
    try:
        with IsolatedEdgeSession(args.root) as browser:
            search = browser.search(args.query, engine=args.engine)
            record["search_page"] = search["search_page"]
            record["result_count"] = len(search["results"])
            for index, result in enumerate(search["results"][:3]):
                if index:
                    browser.navigate(search["search_page"])
                try:
                    page = browser.click_result(result["result_index"], result["url"])
                except BrowserError as exc:
                    record["sources"].append({"index": index, "status": "BLOCKED", "error": str(exc)[:160]})
                    continue
                record["sources"].append({"index": index, "status": "CLICKED_AND_READ",
                                          "source_url": page["source_url"], "title": page["title"],
                                          "click_transport": page["click_transport"],
                                          "retrieved_at": page["retrieved_at"],
                                          "content_sha256": page["content_sha256"],
                                          "text_chars": len(page["text"]),
                                          "text_excerpt": page["text"][:160]})
            record["status"] = "COMPLETED" if len([item for item in record["sources"]
                                                    if item["status"] == "CLICKED_AND_READ"]) == 3 else "PARTIAL"
    except (BrowserError, OSError, TimeoutError) as exc:
        record.update(status="BLOCKED", error=str(exc)[:240])
    print(json.dumps(record, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
