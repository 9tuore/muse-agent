#!/usr/bin/env python3
"""Learn live public search controls, then reuse one approved recipe with new queries."""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from muse_app_learning import RecipeStore
from muse_browser import EDGE_BUNDLE_ID, IsolatedEdgeSession
from muse_browser_learning import BrowserSearchLearningAdapter, SEARCH_PAGE


def main():
    with tempfile.TemporaryDirectory(prefix="muse-g03-browser-learning-") as tmp:
        root = Path(tmp)
        with IsolatedEdgeSession(root, allowed_domains=["python.org"]) as browser:
            browser.navigate(SEARCH_PAGE)
            adapter = BrowserSearchLearningAdapter(browser)
            store = RecipeStore(root, adapter)
            observed = store.observe(EDGE_BUNDLE_ID)
            input_node = next(item for item in observed["elements"] if item["role"] == "AXSearchField")
            button_node = next(item for item in observed["elements"] if item["role"] == "AXButton" and
                               item["name"] == "Search")
            title = input_node["window_title"]
            proposal = store.propose("edge.public_search", EDGE_BUNDLE_ID, [
                {"role": input_node["role"], "name": input_node["name"], "action": "set_value", "input": "query",
                 "window_title": title},
                {"role": button_node["role"], "name": button_node["name"], "action": "press", "input": None,
                 "window_title": title},
            ])
            dry_run = store.dry_run("edge.public_search", {"query": "Python 3.13", "window_title": title})
            decision = store.decide("edge.public_search", proposal["recipe"]["revision"],
                                    proposal["digest"], approved=True)
            runs = []
            for query in ("Python 3.13", "Python 3.14"):
                browser.navigate(SEARCH_PAGE)
                receipt = store.run("edge.public_search", {"query": query, "window_title": title},
                                    approved=True, allowed_bundle_ids=[EDGE_BUNDLE_ID],
                                    allowed_window_titles=[title])
                location = browser._evaluate("location.href")
                result_count = browser._evaluate(
                    "document.querySelectorAll('ul.list-recent-events.menu li h3 a[href]').length")
                runs.append({"query": query, "status": receipt["status"],
                             "revision": receipt.get("revision"), "approval_id": receipt.get("approval_id"),
                             "steps": receipt.get("steps"), "search_url": location,
                             "url_query_matches": parse_qs(urlsplit(location).query).get("q") == [query],
                             "observed_result_count": result_count})
            print(json.dumps({"test_id": "G03-BROWSER-LEARNED-RECIPE-LIVE", "phase": "A",
                              "actual_at": datetime.now(timezone.utc).isoformat(),
                              "status": "PASS_LIVE" if dry_run["status"] == "READY_FOR_APPROVAL" and
                              decision["status"] == "ENABLED" and all(
                                  item["status"] == "COMPLETED" and item["url_query_matches"] and
                                  item["observed_result_count"] > 0 for item in runs) else "BLOCKED",
                              "observed_controls": [{"role": item["role"], "name": item["name"]}
                                                    for item in observed["elements"]],
                              "recipe_id": proposal["recipe"]["id"],
                              "recipe_revision": proposal["recipe"]["revision"],
                              "recipe_digest": proposal["digest"],
                              "dry_run_status": dry_run["status"], "approval_status": decision["status"],
                              "runs": runs, "approval_type": "synthetic_host_fixture",
                              "profile": "isolated_and_removed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
