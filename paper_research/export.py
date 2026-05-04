"""Export workflow results to document formats."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from paper_research.docx import DocxDocument, bullet, heading, paragraph
from paper_research.models import RoundResult


def write_docx(path: Path, rounds: Iterable[RoundResult], language: str = "en") -> None:
    title = "迭代式论文研究报告" if language == "zh" else "Iterative Paper Research Report"
    document = DocxDocument(title=title)
    if language == "zh":
        document.add(heading(title, level=1))
        document.add(
            paragraph(
                "本文档记录每一轮研究报告、benchmark 搜索、评分标准、评分结果和评分标准批评。"
            )
        )
    else:
        document.add(heading("Iterative Paper Research Report", level=1))
        document.add(
            paragraph(
                "This document records every research-report round, benchmark search, "
                "scoring rubric, scorecard, and rubric critic review."
            )
        )
    for round_result in rounds:
        if language == "zh":
            document.add(heading(f"第 {round_result.round_number} 轮", level=1))
            document.add(heading("Benchmark 搜索结果", level=2))
        else:
            document.add(heading(f"Round {round_result.round_number}", level=1))
            document.add(heading("Benchmark Search Results", level=2))
        if not round_result.benchmark_reports:
            empty_text = (
                "未记录可用的 benchmark 搜索结果。"
                if language == "zh"
                else "No usable benchmark search results were recorded."
            )
            document.add(paragraph(empty_text))
        for benchmark in round_result.benchmark_reports:
            document.add(bullet(f"{benchmark.title} ({benchmark.source})"))
            if benchmark.search_note:
                label = "搜索说明" if language == "zh" else "Search note"
                separator = "：" if language == "zh" else ":"
                spacer = "" if language == "zh" else " "
                document.add(bullet(f"{label}{separator}{spacer}{benchmark.search_note}"))
            document.add(paragraph(benchmark.summary))
            for strength in benchmark.strengths:
                prefix = "优点" if language == "zh" else "Strength"
                separator = "：" if language == "zh" else ":"
                spacer = "" if language == "zh" else " "
                document.add(bullet(f"{prefix}{separator}{spacer}{strength}"))

        document.add(heading(round_result.report.title, level=2))
        for name, content in round_result.report.sections.items():
            document.add(heading(name, level=3))
            document.add(paragraph(content))

        document.add(heading("评分标准" if language == "zh" else "Scoring Rubric", level=2))
        document.add(paragraph(round_result.rubric.source_notes))
        for criterion in round_result.rubric.criteria:
            if language == "zh":
                text = f"{criterion.name}（{criterion.max_points} 分）：{criterion.description}"
            else:
                text = f"{criterion.name} ({criterion.max_points} pts): {criterion.description}"
            document.add(bullet(text))

        document.add(heading("评分结果" if language == "zh" else "Scorecard", level=2))
        document.add(paragraph(round_result.scorecard.summary))
        for score in round_result.scorecard.scores:
            if language == "zh":
                text = f"{score.name}：{score.points}/{score.max_points}。{score.rationale}"
            else:
                text = f"{score.name}: {score.points}/{score.max_points}. {score.rationale}"
            document.add(bullet(text))

        document.add(heading("评分标准批评" if language == "zh" else "Rubric Critic Review", level=2))
        for issue in round_result.critic_review.issues:
            prefix = "问题" if language == "zh" else "Issue"
            separator = "：" if language == "zh" else ":"
            spacer = "" if language == "zh" else " "
            document.add(bullet(f"{prefix}{separator}{spacer}{issue}"))
        for recommendation in round_result.critic_review.recommendations:
            prefix = "建议" if language == "zh" else "Recommendation"
            separator = "：" if language == "zh" else ":"
            spacer = "" if language == "zh" else " "
            document.add(bullet(f"{prefix}{separator}{spacer}{recommendation}"))
    document.save(path)
