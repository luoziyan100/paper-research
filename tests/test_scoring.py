import unittest

from paper_research.models import ResearchReport, Rubric, RubricCriterion
from paper_research.scoring import ReportScoringAgent


class ReportScoringAgentTest(unittest.TestCase):
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
