import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.parse import unquote_plus

from paper_research.workflow import (
    BenchmarkSearchAgent,
    ContinuousRunConfig,
    WorkflowConfig,
    run_continuous_workflow,
    run_research_workflow,
)


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
系统依赖 benchmark 报告质量，也可能让评分标准过拟合当前报告。
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
系统仍依赖 benchmark 报告质量。
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
系统仍依赖 benchmark 报告质量。
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


class ResearchWorkflowTest(unittest.TestCase):
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

    def test_second_round_report_uses_prior_low_score_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            refinement = result.rounds[1].report.sections["本轮改进"]

            self.assertIn("上一轮低分项", refinement)
            self.assertIn("问题定义", refinement)
            self.assertIn("限制与失败模式", refinement)

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
            self.assertIn("多智能体", results[0].search_note)
            self.assertIn("评分标准", results[0].search_note)
            self.assertIn("把论文主张连接到实验证据。", results[0].strengths)

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
        self.assertEqual(results[0].source_type, "web")

    def test_builtin_benchmark_fallback_returns_diverse_report_archetypes(self):
        agent = BenchmarkSearchAgent(language="zh")

        results = agent.search(PAPER_TEXT, round_number=1, previous_report=None)
        sources = {result.source for result in results}

        self.assertGreaterEqual(len(results), 3)
        self.assertIn("built-in://claim-evidence-round-1", sources)
        self.assertIn("built-in://methodology-round-1", sources)
        self.assertIn("built-in://limitations-round-1", sources)
        self.assertEqual(results[0].source_type, "built-in")
        self.assertIn("fallback", results[0].search_note)

    def test_chinese_report_records_benchmark_source_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            section = result.rounds[0].report.sections["Benchmark 对照质量"]

            self.assertIn("来源数量：3", section)
            self.assertIn("内置 fallback", section)
            self.assertIn("主张-证据", section)

            with zipfile.ZipFile(result.docx_path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("Benchmark 对照质量", document_xml)
            self.assertIn("搜索说明", document_xml)

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
            self.assertIn("问题定义：12/20。", document_xml)
            self.assertIn("搜索说明：", document_xml)
            self.assertNotIn("20 pts", document_xml)
            self.assertNotIn("搜索说明:", document_xml)
            self.assertNotIn("搜索说明： ", document_xml)

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

    def test_chinese_rubric_source_notes_use_readable_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAPER_TEXT,
                config=WorkflowConfig(rounds=2, output_dir=Path(tmp), language="zh"),
            )

            first_notes = result.rounds[0].rubric.source_notes
            second_notes = result.rounds[1].rubric.source_notes

            self.assertIn("基于 benchmark 报告、当前报告生成", first_notes)
            self.assertIn(
                "基于 benchmark 报告、当前报告、上一轮报告、上一轮评分标准批评生成",
                second_notes,
            )
            self.assertNotIn("基于benchmark 报告, 当前报告", first_notes)

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

            benchmark_section = result.rounds[0].report.sections["基于 Benchmark 的改进"]

            self.assertNotIn("。。", benchmark_section)
            self.assertNotIn(".。", benchmark_section)

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
            self.assertIn("baseline", report.sections["论文主张与证据账本"])
            self.assertNotIn("实验部分声称，实验声称", report.sections["论文主张与证据账本"])
            self.assertIn("benchmark 报告质量", report.sections["限制与风险"])

    def test_numbered_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=NUMBERED_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 编号标题论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("benchmark 报告质量", report.sections["限制与风险"])

    def test_parenthesized_numbered_chinese_headings_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_research_workflow(
                paper_text=PAREN_NUMBERED_CHINESE_PAPER_TEXT,
                config=WorkflowConfig(rounds=1, output_dir=Path(tmp), language="zh"),
            )

            report = result.rounds[0].report

            self.assertEqual(report.title, "深度研究报告 - 括号编号论文审查系统")
            self.assertIn("多角色流程", report.sections["方法与证据"])
            self.assertIn("baseline", report.sections["论文主张与证据账本"])
            self.assertIn("benchmark 报告质量", report.sections["限制与风险"])

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
            self.assertEqual(fake_clock.current, 180)


if __name__ == "__main__":
    unittest.main()
