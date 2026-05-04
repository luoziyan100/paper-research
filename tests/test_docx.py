import tempfile
import unittest
import zipfile
from pathlib import Path

from paper_research.docx import DocxDocument, paragraph
from paper_research.export import write_docx
from paper_research.models import (
    BenchmarkReport,
    CriterionScore,
    CriticReview,
    ResearchReport,
    RoundResult,
    Rubric,
    RubricCriterion,
    Scorecard,
)


class DocxWriterTest(unittest.TestCase):
    def test_preserves_multiline_paragraphs_with_word_breaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument()
            document.add(paragraph("主张：A\n证据：B\n验证缺口：C"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")

            self.assertIn("<w:br/>", document_xml)
            self.assertIn("主张：A", document_xml)
            self.assertIn("证据：B", document_xml)
            self.assertIn("验证缺口：C", document_xml)

    def test_writes_basic_docx_metadata_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument()
            document.add(paragraph("content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())

            self.assertIn("docProps/core.xml", names)
            self.assertIn("docProps/app.xml", names)

    def test_export_uses_nested_heading_levels_for_report_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            round_result = RoundResult(
                round_number=1,
                benchmark_reports=[
                    BenchmarkReport(
                        title="Benchmark",
                        source="built-in://benchmark",
                        summary="Summary",
                        strengths=["Strength"],
                        source_type="built-in",
                        search_note="fallback",
                    )
                ],
                report=ResearchReport(
                    title="Deep Research Report - Example",
                    sections={"Executive Thesis": "Report section body."},
                ),
                rubric=Rubric(
                    title="Rubric",
                    criteria=[
                        RubricCriterion(
                            name="Evidence",
                            description="Uses evidence.",
                            max_points=20,
                        )
                    ],
                    source_notes="Rubric notes.",
                ),
                scorecard=Scorecard(
                    total_score=10,
                    scores=[
                        CriterionScore(
                            name="Evidence",
                            points=10,
                            max_points=20,
                            rationale="Rationale.",
                        )
                    ],
                    summary="Score summary.",
                ),
                critic_review=CriticReview(
                    issues=["Issue"],
                    recommendations=["Recommendation"],
                ),
            )

            write_docx(path, [round_result])

            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
                styles_xml = archive.read("word/styles.xml").decode("utf-8")

            self.assertIn(
                '<w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t xml:space="preserve">Deep Research Report - Example',
                document_xml,
            )
            self.assertIn(
                '<w:pStyle w:val="Heading3"/></w:pPr><w:r><w:t xml:space="preserve">Executive Thesis',
                document_xml,
            )
            self.assertIn('w:styleId="Heading3"', styles_xml)


if __name__ == "__main__":
    unittest.main()
