"""Scoring helper functions shared by agents."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence

from paper_research.models import CriterionScore, CriticReview, ResearchReport, Rubric, Scorecard
from paper_research.text import compact as _compact


class ReportScoringAgent:
    """Scores the report against the current round's rubric."""

    def score(self, report: ResearchReport, rubric: Rubric, language: str = "en") -> Scorecard:
        _validate_language(language)
        report_text = report.as_text().lower()
        scores: List[CriterionScore] = []
        source_confidence_limited = _has_no_external_benchmark_sources(rubric.source_notes)
        if language == "zh":
            keyword_map = {
                "问题定义": ["问题", "范围", "假设", "重要", "研究"],
                "技术贡献": ["贡献", "方法", "新颖", "设计", "智能体"],
                "证据质量": ["证据", "实验", "基线方法", "测量", "结果"],
                "限制与失败模式": ["限制", "风险", "脆弱", "失败", "复现"],
                "研究价值": ["后续", "复现", "议程", "消融实验", "建议"],
                "可复现性与证据引用": ["证据", "复现", "基线方法", "数据", "评估"],
            }
        else:
            keyword_map = {
                "Problem Framing": ["problem", "question", "scope", "assumption", "matters"],
                "Technical Contribution": ["contribution", "method", "novelty", "design", "agent"],
                "Evidence Quality": ["evidence", "experiment", "baseline", "measured", "result"],
                "Limitations and Failure Modes": ["limitation", "risk", "fragile", "failure", "reproduc"],
                "Research Usefulness": ["follow-up", "replicate", "agenda", "ablation", "decision"],
                "Reproducibility and Evidence Citation": [
                    "evidence",
                    "reproduc",
                    "baseline",
                    "data",
                    "evaluation",
                ],
            }
        for criterion in rubric.criteria:
            keywords = keyword_map.get(criterion.name, [])
            matched_keywords = [
                keyword for keyword in keywords if _contains_marker(report_text, keyword, language)
            ]
            hits = len(matched_keywords)
            if language == "zh":
                evidence = _find_evidence_snippet(report, keywords, language)
                points = min(criterion.max_points, 6 + min(hits, 5) * 2)
                if "验证缺口" in evidence or "没有给出" in evidence:
                    points = min(points, 14)
                points, cap_note = _apply_source_confidence_cap(
                    points,
                    criterion.max_points,
                    rubric.source_notes,
                    language,
                )
                marker_text = "、".join(matched_keywords) if matched_keywords else "无"
                rationale = f"找到 {hits} 个相关标记（{marker_text}）。证据：{evidence}{cap_note}"
            else:
                evidence = _find_evidence_snippet(report, keywords, language)
                points = min(criterion.max_points, 8 + min(hits, 5) * 2)
                points, cap_note = _apply_source_confidence_cap(
                    points,
                    criterion.max_points,
                    rubric.source_notes,
                    language,
                )
                marker_text = ", ".join(matched_keywords) if matched_keywords else "none"
                rationale = (
                    f"Found {hits} evidence markers for {criterion.name.lower()} "
                    f"in the generated report. Matched markers: {marker_text}. "
                    f"Evidence: {evidence}{cap_note}"
                )
            scores.append(
                CriterionScore(
                    name=criterion.name,
                    points=points,
                    max_points=criterion.max_points,
                    rationale=rationale,
                )
            )
        total = sum(item.points for item in scores)
        max_total = sum(criterion.max_points for criterion in rubric.criteria) or 100
        quality_total = _normalized_total(total, max_total)
        if language == "zh":
            return Scorecard(
                total_score=total,
                scores=scores,
                summary=(
                    f"本轮报告总分 {total}/{max_total}。质量等级：{_quality_band(quality_total, language)}。"
                    f"主要风险：{_score_risk_summary(scores, language, source_confidence_limited)}。"
                    "低分项应在下一轮优先修订。"
                ),
            )
        return Scorecard(
            total_score=total,
            scores=scores,
            summary=(
                f"The report scores {total}/{max_total}. Quality band: {_quality_band(quality_total, language)}. "
                f"Main risks: {_score_risk_summary(scores, language, source_confidence_limited)}. Strong areas are "
                "the criteria with explicit evidence markers; weaker areas should be revised "
                "in the next round."
            ),
        )


def low_score_summary(scorecard: Optional[Scorecard], language: str) -> str:
    if not scorecard:
        return "暂无上一轮评分" if language == "zh" else "no prior scorecard"
    threshold = 12 if language == "zh" else 14
    low_scores = [
        f"{score.name} {score.points}/{score.max_points}"
        for score in scorecard.scores
        if score.points <= threshold
    ]
    if low_scores:
        return "；".join(low_scores) if language == "zh" else "; ".join(low_scores)
    return "没有明显低分项" if language == "zh" else "no clear low-score items"


def critic_mentions_reproducibility(critic_review: Optional[CriticReview]) -> bool:
    if not critic_review:
        return False
    combined = " ".join(critic_review.issues + critic_review.recommendations).lower()
    return "reproduc" in combined or "可复现" in combined or "证据引用" in combined


def _quality_band(total: int, language: str) -> str:
    if language == "zh":
        if total >= 85:
            return "高"
        if total >= 70:
            return "良好"
        if total >= 55:
            return "中等"
        return "偏低"
    if total >= 85:
        return "high"
    if total >= 70:
        return "good"
    if total >= 55:
        return "moderate"
    return "low"


def _normalized_total(total: int, max_total: int) -> int:
    return round((total / max_total) * 100) if max_total else total


def _score_risk_summary(
    scores: Sequence[CriterionScore],
    language: str,
    source_confidence_limited: bool = False,
) -> str:
    threshold = 12 if language == "zh" else 14
    weak_scores = [
        score.name
        for score in scores
        if score.points <= max(threshold, int(score.max_points * 0.6))
    ]
    if source_confidence_limited:
        source_risk = (
            "来源置信度受限：外部对照报告数量为 0"
            if language == "zh"
            else "source confidence capped by missing external benchmark sources"
        )
        if weak_scores:
            prefix = "、".join(weak_scores[:2]) if language == "zh" else ", ".join(weak_scores[:2])
            return f"{prefix}、{source_risk}" if language == "zh" else f"{prefix}, {source_risk}"
        return source_risk
    if weak_scores:
        return "、".join(weak_scores[:3]) if language == "zh" else ", ".join(weak_scores[:3])
    return "暂无明显低分项" if language == "zh" else "no obvious low-score criteria"


def _find_evidence_snippet(
    report: ResearchReport,
    keywords: Sequence[str],
    language: str,
) -> str:
    separator = "：" if language == "zh" else " - "
    preferred_sections = [
        ("贡献", "贡献分析"),
        ("智能体", "贡献分析"),
        ("限制", "限制与风险"),
        ("风险", "限制与风险"),
        ("复现", "关键假设与验证缺口"),
        ("baseline", "关键假设与验证缺口"),
        ("证据", "论文主张与证据账本"),
        ("实验", "论文主张与证据账本"),
        ("contribution", "Contribution Analysis"),
        ("agent", "Contribution Analysis"),
        ("limitation", "Limitations and Risks"),
        ("risk", "Limitations and Risks"),
        ("reproduc", "Key Assumptions and Verification Gaps"),
        ("evidence", "Claim-Evidence Ledger"),
        ("experiment", "Claim-Evidence Ledger"),
        ("baseline", "Claim-Evidence Ledger"),
    ]
    for keyword, section_name in preferred_sections:
        if keyword in keywords and section_name in report.sections:
            return f"{section_name}{separator}{_matching_line(report.sections[section_name], keywords)}"
    for section_name, content in report.sections.items():
        lowered = content.lower()
        if any(_contains_marker(lowered, keyword, language) for keyword in keywords):
            return f"{section_name}{separator}{_matching_line(content, keywords)}"
    first_section = next(iter(report.sections.items()), None)
    if first_section:
        return f"{first_section[0]}{separator}{_compact(first_section[1], 180)}"
    if language == "zh":
        return "报告没有提供可引用的证据片段。"
    return "The report did not provide a citable evidence snippet."


def _matching_line(content: str, keywords: Sequence[str]) -> str:
    for line in content.splitlines():
        lowered = line.lower()
        if any(_contains_marker(lowered, keyword, "en") for keyword in keywords):
            return _compact(line, 180)
    first_line = content.splitlines()[0] if content.splitlines() else content
    return _compact(first_line, 180)


def _contains_marker(text: str, keyword: str, language: str) -> bool:
    lowered_keyword = keyword.lower()
    if language == "zh" or not re.fullmatch(r"[a-z-]+", lowered_keyword):
        return lowered_keyword in text
    if lowered_keyword in {"reproduc", "result", "experiment"}:
        return lowered_keyword in text
    return (
        re.search(rf"(?<![a-z]){re.escape(lowered_keyword)}s?(?![a-z])", text)
        is not None
    )


def _apply_source_confidence_cap(
    points: int,
    max_points: int,
    source_notes: str,
    language: str,
) -> tuple[int, str]:
    if not _has_no_external_benchmark_sources(source_notes):
        return points, ""
    cap = max(1, int(max_points * 0.8))
    if points <= cap:
        return points, ""
    if language == "zh":
        return cap, " 来源置信度上限已应用：外部对照报告数量为 0。"
    return cap, " source confidence cap applied: external benchmark source count is 0."


def _has_no_external_benchmark_sources(source_notes: str) -> bool:
    return (
        re.search(r"external source count:\s*0\b", source_notes, re.IGNORECASE)
        is not None
        or re.search(r"外部来源数量：\s*0\b", source_notes) is not None
    )


def _validate_language(language: str) -> None:
    if language not in {"en", "zh"}:
        raise ValueError("language must be 'en' or 'zh'.")
