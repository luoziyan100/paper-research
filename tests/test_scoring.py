import unittest

from paper_research.models import ResearchReport, Rubric, RubricCriterion
from paper_research.scoring import ReportScoringAgent


class ReportScoringAgentTest(unittest.TestCase):
    def test_builtin_only_rubric_caps_high_english_scores(self):
        report = ResearchReport(
            title="Sample",
            sections={
                "Executive Thesis": (
                    "Research question: define the problem and scope. "
                    "Why it matters: each assumption should be explicit."
                )
            },
        )
        rubric = Rubric(
            title="Rubric",
            criteria=[
                RubricCriterion(
                    name="Problem Framing",
                    description="Evaluate problem framing.",
                    max_points=20,
                )
            ],
            source_notes="Created from benchmark reports. External source count: 0.",
        )

        scorecard = ReportScoringAgent().score(report, rubric)

        self.assertEqual(scorecard.scores[0].points, 16)
        self.assertIn("source confidence cap", scorecard.scores[0].rationale)
        self.assertIn("source confidence", scorecard.summary)

    def test_builtin_only_rubric_notes_chinese_source_confidence_risk(self):
        report = ResearchReport(
            title="样例",
            sections={
                "执行摘要": (
                    "问题范围清楚，关键假设明确，重要性充足，研究目标可审查。"
                )
            },
        )
        rubric = Rubric(
            title="评分标准",
            criteria=[
                RubricCriterion(
                    name="问题定义",
                    description="评价问题定义。",
                    max_points=20,
                )
            ],
            source_notes="基于对照报告生成。外部来源数量：0。当前报告：样例。",
        )

        scorecard = ReportScoringAgent().score(report, rubric, language="zh")

        self.assertEqual(scorecard.scores[0].points, 16)
        self.assertIn("来源置信度", scorecard.summary)

    def test_score_rejects_unknown_language(self):
        report = ResearchReport(
            title="Sample",
            sections={"Evidence": "The report discusses evidence, data, and baselines."},
        )
        rubric = Rubric(
            title="Rubric",
            criteria=[
                RubricCriterion(
                    name="Evidence Quality",
                    description="Evaluate evidence.",
                    max_points=20,
                )
            ],
            source_notes="unit test",
        )

        with self.assertRaisesRegex(ValueError, "language must be 'en' or 'zh'"):
            ReportScoringAgent().score(report, rubric, language="fr")


if __name__ == "__main__":
    unittest.main()
