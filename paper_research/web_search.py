"""Web search fetching and DuckDuckGo result parsing helpers."""

from __future__ import annotations

import re
from html import unescape
from typing import Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen


def fetch_url(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 paper-research/0.1 "
                "(https://github.com/luoziyan100/paper-research)"
            )
        },
    )
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_duckduckgo_results(raw_html: str) -> List[Dict[str, str]]:
    anchor_pattern = re.compile(r"<a\s+([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
    snippet_pattern = re.compile(
        r"<([a-zA-Z][a-zA-Z0-9:-]*)\s+([^>]*result__snippet[^>]*)>(.*?)</\1>",
        re.IGNORECASE | re.DOTALL,
    )
    events = []
    for match in anchor_pattern.finditer(raw_html):
        attrs = _parse_html_attrs(match.group(1))
        if _has_class(attrs, "result__a"):
            events.append((match.start(), "anchor", attrs, match.group(2)))
    for match in snippet_pattern.finditer(raw_html):
        attrs = _parse_html_attrs(match.group(2))
        if _has_class(attrs, "result__snippet"):
            events.append((match.start(), "snippet", attrs, match.group(3)))
    events.sort(key=lambda item: item[0])

    results: List[Dict[str, str]] = []
    pending_result_index: Optional[int] = None
    for _, event_type, attrs, body in events:
        if event_type == "anchor":
            title = _strip_html(body)
            source = _clean_result_url(attrs.get("href", ""))
            if source:
                results.append({"title": title, "url": source, "snippet": ""})
                pending_result_index = len(results) - 1
            else:
                pending_result_index = None
        elif pending_result_index is not None and not results[pending_result_index]["snippet"]:
            results[pending_result_index]["snippet"] = _strip_html(body)
            pending_result_index = None
    return results


def _parse_html_attrs(attrs: str) -> Dict[str, str]:
    attr_pattern = re.compile(
        r"""([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""",
        re.DOTALL,
    )
    return {
        name.lower(): unescape(double_quoted or single_quoted or unquoted)
        for name, double_quoted, single_quoted, unquoted in attr_pattern.findall(attrs)
    }


def _has_class(attrs: Dict[str, str], class_name: str) -> bool:
    return class_name in attrs.get("class", "").split()


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(without_tags).split())


def _clean_result_url(href: str) -> str:
    href = unescape(href)
    if _has_unsupported_scheme(href):
        return ""
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    for redirect_param in ("uddg", "q"):
        if redirect_param in query and query[redirect_param]:
            candidate = unquote(query[redirect_param][0])
            if _has_unsupported_scheme(candidate):
                return ""
            if candidate.lower().startswith(("http://", "https://")):
                return candidate
    return href


def _has_unsupported_scheme(href: str) -> bool:
    scheme = urlparse(href).scheme.lower()
    return bool(scheme) and scheme not in {"http", "https"}
