"""Export workflow results to document formats."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from paper_research.docx import DocxDocument, bullet, heading, paragraph
from paper_research.models import RoundResult


def write_docx(path: Path, rounds: Iterable[RoundResult], language: str = "en") -> None:
    document = DocxDocument()
    if language == "zh":
        document.add(heading("迭代式论文研究报告", level=1))
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
        for benchmark in round_result.benchmark_reports:
            document.add(bullet(f"{benchmark.title} ({benchmark.source})"))
            if benchmark.search_note:
                label = "搜索说明" if language == "zh" else "Search note"
                document.add(bullet(f"{label}: {benchmark.search_note}"))
            document.add(paragraph(benchmark.summary))
            for strength in benchmark.strengths:
                prefix = "优点" if language == "zh" else "Strength"
                document.add(bullet(f"{prefix}: {strength}"))

        document.add(heading(round_result.report.title, level=2))
        for name, content in round_result.report.sections.items():
            document.add(heading(name, level=2))
            document.add(paragraph(content))

        document.add(heading("评分标准" if language == "zh" else "Scoring Rubric", level=2))
        document.add(paragraph(round_result.rubric.source_notes))
        for criterion in round_result.rubric.criteria:
            document.add(
                bullet(f"{criterion.name} ({criterion.max_points} pts): {criterion.description}")
            )

        document.add(heading("评分结果" if language == "zh" else "Scorecard", level=2))
        document.add(paragraph(round_result.scorecard.summary))
        for score in round_result.scorecard.scores:
            document.add(
                bullet(
                    f"{score.name}: {score.points}/{score.max_points}. {score.rationale}"
                )
            )

        document.add(heading("评分标准批评" if language == "zh" else "Rubric Critic Review", level=2))
        for issue in round_result.critic_review.issues:
            document.add(bullet(f"{'问题' if language == 'zh' else 'Issue'}: {issue}"))
        for recommendation in round_result.critic_review.recommendations:
            prefix = "建议" if language == "zh" else "Recommendation"
            document.add(bullet(f"{prefix}: {recommendation}"))
    document.save(path)
