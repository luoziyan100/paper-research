import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from paper_research.workflow import (
    BenchmarkSearchAgent,
    WorkflowConfig,
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


if __name__ == "__main__":
    unittest.main()
