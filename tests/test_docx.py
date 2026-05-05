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

    def test_writes_numbering_part_for_bullets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument()
            document.add(paragraph("content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                styles_xml = archive.read("word/styles.xml").decode("utf-8")

            self.assertIn("word/numbering.xml", names)
            self.assertIn("word/_rels/document.xml.rels", names)
            self.assertIn("<w:numPr>", styles_xml)

    def test_bullet_numbering_defines_indentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument()
            document.add(paragraph("content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                numbering_xml = archive.read("word/numbering.xml").decode("utf-8")

            self.assertIn('<w:ind w:left="720" w:hanging="360"/>', numbering_xml)

    def test_writes_custom_docx_core_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument(title="迭代式论文研究报告")
            document.add(paragraph("content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                core_xml = archive.read("docProps/core.xml").decode("utf-8")

            self.assertIn("迭代式论文研究报告", core_xml)
            self.assertNotIn("Iterative Paper Research Report", core_xml)

    def test_styles_define_multilingual_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument(title="迭代式论文研究报告")
            document.add(paragraph("中文 content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                styles_xml = archive.read("word/styles.xml").decode("utf-8")

            self.assertIn('w:rFonts w:ascii="Aptos"', styles_xml)
            self.assertIn('w:hAnsi="Aptos"', styles_xml)
            self.assertIn('w:eastAsia="Microsoft YaHei"', styles_xml)

    def test_heading_styles_define_outline_levels(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            document = DocxDocument(title="迭代式论文研究报告")
            document.add(paragraph("content"))

            document.save(path)

            with zipfile.ZipFile(path) as archive:
                styles_xml = archive.read("word/styles.xml").decode("utf-8")

            self.assertIn('<w:outlineLvl w:val="0"/>', styles_xml)
            self.assertIn('<w:outlineLvl w:val="1"/>', styles_xml)
            self.assertIn('<w:outlineLvl w:val="2"/>', styles_xml)

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

    def test_export_uses_language_specific_core_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            round_result = RoundResult(
                round_number=1,
                benchmark_reports=[],
                report=ResearchReport(title="深度研究报告 - 示例", sections={"执行摘要": "内容"}),
                rubric=Rubric(title="评分标准", criteria=[], source_notes="说明"),
                scorecard=Scorecard(total_score=0, scores=[], summary="总结"),
                critic_review=CriticReview(issues=[], recommendations=[]),
            )

            write_docx(path, [round_result], language="zh")

            with zipfile.ZipFile(path) as archive:
                core_xml = archive.read("docProps/core.xml").decode("utf-8")

            self.assertIn("迭代式论文研究报告", core_xml)
            self.assertNotIn("Iterative Paper Research Report", core_xml)

    def test_chinese_export_explains_empty_benchmark_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            round_result = RoundResult(
                round_number=1,
                benchmark_reports=[],
                report=ResearchReport(title="深度研究报告 - 示例", sections={"执行摘要": "内容"}),
                rubric=Rubric(title="评分标准", criteria=[], source_notes="说明"),
                scorecard=Scorecard(total_score=0, scores=[], summary="总结"),
                critic_review=CriticReview(issues=[], recommendations=[]),
            )

            write_docx(path, [round_result], language="zh")

            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")

            self.assertIn("本文档记录每一轮研究报告、对照报告搜索、评分标准", document_xml)
            self.assertIn("对照报告搜索结果", document_xml)
            self.assertIn("未记录可用的对照报告搜索结果。", document_xml)
            self.assertNotIn("benchmark 搜索", document_xml)
            self.assertNotIn("Benchmark 搜索", document_xml)

    def test_export_inserts_page_break_between_rounds(self):
        def make_round(round_number: int) -> RoundResult:
            return RoundResult(
                round_number=round_number,
                benchmark_reports=[],
                report=ResearchReport(
                    title=f"Deep Research Report - Round {round_number}",
                    sections={"Executive Thesis": "Content"},
                ),
                rubric=Rubric(title="Rubric", criteria=[], source_notes="Notes"),
                scorecard=Scorecard(total_score=0, scores=[], summary="Score"),
                critic_review=CriticReview(issues=[], recommendations=[]),
            )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"

            write_docx(path, [make_round(1), make_round(2)])

            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")

            self.assertIn('<w:br w:type="page"/>', document_xml)
            self.assertLess(
                document_xml.index('<w:br w:type="page"/>'),
                document_xml.index("Round 2"),
            )


if __name__ == "__main__":
    unittest.main()
