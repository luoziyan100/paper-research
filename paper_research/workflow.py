"""Iterative multi-agent research report workflow."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from paper_research.benchmark import BenchmarkSearchAgent
from paper_research.export import write_docx
from paper_research.models import BenchmarkReport, ContinuousRunConfig, CriterionScore, CriticReview, ResearchReport, RoundResult, Rubric, RubricCriterion, Scorecard, WorkflowConfig, WorkflowResult
from paper_research.scoring import ReportScoringAgent, critic_mentions_reproducibility, low_score_summary
from paper_research.text import compact as _compact, first_sentences as _first_sentences, join_english_phrases as _join_english_phrases, join_phrases as _join_phrases, paper_title as _paper_title, parse_sections as _parse_sections, problem_statement as _problem_statement, zh_evidence_summary as _zh_evidence_summary, zh_limitation_summary as _zh_limitation_summary, zh_method_summary as _zh_method_summary, zh_problem_summary as _zh_problem_summary


class ReportWriterAgent:
    """Writes a deep paper interpretation from paper text and benchmark traits."""

    def write(
        self,
        paper_text: str,
        benchmark_reports: Sequence[BenchmarkReport],
        previous_report: Optional[ResearchReport],
        prior_scorecard: Optional[Scorecard],
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
        benchmark_lessons = "; ".join(dict.fromkeys(
            strength
            for report in benchmark_reports
            for strength in report.strengths[:3]
        ))
        abstract = parsed.get("abstract", _first_sentences(paper_text, count=3))
        method = parsed.get("method", parsed.get("methods", "The method section was not explicit."))
        experiments = parsed.get(
            "experiments",
            parsed.get("results", "The experiments or results section was not explicit."),
        )
        limitations = parsed.get("limitations", "The paper does not state limitations directly.")

        if language == "zh":
            problem_summary = _zh_problem_summary(abstract)
            method_summary = _zh_method_summary(method)
            evidence_summary = _zh_evidence_summary(experiments)
            limitation_summary = _zh_limitation_summary(limitations)
            sections = {
                "执行摘要": (
                    f"本报告将论文理解为一个关于{problem_summary}的研究。"
                    "问题范围包括论文长文本理解、外部对照报告、评分标准迭代和过程记录。"
                    "重要性在于把论文主张、外部对照报告、"
                    "评分标准和批评意见放进可迭代的研究审查流程。"
                ),
                "贡献分析": (
                    f"核心贡献信号：{_extract_contribution(abstract, method, language)}"
                    "本报告区分论文原始主张和评审者解释，让后续评分可以同时挑战二者。"
                ),
                "论文主张与证据账本": (
                    f"主张：论文试图证明{problem_summary}可以通过多角色流程持续改进。"
                    f"\n证据：{evidence_summary}。"
                    f"\n解释：方法部分显示，{method_summary}；实验部分提供了覆盖提升的方向性证据。"
                    "\n验证缺口：当前样例没有给出详细数据表、基线方法设置或显著性检验，"
                    "因此结论只能被视为需要复核的方向性证据。"
                ),
                "方法与证据": (
                    f"方法解读：{method_summary}。证据解读：{evidence_summary}。"
                    "最有价值的解读应把设计选择、评估对象、对照组和测量指标连接起来。"
                ),
                "限制与风险": (
                    f"已知或推断的限制：{limitation_summary}。"
                    "主要失败模式是对照报告质量不足、评分标准过拟合或批评角色没有发现偏差。"
                    "脆弱点包括对照报告敏感性、可复现性细节，以及实验设定是否匹配论文主张。"
                ),
                "关键假设与验证缺口": (
                    "关键假设 1：搜索到的优秀对照报告确实能代表高质量研究解读。"
                    "\n关键假设 2：评分标准会提升报告质量，而不是诱导报告迎合评分项。"
                    "\n关键假设 3：批评智能体能发现评分标准本身的偏差。"
                    "\n需要补充的验证：对照报告多样性统计、跨论文复现实验、人工专家盲评和消融实验。"
                ),
                "基于对照报告的改进": (
                    f"第 {round_number} 轮先搜索优秀研究报告。可复用特征："
                    f"{_join_phrases(benchmark_lessons) or '清晰主张、证据、限制和后续问题'}。"
                ),
                "对照报告质量": _benchmark_quality_summary(
                    benchmark_reports,
                    language,
                ),
                "后续研究议程": (
                    "可继续推进的工作包括：复现核心结果，在分布外论文上测试稳健性，"
                    "与更简单的基线方法对比，并做消融实验来隔离各个智能体角色的贡献。"
                ),
            }
            if previous_report:
                low_score_text = low_score_summary(prior_scorecard, language)
                sections["本轮改进"] = (
                    "本轮结合上一轮报告，进一步关注缺失证据、评分标准过拟合风险，"
                    "以及评分标准本身是否公平。"
                    f"上一轮低分项：{low_score_text}。"
                )
            return ResearchReport(title=title, sections=sections)

        sections = {
            "Executive Thesis": (
                f"Research question: how should we evaluate {_problem_statement(abstract)} "
                "Scope: the report covers the paper's claims, benchmark comparisons, rubric iteration, "
                "evidence support, and fragile assumptions. "
                "Why it matters: stronger problem framing makes the later evidence and limitation review "
                "auditable instead of a generic summary."
            ),
            "Contribution Analysis": (
                f"Core contribution signals: {_extract_contribution(abstract, method)} "
                "The report distinguishes the paper's own claims from the evaluator's "
                "judgment so later scoring can challenge both."
            ),
            "Claim-Evidence Ledger": (
                f"Claim: the paper argues that {_problem_statement(abstract)} can be "
                "improved through the proposed workflow or method.\n"
                f"Evidence: {_compact(experiments) if experiments else _compact(abstract)}\n"
                f"Interpretation: method evidence shows {_compact(method)}\n"
                "Verification gap: the report should still inspect baseline settings, "
                "measurement design, statistical support, and reproducibility details."
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
                f"{_join_english_phrases(benchmark_lessons) or 'clear claims, evidence, limitations, and next steps'}."
            ),
            "Benchmark Quality": _benchmark_quality_summary(benchmark_reports, language),
            "Key Assumptions and Verification Gaps": (
                "Assumption 1: retrieved benchmark reports represent high-quality analysis. "
                "Assumption 2: the rubric improves analysis depth instead of rewarding rubric gaming. "
                "Assumption 3: the critic can detect weaknesses in the rubric itself. "
                "Needed validation: benchmark diversity checks, cross-paper replication, expert blind review, "
                "and ablations over agent roles."
            ),
            "Research Agenda": (
                "Useful follow-up work: reproduce the central result, test robustness on "
                "out-of-distribution papers, compare against simpler baselines, and run an "
                "ablation that isolates the agent roles."
            ),
        }
        if previous_report:
            low_score_text = low_score_summary(prior_scorecard, language)
            sections["Round Refinement"] = (
                "This round incorporates the previous report by adding sharper attention "
                "to missing evidence, rubric overfitting risk, and whether the scoring "
                "standard itself is fair. "
                f"Prior low-score items: {low_score_text}."
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
        external_count = sum(
            1
            for report in benchmark_reports
            if _raw_benchmark_source_type(report) != "built-in"
        )
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
                    description="评价实验、基线方法、测量方式和主张支撑。",
                    max_points=20,
                ),
                RubricCriterion(
                    name="限制与失败模式",
                    description="揭示弱点、缺失控制、可复现性风险和注意事项。",
                    max_points=20,
                ),
                RubricCriterion(
                    name=(
                        "可复现性与证据引用"
                        if critic_mentions_reproducibility(prior_critic_review)
                        else "研究价值"
                    ),
                    description=(
                        "要求报告引用具体论文证据，并说明复现实验、数据、基线方法和评估缺口。"
                        if critic_mentions_reproducibility(prior_critic_review)
                        else "产出可执行的后续问题、复现实验和决策建议。"
                    ),
                    max_points=20,
                ),
            ]
            sources = ["对照报告", "当前报告"]
            if previous_report:
                sources.append("上一轮报告")
            if prior_critic_review:
                sources.append("上一轮评分标准批评")
            return Rubric(
                title=f"第 {round_number} 轮评分标准",
                criteria=criteria,
                source_notes=(
                    f"基于{'、'.join(sources)}生成。对照报告数量："
                    f"{len(benchmark_reports)}。外部来源数量：{external_count}。"
                    f"当前报告：{current_report.title}。"
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
                name=(
                    "Reproducibility and Evidence Citation"
                    if critic_mentions_reproducibility(prior_critic_review)
                    else "Research Usefulness"
                ),
                description=(
                    "Requires concrete paper evidence and explains replication, data, baseline, and evaluation gaps."
                    if critic_mentions_reproducibility(prior_critic_review)
                    else "Produces actionable follow-up questions, replications, and decision guidance."
                ),
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
                f"{len(benchmark_reports)}. External source count: {external_count}. "
                f"Current report: {current_report.title}. "
                "Each criterion is capped to keep the total at 100."
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
                "如果对照报告来自相同风格或相同领域，评分标准可能被样式偏见污染。",
            ]
            criterion_names = {criterion.name for criterion in rubric.criteria}
            if not any("可复现性" in name for name in criterion_names):
                issues.append("可复现性目前嵌在限制项中，对实证论文可能应该单独成为评分项。")
            recommendations = [
                "要求未来每个评分都包含一个论文证据引用或转述。",
                "记录对照报告的来源类型、领域和报告结构，避免样本单一。",
                f"基于当前 {scorecard.total_score}/100 的评估，优先复查低分项。",
            ]
            if not benchmark_reports:
                recommendations.append("如果对照报告搜索没有返回结果，就不要进入评分环节。")
            elif all(_raw_benchmark_source_type(report) == "built-in" for report in benchmark_reports):
                recommendations.append("本轮仅使用内置回退模式，下一轮应优先接入真实外部对照报告。")
            return CriticReview(issues=issues, recommendations=recommendations)

        issues = [
            "The rubric may reward keyword coverage more than causal depth unless each score cites concrete paper evidence.",
            "Benchmark reports can bias the scoring standard if they share the same style or research field.",
        ]
        criterion_names = {criterion.name for criterion in rubric.criteria}
        if not any("Reproducibility" in name for name in criterion_names):
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
        elif all(_raw_benchmark_source_type(report) == "built-in" for report in benchmark_reports):
            recommendations.append(
                "This round used only built-in fallback patterns; prioritize real external benchmark reports next."
            )
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
    prior_scorecard: Optional[Scorecard] = None
    for round_number in range(1, config.rounds + 1):
        benchmark_reports = search_agent.search(paper_text, round_number, previous_report)
        report = report_agent.write(
            paper_text=paper_text,
            benchmark_reports=benchmark_reports,
            previous_report=previous_report,
            prior_scorecard=prior_scorecard,
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
        prior_scorecard = scorecard

    write_docx(docx_path, rounds, config.language)
    return WorkflowResult(rounds=rounds, jsonl_path=jsonl_path, docx_path=docx_path)


def run_continuous_workflow(
    paper_text: str,
    config: WorkflowConfig,
    continuous_config: ContinuousRunConfig,
    clock: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
) -> WorkflowResult:
    if config.rounds < 1:
        raise ValueError("WorkflowConfig.rounds must be at least 1.")
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
        rounds = _load_jsonl_rounds(jsonl_path, config.language)
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
    prior_scorecard = rounds[-1].scorecard if rounds else None
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
            prior_scorecard=prior_scorecard,
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
        write_docx(docx_path, rounds, config.language)
        previous_report = report
        prior_critic_review = critic_review
        prior_scorecard = scorecard
        new_rounds += 1

        if continuous_config.max_rounds is not None and new_rounds >= continuous_config.max_rounds:
            break
        if continuous_config.max_rounds is None and clock() >= deadline:
            break
        sleeper(continuous_config.sleep_seconds)

    if not docx_path.exists():
        write_docx(docx_path, rounds, config.language)
    return WorkflowResult(rounds=rounds, jsonl_path=jsonl_path, docx_path=docx_path)


def _append_jsonl(path: Path, round_result: RoundResult) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(round_result), ensure_ascii=False) + "\n")


def _load_jsonl_rounds(path: Path, language: str = "en") -> List[RoundResult]:
    if not path.exists():
        return []
    rounds = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if raw_line.strip():
            try:
                data = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Could not load existing JSONL {path}: invalid JSON on line {line_number}."
                ) from exc
            try:
                round_result = _round_from_dict(data, language)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Could not load existing JSONL {path}: invalid round record on line {line_number}."
                ) from exc
            expected_round_number = len(rounds) + 1
            if round_result.round_number != expected_round_number:
                raise ValueError(
                    f"Could not load existing JSONL {path}: non-contiguous round number on line {line_number}."
                )
            rounds.append(round_result)
    return rounds


def _round_from_dict(data: Dict[str, object], language: str = "en") -> RoundResult:
    benchmark_reports = [
        BenchmarkReport(
            title=str(item["title"]),
            source=str(item["source"]),
            summary=str(item["summary"]),
            strengths=_string_list(item["strengths"]),
            source_type=str(
                item.get(  # type: ignore[union-attr]
                    "source_type",
                    _infer_benchmark_source_type(str(item["source"])),
                )
            ),
            search_note=str(
                item.get(  # type: ignore[union-attr]
                    "search_note",
                    _legacy_search_note(str(item["source"]), language),
                )
            ),
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
        issues=_string_list(critic_data["issues"]),  # type: ignore[index]
        recommendations=_string_list(critic_data["recommendations"]),  # type: ignore[index]
    )
    return RoundResult(
        round_number=int(data["round_number"]),
        benchmark_reports=benchmark_reports,
        report=report,
        rubric=rubric,
        scorecard=scorecard,
        critic_review=critic_review,
    )


def _benchmark_quality_summary(
    benchmark_reports: Sequence[BenchmarkReport],
    language: str,
) -> str:
    source_count = len(benchmark_reports)
    external_count = sum(
        1
        for report in benchmark_reports
        if _raw_benchmark_source_type(report) != "built-in"
    )
    source_types = sorted({_benchmark_source_type(report, language) for report in benchmark_reports})
    strength_text = " ".join(
        strength
        for report in benchmark_reports
        for strength in report.strengths
    )
    if language == "zh":
        coverage = []
        if "主张" in strength_text or "claims" in strength_text.lower():
            coverage.append("主张-证据")
        if "baseline" in strength_text.lower() or "基线" in strength_text or "消融" in strength_text:
            coverage.append("方法审计")
        if "限制" in strength_text or "limitations" in strength_text.lower():
            coverage.append("限制/可复现性")
        if not coverage:
            coverage.append("通用研究报告模式")
        source_type_text = "、".join(source_types) if source_types else "无"
        built_in_only_note = (
            "注意：本轮仅使用内置回退模式，结论不应视为外部文献对照。"
            if source_count and external_count == 0
            else ""
        )
        return (
            f"来源数量：{source_count}。外部来源数量：{external_count}。"
            f"来源类型：{source_type_text}。"
            f"覆盖维度：{'、'.join(coverage)}。"
            f"{built_in_only_note}"
            "如果后续接入真实网页或本地对照报告，应继续记录来源多样性和领域差异。"
        )

    coverage = []
    lower_strengths = strength_text.lower()
    if "claim" in lower_strengths:
        coverage.append("claim-evidence")
    if "baseline" in lower_strengths or "ablation" in lower_strengths:
        coverage.append("methodology audit")
    if "limitation" in lower_strengths or "reproduc" in lower_strengths:
        coverage.append("limitations/reproducibility")
    if not coverage:
        coverage.append("general research-report pattern")
    source_type_text = ", ".join(source_types) if source_types else "none"
    built_in_only_note = (
        "Only built-in fallback patterns were used; this is not external literature evidence. "
        if source_count and external_count == 0
        else ""
    )
    return (
        f"Source count: {source_count}. External source count: {external_count}. "
        f"Source types: {source_type_text}. "
        f"Coverage: {', '.join(coverage)}. Future web or local benchmarks should "
        f"{built_in_only_note}"
        "continue tracking source diversity and field differences."
    )


def _benchmark_source_type(report: BenchmarkReport, language: str) -> str:
    source_type = _raw_benchmark_source_type(report)
    if source_type == "built-in":
        return "内置回退模式" if language == "zh" else "built-in fallback"
    if source_type == "web":
        return "网页搜索" if language == "zh" else "web search"
    if source_type == "local":
        return "本地对照报告" if language == "zh" else "local benchmark"
    return "未知来源" if language == "zh" else "unknown source"


def _raw_benchmark_source_type(report: BenchmarkReport) -> str:
    return report.source_type or _infer_benchmark_source_type(report.source)


def _infer_benchmark_source_type(source: str) -> str:
    if source.startswith("built-in://"):
        return "built-in"
    if source.startswith(("http://", "https://", "web-search://")):
        return "web"
    return "local"


def _legacy_search_note(source: str, language: str = "en") -> str:
    if language == "zh":
        return f"从缺少对照报告追踪元数据的旧版 JSONL 恢复：{source}。"
    return f"Recovered from legacy JSONL without benchmark trace metadata: {source}."


def _string_list(value: object) -> List[str]:
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]  # type: ignore[union-attr]


def _validate_language(language: str) -> None:
    if language not in {"en", "zh"}:
        raise ValueError("WorkflowConfig.language must be 'en' or 'zh'.")


def _extract_contribution(abstract: str, method: str, language: str = "en") -> str:
    combined = f"{abstract} {method}"
    marker_labels = [
        ("multi-agent", "多智能体", ["multi-agent", "multi agent", "多智能体"]),
        ("agent", "智能体", ["agent", "智能体"]),
        ("workflow", "工作流", ["workflow", "流程", "工作流"]),
        ("rubric", "评分标准", ["rubric", "评分标准"]),
        ("search", "检索", ["search", "retrieval", "检索"]),
        ("evidence", "证据", ["evidence", "证据"]),
        ("experiments", "实验", ["experiment", "experiments", "实验"]),
        ("reproducibility", "可复现性", ["reproducibility", "可复现性", "复现"]),
    ]
    lower_combined = combined.lower()
    found = []
    for marker, zh_label, aliases in marker_labels:
        if any(alias in lower_combined for alias in aliases):
            if zh_label == "智能体" and any(label == "多智能体" for _, label in found):
                continue
            found.append((marker, zh_label))
    if found:
        if language == "zh":
            return "论文强调" + "、".join(label for _, label in found[:5]) + "。"
        return "the paper emphasizes " + ", ".join(marker for marker, _ in found[:5]) + "."
    if language == "zh":
        return _first_sentences(combined, count=1) or "论文贡献没有明确表述。"
    return _first_sentences(combined, count=1) or "the contribution is not explicit."
