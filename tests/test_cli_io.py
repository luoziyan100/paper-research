import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from paper_research.cli import main
from paper_research.io import load_paper_text


class InputAndCliTest(unittest.TestCase):
    def test_load_paper_text_reports_missing_file_clearly(self):
        missing = Path("/tmp/paper-research-definitely-missing.txt")

        with self.assertRaisesRegex(FileNotFoundError, "Paper file does not exist"):
            load_paper_text(missing)

    def test_cli_rejects_invalid_rounds_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.txt"
            paper.write_text("Title: T\n\nAbstract\ncontent", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main([str(paper), "--rounds", "0"])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("--rounds must be at least 1", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_rejects_bad_continuous_sleep_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.txt"
            paper.write_text("Title: T\n\nAbstract\ncontent", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(
                        [
                            str(paper),
                            "--duration-hours",
                            "1",
                            "--sleep-seconds",
                            "0",
                        ]
                    )

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("--sleep-seconds must be positive", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_accepts_custom_output_filenames(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper = root / "paper.txt"
            output_dir = root / "out"
            paper.write_text("Title: T\n\nAbstract\ncontent", encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(paper),
                        "--rounds",
                        "1",
                        "--output-dir",
                        str(output_dir),
                        "--jsonl-filename",
                        "custom-rounds.jsonl",
                        "--docx-filename",
                        "custom-report.docx",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "custom-rounds.jsonl").exists())
            self.assertTrue((output_dir / "custom-report.docx").exists())
            self.assertIn("custom-rounds.jsonl", stdout.getvalue())
            self.assertIn("custom-report.docx", stdout.getvalue())

    def test_cli_rejects_output_filenames_with_path_segments(self):
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.txt"
            paper.write_text("Title: T\n\nAbstract\ncontent", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(
                        [
                            str(paper),
                            "--jsonl-filename",
                            "../outside.jsonl",
                        ]
                    )

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("--jsonl-filename must be a filename", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_rejects_output_filenames_with_wrong_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "paper.txt"
            paper.write_text("Title: T\n\nAbstract\ncontent", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(
                        [
                            str(paper),
                            "--jsonl-filename",
                            "rounds.txt",
                            "--docx-filename",
                            "report.txt",
                        ]
                    )

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("--jsonl-filename must end with .jsonl", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
