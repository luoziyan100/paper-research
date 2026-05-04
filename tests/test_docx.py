import tempfile
import unittest
import zipfile
from pathlib import Path

from paper_research.docx import DocxDocument, paragraph


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


if __name__ == "__main__":
    unittest.main()
