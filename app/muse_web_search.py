"""Bounded public search results as untrusted candidate sources."""

from __future__ import annotations

import hashlib
import html.parser
from datetime import datetime, timezone
from urllib.parse import quote

from muse_capabilities import MAX_WEB_BYTES, _PinnedHTTPS, _public_address, _public_url


class _BingResults(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self.depth = 0
        self.in_h2 = False
        self.in_title = False
        self.in_snippet = False
        self.current = None

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        classes = set(props.get("class", "").split())
        if tag == "li" and "b_algo" in classes and not self.depth:
            self.depth = 1
            self.current = {"url": "", "title": [], "snippet": []}
            return
        if not self.depth:
            return
        if tag == "li":
            self.depth += 1
        elif tag == "h2":
            self.in_h2 = True
        elif tag == "a" and self.in_h2 and not self.current["url"]:
            self.current["url"] = props.get("href", "")
            self.in_title = True
        elif tag == "p" and "b_lineclamp2" in classes:
            self.in_snippet = True

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == "a":
            self.in_title = False
        elif tag == "h2":
            self.in_h2 = False
        elif tag == "p":
            self.in_snippet = False
        elif tag == "li":
            self.depth -= 1
            if self.depth == 0:
                self.results.append(self.current)
                self.current = None
                self.in_h2 = self.in_title = self.in_snippet = False

    def handle_data(self, data):
        if self.depth and self.current:
            value = " ".join(data.split())
            if value and self.in_title:
                self.current["title"].append(value)
            elif value and self.in_snippet:
                self.current["snippet"].append(value)


def search_public(query: str, *, max_results: int = 10, allowed_domains: list[str] | None = None) -> dict:
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= 160 or type(max_results) is not int or not 1 <= max_results <= 10:
        raise ValueError("search_query_or_limit_invalid")
    url, host, target = _public_url("https://cn.bing.com/search?q=" + quote(query.strip()))
    connection = _PinnedHTTPS(host, _public_address(host))
    try:
        connection.request("GET", target, headers={"Host": host, "User-Agent": "Mozilla/5.0 MuseLocalAgent/0.2",
                                                    "Accept": "text/html", "Accept-Encoding": "identity"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("search_http_status_" + str(response.status))
        if "text/html" not in response.getheader("Content-Type", "").lower():
            raise ValueError("search_content_type_invalid")
        raw = response.read(MAX_WEB_BYTES + 1)
        if len(raw) > MAX_WEB_BYTES:
            raise ValueError("search_page_too_large")
    finally:
        connection.close()
    parser = _BingResults()
    parser.feed(raw.decode("utf-8", errors="replace"))
    candidates = []
    for rank, item in enumerate(parser.results, start=1):
        if not item["url"]:
            continue
        try:
            result_url, result_host, _ = _public_url(item["url"], allowed_domains)
            _public_address(result_host)
        except (ValueError, OSError, TimeoutError):
            continue
        title = " ".join(item["title"])[:240]
        snippet = " ".join(item["snippet"])[:400]
        candidates.append({"rank": rank, "title": title, "url": result_url,
                           "source_id": "web:" + hashlib.sha256(result_url.encode("utf-8")).hexdigest()[:24],
                           "snippet": snippet})
        if len(candidates) >= max_results:
            break
    return {"query": query.strip(), "search_page": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "content_sha256": hashlib.sha256(raw).hexdigest(), "results": candidates,
            "candidate_count": len(parser.results), "untrusted_source": True}
