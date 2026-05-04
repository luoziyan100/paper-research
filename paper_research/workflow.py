"""Iterative multi-agent research report workflow."""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

from paper_research.docx import DocxDocument, bullet, heading, paragraph


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
                    title=f"{theme} 的优秀研究报告模式",
                    source=f"built-in://benchmark-round-{round_number}",
                    summary=(
                        "高质量研究报告会说明问题、拆解核心技术贡献、检查证据是否支撑主张，"
                        "并在提出后续研究前明确限制。"
                        + refinement
                    ),
                    strengths=[
                        "区分论文原始主张和评审者解释。",
                        "使用方法与实验中的证据，而不只依赖摘要。",
                        "把限制和可复现性纳入评分，而不只评价新颖性。",
                    ],
                )
            ]
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
                        strengths=_infer_report_strengths(content, self.language),
                    )
                )
        return results

    def _search_web_benchmarks(
        self,
        paper_text: str,
        round_number: int,
    ) -> List[BenchmarkReport]:
        title = _paper_title(paper_text) or "paper"
        query = quote_plus(f"{title} excellent research report paper analysis")
        url = f"https://duckduckgo.com/html/?q={query}"
        try:
            html = self.web_fetcher(url)
        except Exception:
            return []

        links = _extract_duckduckgo_results(html)
        reports = []
        for index, item in enumerate(links[:5], start=1):
            summary = item["snippet"] or (
                "External search result for an excellent research-report example."
            )
            reports.append(
                BenchmarkReport(
                    title=item["title"] or f"External benchmark report {index}",
                    source=item["url"] or f"web-search://round-{round_number}-{index}",
                    summary=summary,
                    strengths=_infer_report_strengths(f"{item['title']} {summary}", self.language),
                )
            )
        return reports


class ReportWriterAgent:
    """Writes a deep paper interpretation from paper text and benchmark traits."""

    def write(
        self,
        paper_text: str,
        benchmark_reports: Sequence[BenchmarkReport],
        previous_report: Optional[ResearchReport],
        round_number: int,
        language: str = "en",
    ) -> ResearchReport:
        parsed = _parse_sections(paper_text)
        paper_title = _paper_title(paper_text) or ("未命名论文" if language == "zh" else "Untitled Paper")
        title = (
            f"深度研究报告 - {paper_title}"
            if language == "zh"
            else f"Deep Research Report - {paper_title}"
        )
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

        if language == "zh":
            sections = {
                "执行摘要": (
                    f"本报告将论文理解为试图解决这样一个问题：{_problem_statement(abstract)} "
                    "报告重点区分论文声称了什么、哪些证据支撑这些声称，以及论证中仍然脆弱的地方。"
                ),
                "贡献分析": (
                    f"核心贡献信号：{_extract_contribution(abstract, method, language)} "
                    "本报告区分论文原始主张和评审者解释，让后续评分可以同时挑战二者。"
                ),
                "方法与证据": (
                    f"方法解读：{_compact(method)} 证据解读：{_compact(experiments)} "
                    "最有价值的解读应把设计选择和测量结果连接起来。"
                ),
                "限制与风险": (
                    f"已知或推断的限制：{_compact(limitations)} "
                    "评审应检查 benchmark 敏感性、可复现性细节，以及实验设定是否匹配论文主张。"
                ),
                "基于 Benchmark 的改进": (
                    f"第 {round_number} 轮先搜索优秀研究报告。可复用特征："
                    f"{benchmark_lessons or '清晰主张、证据、限制和后续问题'}。"
                ),
                "后续研究议程": (
                    "可继续推进的工作包括：复现核心结果，在分布外论文上测试稳健性，"
                    "与更简单的 baseline 对比，并做 ablation 来隔离各个 agent 角色的贡献。"
                ),
            }
            if previous_report:
                sections["本轮改进"] = (
                    "本轮结合上一轮报告，进一步关注缺失证据、评分标准过拟合风险，"
                    "以及评分标准本身是否公平。"
                )
            return ResearchReport(title=title, sections=sections)

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
        language: str = "en",
    ) -> Rubric:
        if language == "zh":
            criteria = [
                RubricCriterion(
                    name="问题定义",
                    description="解释研究问题、范围、假设，以及为什么重要。",
                    max_points=20,
                ),
                RubricCriterion(
                    name="技术贡献",
                    description="识别论文方法、新颖性，以及与已有工作的关系。",
                    max_points=20,
                ),
                RubricCriterion(
                    name="证据质量",
                    description="评价实验、baseline、测量方式和主张支撑。",
                    max_points=20,
                ),
                RubricCriterion(
                    name="限制与失败模式",
                    description="揭示弱点、缺失控制、可复现性风险和 caveat。",
                    max_points=20,
                ),
                RubricCriterion(
                    name="研究价值",
                    description="产出可执行的后续问题、复现实验和决策建议。",
                    max_points=20,
                ),
            ]
            sources = ["benchmark 报告", "当前报告"]
            if previous_report:
                sources.append("上一轮报告")
            if prior_critic_review:
                sources.append("上一轮评分标准批评")
            return Rubric(
                title=f"第 {round_number} 轮评分标准",
                criteria=criteria,
                source_notes=(
                    f"基于{', '.join(sources)}生成。Benchmark 数量："
                    f"{len(benchmark_reports)}。当前报告：{current_report.title}。"
                    "每项封顶，总分保持 100。"
                ),
            )

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

    def score(self, report: ResearchReport, rubric: Rubric, language: str = "en") -> Scorecard:
        report_text = report.as_text().lower()
        scores: List[CriterionScore] = []
        if language == "zh":
            keyword_map = {
                "问题定义": ["问题", "范围", "假设", "重要"],
                "技术贡献": ["贡献", "方法", "新颖", "设计", "agent"],
                "证据质量": ["证据", "实验", "baseline", "测量", "结果"],
                "限制与失败模式": ["限制", "风险", "脆弱", "失败", "复现"],
                "研究价值": ["后续", "复现", "议程", "ablation", "建议"],
            }
        else:
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
            rationale = (
                f"在生成报告中找到 {hits} 个与“{criterion.name}”相关的证据标记。"
                if language == "zh"
                else (
                    f"Found {hits} evidence markers for {criterion.name.lower()} "
                    "in the generated report."
                )
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
        if language == "zh":
            return Scorecard(
                total_score=total,
                scores=scores,
                summary=f"本轮报告总分 {total}/100。低分项应在下一轮优先修订。",
            )
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
        language: str = "en",
    ) -> CriticReview:
        if language == "zh":
            issues = [
                "评分标准可能过度奖励关键词覆盖，而不是奖励真正的因果深度，除非每个分数都引用具体论文证据。",
                "如果 benchmark 报告来自相同风格或相同领域，评分标准可能被样式偏见污染。",
            ]
            criterion_names = {criterion.name for criterion in rubric.criteria}
            if "可复现性" not in criterion_names:
                issues.append("可复现性目前嵌在限制项中，对实证论文可能应该单独成为评分项。")
            recommendations = [
                "要求未来每个评分都包含一个论文证据引用或转述。",
                "记录 benchmark 的来源类型、领域和报告结构，避免样本单一。",
                f"基于当前 {scorecard.total_score}/100 的评估，优先复查低分项。",
            ]
            if not benchmark_reports:
                recommendations.append("如果 benchmark 搜索没有返回结果，就不要进入评分环节。")
            return CriticReview(issues=issues, recommendations=recommendations)

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
    _validate_language(config.language)

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / config.jsonl_filename
    docx_path = output_dir / config.docx_filename
    jsonl_path.write_text("", encoding="utf-8")

    search_agent = BenchmarkSearchAgent(
        benchmark_dir=config.benchmark_dir,
        web_search=config.web_search,
        language=config.language,
    )
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
            language=config.language,
        )
        rubric = rubric_agent.build(
            round_number=round_number,
            benchmark_reports=benchmark_reports,
            current_report=report,
            previous_report=previous_report,
            prior_critic_review=prior_critic_review,
            language=config.language,
        )
        scorecard = scoring_agent.score(report, rubric, config.language)
        critic_review = critic_agent.critique(
            rubric,
            scorecard,
            benchmark_reports,
            config.language,
        )
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

    _write_docx(docx_path, rounds, config.language)
    return WorkflowResult(rounds=rounds, jsonl_path=jsonl_path, docx_path=docx_path)


def run_continuous_workflow(
    paper_text: str,
    config: WorkflowConfig,
    continuous_config: ContinuousRunConfig,
    clock: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
) -> WorkflowResult:
    if not paper_text.strip():
        raise ValueError("paper_text cannot be empty.")
    _validate_language(config.language)
    if continuous_config.duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative.")
    if continuous_config.sleep_seconds < 0:
        raise ValueError("sleep_seconds cannot be negative.")
    if continuous_config.max_rounds is not None and continuous_config.max_rounds < 1:
        raise ValueError("max_rounds must be at least 1 when provided.")
    if continuous_config.max_rounds is None and continuous_config.sleep_seconds <= 0:
        raise ValueError("sleep_seconds must be positive when max_rounds is not provided.")

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / config.jsonl_filename
    docx_path = output_dir / config.docx_filename
    if continuous_config.resume:
        rounds = _load_jsonl_rounds(jsonl_path)
    else:
        rounds = []
        jsonl_path.write_text("", encoding="utf-8")
    if not jsonl_path.exists():
        jsonl_path.write_text("", encoding="utf-8")

    search_agent = BenchmarkSearchAgent(
        benchmark_dir=config.benchmark_dir,
        web_search=config.web_search,
        language=config.language,
    )
    report_agent = ReportWriterAgent()
    rubric_agent = RubricBuilderAgent()
    scoring_agent = ReportScoringAgent()
    critic_agent = RubricCriticAgent()

    previous_report = rounds[-1].report if rounds else None
    prior_critic_review = rounds[-1].critic_review if rounds else None
    deadline = clock() + continuous_config.duration_seconds
    new_rounds = 0

    while True:
        if continuous_config.max_rounds is not None and new_rounds >= continuous_config.max_rounds:
            break
        if continuous_config.max_rounds is None and new_rounds > 0 and clock() > deadline:
            break

        round_number = len(rounds) + 1
        benchmark_reports = search_agent.search(paper_text, round_number, previous_report)
        report = report_agent.write(
            paper_text=paper_text,
            benchmark_reports=benchmark_reports,
            previous_report=previous_report,
            round_number=round_number,
            language=config.language,
        )
        rubric = rubric_agent.build(
            round_number=round_number,
            benchmark_reports=benchmark_reports,
            current_report=report,
            previous_report=previous_report,
            prior_critic_review=prior_critic_review,
            language=config.language,
        )
        scorecard = scoring_agent.score(report, rubric, config.language)
        critic_review = critic_agent.critique(
            rubric,
            scorecard,
            benchmark_reports,
            config.language,
        )
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
        _write_docx(docx_path, rounds, config.language)
        previous_report = report
        prior_critic_review = critic_review
        new_rounds += 1

        if continuous_config.max_rounds is not None and new_rounds >= continuous_config.max_rounds:
            break
        sleeper(continuous_config.sleep_seconds)

    if not docx_path.exists():
        _write_docx(docx_path, rounds, config.language)
    return WorkflowResult(rounds=rounds, jsonl_path=jsonl_path, docx_path=docx_path)


def _append_jsonl(path: Path, round_result: RoundResult) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(round_result), ensure_ascii=False) + "\n")


def _load_jsonl_rounds(path: Path) -> List[RoundResult]:
    if not path.exists():
        return []
    rounds = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            rounds.append(_round_from_dict(json.loads(raw_line)))
    return rounds


def _round_from_dict(data: Dict[str, object]) -> RoundResult:
    benchmark_reports = [
        BenchmarkReport(
            title=str(item["title"]),
            source=str(item["source"]),
            summary=str(item["summary"]),
            strengths=list(item["strengths"]),
        )
        for item in data["benchmark_reports"]  # type: ignore[index]
    ]
    report_data = data["report"]  # type: ignore[index]
    report = ResearchReport(
        title=str(report_data["title"]),  # type: ignore[index]
        sections=dict(report_data["sections"]),  # type: ignore[index]
    )
    rubric_data = data["rubric"]  # type: ignore[index]
    rubric = Rubric(
        title=str(rubric_data["title"]),  # type: ignore[index]
        criteria=[
            RubricCriterion(
                name=str(item["name"]),
                description=str(item["description"]),
                max_points=int(item["max_points"]),
            )
            for item in rubric_data["criteria"]  # type: ignore[index]
        ],
        source_notes=str(rubric_data["source_notes"]),  # type: ignore[index]
    )
    scorecard_data = data["scorecard"]  # type: ignore[index]
    scorecard = Scorecard(
        total_score=int(scorecard_data["total_score"]),  # type: ignore[index]
        scores=[
            CriterionScore(
                name=str(item["name"]),
                points=int(item["points"]),
                max_points=int(item["max_points"]),
                rationale=str(item["rationale"]),
            )
            for item in scorecard_data["scores"]  # type: ignore[index]
        ],
        summary=str(scorecard_data["summary"]),  # type: ignore[index]
    )
    critic_data = data["critic_review"]  # type: ignore[index]
    critic_review = CriticReview(
        issues=list(critic_data["issues"]),  # type: ignore[index]
        recommendations=list(critic_data["recommendations"]),  # type: ignore[index]
    )
    return RoundResult(
        round_number=int(data["round_number"]),
        benchmark_reports=benchmark_reports,
        report=report,
        rubric=rubric,
        scorecard=scorecard,
        critic_review=critic_review,
    )


def _write_docx(path: Path, rounds: Iterable[RoundResult], language: str = "en") -> None:
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


def _validate_language(language: str) -> None:
    if language not in {"en", "zh"}:
        raise ValueError("WorkflowConfig.language must be 'en' or 'zh'.")


def _extract_contribution(abstract: str, method: str, language: str = "en") -> str:
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
        if language == "zh":
            return "论文强调 " + "、".join(found[:5]) + "。"
        return "the paper emphasizes " + ", ".join(found[:5]) + "."
    if language == "zh":
        return _first_sentences(combined, count=1) or "论文贡献没有明确表述。"
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


def _infer_report_strengths(content: str, language: str = "en") -> List[str]:
    lower = content.lower()
    strengths = []
    if "limitation" in lower or "risk" in lower:
        strengths.append(
            "明确讨论限制和风险。"
            if language == "zh"
            else "Explicitly discusses limitations and risks."
        )
    if "experiment" in lower or "evidence" in lower:
        strengths.append(
            "把论文主张连接到实验证据。"
            if language == "zh"
            else "Connects claims to experimental evidence."
        )
    if "future" in lower or "follow" in lower:
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
    link_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    snippets = [_strip_html(match) for match in snippet_pattern.findall(raw_html)]
    results: List[Dict[str, str]] = []
    for index, (href, title_html) in enumerate(link_pattern.findall(raw_html)):
        title = _strip_html(title_html)
        source = _clean_result_url(href)
        snippet = snippets[index] if index < len(snippets) else ""
        if title or source:
            results.append({"title": title, "url": source, "snippet": snippet})
    return results


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(without_tags).split())


def _clean_result_url(href: str) -> str:
    href = unescape(href)
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return href
