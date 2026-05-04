"""Command-line interface for the paper research workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_research.io import load_paper_text
from paper_research.workflow import WorkflowConfig, run_research_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-research",
        description="Generate iterative deep research reports for a paper.",
    )
    parser.add_argument("paper", type=Path, help="Path to a txt, md, or PDF paper.")
    parser.add_argument("--rounds", type=int, default=3, help="Number of analysis rounds.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("research_output"),
        help="Directory for JSONL and DOCX outputs.",
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=None,
        help="Optional directory of excellent research reports to search each round.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paper_text = load_paper_text(args.paper)
    result = run_research_workflow(
        paper_text=paper_text,
        config=WorkflowConfig(
            rounds=args.rounds,
            output_dir=args.output_dir,
            benchmark_dir=args.benchmark_dir,
        ),
    )
    print(f"Wrote {result.jsonl_path}")
    print(f"Wrote {result.docx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
