"""Command-line interface for the paper research workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_research.io import load_paper_text
from paper_research.workflow import (
    ContinuousRunConfig,
    WorkflowConfig,
    run_continuous_workflow,
    run_research_workflow,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-research",
        description="Generate iterative deep research reports for a paper.",
    )
    parser.add_argument("paper", type=Path, help="Path to a txt, md, or PDF paper.")
    parser.add_argument("--rounds", type=int, default=3, help="Number of analysis rounds.")
    parser.add_argument(
        "--language",
        choices=["en", "zh"],
        default="en",
        help="Output language for generated reports.",
    )
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
    parser.add_argument(
        "--web-search",
        action="store_true",
        help="Search the web for external benchmark reports when no local reports match.",
    )
    parser.add_argument(
        "--duration-hours",
        type=float,
        default=None,
        help="Run continuously for this many hours, appending and rewriting outputs each round.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=300,
        help="Seconds to wait between continuous iterations.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=None,
        help="Optional cap for continuous mode; useful for dry runs.",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start a fresh continuous run instead of resuming existing JSONL records.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paper_text = load_paper_text(args.paper)
    config = WorkflowConfig(
        rounds=args.rounds,
        output_dir=args.output_dir,
        benchmark_dir=args.benchmark_dir,
        web_search=args.web_search,
        language=args.language,
    )
    if args.duration_hours is None:
        result = run_research_workflow(paper_text=paper_text, config=config)
    else:
        result = run_continuous_workflow(
            paper_text=paper_text,
            config=config,
            continuous_config=ContinuousRunConfig(
                duration_seconds=args.duration_hours * 3600,
                sleep_seconds=args.sleep_seconds,
                max_rounds=args.max_rounds,
                resume=not args.no_resume,
            ),
        )
    print(f"Wrote {result.jsonl_path}")
    print(f"Wrote {result.docx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
