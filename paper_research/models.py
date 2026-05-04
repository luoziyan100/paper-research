"""Shared data models for paper-research workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class WorkflowConfig:
    rounds: int = 3
    output_dir: Path = Path("research_output")
    benchmark_dir: Optional[Path] = None
    web_search: bool = False
    language: str = "en"
    jsonl_filename: str = "research_rounds.jsonl"
    docx_filename: str = "research_report.docx"


@dataclass(frozen=True)
class ContinuousRunConfig:
    duration_seconds: float
    sleep_seconds: float = 300
    max_rounds: Optional[int] = None
    resume: bool = True


@dataclass(frozen=True)
class BenchmarkReport:
    title: str
    source: str
    summary: str
    strengths: List[str]
    source_type: str = "unknown"
    search_note: str = ""


@dataclass(frozen=True)
class ResearchReport:
    title: str
    sections: Dict[str, str]

    def as_text(self) -> str:
        lines = [self.title]
        for name, content in self.sections.items():
            lines.append(f"{name}\n{content}")
        return "\n\n".join(lines)


@dataclass(frozen=True)
class RubricCriterion:
    name: str
    description: str
    max_points: int


@dataclass(frozen=True)
class Rubric:
    title: str
    criteria: List[RubricCriterion]
    source_notes: str


@dataclass(frozen=True)
class CriterionScore:
    name: str
    points: int
    max_points: int
    rationale: str


@dataclass(frozen=True)
class Scorecard:
    total_score: int
    scores: List[CriterionScore]
    summary: str


@dataclass(frozen=True)
class CriticReview:
    issues: List[str]
    recommendations: List[str]


@dataclass(frozen=True)
class RoundResult:
    round_number: int
    benchmark_reports: List[BenchmarkReport]
    report: ResearchReport
    rubric: Rubric
    scorecard: Scorecard
    critic_review: CriticReview


@dataclass(frozen=True)
class WorkflowResult:
    rounds: List[RoundResult]
    jsonl_path: Path
    docx_path: Path
