import unittest
from pathlib import Path


class DocumentationTest(unittest.TestCase):
    def test_readme_documents_benchmark_traceability_and_library_import(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("source_type", readme)
        self.assertIn("search_note", readme)
        self.assertIn("from paper_research import BenchmarkSearchAgent", readme)
        self.assertIn("--jsonl-filename", readme)
        self.assertIn("--docx-filename", readme)
        self.assertIn("`--benchmark-dir` must point to an existing directory", readme)
        self.assertIn("`.markdown`", readme)
        self.assertIn("Hidden files and placeholder files are ignored", readme)
        self.assertIn("--no-resume", readme)


if __name__ == "__main__":
    unittest.main()
