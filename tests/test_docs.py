import unittest
from pathlib import Path


class DocumentationTest(unittest.TestCase):
    def test_readme_documents_benchmark_traceability_and_library_import(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("source_type", readme)
        self.assertIn("search_note", readme)
        self.assertIn("from paper_research import BenchmarkSearchAgent", readme)


if __name__ == "__main__":
    unittest.main()
