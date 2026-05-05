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
