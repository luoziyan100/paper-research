import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.parse import unquote_plus

from paper_research.workflow import (
    BenchmarkSearchAgent,
    ContinuousRunConfig,
    ReportWriterAgent,
    ReportScoringAgent,
    RubricCriticAgent,
    WorkflowConfig,
    run_continuous_workflow,
    run_research_workflow,
)
from paper_research.models import BenchmarkReport, ResearchReport, Rubric, RubricCriterion
from paper_research.text import first_sentences


PAPER_TEXT = """
Title: Retrieval Augmented Agents for Scientific Analysis

Abstract
We study an agent workflow that reads long papers, compares the current
analysis with external benchmark reports, updates a scoring rubric, and
records every iteration.

Method
The system separates report writing, rubric design, scoring, and rubric
critique into independent roles. Each round starts by searching for high
quality public research reports and extracting reusable evaluation traits.

Experiments
Across three papers, iterative scoring improved coverage of assumptions,
limitations, and reproducibility details.

Limitations
The workflow depends on the quality of retrieved benchmark reports and can
overfit the rubric if a critic does not challenge the criteria.
"""

CHINESE_PAPER_TEXT = """
标题：多智能体论文审查系统

摘要
本文研究一个多智能体系统，用于阅读长论文、检索优秀研究报告、生成评分标准并记录每轮审查。

方法
系统把报告写作、评分标准生成、报告评分和评分标准批评拆分为多角色流程。每轮先检索外部优秀报告，再结合当前报告更新评分标准。

实验
在三篇论文上，迭代审查提高了对假设、限制、baseline 和可复现性细节的覆盖。

局限
系统依赖对照报告质量，也可能让评分标准过拟合当前报告。
"""

NUMBERED_CHINESE_PAPER_TEXT = """
标题：编号标题论文审查系统

一、摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

二、方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

三、实验
实验显示该系统提高了 baseline、限制和可复现性细节覆盖。

四、局限
系统仍依赖对照报告质量。
"""

PAREN_NUMBERED_CHINESE_PAPER_TEXT = """
标题：括号编号论文审查系统

（一）摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

（二）方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

(三) 实验
实验显示该系统提高了 baseline、限制和可复现性细节覆盖。

(四) 局限
系统仍依赖对照报告质量。
"""

INLINE_CHINESE_PAPER_TEXT = """
标题：行内标题论文审查系统

摘要：本文研究一个多智能体系统，用于生成中文论文研究报告。
方法：系统把报告写作、评分标准生成和证据审查拆分为多角色流程。
实验：实验显示该系统提高了 baseline、限制和可复现性细节覆盖。
局限：系统仍依赖对照报告质量。
"""

CHINESE_EVALUATION_HEADING_PAPER_TEXT = """
标题：中文评估标题论文

摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

评估
评估显示该系统提高了基线方法、限制和可复现性细节覆盖。

局限
系统仍依赖对照报告质量。
"""

CHINESE_TECHNICAL_ROUTE_PAPER_TEXT = """
标题：中文技术路线论文

摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

技术路线
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

评估
评估显示该系统提高了基线方法和可复现性细节覆盖。

不足
系统仍依赖对照报告质量。
"""

CHINESE_ABLATION_HEADING_PAPER_TEXT = """
标题：中文消融标题论文

摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

消融实验
消融实验显示评分标准和批评角色提高了基线方法、限制和可复现性细节覆盖。

不足
系统仍依赖对照报告质量。
"""

SPACE_NUMBERED_CHINESE_PAPER_TEXT = """
标题：空格编号论文审查系统

一 摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

二 方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

三 实验
实验显示该系统提高了 baseline、限制和可复现性细节覆盖。

四 局限
系统仍依赖对照报告质量。
"""

APPROACH_EVALUATION_PAPER_TEXT = """
Title: Contrastive Pretraining for Reliable Reasoning

Abstract
We introduce a contrastive pretraining system for reliable reasoning over
multi-hop questions.

Approach
The model combines contrastive pretraining, retrieval filtering, and verifier
reranking to reduce unsupported intermediate claims.

Evaluation
On MMLU and HotpotQA, the system improves factual consistency and calibration
over retrieval-only baselines.

Limitations
The approach depends on curated negative examples and has not been tested on
low-resource domains.
"""

ROMAN_NUMBERED_ENGLISH_PAPER_TEXT = """
Title: Roman Numbered Parsing

I. Abstract
We study a retrieval workflow for long paper analysis.

II. Method
The method combines retrieval filtering and verifier reranking.

III. Evaluation
On MMLU, the workflow improves factual consistency.

IV. Limitations
The approach depends on curated negative examples.
"""

ABLATION_HEADING_PAPER_TEXT = """
Title: Ablation Heading Parsing

Abstract
We study a verifier workflow for reliable reasoning.

Method
The method combines retrieval filtering and verifier reranking.

Ablation Study
The ablation shows verifier reranking improves factual consistency.

Limitations
The approach depends on curated negative examples.
"""

MARKDOWN_TITLE_PAPER_TEXT = """
# Markdown Research Paper

Abstract
We study markdown parsing for research reports.

Method
The system reads markdown headings without leaking markup into titles.

Experiments
The parser keeps report titles clean.

Limitations
The sample is small.
"""

MARKDOWN_CHINESE_TITLE_PAPER_TEXT = """
# 标题：Markdown 中文论文

摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

实验
实验显示该系统提高了 baseline、限制和可复现性细节覆盖。

局限
系统仍依赖对照报告质量。
"""

MARKDOWN_BOLD_TITLE_PAPER_TEXT = """
# **Title: Bold Markdown Paper**

Abstract
We study markdown title cleanup for research reports.

Method
The system reads emphasized markdown headings without leaking markup.

Experiments
The parser keeps report titles clean.

Limitations
The sample is small.
"""

MARKDOWN_CHINESE_SECTION_PAPER_TEXT = """
# 标题：Markdown 中文章节论文

## 摘要
本文研究一个多智能体系统，用于生成中文论文研究报告。

## 方法
系统把报告写作、评分标准生成和证据审查拆分为多角色流程。

## 实验
实验显示该系统提高了基线方法、限制和可复现性细节覆盖。

## 局限
系统仍依赖对照报告质量。
"""

MARKDOWN_CHINESE_BOLD_SECTION_PAPER_TEXT = """
# 标题：Markdown 中文粗体章节论文

## **摘要**
本文研究图神经网络鲁棒推理报告。

## **方法**
模型结合结构编码和路径验证来减少错误推理链。

## **评估**
评估显示该系统提高了复杂关系推理准确率。

## **局限**
系统依赖高质量图结构，跨领域泛化仍需验证。
"""

GENERAL_CHINESE_PAPER_TEXT = """
标题：可靠推理的对比预训练

摘要
本文提出一种对比预训练方法，用于提升多跳问题回答中的可靠推理。

方法
模型结合对比预训练、检索过滤和验证器重排序，减少不受支持的中间推理主张。

评估
在 MMLU 和 HotpotQA 上，该系统相对检索基线提高了事实一致性和校准效果。

局限
该方法依赖人工构造的负样本，尚未在低资源领域验证。
"""

CHINESE_INTRO_LE_PAPER_TEXT = """
标题：图神经网络鲁棒推理

摘要
本文提出了一种图神经网络方法，用于提升复杂关系推理的鲁棒性。

方法
模型结合结构编码和路径验证来减少错误推理链。

实验
实验显示该方法在多个关系推理数据集上提高了准确率。

局限
该方法依赖高质量图结构，跨领域泛化仍需验证。
"""


class ResearchWorkflowTest(unittest.TestCase):
    def test_first_sentences_splits_chinese_punctuation(self):
        text = "第一句说明研究问题。第二句说明方法！第三句说明限制？"

        summary = first_sentences(text, count=2)

        self.assertEqual(summary, "第一句说明研究问题。 第二句说明方法！")

    def test_first_sentences_preserves_english_abbreviations_without_space(self):
        text = "The system uses e.g. retrieval filtering. It then scores the report."

        summary = first_sentences(text, count=1)

        self.assertEqual(summary, "The system uses e.g. retrieval filtering.")

    def test_first_sentences_preserves_capitalized_english_abbreviations(self):
        text = "E.g. retrieval filtering improves evidence coverage. It then scores the report."

        summary = first_sentences(text, count=1)

        self.assertEqual(summary, "E.g. retrieval filtering improves evidence coverage.")

    def test_first_sentences_preserves_figure_abbreviations(self):
        text = "Fig. 1 shows the workflow. The report then scores each section."

        summary = first_sentences(text, count=1)

        self.assertEqual(summary, "Fig. 1 shows the workflow.")

    def test_runs_iterative_agents_and_records_every_round(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=output_dir),
            )

            self.assertEqual(len(result.rounds), 2)
            for index, round_result in enumerate(result.rounds, start=1):
                self.assertEqual(round_result.round_number, index)
                self.assertGreaterEqual(len(round_result.benchmark_reports), 1)
                self.assertIn("benchmark", round_result.rubric.source_notes.lower())
                self.assertIn("current report", round_result.rubric.source_notes.lower())
                self.assertGreater(round_result.scorecard.total_score, 0)
                self.assertLessEqual(round_result.scorecard.total_score, 100)
                self.assertGreaterEqual(len(round_result.critic_review.issues), 1)
                self.assertIn("Deep Research Report", round_result.report.title)

            jsonl_path = output_dir / "research_rounds.jsonl"
            docx_path = output_dir / "research_report.docx"
            self.assertTrue(jsonl_path.exists())
            self.assertTrue(docx_path.exists())

            lines = jsonl_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            persisted = [json.loads(line) for line in lines]
            self.assertEqual(persisted[0]["round_number"], 1)
            self.assertIn("benchmark_reports", persisted[0])
            self.assertIn("source_type", persisted[0]["benchmark_reports"][0])
            self.assertIn("search_note", persisted[0]["benchmark_reports"][0])
            self.assertIn("rubric", persisted[0])
            self.assertIn("scorecard", persisted[0])
            self.assertIn("critic_review", persisted[0])

            with zipfile.ZipFile(docx_path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("Round 1", document_xml)
            self.assertIn("Round 2", document_xml)
            self.assertIn("Scoring Rubric", document_xml)
            self.assertIn("Rubric Critic Review", document_xml)
            self.assertIn("Deep Research Report", document_xml)

    def test_uses_previous_round_report_when_building_next_rubric(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp)),
            )

            second_round = result.rounds[1]
            self.assertIn(
                "previous report",
                second_round.rubric.source_notes.lower(),
            )

    def test_english_report_records_external_benchmark_source_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            section = result.rounds[0].report.sections["Benchmark Quality"]

            self.assertIn("Source count: 3", section)
            self.assertIn("External source count: 0", section)
            self.assertIn("built-in fallback", section)
            self.assertIn("Only built-in fallback patterns were used", section)

    def test_english_benchmark_quality_avoids_broken_builtin_sentence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            section = result.rounds[0].report.sections["Benchmark Quality"]

            self.assertNotIn("should Only built-in", section)
            self.assertIn(
                "Only built-in fallback patterns were used; this is not external literature evidence.",
                section,
            )
            self.assertIn(
                "Future web or local benchmarks should continue tracking source diversity",
                section,
            )

    def test_english_critic_flags_builtin_only_benchmark_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            recommendations = " ".join(result.rounds[0].critic_review.recommendations)

            self.assertIn("built-in fallback", recommendations)
            self.assertIn("external benchmark reports", recommendations)

    def test_parses_approach_and_evaluation_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=APPROACH_EVALUATION_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            report = result.rounds[0].report

            self.assertIn("contrastive pretraining", report.sections["Method and Evidence"])
            self.assertIn("MMLU", report.sections["Method and Evidence"])
            self.assertNotIn("method section was not explicit", report.sections["Method and Evidence"].lower())

    def test_parses_roman_numbered_english_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=ROMAN_NUMBERED_ENGLISH_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            report = result.rounds[0].report

            self.assertIn("retrieval filtering", report.sections["Method and Evidence"])
            self.assertIn("MMLU", report.sections["Method and Evidence"])
            self.assertNotIn("method section was not explicit", report.sections["Method and Evidence"].lower())

    def test_parses_ablation_heading_as_evaluation_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=ABLATION_HEADING_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            evidence = result.rounds[0].report.sections["Method and Evidence"]

            self.assertIn("verifier reranking improves factual consistency", evidence)
            self.assertNotIn("experiments or results section was not explicit", evidence.lower())

    def test_markdown_title_heading_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=MARKDOWN_TITLE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "Deep Research Report - Markdown Research Paper")
            self.assertNotIn("#", report.title)

    def test_markdown_chinese_title_label_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=MARKDOWN_CHINESE_TITLE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - Markdown 中文论文")
            self.assertNotIn("标题：", report.title)

    def test_markdown_bold_title_markup_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=MARKDOWN_BOLD_TITLE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "Deep Research Report - Bold Markdown Paper")
            self.assertNotIn("**", report.title)

    def test_markdown_chinese_bold_section_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=MARKDOWN_CHINESE_BOLD_SECTION_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertIn("结构编码", report.sections["方法与证据"])
            self.assertIn("复杂关系推理准确率", report.sections["论文主张与证据账本"])
            self.assertNotIn("方法描述不够明确", report.as_text())

    def test_english_report_uses_claim_evidence_ledger_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            sections = result.rounds[0].report.sections

            self.assertIn("Claim-Evidence Ledger", sections)
            self.assertIn("Key Assumptions and Verification Gaps", sections)
            self.assertIn("Claim:", sections["Claim-Evidence Ledger"])
            self.assertIn("Evidence:", sections["Claim-Evidence Ledger"])
            self.assertIn("Verification gap:", sections["Claim-Evidence Ledger"])
            self.assertNotIn(". can be improved", sections["Claim-Evidence Ledger"])
            self.assertNotIn("shows The", sections["Claim-Evidence Ledger"])
            self.assertIn("the method section shows that", sections["Claim-Evidence Ledger"])

    def test_english_executive_thesis_states_question_scope_and_importance(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            thesis = result.rounds[0].report.sections["Executive Thesis"]

            self.assertIn("Research question:", thesis)
            self.assertIn("Scope:", thesis)
            self.assertIn("Why it matters:", thesis)
            self.assertNotIn("evaluate we study", thesis.lower())
            self.assertNotIn("argues that we study", result.rounds[0].report.as_text().lower())

    def test_english_problem_statement_cleans_we_introduce(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=APPROACH_EVALUATION_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            report_text = result.rounds[0].report.as_text().lower()

            self.assertIn("contrastive pretraining", report_text)
            self.assertNotIn("evaluate we introduce", report_text)
            self.assertNotIn("argues that we introduce", report_text)

    def test_english_scorecard_cites_report_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            rationales = [score.rationale for score in result.rounds[0].scorecard.scores]

            self.assertTrue(
                all("Evidence:" in rationale for rationale in rationales),
                rationales,
            )
            self.assertTrue(
                any("Claim-Evidence Ledger" in rationale for rationale in rationales),
                rationales,
            )

    def test_english_scorecard_lists_matched_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            evidence_score = next(
                score
                for score in result.rounds[0].scorecard.scores
                if score.name == "Evidence Quality"
            )

            self.assertIn("Matched markers:", evidence_score.rationale)
            self.assertIn("evidence", evidence_score.rationale)
            self.assertIn("experiment", evidence_score.rationale)

    def test_english_scoring_does_not_match_data_inside_metadata(self):
        report = ResearchReport(
            title="Metadata-only report",
            sections={"Summary": "This metadata overview describes catalog fields only."},
        )
        rubric = Rubric(
            title="Rubric",
            criteria=[
                RubricCriterion(
                    name="Reproducibility and Evidence Citation",
                    description="Checks evidence and data use.",
                    max_points=20,
                )
            ],
            source_notes="test",
        )

        scorecard = ReportScoringAgent().score(report, rubric)

        self.assertIn("Matched markers: none", scorecard.scores[0].rationale)
        self.assertNotIn("Matched markers: data", scorecard.scores[0].rationale)

    def test_english_scorecard_avoids_inflated_sample_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            scorecard = result.rounds[0].scorecard

            self.assertLessEqual(scorecard.total_score, 85)
            self.assertIn("Quality band:", scorecard.summary)
            self.assertTrue(
                all("Evidence:" in score.rationale for score in scorecard.scores),
                [score.rationale for score in scorecard.scores],
            )

    def test_english_builtin_only_second_round_does_not_reach_high_band(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp)),
            )

            second_scorecard = result.rounds[1].scorecard

            self.assertLess(second_scorecard.total_score, 85)
            self.assertIn("Quality band: good", second_scorecard.summary)
            self.assertTrue(
                any("source confidence cap" in score.rationale for score in second_scorecard.scores),
                [score.rationale for score in second_scorecard.scores],
            )

    def test_english_scorecard_summary_matches_low_score_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp)),
            )

            first_summary = result.rounds[0].scorecard.summary
            second_refinement = result.rounds[1].report.sections["Round Refinement"]

            self.assertIn("Research Usefulness", second_refinement)
            self.assertIn("Research Usefulness", first_summary)

    def test_second_round_report_summarizes_prior_score_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            refinement = result.rounds[1].report.sections["本轮改进"]

            self.assertIn("上一轮低分项", refinement)
            self.assertIn("没有明显低分项", refinement)
            self.assertNotIn("问题定义 12/20", refinement)
            self.assertNotIn("限制与失败模式 12/20", refinement)

    def test_searches_local_benchmark_reports_when_provided(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_dir = root / "benchmarks"
            benchmark_dir.mkdir()
            benchmark = benchmark_dir / "excellent_report.md"
            benchmark.write_text(
                "This excellent report ties experiment evidence to limitations "
                "and future follow-up questions.",
                encoding="utf-8",
            )

            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(
                    rounds=1,
                    output_dir=root / "out",
                    benchmark_dir=benchmark_dir,
                ),
            )

            source = result.rounds[0].benchmark_reports[0].source
            self.assertIn("excellent_report.md", source)
            strengths = result.rounds[0].benchmark_reports[0].strengths
            self.assertIn("Connects claims to experimental evidence.", strengths)
            self.assertEqual(result.rounds[0].benchmark_reports[0].source_type, "local")
            self.assertIn("keyword", result.rounds[0].benchmark_reports[0].search_note)

    def test_searches_local_markdown_extension_benchmark_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "excellent_report.markdown").write_text(
                "This excellent report connects experiment evidence, limitations, "
                "and future follow-up questions.",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("excellent_report.markdown", results[0].source)
            self.assertEqual(results[0].source_type, "local")

    def test_local_benchmark_extracts_reproducibility_strength(self):
        paper_text = """
Title: Reproducibility Audit

Abstract
We study reproducibility checks for paper reports.
"""
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "reproducibility.md").write_text(
                "A strong review checks reproducibility setup and replication details.",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(paper_text, round_number=1, previous_report=None)

            self.assertIn("Checks reproducibility and replication details.", results[0].strengths)

    def test_local_benchmark_search_avoids_substring_keyword_matches(self):
        paper_text = """
Title: Data Audit

Abstract
We analyze data quality.
"""
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "aaa_metadata.md").write_text(
                "This report only describes metadata catalogs.",
                encoding="utf-8",
            )
            (benchmark_dir / "zzz_data.md").write_text(
                "This report studies data values directly.",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(paper_text, round_number=1, previous_report=None)

            self.assertIn("zzz_data.md", results[0].source)
            self.assertNotIn("aaa_metadata.md", results[0].source)

    def test_local_benchmark_search_ignores_hidden_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / ".draft.md").write_text(
                "This draft mentions agent workflow benchmark reports and rubric scoring.",
                encoding="utf-8",
            )
            (benchmark_dir / "published.md").write_text(
                "This excellent report connects experiment evidence, limitations, "
                "and future follow-up questions.",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("published.md", results[0].source)
            self.assertNotIn(".draft.md", [Path(result.source).name for result in results])

    def test_local_benchmark_search_ignores_empty_files_and_uses_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "empty.md").write_text("   \n", encoding="utf-8")
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

            self.assertEqual(results[0].source_type, "built-in")
            self.assertTrue(results[0].source.startswith("built-in://"))
            self.assertNotIn("empty.md", [Path(result.source).name for result in results])

    def test_local_benchmark_search_ignores_placeholder_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "placeholder.md").write_text("TBD", encoding="utf-8")
            (benchmark_dir / "todo.md").write_text(
                "TODO: fill later with agent workflow evidence and baseline notes.",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir)

            results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

            self.assertEqual(results[0].source_type, "built-in")
            self.assertNotIn("placeholder.md", [Path(result.source).name for result in results])
            self.assertNotIn("todo.md", [Path(result.source).name for result in results])

    def test_local_benchmark_search_prioritizes_chinese_keyword_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "aaa_irrelevant.md").write_text(
                "这是一份关于天气和城市交通的普通说明。",
                encoding="utf-8",
            )
            (benchmark_dir / "zzz_relevant.md").write_text(
                "优秀论文审查报告应关注多智能体流程、评分标准、可复现性和证据引用。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("zzz_relevant.md", results[0].source)
            self.assertIn("本地对照报告文件", results[0].search_note)
            self.assertIn("关键词命中", results[0].search_note)
            self.assertIn("多智能体", results[0].search_note)
            self.assertIn("评分标准", results[0].search_note)
            self.assertNotIn("本地 benchmark", results[0].search_note)
            self.assertNotIn("keyword", results[0].search_note.lower())
            self.assertIn("把论文主张连接到实验证据。", results[0].strengths)

    def test_chinese_local_benchmark_extracts_method_audit_strength(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "method_audit.md").write_text(
                "优秀论文审查报告应关注评分标准、baseline、数据、消融实验和可复现性。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("检查基线方法、数据和消融实验是否充分。", results[0].strengths)
            self.assertNotIn("检查 baseline、数据和消融实验是否充分。", results[0].strengths)

    def test_chinese_local_benchmark_matches_baseline_data_ablation_terms(self):
        paper_text = """
标题：基线消融评估论文

摘要
本文研究基线方法、数据质量和消融实验对系统评估的影响。
"""
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "method_audit.md").write_text(
                "优秀报告会检查基线方法、数据质量和消融实验是否支撑主张。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(paper_text, round_number=1, previous_report=None)

            self.assertIn("基线", results[0].search_note)
            self.assertIn("数据", results[0].search_note)
            self.assertIn("消融", results[0].search_note)

    def test_local_benchmark_search_scores_more_than_first_five_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            for index in range(5):
                (benchmark_dir / f"aaa_irrelevant_{index}.md").write_text(
                    "这是一份关于天气和城市交通的普通说明。",
                    encoding="utf-8",
                )
            (benchmark_dir / "zzz_relevant.md").write_text(
                "优秀论文审查报告应关注多智能体流程、评分标准、可复现性和证据引用。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("zzz_relevant.md", results[0].source)

    def test_local_benchmark_search_tiebreaks_on_report_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "aaa_thin.md").write_text(
                "多智能体 论文审查 评分标准 可复现性 限制 局限 方法 实验。",
                encoding="utf-8",
            )
            (benchmark_dir / "zzz_structured.md").write_text(
                "主张：多智能体论文审查流程需要清晰定义。\n"
                "证据：评分标准应引用论文证据。\n"
                "限制：可复现性、局限和失败模式需要单独检查。\n"
                "后续：用方法审计和实验复核结论。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("zzz_structured.md", results[0].source)

    def test_chinese_local_benchmark_note_localizes_no_keyword_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "unmatched.md").write_text(
                "这是一份关于天气和城市交通的普通说明。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("无直接关键词命中", results[0].search_note)
            self.assertNotIn("no direct keyword overlap", results[0].search_note)
            self.assertNotIn("本地 benchmark", results[0].search_note)
            self.assertNotIn("keyword", results[0].search_note.lower())

    def test_local_benchmark_fallback_prefers_structured_reports_without_keyword_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            benchmark_dir = Path(tmp)
            (benchmark_dir / "aaa_plain.md").write_text(
                "天气、交通和城市说明。",
                encoding="utf-8",
            )
            (benchmark_dir / "bbb_plain.md").write_text(
                "餐饮、旅游和普通笔记。",
                encoding="utf-8",
            )
            (benchmark_dir / "zzz_structured.md").write_text(
                "主张：城市交通需要分层分析。\n"
                "证据：报告引用观测数据。\n"
                "边界：样本覆盖不足。\n"
                "后续：补充复核计划。",
                encoding="utf-8",
            )
            agent = BenchmarkSearchAgent(benchmark_dir=benchmark_dir, language="zh")

            results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

            self.assertIn("zzz_structured.md", results[0].source)

    def test_web_search_agent_extracts_external_report_results(self):
        html = """
        <a class="result__a" href="https://example.com/excellent-report">
          Excellent Paper Research Report
        </a>
        <a class="result__snippet">
          This report connects experiment evidence, limitations, and future work.
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/excellent-report")
        self.assertIn("Excellent Paper Research Report", results[0].title)
        self.assertIn("Connects claims to experimental evidence.", results[0].strengths)
        self.assertEqual(results[0].source_type, "web")
        self.assertIn("DuckDuckGo query", results[0].search_note)

    def test_web_search_agent_handles_single_quoted_result_attributes(self):
        html = """
        <a class='result__a' href='https://example.com/excellent-report'>
          Excellent Paper Research Report
        </a>
        <a class='result__snippet'>
          This report connects experiment evidence and limitations.
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/excellent-report")
        self.assertIn("Excellent Paper Research Report", results[0].title)

    def test_web_search_agent_handles_href_before_class(self):
        html = """
        <a href="https://example.com/reversed-report" class="result__a">
          Reversed Attribute Report
        </a>
        <a class="result__snippet">
          This report connects evidence and limitations.
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/reversed-report")
        self.assertIn("Reversed Attribute Report", results[0].title)

    def test_web_search_agent_extracts_div_snippets(self):
        html = """
        <a class="result__a" href="https://example.com/div-snippet">
          Div Snippet Report
        </a>
        <div class="result__snippet">
          Div snippet connects experiment evidence and limitations.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertIn("Div snippet connects experiment evidence", results[0].summary)

    def test_web_search_agent_handles_unquoted_attributes(self):
        html = """
        <a class=result__a href=https://example.com/unquoted>
          Unquoted Attribute Report
        </a>
        <div class=result__snippet>
          Unquoted snippet connects evidence and limitations.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/unquoted")
        self.assertIn("Unquoted snippet connects evidence", results[0].summary)

    def test_web_search_agent_cleans_q_redirect_urls(self):
        html = """
        <a class="result__a" href="/url?q=https%3A%2F%2Fexample.com%2Fclean-report">
          Clean Redirect Report
        </a>
        <div class="result__snippet">
          Redirect result connects evidence and limitations.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/clean-report")

    def test_web_search_agent_keeps_non_url_q_values_as_original_href(self):
        html = """
        <a class="result__a" href="/search?q=paper-analysis">
          Search Page Result
        </a>
        <div class="result__snippet">
          Search page snippet connects evidence and limitations.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "/search?q=paper-analysis")

    def test_web_search_agent_cleans_uppercase_scheme_redirect_urls(self):
        html = """
        <a class="result__a" href="/url?q=HTTPS%3A%2F%2Fexample.com%2Fcase-report">
          Uppercase Scheme Redirect Report
        </a>
        <div class="result__snippet">
          Redirect result connects evidence and limitations.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "HTTPS://example.com/case-report")

    def test_web_search_agent_requires_result_class_tokens(self):
        html = """
        <a class="not-result__a" href="https://example.com/false-positive">
          False Positive Result
        </a>
        <div class="not-result__snippet">
          This should not be treated as a result snippet.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source_type, "built-in")
        self.assertNotEqual(results[0].source, "https://example.com/false-positive")

    def test_web_search_agent_ignores_result_anchors_without_href(self):
        html = """
        <a class="result__a">
          Missing Href Result
        </a>
        <div class="result__snippet">
          Missing href snippets should not create a synthetic source.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source_type, "built-in")
        self.assertNotEqual(results[0].title, "Missing Href Result")

    def test_web_search_agent_ignores_unsafe_result_links(self):
        html = """
        <a class="result__a" href="javascript:void(0)">
          JavaScript Result
        </a>
        <div class="result__snippet">
          This snippet should not be used.
        </div>
        <a class="result__a" href="mailto:paper@example.com">
          Mail Result
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source_type, "built-in")
        self.assertNotIn("JavaScript Result", [result.title for result in results])

    def test_web_search_agent_ignores_unsupported_absolute_result_links(self):
        html = """
        <a class="result__a" href="ftp://example.com/report">
          FTP Result
        </a>
        <div class="result__snippet">
          FTP snippet should not be used.
        </div>
        <a class="result__a" href="file:///tmp/report.html">
          File Result
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source_type, "built-in")
        self.assertNotIn("FTP Result", [result.title for result in results])
        self.assertNotIn("File Result", [result.title for result in results])

    def test_web_search_agent_ignores_unsafe_redirect_targets(self):
        html = """
        <a class="result__a" href="/url?q=javascript%3Aalert%281%29">
          Unsafe Redirect Result
        </a>
        <div class="result__snippet">
          This redirect snippet should not be used.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source_type, "built-in")
        self.assertNotIn("Unsafe Redirect Result", [result.title for result in results])

    def test_web_search_agent_keeps_snippet_after_skipped_anchor_without_snippet(self):
        html = """
        <a class="result__a">
          Missing Href Result
        </a>
        <a class="result__a" href="https://example.com/real-report">
          Real Result
        </a>
        <div class="result__snippet">
          Real snippet connects evidence, limitations, and follow-up work.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/real-report")
        self.assertIn("Real snippet connects evidence", results[0].summary)

    def test_web_search_agent_does_not_reuse_snippet_from_skipped_anchor(self):
        html = """
        <a class="result__a">
          Missing Href Result
        </a>
        <div class="result__snippet">
          Missing href snippet should be ignored.
        </div>
        <a class="result__a" href="https://example.com/real-report">
          Real Result
        </a>
        <div class="result__snippet">
          Real snippet connects evidence, limitations, and follow-up work.
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/real-report")
        self.assertIn("Real snippet connects evidence", results[0].summary)
        self.assertNotIn("Missing href snippet", results[0].summary)

    def test_web_search_agent_extracts_nested_result_snippets(self):
        html = """
        <div class="result">
          <a class="result__a" href="https://example.com/nested-report">
            Nested Result
          </a>
          <div class="result__snippet">
            Nested snippet connects evidence and limitations.
          </div>
        </div>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
        )

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].source, "https://example.com/nested-report")
        self.assertIn("Nested snippet connects evidence", results[0].summary)

    def test_chinese_web_search_uses_chinese_query_terms(self):
        captured_urls = []
        html = """
        <a class="result__a" href="https://example.com/zh-report">
          中文优秀论文研究报告
        </a>
        <a class="result__snippet">
          这份报告连接论文证据、限制和后续研究。
        </a>
        """

        def fetcher(url: str) -> str:
            captured_urls.append(url)
            return html

        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=fetcher,
            language="zh",
        )

        results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

        decoded_query = unquote_plus(captured_urls[0])
        self.assertIn("优秀", decoded_query)
        self.assertIn("论文", decoded_query)
        self.assertIn("研究报告", decoded_query)
        self.assertNotIn("excellent research report", decoded_query)
        self.assertIn("优秀 论文 研究报告", results[0].search_note)
        self.assertIn("DuckDuckGo 查询：", results[0].search_note)
        self.assertNotIn("DuckDuckGo query:", results[0].search_note)
        self.assertEqual(results[0].source_type, "web")

    def test_chinese_web_search_localizes_missing_snippet_summary(self):
        html = """
        <a class="result__a" href="https://example.com/zh-report">
          中文优秀论文研究报告
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
            language="zh",
        )

        results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

        self.assertIn("外部搜索结果", results[0].summary)
        self.assertNotIn("External search result", results[0].summary)

    def test_chinese_web_search_localizes_missing_title(self):
        html = """
        <a class="result__a" href="https://example.com/zh-report">
        </a>
        """
        agent = BenchmarkSearchAgent(
            web_search=True,
            web_fetcher=lambda url: html,
            language="zh",
        )

        results = agent.search(CHINESE_PAPER_TEXT, round_number=1, previous_report=None)

        self.assertEqual(results[0].title, "外部对照报告 1")
        self.assertNotIn("benchmark", results[0].title.lower())
        self.assertNotIn("External benchmark report", results[0].title)

    def test_builtin_benchmark_fallback_returns_diverse_report_archetypes(self):
        agent = BenchmarkSearchAgent(language="zh")

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)
        sources = {result.source for result in results}

        self.assertGreaterEqual(len(results), 3)
        self.assertIn("built-in://claim-evidence-round-1", sources)
        self.assertIn("built-in://methodology-round-1", sources)
        self.assertIn("built-in://limitations-round-1", sources)
        self.assertEqual(results[0].source_type, "built-in")
        self.assertIn("内置回退", results[0].search_note)
        self.assertNotIn("fallback", results[0].search_note.lower())
        self.assertNotIn("benchmark", results[0].search_note.lower())

    def test_chinese_report_records_benchmark_source_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            section = result.rounds[0].report.sections["对照报告质量"]

            self.assertIn("来源数量：3", section)
            self.assertIn("外部来源数量：0", section)
            self.assertIn("内置回退模式", section)
            self.assertIn("仅使用内置回退模式", section)
            self.assertIn("主张-证据", section)
            self.assertNotIn("fallback", section.lower())
            self.assertNotIn("benchmark", section.lower())

            with zipfile.ZipFile(result.docx_path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("对照报告质量", document_xml)
            self.assertIn("搜索说明", document_xml)

    def test_chinese_benchmark_quality_uses_chinese_source_delimiter(self):
        benchmarks = [
            BenchmarkReport(
                title="Local report",
                source="/tmp/local.md",
                summary="local",
                strengths=["把论文主张连接到实验证据。"],
                source_type="local",
                search_note="local",
            ),
            BenchmarkReport(
                title="Web report",
                source="https://example.com/report",
                summary="web",
                strengths=["关注限制与可复现性。"],
                source_type="web",
                search_note="web",
            ),
        ]
        report = ReportWriterAgent().write(
            paper_text=PAPER_TEXT,
            benchmark_reports=benchmarks,
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        section = report.sections["对照报告质量"]

        self.assertIn("来源类型：本地对照报告、网页搜索", section)
        self.assertNotIn("本地 benchmark", section)
        self.assertNotIn("本地对照报告, 网页搜索", section)

    def test_chinese_benchmark_quality_counts_localized_baseline_coverage(self):
        benchmarks = [
            BenchmarkReport(
                title="Method report",
                source="/tmp/method.md",
                summary="method",
                strengths=["检查基线方法是否充分。"],
                source_type="local",
                search_note="local",
            )
        ]
        report = ReportWriterAgent().write(
            paper_text=CHINESE_PAPER_TEXT,
            benchmark_reports=benchmarks,
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        section = report.sections["对照报告质量"]

        self.assertIn("方法审计", section)
        self.assertNotIn("通用研究报告模式", section)

    def test_chinese_benchmark_quality_handles_empty_sources_readably(self):
        report = ReportWriterAgent().write(
            paper_text=CHINESE_PAPER_TEXT,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        section = report.sections["对照报告质量"]

        self.assertIn("来源数量：0", section)
        self.assertIn("来源类型：无", section)
        self.assertNotIn("来源类型：。", section)

    def test_can_generate_chinese_report_and_docx(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(
                    rounds=1,
                    output_dir=Path(tmp),
                    language="zh",
                ),
            )

            first_round = result.rounds[0]
            self.assertIn("深度研究报告", first_round.report.title)
            self.assertIn("执行摘要", first_round.report.sections)
            self.assertIn("当前报告", first_round.rubric.source_notes)
            self.assertIn("总分", first_round.scorecard.summary)
            self.assertIn("评分标准", first_round.critic_review.issues[0])

            with zipfile.ZipFile(result.docx_path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("第 1 轮", document_xml)
            self.assertIn("评分标准", document_xml)
            self.assertIn("评分标准批评", document_xml)
            self.assertIn("问题定义（20 分）：", document_xml)
            self.assertIn("问题定义：16/20。", document_xml)
            self.assertIn("搜索说明：", document_xml)
            self.assertNotIn("20 pts", document_xml)
            self.assertNotIn("搜索说明:", document_xml)
            self.assertNotIn("搜索说明： ", document_xml)

    def test_chinese_rubric_critic_localizes_benchmark_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            first_round = result.rounds[0]
            critic = RubricCriticAgent().critique(
                first_round.rubric,
                first_round.scorecard,
                [],
                language="zh",
            )
            critic_text = " ".join(critic.issues + critic.recommendations)

            self.assertIn("对照报告", critic_text)
            self.assertIn("对照报告搜索", critic_text)
            self.assertNotIn("benchmark", critic_text.lower())

    def test_chinese_critic_flags_builtin_only_benchmark_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            recommendations = " ".join(result.rounds[0].critic_review.recommendations)

            self.assertIn("内置回退", recommendations)
            self.assertIn("外部对照报告", recommendations)

    def test_chinese_report_uses_evidence_ledger_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            sections = result.rounds[0].report.sections

            self.assertIn("论文主张与证据账本", sections)
            self.assertIn("关键假设与验证缺口", sections)
            self.assertIn("主张", sections["论文主张与证据账本"])
            self.assertIn("证据", sections["论文主张与证据账本"])
            self.assertIn("解释", sections["论文主张与证据账本"])
            self.assertNotIn("Across three papers", sections["论文主张与证据账本"])
            self.assertIn("在三篇论文上", sections["论文主张与证据账本"])
            self.assertNotIn(
                "we study an agent workflow",
                sections["执行摘要"].lower(),
            )

    def test_chinese_evidence_ledger_avoids_repeating_evidence_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            ledger = result.rounds[0].report.sections["论文主张与证据账本"]

            self.assertEqual(
                ledger.count("迭代审查提高了假设、限制、基线方法和可复现性细节的覆盖"),
                1,
            )
            self.assertIn("实验部分提供了覆盖提升的方向性证据", ledger)

    def test_chinese_executive_summary_localizes_benchmark_term(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            summary = result.rounds[0].report.sections["执行摘要"]

            self.assertIn("外部对照报告", summary)
            self.assertNotIn("benchmark", summary.lower())

    def test_chinese_executive_summary_states_problem_scope_and_importance(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            summary = result.rounds[0].report.sections["执行摘要"]

            self.assertIn("问题范围", summary)
            self.assertIn("重要性", summary)

    def test_chinese_report_preserves_domain_specific_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=GENERAL_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report_text = result.rounds[0].report.as_text()

            self.assertIn("可靠推理", report_text)
            self.assertIn("对比预训练", report_text)
            self.assertIn("检索过滤", report_text)
            self.assertNotIn("多角色流程持续改进", report_text)
            self.assertNotIn("论文长文本理解、外部对照报告、评分标准迭代和过程记录", report_text)

    def test_chinese_contribution_analysis_keeps_domain_markers(self):
        report = ReportWriterAgent().write(
            paper_text=GENERAL_CHINESE_PAPER_TEXT,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        contribution = report.sections["贡献分析"]

        self.assertIn("对比预训练", contribution)
        self.assertIn("可靠推理", contribution)
        self.assertIn("验证器", contribution)

    def test_chinese_problem_summary_strips_le_after_intro_verb(self):
        report = ReportWriterAgent().write(
            paper_text=CHINESE_INTRO_LE_PAPER_TEXT,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        summary = report.sections["执行摘要"]

        self.assertIn("图神经网络", summary)
        self.assertNotIn("关于了", summary)

    def test_chinese_missing_sections_use_chinese_defaults(self):
        paper_text = """
标题：缺少章节的中文论文

摘要
本文研究一种用于论文审查的自动分析流程。
"""
        report = ReportWriterAgent().write(
            paper_text=paper_text,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        report_text = report.as_text()

        self.assertIn("方法描述不够明确", report_text)
        self.assertIn("实验或结果部分不够明确", report_text)
        self.assertNotIn("The method section was not explicit", report_text)
        self.assertNotIn("The experiments or results section was not explicit", report_text)

    def test_chinese_limitation_section_localizes_framework_terms(self):
        paper_text = """
标题：中文限制术语测试

摘要
本文研究一个多智能体论文审查系统。

方法
系统把报告写作、评分标准生成和批评拆分为多角色流程。

实验
实验显示该系统提高了限制和可复现性细节覆盖。

局限
系统依赖对照报告质量，rubric 可能过拟合，critic 能力会影响纠偏。
"""
        report = ReportWriterAgent().write(
            paper_text=paper_text,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        limitations = report.sections["限制与风险"]

        self.assertIn("对照报告质量", limitations)
        self.assertIn("评分标准可能过拟合当前报告", limitations)
        self.assertIn("批评智能体的能力", limitations)
        self.assertIn("对照报告敏感性", limitations)
        self.assertIn("失败模式", limitations)
        self.assertIn("脆弱点", limitations)
        self.assertNotIn("benchmark", limitations.lower())
        self.assertNotIn("rubric", limitations.lower())
        self.assertNotIn("agent", limitations.lower())

    def test_chinese_shortcoming_heading_is_parsed_as_limitations(self):
        paper_text = """
标题：中文不足标题测试

摘要
本文研究一个多智能体论文审查系统。

方法
系统把报告写作、评分标准生成和批评拆分为多角色流程。

评估
评估显示该系统提高了基线方法和可复现性细节覆盖。

不足
系统依赖对照报告质量，评分标准可能过拟合当前报告。
"""
        report = ReportWriterAgent().write(
            paper_text=paper_text,
            benchmark_reports=[],
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        limitations = report.sections["限制与风险"]

        self.assertIn("结果依赖对照报告质量", limitations)
        self.assertIn("评分标准可能过拟合当前报告", limitations)
        self.assertNotIn("论文限制没有充分展开", limitations)

    def test_chinese_research_agenda_localizes_agent_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            agenda = result.rounds[0].report.sections["后续研究议程"]

            self.assertIn("基线", agenda)
            self.assertIn("消融实验", agenda)
            self.assertIn("智能体角色", agenda)
            self.assertNotIn("baseline", agenda)
            self.assertNotIn("ablation", agenda)
            self.assertNotIn("agent", agenda.lower())

    def test_chinese_assumption_gap_section_localizes_framework_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            gaps = result.rounds[0].report.sections["关键假设与验证缺口"]

            self.assertIn("对照报告", gaps)
            self.assertIn("智能体", gaps)
            self.assertIn("评分标准", gaps)
            self.assertNotIn("benchmark", gaps.lower())
            self.assertNotIn("agent", gaps.lower())
            self.assertNotIn("rubric", gaps.lower())

    def test_chinese_contribution_analysis_localizes_marker_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            contribution = result.rounds[0].report.sections["贡献分析"]

            self.assertIn("智能体", contribution)
            self.assertIn("工作流", contribution)
            self.assertIn("评分标准", contribution)
            self.assertNotIn("。 ", contribution)
            self.assertNotIn("agent、workflow、rubric", contribution)

    def test_chinese_contribution_analysis_extracts_chinese_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            contribution = result.rounds[0].report.sections["贡献分析"]

            self.assertIn("论文强调多智能体", contribution)
            self.assertNotIn("论文强调 多智能体", contribution)
            self.assertIn("评分标准", contribution)
            self.assertIn("检索", contribution)
            self.assertNotIn("论文贡献没有明确表述", contribution)

    def test_chinese_rubric_source_notes_use_readable_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            first_notes = result.rounds[0].rubric.source_notes
            second_notes = result.rounds[1].rubric.source_notes

            self.assertIn("基于对照报告、当前报告生成", first_notes)
            self.assertIn("对照报告数量", first_notes)
            self.assertIn("外部来源数量：0", first_notes)
            self.assertIn(
                "基于对照报告、当前报告、上一轮报告、上一轮评分标准批评生成",
                second_notes,
            )
            self.assertIn("外部来源数量：0", second_notes)
            self.assertNotIn("benchmark", first_notes.lower())
            self.assertNotIn("基于benchmark 报告, 当前报告", first_notes)

    def test_chinese_rubric_descriptions_localize_baseline_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            descriptions = " ".join(
                criterion.description
                for round_result in result.rounds
                for criterion in round_result.rubric.criteria
            )

            self.assertIn("基线方法", descriptions)
            self.assertIn("注意事项", descriptions)
            self.assertNotIn("baseline", descriptions.lower())
            self.assertNotIn("caveat", descriptions.lower())

    def test_second_round_chinese_rubric_evolves_from_critic_feedback(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            second_criteria = [criterion.name for criterion in result.rounds[1].rubric.criteria]

            self.assertIn("可复现性与证据引用", second_criteria)
            self.assertNotIn("研究价值", second_criteria)
            self.assertIn("上一轮评分标准批评", result.rounds[1].rubric.source_notes)

    def test_second_round_chinese_critic_recognizes_explicit_reproducibility_criterion(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            second_issues = result.rounds[1].critic_review.issues

            self.assertFalse(
                any("可复现性目前嵌在限制项中" in issue for issue in second_issues),
                second_issues,
            )

    def test_second_round_english_rubric_evolves_from_critic_feedback(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp)),
            )

            second_criteria = [criterion.name for criterion in result.rounds[1].rubric.criteria]

            self.assertIn("Reproducibility and Evidence Citation", second_criteria)
            self.assertNotIn("Research Usefulness", second_criteria)
            self.assertIn("prior rubric critic review", result.rounds[1].rubric.source_notes)

    def test_chinese_scoring_counts_localized_baseline_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            evidence_score = next(
                score
                for score in result.rounds[0].scorecard.scores
                if score.name == "证据质量"
            )

            self.assertGreaterEqual(evidence_score.points, 12)
            self.assertIn("基线方法", evidence_score.rationale)
            self.assertNotIn("baseline", evidence_score.rationale.lower())

    def test_chinese_scoring_counts_localized_agent_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            contribution_score = next(
                score
                for score in result.rounds[0].scorecard.scores
                if score.name == "技术贡献"
            )

            self.assertGreaterEqual(contribution_score.points, 16)
            self.assertIn("多智能体", contribution_score.rationale)
            self.assertNotIn("agent", contribution_score.rationale.lower())

    def test_chinese_scoring_counts_localized_ablation_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            usefulness_score = next(
                score
                for score in result.rounds[0].scorecard.scores
                if score.name == "研究价值"
            )

            self.assertGreaterEqual(usefulness_score.points, 14)
            self.assertIn("消融实验", usefulness_score.rationale)
            self.assertNotIn("ablation", usefulness_score.rationale.lower())

    def test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            scorecard = result.rounds[0].scorecard

            self.assertLessEqual(scorecard.total_score, 82)
            self.assertIn("质量等级：", scorecard.summary)
            self.assertIn("主要风险：", scorecard.summary)
            self.assertTrue(
                all("证据：" in score.rationale for score in scorecard.scores),
                [score.rationale for score in scorecard.scores],
            )
            self.assertTrue(
                all(" - " not in score.rationale for score in scorecard.scores),
                [score.rationale for score in scorecard.scores],
            )

            limitation_score = next(
                score for score in scorecard.scores if score.name == "限制与失败模式"
            )
            self.assertIn("限制与风险", limitation_score.rationale)

    def test_chinese_benchmark_improvement_has_clean_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            benchmark_section = result.rounds[0].report.sections["基于对照报告的改进"]

            self.assertNotIn("。。", benchmark_section)
            self.assertNotIn(".。", benchmark_section)

    def test_chinese_benchmark_improvement_section_title_is_localized(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            sections = result.rounds[0].report.sections

            self.assertIn("基于对照报告的改进", sections)
            self.assertNotIn("基于 Benchmark 的改进", sections)

    def test_chinese_benchmark_improvement_includes_method_audit_lessons(self):
        benchmarks = [
            BenchmarkReport(
                title="Method audit",
                source="local",
                summary="summary",
                strengths=[
                    "明确讨论限制和风险。",
                    "把论文主张连接到实验证据。",
                    "检查基线方法、数据和消融实验是否充分。",
                ],
                source_type="local",
                search_note="local",
            )
        ]

        report = ReportWriterAgent().write(
            paper_text=CHINESE_PAPER_TEXT,
            benchmark_reports=benchmarks,
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        benchmark_section = report.sections["基于对照报告的改进"]

        self.assertIn("检查基线方法、数据和消融实验是否充分", benchmark_section)
        self.assertNotIn("baseline", benchmark_section)

    def test_chinese_benchmark_improvement_includes_reproducibility_lesson(self):
        benchmarks = [
            BenchmarkReport(
                title="Reproducibility audit",
                source="local",
                summary="summary",
                strengths=[
                    "明确讨论限制和风险。",
                    "把论文主张连接到实验证据。",
                    "检查基线方法、数据和消融实验是否充分。",
                    "检查可复现性和复现实验细节。",
                ],
                source_type="local",
                search_note="local",
            )
        ]

        report = ReportWriterAgent().write(
            paper_text=CHINESE_PAPER_TEXT,
            benchmark_reports=benchmarks,
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        benchmark_section = report.sections["基于对照报告的改进"]

        self.assertIn("检查可复现性和复现实验细节", benchmark_section)

    def test_chinese_benchmark_improvement_deduplicates_repeated_lessons(self):
        benchmarks = [
            BenchmarkReport(
                title="Report A",
                source="local-a",
                summary="summary",
                strengths=["把论文主张连接到实验证据。"],
                source_type="local",
                search_note="local",
            ),
            BenchmarkReport(
                title="Report B",
                source="local-b",
                summary="summary",
                strengths=["把论文主张连接到实验证据。"],
                source_type="local",
                search_note="local",
            ),
        ]

        report = ReportWriterAgent().write(
            paper_text=CHINESE_PAPER_TEXT,
            benchmark_reports=benchmarks,
            previous_report=None,
            prior_scorecard=None,
            round_number=1,
            language="zh",
        )

        benchmark_section = report.sections["基于对照报告的改进"]

        self.assertEqual(benchmark_section.count("把论文主张连接到实验证据"), 1)

    def test_english_benchmark_improvement_has_clean_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
            )

            benchmark_section = result.rounds[0].report.sections["Benchmark-Informed Improvements"]

            self.assertNotIn("..", benchmark_section)
            self.assertNotIn(".;", benchmark_section)

    def test_chinese_paper_headings_and_title_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 多智能体论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertNotIn("baseline", report.sections["论文主张与证据账本"])
            self.assertNotIn("实验部分声称，实验声称", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_chinese_markdown_section_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=MARKDOWN_CHINESE_SECTION_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - Markdown 中文章节论文")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_numbered_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=NUMBERED_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 编号标题论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertNotIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_chinese_evaluation_heading_is_parsed_as_experiments(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_EVALUATION_HEADING_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            ledger = result.rounds[0].report.sections["论文主张与证据账本"]

            self.assertIn("评估显示", ledger)
            self.assertIn("基线方法", ledger)
            self.assertNotIn("实验声称支持主要结论", ledger)

    def test_chinese_ablation_heading_is_parsed_as_experiments(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_ABLATION_HEADING_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            ledger = result.rounds[0].report.sections["论文主张与证据账本"]

            self.assertIn("消融实验显示", ledger)
            self.assertNotIn("实验声称支持主要结论", ledger)

    def test_chinese_technical_route_heading_is_parsed_as_method(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=CHINESE_TECHNICAL_ROUTE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            method_section = result.rounds[0].report.sections["方法与证据"]

            self.assertIn("多角色流程", method_section)
            self.assertNotIn("需要进一步拆解的技术流程", method_section)

    def test_parenthesized_numbered_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAREN_NUMBERED_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 括号编号论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertNotIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_inline_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=INLINE_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 行内标题论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertNotIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_space_numbered_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=SPACE_NUMBERED_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 空格编号论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("基线方法", report.sections["论文主张与证据账本"])
            self.assertNotIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("对照报告质量", report.sections["限制与风险"])

    def test_continuous_runner_resumes_and_keeps_appending_rounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            first = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=1,
                ),
            )
            second = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=2,
                    resume=True,
                ),
            )

            self.assertEqual([round.round_number for round in first.rounds], [1])
            self.assertEqual(
                [round.round_number for round in second.rounds],
                [1, 2, 3],
            )
            lines = (output_dir / "research_rounds.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 3)
            with zipfile.ZipFile(output_dir / "research_report.docx") as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("Round 3", document_xml)

    def test_continuous_runner_rejects_invalid_workflow_rounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "WorkflowConfig.rounds must be at least 1"):
                run_continuous_workflow(
                    paper_text=PAPER_TEXT,
                    config=WorkflowConfig(rounds=0, output_dir=Path(tmp)),
                    continuous_config=ContinuousRunConfig(
                        duration_seconds=0,
                        sleep_seconds=0,
                        max_rounds=1,
                    ),
                )

    def test_resume_hydrates_legacy_benchmark_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            legacy_round = {
                "round_number": 1,
                "benchmark_reports": [
                    {
                        "title": "Legacy fallback",
                        "source": "built-in://legacy",
                        "summary": "A legacy benchmark report without trace metadata.",
                        "strengths": ["Separates paper claims from evaluator interpretation."],
                    }
                ],
                "report": {"title": "Legacy report", "sections": {"Summary": "Old output"}},
                "rubric": {
                    "title": "Legacy rubric",
                    "criteria": [
                        {
                            "name": "Problem Framing",
                            "description": "Frames the problem.",
                            "max_points": 20,
                        }
                    ],
                    "source_notes": "Legacy notes",
                },
                "scorecard": {
                    "total_score": 12,
                    "scores": [
                        {
                            "name": "Problem Framing",
                            "points": 12,
                            "max_points": 20,
                            "rationale": "Legacy rationale",
                        }
                    ],
                    "summary": "Legacy score",
                },
                "critic_review": {
                    "issues": ["Legacy issue"],
                    "recommendations": ["Legacy recommendation"],
                },
            }
            (output_dir / "research_rounds.jsonl").write_text(
                json.dumps(legacy_round) + "\n",
                encoding="utf-8",
            )

            result = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=1,
                    resume=True,
                ),
            )

            legacy_benchmark = result.rounds[0].benchmark_reports[0]
            self.assertEqual(legacy_benchmark.source_type, "built-in")
            self.assertIn("legacy JSONL", legacy_benchmark.search_note)

    def test_resume_rejects_non_contiguous_round_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            bad_round = {
                "round_number": 2,
                "benchmark_reports": [],
                "report": {"title": "Bad report", "sections": {"Summary": "Bad output"}},
                "rubric": {"title": "Bad rubric", "criteria": [], "source_notes": "Bad notes"},
                "scorecard": {"total_score": 0, "scores": [], "summary": "Bad score"},
                "critic_review": {"issues": [], "recommendations": []},
            }
            (output_dir / "research_rounds.jsonl").write_text(
                json.dumps(bad_round) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "non-contiguous round number on line 1"):
                run_continuous_workflow(
                    paper_text=PAPER_TEXT,
                    config=WorkflowConfig(rounds=1, output_dir=output_dir),
                    continuous_config=ContinuousRunConfig(
                        duration_seconds=0,
                        sleep_seconds=0,
                        max_rounds=1,
                        resume=True,
                    ),
                )

    def test_resume_keeps_scalar_legacy_benchmark_strength_as_single_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            legacy_round = {
                "round_number": 1,
                "benchmark_reports": [
                    {
                        "title": "Legacy fallback",
                        "source": "built-in://legacy",
                        "summary": "A legacy benchmark report.",
                        "strengths": "Separates paper claims from evaluator interpretation.",
                    }
                ],
                "report": {"title": "Legacy report", "sections": {"Summary": "Old output"}},
                "rubric": {
                    "title": "Legacy rubric",
                    "criteria": [
                        {
                            "name": "Problem Framing",
                            "description": "Frames the problem.",
                            "max_points": 20,
                        }
                    ],
                    "source_notes": "Legacy notes",
                },
                "scorecard": {
                    "total_score": 12,
                    "scores": [
                        {
                            "name": "Problem Framing",
                            "points": 12,
                            "max_points": 20,
                            "rationale": "Legacy rationale",
                        }
                    ],
                    "summary": "Legacy score",
                },
                "critic_review": {
                    "issues": ["Legacy issue"],
                    "recommendations": ["Legacy recommendation"],
                },
            }
            (output_dir / "research_rounds.jsonl").write_text(
                json.dumps(legacy_round) + "\n",
                encoding="utf-8",
            )

            result = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=1,
                    resume=True,
                ),
            )

            legacy_benchmark = result.rounds[0].benchmark_reports[0]
            self.assertEqual(
                legacy_benchmark.strengths,
                ["Separates paper claims from evaluator interpretation."],
            )

    def test_resume_keeps_scalar_legacy_critic_lists_as_single_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            legacy_round = {
                "round_number": 1,
                "benchmark_reports": [
                    {
                        "title": "Legacy fallback",
                        "source": "built-in://legacy",
                        "summary": "A legacy benchmark report.",
                        "strengths": ["Strength"],
                    }
                ],
                "report": {"title": "Legacy report", "sections": {"Summary": "Old output"}},
                "rubric": {
                    "title": "Legacy rubric",
                    "criteria": [
                        {
                            "name": "Problem Framing",
                            "description": "Frames the problem.",
                            "max_points": 20,
                        }
                    ],
                    "source_notes": "Legacy notes",
                },
                "scorecard": {
                    "total_score": 12,
                    "scores": [
                        {
                            "name": "Problem Framing",
                            "points": 12,
                            "max_points": 20,
                            "rationale": "Legacy rationale",
                        }
                    ],
                    "summary": "Legacy score",
                },
                "critic_review": {
                    "issues": "Legacy issue",
                    "recommendations": "Legacy recommendation",
                },
            }
            (output_dir / "research_rounds.jsonl").write_text(
                json.dumps(legacy_round) + "\n",
                encoding="utf-8",
            )

            result = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=1,
                    resume=True,
                ),
            )

            critic = result.rounds[0].critic_review
            self.assertEqual(critic.issues, ["Legacy issue"])
            self.assertEqual(critic.recommendations, ["Legacy recommendation"])

    def test_chinese_resume_hydrates_legacy_benchmark_note_in_chinese(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            legacy_round = {
                "round_number": 1,
                "benchmark_reports": [
                    {
                        "title": "旧版 fallback",
                        "source": "built-in://legacy",
                        "summary": "旧版记录没有 benchmark trace metadata。",
                        "strengths": ["区分论文原始主张和评审者解释。"],
                    }
                ],
                "report": {"title": "旧版报告", "sections": {"摘要": "旧输出"}},
                "rubric": {
                    "title": "旧版评分标准",
                    "criteria": [
                        {
                            "name": "问题定义",
                            "description": "解释问题。",
                            "max_points": 20,
                        }
                    ],
                    "source_notes": "旧版说明",
                },
                "scorecard": {
                    "total_score": 12,
                    "scores": [
                        {
                            "name": "问题定义",
                            "points": 12,
                            "max_points": 20,
                            "rationale": "旧版理由",
                        }
                    ],
                    "summary": "旧版评分",
                },
                "critic_review": {
                    "issues": ["旧版问题"],
                    "recommendations": ["旧版建议"],
                },
            }
            (output_dir / "research_rounds.jsonl").write_text(
                json.dumps(legacy_round, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = run_continuous_workflow(
                paper_text=CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=output_dir, language="zh"),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=0,
                    max_rounds=1,
                    resume=True,
                ),
            )

            legacy_benchmark = result.rounds[0].benchmark_reports[0]
            self.assertIn("旧版 JSONL", legacy_benchmark.search_note)
            self.assertIn("对照报告追踪元数据", legacy_benchmark.search_note)
            self.assertNotIn("benchmark", legacy_benchmark.search_note.lower())
            self.assertNotIn("trace metadata", legacy_benchmark.search_note.lower())
            self.assertNotIn("Recovered from legacy JSONL", legacy_benchmark.search_note)

    def test_continuous_runner_uses_duration_without_waiting_in_tests(self):
        class FakeClock:
            def __init__(self) -> None:
                self.current = 0.0

            def monotonic(self) -> float:
                return self.current

            def sleep(self, seconds: float) -> None:
                self.current += seconds

        fake_clock = FakeClock()
        with tempfile.TemporaryDirectory() as tmp:
            result = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=120,
                    sleep_seconds=60,
                ),
                clock=fake_clock.monotonic,
                sleeper=fake_clock.sleep,
            )

            self.assertEqual([round.round_number for round in result.rounds], [1, 2, 3])
            self.assertEqual(fake_clock.current, 120)

    def test_continuous_runner_does_not_sleep_after_duration_deadline(self):
        class FakeClock:
            def __init__(self) -> None:
                self.current = 0.0

            def monotonic(self) -> float:
                return self.current

            def sleep(self, seconds: float) -> None:
                self.current += seconds

        fake_clock = FakeClock()
        with tempfile.TemporaryDirectory() as tmp:
            result = run_continuous_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp)),
                continuous_config=ContinuousRunConfig(
                    duration_seconds=0,
                    sleep_seconds=60,
                ),
                clock=fake_clock.monotonic,
                sleeper=fake_clock.sleep,
            )

            self.assertEqual([round.round_number for round in result.rounds], [1])
            self.assertEqual(fake_clock.current, 0)


if __name__ == "__main__":
    unittest.main()
