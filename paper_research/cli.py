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
        "--jsonl-filename",
        default="research_rounds.jsonl",
        help="JSONL filename to write inside --output-dir.",
    )
    parser.add_argument(
        "--docx-filename",
        default="research_report.docx",
        help="DOCX filename to write inside --output-dir.",
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
    if args.rounds < 1:
        parser.error("--rounds must be at least 1")
    if args.duration_hours is not None and args.duration_hours < 0:
        parser.error("--duration-hours cannot be negative")
    if args.sleep_seconds < 0:
        parser.error("--sleep-seconds cannot be negative")
    if (
        args.duration_hours is not None
        and args.max_rounds is None
        and args.sleep_seconds <= 0
    ):
        parser.error("--sleep-seconds must be positive unless --max-rounds is set")
    if args.max_rounds is not None and args.max_rounds < 1:
        parser.error("--max-rounds must be at least 1")
    if args.output_dir.exists() and not args.output_dir.is_dir():
        parser.error(f"--output-dir must be a directory: {args.output_dir}")
    for option_name, filename in (
        ("--jsonl-filename", args.jsonl_filename),
        ("--docx-filename", args.docx_filename),
    ):
        if Path(filename).name != filename:
            parser.error(f"{option_name} must be a filename, not a path")
    if not args.jsonl_filename.endswith(".jsonl"):
        parser.error("--jsonl-filename must end with .jsonl")
    if not args.docx_filename.endswith(".docx"):
        parser.error("--docx-filename must end with .docx")
    if args.benchmark_dir is not None and not args.benchmark_dir.exists():
        parser.error(f"--benchmark-dir does not exist: {args.benchmark_dir}")
    if args.benchmark_dir is not None and not args.benchmark_dir.is_dir():
        parser.error(f"--benchmark-dir must be a directory: {args.benchmark_dir}")
    try:
        paper_text = load_paper_text(args.paper)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    config = WorkflowConfig(
        rounds=args.rounds,
        output_dir=args.output_dir,
        benchmark_dir=args.benchmark_dir,
        web_search=args.web_search,
        language=args.language,
        jsonl_filename=args.jsonl_filename,
        docx_filename=args.docx_filename,
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
