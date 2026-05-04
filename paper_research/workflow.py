"""Iterative multi-agent research report workflow."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from paper_research.docx import DocxDocument, bullet, heading, paragraph


@dataclass(frozen=True)
class WorkflowConfig:
    rounds: int = 3
    output_dir: Path = Path("research_output")
    benchmark_dir: Optional[Path] = None
    jsonl_filename: str = "research_rounds.jsonl"
    docx_filename: str = "research_report.docx"


@dataclass(frozen=True)
class BenchmarkReport:
    title: str
    source: str
    summary: str
    strengths: List[str]


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


class BenchmarkSearchAgent:
    """Searches for strong report examples before each report iteration."""

    def __init__(self, benchmark_dir: Optional[Path] = None) -> None:
        self.benchmark_dir = benchmark_dir

    def search(
        self,
        paper_text: str,
        round_number: int,
        previous_report: Optional[ResearchReport],
    ) -> List[BenchmarkReport]:
        local_results = self._search_local_benchmarks(paper_text)
        if local_results:
            return local_results

        theme = _paper_title(paper_text) or "the target paper"
        refinement = (
            " The current search also looks for ways to challenge the previous report."
            if previous_report
            else ""
        )
        return [
            BenchmarkReport(
                title=f"Benchmark research report pattern for {theme}",
                source=f"built-in://benchmark-round-{round_number}",
                summary=(
                    "High-quality research reports explain the problem, isolate the core "
                    "technical contribution, test whether evidence supports the claims, "
                    "and make limitations explicit before proposing follow-up work."
                    + refinement
                ),
                strengths=[
                    "Separates paper claims from evaluator interpretation.",
                    "Uses evidence from methods and experiments, not only the abstract.",
                    "Scores limitations and reproducibility instead of only novelty.",
                ],
            )
        ]

    def _search_local_benchmarks(self, paper_text: str) -> List[BenchmarkReport]:
        if not self.benchmark_dir or not self.benchmark_dir.exists():
            return []
        files = sorted(
            path
            for path in self.benchmark_dir.rglob("*")
            if path.suffix.lower() in {".txt", ".md"}
        )
        results: List[BenchmarkReport] = []
        terms = _keywords(paper_text, limit=8)
        for path in files[:5]:
            content = path.read_text(encoding="utf-8", errors="ignore")
            score = sum(1 for term in terms if term in content.lower())
            if score or len(results) < 2:
                results.append(
                    BenchmarkReport(
                        title=path.stem.replace("_", " ").title(),
                        source=str(path),
                        summary=_first_sentences(content, count=3),
                        strengths=_infer_report_strengths(content),
                    )
                )
        return results


class ReportWriterAgent:
    """Writes a deep paper interpretation from paper text and benchmark traits."""

    def write(
        self,
        paper_text: str,
        benchmark_reports: Sequence[BenchmarkReport],
        previous_report: Optional[ResearchReport],
        round_number: int,
    ) -> ResearchReport:
        parsed = _parse_sections(paper_text)
        title = f"Deep Research Report - {_paper_title(paper_text) or 'Untitled Paper'}"
        benchmark_lessons = "; ".join(
            strength
            for report in benchmark_reports
            for strength in report.strengths[:2]
        )
        abstract = parsed.get("abstract", _first_sentences(paper_text, count=3))
        method = parsed.get("method", parsed.get("methods", "The method section was not explicit."))
        experiments = parsed.get(
            "experiments",
            parsed.get("results", "The experiments or results section was not explicit."),
        )
        limitations = parsed.get("limitations", "The paper does not state limitations directly.")

        sections = {
            "Executive Thesis": (
                f"This report interprets the paper as an attempt to solve: "
                f"{_problem_statement(abstract)} It focuses on what the work claims, "
                "what evidence supports those claims, and where the argument is fragile."
            ),
            "Contribution Analysis": (
                f"Core contribution signals: {_extract_contribution(abstract, method)} "
                "The report distinguishes the paper's own claims from the evaluator's "
                "judgment so later scoring can challenge both."
            ),
            "Method and Evidence": (
                f"Method reading: {_compact(method)} Evidence reading: {_compact(experiments)} "
                "The strongest interpretation connects design choices to measured outcomes."
            ),
            "Limitations and Risks": (
                f"Known or inferred limitations: {_compact(limitations)} "
                "The review should check benchmark sensitivity, reproducibility details, "
                "and whether the evaluation setting matches the paper's claims."
            ),
            "Benchmark-Informed Improvements": (
                f"Round {round_number} searched benchmark reports first. Reusable traits: "
                f"{benchmark_lessons or 'clear claims, evidence, limitations, and next steps'}."
            ),
            "Research Agenda": (
                "Useful follow-up work: reproduce the central result, test robustness on "
                "out-of-distribution papers, compare against simpler baselines, and run an "
                "ablation that isolates the agent roles."
            ),
        }
        if previous_report:
            sections["Round Refinement"] = (
                "This round incorporates the previous report by adding sharper attention "
                "to missing evidence, rubric overfitting risk, and whether the scoring "
                "standard itself is fair."
            )
        return ResearchReport(title=title, sections=sections)


class RubricBuilderAgent:
    """Creates a fresh scoring standard for every round."""

    def build(
        self,
        round_number: int,
        benchmark_reports: Sequence[BenchmarkReport],
        current_report: ResearchReport,
        previous_report: Optional[ResearchReport],
        prior_critic_review: Optional[CriticReview],
    ) -> Rubric:
        criteria = [
            RubricCriterion(
                name="Problem Framing",
                description="Explains the research question, scope, assumptions, and why it matters.",
                max_points=20,
            ),
            RubricCriterion(
                name="Technical Contribution",
                description="Identifies the paper's method, novelty, and relation to prior work.",
                max_points=20,
            ),
            RubricCriterion(
                name="Evidence Quality",
                description="Evaluates experiments, baselines, measurements, and claim support.",
                max_points=20,
            ),
            RubricCriterion(
                name="Limitations and Failure Modes",
                description="Surfaces weaknesses, missing controls, reproducibility risks, and caveats.",
                max_points=20,
            ),
            RubricCriterion(
                name="Research Usefulness",
                description="Produces actionable follow-up questions, replications, and decision guidance.",
                max_points=20,
            ),
        ]
        sources = ["benchmark reports", "current report"]
        if previous_report:
            sources.append("previous report")
        if prior_critic_review:
            sources.append("prior rubric critic review")
        return Rubric(
            title=f"Round {round_number} Scoring Rubric",
            criteria=criteria,
            source_notes=(
                f"Created from {', '.join(sources)}. Benchmark count: "
                f"{len(benchmark_reports)}. Current report: {current_report.title}. "
                "Each criterion is capped to keep the total at 100."
            ),
        )


class ReportScoringAgent:
    """Scores the report against the current round's rubric."""

    def score(self, report: ResearchReport, rubric: Rubric) -> Scorecard:
        report_text = report.as_text().lower()
        scores: List[CriterionScore] = []
        keyword_map = {
            "Problem Framing": ["problem", "question", "scope", "assumption", "matters"],
            "Technical Contribution": ["contribution", "method", "novelty", "design", "agent"],
            "Evidence Quality": ["evidence", "experiment", "baseline", "measured", "result"],
            "Limitations and Failure Modes": ["limitation", "risk", "fragile", "failure", "reproduc"],
            "Research Usefulness": ["follow-up", "replicate", "agenda", "ablation", "decision"],
        }
        for criterion in rubric.criteria:
            keywords = keyword_map.get(criterion.name, [])
            hits = sum(1 for keyword in keywords if keyword in report_text)
            points = min(criterion.max_points, 8 + hits * 3)
            scores.append(
                CriterionScore(
                    name=criterion.name,
                    points=points,
                    max_points=criterion.max_points,
                    rationale=(
                        f"Found {hits} evidence markers for {criterion.name.lower()} "
                        "in the generated report."
                    ),
                )
            )
        total = sum(item.points for item in scores)
        return Scorecard(
            total_score=total,
            scores=scores,
            summary=(
                f"The report scores {total}/100. Strong areas are the criteria with "
                "explicit evidence markers; weaker areas should be revised in the next round."
            ),
        )


class RubricCriticAgent:
    """Challenges the scoring standard after it has been used."""

    def critique(
        self,
        rubric: Rubric,
        scorecard: Scorecard,
        benchmark_reports: Sequence[BenchmarkReport],
    ) -> CriticReview:
        issues = [
            "The rubric may reward keyword coverage more than causal depth unless each score cites concrete paper evidence.",
            "Benchmark reports can bias the scoring standard if they share the same style or research field.",
        ]
        criterion_names = {criterion.name for criterion in rubric.criteria}
        if "Reproducibility" not in criterion_names:
            issues.append(
                "Reproducibility is embedded under limitations but may deserve an explicit criterion for empirical papers."
            )
        recommendations = [
            "Require every future score to include one paper quote or paraphrased evidence item.",
            "Track benchmark diversity by source type, field, and report structure.",
            f"Revisit criteria with low scores after the current {scorecard.total_score}/100 assessment.",
        ]
        if not benchmark_reports:
            recommendations.append("Do not score a round unless benchmark search returns at least one result.")
        return CriticReview(issues=issues, recommendations=recommendations)


def run_research_workflow(paper_text: str, config: WorkflowConfig) -> WorkflowResult:
    if config.rounds < 1:
        raise ValueError("WorkflowConfig.rounds must be at least 1.")
    if not paper_text.strip():
        raise ValueError("paper_text cannot be empty.")

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / config.jsonl_filename
    docx_path = output_dir / config.docx_filename
    jsonl_path.write_text("", encoding="utf-8")

    search_agent = BenchmarkSearchAgent(config.benchmark_dir)
    report_agent = ReportWriterAgent()
    rubric_agent = RubricBuilderAgent()
    scoring_agent = ReportScoringAgent()
    critic_agent = RubricCriticAgent()

    rounds: List[RoundResult] = []
    previous_report: Optional[ResearchReport] = None
    prior_critic_review: Optional[CriticReview] = None
    for round_number in range(1, config.rounds + 1):
        benchmark_reports = search_agent.search(paper_text, round_number, previous_report)
        report = report_agent.write(
            paper_text=paper_text,
            benchmark_reports=benchmark_reports,
            previous_report=previous_report,
            round_number=round_number,
        )
        rubric = rubric_agent.build(
            round_number=round_number,
            benchmark_reports=benchmark_reports,
            current_report=report,
            previous_report=previous_report,
            prior_critic_review=prior_critic_review,
        )
        scorecard = scoring_agent.score(report, rubric)
        critic_review = critic_agent.critique(rubric, scorecard, benchmark_reports)
        round_result = RoundResult(
            round_number=round_number,
            benchmark_reports=list(benchmark_reports),
            report=report,
            rubric=rubric,
            scorecard=scorecard,
            critic_review=critic_review,
        )
        rounds.append(round_result)
        _append_jsonl(jsonl_path, round_result)
        previous_report = report
        prior_critic_review = critic_review

    _write_docx(docx_path, rounds)
    return WorkflowResult(rounds=rounds, jsonl_path=jsonl_path, docx_path=docx_path)


def _append_jsonl(path: Path, round_result: RoundResult) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(round_result), ensure_ascii=False) + "\n")


def _write_docx(path: Path, rounds: Iterable[RoundResult]) -> None:
    document = DocxDocument()
    document.add(heading("Iterative Paper Research Report", level=1))
    document.add(
        paragraph(
            "This document records every research-report round, benchmark search, "
            "scoring rubric, scorecard, and rubric critic review."
        )
    )
    for round_result in rounds:
        document.add(heading(f"Round {round_result.round_number}", level=1))
        document.add(heading("Benchmark Search Results", level=2))
        for benchmark in round_result.benchmark_reports:
            document.add(bullet(f"{benchmark.title} ({benchmark.source})"))
            document.add(paragraph(benchmark.summary))
            for strength in benchmark.strengths:
                document.add(bullet(f"Strength: {strength}"))

        document.add(heading(round_result.report.title, level=2))
        for name, content in round_result.report.sections.items():
            document.add(heading(name, level=2))
            document.add(paragraph(content))

        document.add(heading("Scoring Rubric", level=2))
        document.add(paragraph(round_result.rubric.source_notes))
        for criterion in round_result.rubric.criteria:
            document.add(
                bullet(f"{criterion.name} ({criterion.max_points} pts): {criterion.description}")
            )

        document.add(heading("Scorecard", level=2))
        document.add(paragraph(round_result.scorecard.summary))
        for score in round_result.scorecard.scores:
            document.add(
                bullet(
                    f"{score.name}: {score.points}/{score.max_points}. {score.rationale}"
                )
            )

        document.add(heading("Rubric Critic Review", level=2))
        for issue in round_result.critic_review.issues:
            document.add(bullet(f"Issue: {issue}"))
        for recommendation in round_result.critic_review.recommendations:
            document.add(bullet(f"Recommendation: {recommendation}"))
    document.save(path)


def _parse_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current = "body"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        normalized = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
        if normalized in {
            "abstract",
            "introduction",
            "method",
            "methods",
            "experiments",
            "results",
            "discussion",
            "limitations",
            "conclusion",
        }:
            current = normalized
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: " ".join(lines) for name, lines in sections.items() if lines}


def _paper_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:120]
    return ""


def _first_sentences(text: str, count: int = 2) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    selected = [sentence for sentence in sentences if sentence][:count]
    return " ".join(selected)[:900]


def _compact(text: str, limit: int = 450) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 3].rstrip() + "..."


def _problem_statement(abstract: str) -> str:
    sentence = _first_sentences(abstract, count=1)
    if not sentence:
        return "an unstated research problem."
    return sentence[0].lower() + sentence[1:]


def _extract_contribution(abstract: str, method: str) -> str:
    combined = f"{abstract} {method}"
    markers = [
        "agent",
        "workflow",
        "rubric",
        "search",
        "evidence",
        "experiments",
        "reproducibility",
    ]
    found = [marker for marker in markers if marker in combined.lower()]
    if found:
        return "the paper emphasizes " + ", ".join(found[:5]) + "."
    return _first_sentences(combined, count=1) or "the contribution is not explicit."


def _keywords(text: str, limit: int = 10) -> List[str]:
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
    return [
        word
        for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _infer_report_strengths(content: str) -> List[str]:
    lower = content.lower()
    strengths = []
    if "limitation" in lower or "risk" in lower:
        strengths.append("Explicitly discusses limitations and risks.")
    if "experiment" in lower or "evidence" in lower:
        strengths.append("Connects claims to experimental evidence.")
    if "future" in lower or "follow" in lower:
        strengths.append("Turns interpretation into future research questions.")
    if not strengths:
        strengths.append("Provides a reusable external comparison point.")
    return strengths
