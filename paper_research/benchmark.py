"""Benchmark report search for paper-research workflows."""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

from paper_research.models import BenchmarkReport, ResearchReport
from paper_research.text import first_sentences as _first_sentences
from paper_research.text import paper_title as _paper_title


class BenchmarkSearchAgent:
    """Searches for strong report examples before each report iteration."""

    def __init__(
        self,
        benchmark_dir: Optional[Path] = None,
        web_search: bool = False,
        web_fetcher: Optional[Callable[[str], str]] = None,
        language: str = "en",
    ) -> None:
        self.benchmark_dir = benchmark_dir
        self.web_search = web_search
        self.web_fetcher = web_fetcher or _fetch_url
        self.language = language

    def search(
        self,
        paper_text: str,
        round_number: int,
        previous_report: Optional[ResearchReport],
    ) -> List[BenchmarkReport]:
        local_results = self._search_local_benchmarks(paper_text)
        if local_results:
            return local_results

        if self.web_search:
            web_results = self._search_web_benchmarks(paper_text, round_number)
            if web_results:
                return web_results

        theme = _paper_title(paper_text) or ("目标论文" if self.language == "zh" else "the target paper")
        refinement = (
            (
                " 本轮搜索还会寻找能挑战上一轮报告的视角。"
                if self.language == "zh"
                else " The current search also looks for ways to challenge the previous report."
            )
            if previous_report
            else ""
        )
        if self.language == "zh":
            return [
                BenchmarkReport(
                    title=f"{theme} 的主张-证据型优秀报告模式",
                    source=f"built-in://claim-evidence-round-{round_number}",
                    summary=(
                        "主张-证据型报告会先列出论文核心主张，再逐条检查方法、实验和限制是否支撑这些主张。"
                    ),
                    strengths=[
                        "区分论文原始主张和评审者解释。",
                        "使用方法与实验中的证据，而不只依赖摘要。",
                    ],
                    source_type="built-in",
                    search_note=_fallback_search_note(self.language),
                ),
                BenchmarkReport(
                    title=f"{theme} 的方法审计型优秀报告模式",
                    source=f"built-in://methodology-round-{round_number}",
                    summary="方法审计型报告关注研究设计、基线方法、评估指标、消融实验和可复现设置。",
                    strengths=[
                        "检查方法选择是否匹配论文目标。",
                        "追问基线方法、数据和消融实验是否充分。",
                    ],
                    source_type="built-in",
                    search_note=_fallback_search_note(self.language),
                ),
                BenchmarkReport(
                    title=f"{theme} 的限制与后续研究型优秀报告模式",
                    source=f"built-in://limitations-round-{round_number}",
                    summary=(
                        "限制型报告把失败模式、适用边界和后续研究计划作为核心产物。"
                        + refinement
                    ),
                    strengths=[
                        "把限制和可复现性纳入评分，而不只评价新颖性。",
                        "将批评意见转化为下一轮可验证的研究问题。",
                    ],
                    source_type="built-in",
                    search_note=_fallback_search_note(self.language),
                ),
            ]
        return [
            BenchmarkReport(
                title=f"Claim-evidence benchmark report pattern for {theme}",
                source=f"built-in://claim-evidence-round-{round_number}",
                summary=(
                    "Claim-evidence reports list the paper's core claims and test whether "
                    "method, experiment, and limitation evidence supports them."
                ),
                strengths=[
                    "Separates paper claims from evaluator interpretation.",
                    "Uses evidence from methods and experiments, not only the abstract.",
                ],
                source_type="built-in",
                search_note=_fallback_search_note(self.language),
            ),
            BenchmarkReport(
                title=f"Methodology audit benchmark report pattern for {theme}",
                source=f"built-in://methodology-round-{round_number}",
                summary=(
                    "Methodology-audit reports examine research design, baselines, metrics, "
                    "ablations, and reproducibility setup."
                ),
                strengths=[
                    "Checks whether method choices match the paper's goals.",
                    "Questions whether baselines, data, and ablations are sufficient.",
                ],
                source_type="built-in",
                search_note=_fallback_search_note(self.language),
            ),
            BenchmarkReport(
                title=f"Limitations benchmark report pattern for {theme}",
                source=f"built-in://limitations-round-{round_number}",
                summary=(
                    "Limitations-focused reports make failure modes, scope boundaries, and "
                    "future research plans central outputs."
                    + refinement
                ),
                strengths=[
                    "Scores limitations and reproducibility instead of only novelty.",
                    "Turns critique into testable next-round research questions.",
                ],
                source_type="built-in",
                search_note=_fallback_search_note(self.language),
            ),
        ]

    def _search_local_benchmarks(self, paper_text: str) -> List[BenchmarkReport]:
        if not self.benchmark_dir or not self.benchmark_dir.exists():
            return []
        files = sorted(
            path
            for path in self.benchmark_dir.rglob("*")
            if path.suffix.lower() in {".txt", ".md", ".markdown"}
            and not any(part.startswith(".") for part in path.relative_to(self.benchmark_dir).parts)
        )
        scored_reports = []
        terms = _keywords(paper_text, limit=8)
        for path in files:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if len(content.strip()) < 10 or _is_placeholder_benchmark(content):
                continue
            lowered_content = content.lower()
            matched_terms = [term for term in terms if term.lower() in lowered_content]
            score = len(matched_terms)
            structure_score = _report_structure_score(content, self.language)
            scored_reports.append((score, structure_score, path, content, matched_terms))
        matched_reports = [item for item in scored_reports if item[0] > 0]
        selected_reports = matched_reports or sorted(
            scored_reports,
            key=lambda item: (-item[1], item[2].name),
        )[:2]
        results: List[BenchmarkReport] = []
        for _, _, path, content, matched_terms in sorted(
            selected_reports,
            key=lambda item: (-item[0], -item[1], item[2].name),
        )[:5]:
            results.append(
                BenchmarkReport(
                    title=path.stem.replace("_", " ").title(),
                    source=str(path),
                    summary=_first_sentences(content, count=3),
                    strengths=_infer_report_strengths(content, self.language),
                    source_type="local",
                    search_note=_local_search_note(path, matched_terms, self.language),
                )
            )
        return results

    def _search_web_benchmarks(
        self,
        paper_text: str,
        round_number: int,
    ) -> List[BenchmarkReport]:
        title = _paper_title(paper_text) or "paper"
        if self.language == "zh":
            query_text = f"{title} 优秀 论文 研究报告 分析"
        else:
            query_text = f"{title} excellent research report paper analysis"
        query = quote_plus(query_text)
        url = f"https://duckduckgo.com/html/?q={query}"
        try:
            html = self.web_fetcher(url)
        except Exception:
            return []

        links = _extract_duckduckgo_results(html)
        reports = []
        for index, item in enumerate(links[:5], start=1):
            summary = item["snippet"] or (
                "外部搜索结果：可能包含优秀研究报告样例。"
                if self.language == "zh"
                else "External search result for an excellent research-report example."
            )
            reports.append(
                BenchmarkReport(
                    title=item["title"] or (
                        f"外部对照报告 {index}"
                        if self.language == "zh"
                        else f"External benchmark report {index}"
                    ),
                    source=item["url"] or f"web-search://round-{round_number}-{index}",
                    summary=summary,
                    strengths=_infer_report_strengths(f"{item['title']} {summary}", self.language),
                    source_type="web",
                    search_note=(
                        f"DuckDuckGo 查询：{query_text}"
                        if self.language == "zh"
                        else f"DuckDuckGo query: {query_text}"
                    ),
                )
            )
        return reports


def _report_structure_score(content: str, language: str) -> int:
    if language == "zh":
        markers = ["主张", "证据", "限制", "局限", "后续", "方法", "实验"]
        return sum(1 for marker in markers if marker in content)
    lower = content.lower()
    markers = ["claim", "evidence", "limitation", "risk", "future", "method", "experiment"]
    return sum(1 for marker in markers if marker in lower)


def _is_placeholder_benchmark(content: str) -> bool:
    normalized = " ".join(content.strip().lower().split())
    if normalized in {"tbd", "todo", "placeholder", "draft"}:
        return True
    return normalized.startswith(("todo:", "tbd:")) or "fill later" in normalized


def _fallback_search_note(language: str) -> str:
    if language == "zh":
        return "内置回退：未找到可用的本地或网页对照报告，使用内置优秀报告模式。"
    return "built-in fallback: no usable local or web benchmark reports were found."


def _local_search_note(path: Path, matched_terms: Sequence[str], language: str) -> str:
    if language == "zh":
        terms = "、".join(matched_terms[:5]) if matched_terms else "无直接关键词命中"
        return f"本地对照报告文件：{path.name}；关键词命中：{terms}。"
    terms = ", ".join(matched_terms[:5]) if matched_terms else "no direct keyword overlap"
    return f"Local benchmark file: {path.name}; keyword matches: {terms}."


def _keywords(text: str, limit: int = 10) -> List[str]:
    chinese_terms = [
        "多智能体",
        "论文审查",
        "评分标准",
        "可复现性",
        "基线",
        "数据",
        "消融",
        "证据引用",
        "证据",
        "限制",
        "局限",
        "方法",
        "实验",
        "报告",
    ]
    found_chinese_terms = [term for term in chinese_terms if term in text]
    words = re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", text.lower())
    stopwords = {
        "that",
        "with",
        "from",
        "this",
        "paper",
        "study",
        "system",
        "reports",
        "quality",
        "current",
        "each",
    }
    counts: Dict[str, int] = {}
    for word in words:
        if word not in stopwords:
            counts[word] = counts.get(word, 0) + 1
    english_terms = [
        word
        for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]
    return (found_chinese_terms + english_terms)[:limit]


def _infer_report_strengths(content: str, language: str = "en") -> List[str]:
    lower = content.lower()
    strengths = []
    if "limitation" in lower or "risk" in lower or "限制" in content or "风险" in content or "局限" in content:
        strengths.append(
            "明确讨论限制和风险。"
            if language == "zh"
            else "Explicitly discusses limitations and risks."
        )
    if "experiment" in lower or "evidence" in lower or "实验" in content or "证据" in content:
        strengths.append(
            "把论文主张连接到实验证据。"
            if language == "zh"
            else "Connects claims to experimental evidence."
        )
    if (
        "baseline" in lower
        or "ablation" in lower
        or "data" in lower
        or "消融" in content
        or "数据" in content
    ):
        strengths.append(
            "检查基线方法、数据和消融实验是否充分。"
            if language == "zh"
            else "Audits baselines, data, and ablation evidence."
        )
    if "future" in lower or "follow" in lower or "未来" in content or "后续" in content:
        strengths.append(
            "把论文解读转化为后续研究问题。"
            if language == "zh"
            else "Turns interpretation into future research questions."
        )
    if not strengths:
        strengths.append(
            "提供可复用的外部对照样例。"
            if language == "zh"
            else "Provides a reusable external comparison point."
        )
    return strengths


def _fetch_url(url: str) -> str:
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


def _extract_duckduckgo_results(raw_html: str) -> List[Dict[str, str]]:
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
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    for redirect_param in ("uddg", "q"):
        if redirect_param in query and query[redirect_param]:
            candidate = unquote(query[redirect_param][0])
            if candidate.lower().startswith(("http://", "https://")):
                return candidate
    return href
