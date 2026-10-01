#!/usr/bin/env python3
"""Run one real isolated Edge search, click, and source readback."""

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
    parser.add_argument("--engine", choices=("bing", "python.org", "wikipedia"), default="bing")
    parser.add_argument("--click-index", type=int, default=0)
    args = parser.parse_args()
    try:
        with IsolatedEdgeSession(args.root) as browser:
            search = browser.search(args.query, engine=args.engine)
            result = {"status": "SEARCHED", "query": args.query,
                      "engine": args.engine, "search_page": search["search_page"],
                      "results": search["results"][:5],
                      "profile_isolated": True}
            if not search["results"]:
                print(json.dumps(result, ensure_ascii=False)); return 0
            if args.click_index >= len(search["results"]):
                raise BrowserError("result_index_out_of_range")
            chosen = search["results"][args.click_index]
            page = browser.click_result(chosen["result_index"], chosen["url"])
            result.update(status="CLICKED_AND_READ", clicked_result_index=args.click_index,
                          click_transport=page["click_transport"],
                          source_url=page["source_url"], title=page["title"],
                          retrieved_at=page["retrieved_at"], content_sha256=page["content_sha256"],
                          text_chars=len(page["text"]), text_excerpt=page["text"][:240],
                          untrusted_source=page["untrusted_source"])
            print(json.dumps(result, ensure_ascii=False))
    except (BrowserError, OSError, TimeoutError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)[:240]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
