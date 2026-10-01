"""Deterministic search candidate selection; search text stays untrusted data."""

from __future__ import annotations

import re
import ipaddress
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit


_GENERIC_EN = {"official", "documentation", "documents", "latest", "updates", "update",
               "news", "guide", "research", "about", "progress", "report"}
_GENERIC_ZH = {"官方", "资料", "进展", "最新", "公开", "文档", "搜索", "整理", "持续",
               "关注", "变化", "报告", "总结", "阅读", "内容", "信息", "汇报", "提纲", "发布"}
_EXCLUDED = re.compile(r"\b(?:jobs?|careers?|hiring|salary|retired|obsolete|unmaintained)\b|招聘|职位|退役|已弃用",
                        re.IGNORECASE)


def topic_terms(query: str) -> List[str]:
    if not isinstance(query, str):
        return []
    latin = [term for term in re.findall(r"[a-z][a-z0-9._-]{2,}", query.lower())
             if term not in _GENERIC_EN]
    han_text = query
    for word in sorted(_GENERIC_ZH, key=len, reverse=True):
        han_text = han_text.replace(word, " ")
    han = re.findall(r"[\u4e00-\u9fff]{2,}", han_text)
    named = latin + han
    versions = re.findall(r"(?<![\w.])(?:20\d{2}|\d+\.\d+(?:\.\d+)?)(?![\w.])", query)
    return list(dict.fromkeys(named + versions))[:8] if named else []


def select_results(query: str, results: Any, *, limit: int = 3,
                   allowed_domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Return ranked original candidates with stable original_index for host binding."""
    terms = topic_terms(query)
    if not terms or not isinstance(results, list) or not 1 <= limit <= 10:
        return []
    candidates = []
    seen_urls = set()
    for original_index, item in enumerate(results[:10]):
        if not isinstance(item, dict):
            continue
        url, title, snippet = item.get("url"), item.get("title"), item.get("snippet", "")
        if not all(isinstance(value, str) for value in (url, title, snippet)):
            continue
        try:
            parsed = urlsplit(url)
            port = parsed.port
        except ValueError:
            continue
        host = (parsed.hostname or "").lower().rstrip(".")
        if (parsed.scheme != "https" or not host or parsed.username or parsed.password or
            port not in (None, 443) or url in seen_urls or
            host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal"))):
            continue
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            continue
        if allowed_domains is not None and not any(
            host == domain or host.endswith("." + domain) for domain in allowed_domains
        ):
            continue
        seen_urls.add(url)
        if _EXCLUDED.search(title) or _EXCLUDED.search(snippet[:240]):
            continue
        title_lower, snippet_lower = title.lower(), snippet.lower()
        if not all(term in title_lower or term in snippet_lower for term in terms):
            continue
        official_python = host == "python.org" or host.endswith(".python.org")
        priority = (0 if host == "docs.python.org" else 1 if official_python else
                    2 if host.startswith(("docs.", "developer.")) else 3)
        candidates.append((priority, original_index,
                           {"original_index": original_index, "url": url,
                            "title": title[:240], "snippet": snippet[:500],
                            "source_id": item.get("source_id")}))
    candidates.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in candidates[:limit]]


def page_relevance(query: str, output: Dict[str, Any]) -> tuple[bool, str]:
    """A topical gate, not a claim that the page's facts are verified."""
    title = str(output.get("title") or "")[:240].lower()
    body = str(output.get("text") or "")[:2000].lower()
    if _EXCLUDED.search(title):
        return False, "excluded_or_historical_title"
    if re.search(r"\b(?:retired|obsolete|unmaintained)\b|已停止维护|已退役", body[:400]):
        return False, "historical_body_warning"
    terms = topic_terms(query)
    if not terms:
        return False, "query_has_no_topic_terms"
    if not all(term in title or term in body for term in terms):
        return False, "topic_not_found_in_page"
    if not all(term in body for term in terms):
        return False, "topic_not_found_in_body"
    return True, "topic_present"
