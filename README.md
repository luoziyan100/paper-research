# paper-research

`paper-research` is a dependency-light Python workflow for iterative deep
paper interpretation. It reads a paper, runs multiple analysis rounds, and
records every round in both JSONL and DOCX.

## What It Does

Each round follows the same agent pipeline:

1. `BenchmarkSearchAgent` searches for strong external research-report examples.
   It can search a local benchmark directory of `.txt`, `.md`, or `.markdown`
   reports, and `--web-search` enables a lightweight web search fallback. If
   neither returns results, it uses a built-in benchmark pattern so the workflow
   still runs from an empty repo.
2. `ReportWriterAgent` writes the current deep research report for the paper.
3. `RubricBuilderAgent` creates a fresh scoring standard from the benchmark
   results, the current report, the previous report, and the previous rubric
   critique.
4. `ReportScoringAgent` scores the report against the current rubric.
5. `RubricCriticAgent` critiques the scoring standard and suggests fixes.

The workflow writes:

- `research_rounds.jsonl`: structured per-round records.
- `research_report.docx`: readable DOCX containing benchmark results, reports,
  rubrics, scorecards, and rubric critiques for every round.

Benchmark entries in `research_rounds.jsonl` include traceability metadata:

- `source_type`: `local`, `web`, or `built-in`.
- `search_note`: why the benchmark was selected, such as local keyword matches,
  a DuckDuckGo query, or built-in fallback usage.

Scoring uses that provenance. When rubric notes contain `External source count: 0`,
high per-criterion scores are capped by source confidence, and the scorecard
summary calls out the missing external benchmark evidence instead of presenting
a built-in-only run as high-confidence validation.

## Usage

Run from the repository root:

```bash
python3 -m paper_research examples/sample_paper.txt --rounds 2 --output-dir research_output
```

Successful runs print both output paths and a `Final score summary` line so you
can see the latest score, quality band, and source-confidence risks without
opening the generated files first.

Generate a Chinese report:

```bash
python3 -m paper_research examples/sample_paper.txt \
  --rounds 2 \
  --language zh \
  --output-dir research_output
```

Use custom output filenames inside the output directory:

```bash
python3 -m paper_research examples/sample_paper.txt \
  --rounds 1 \
  --output-dir research_output \
  --jsonl-filename custom-rounds.jsonl \
  --docx-filename custom-report.docx
```

Output filename options must be plain filenames, not paths; JSONL filenames must
end with `.jsonl`, and DOCX filenames must end with `.docx`.

With your own benchmark report folder:

```bash
python3 -m paper_research path/to/paper.txt \
  --rounds 3 \
  --benchmark-dir path/to/excellent-reports \
  --output-dir research_output
```

`--benchmark-dir` must point to an existing directory containing `.txt`, `.md`,
or `.markdown` benchmark reports. Hidden files and placeholder files are ignored.

With web search fallback enabled:

```bash
python3 -m paper_research path/to/paper.txt --rounds 3 --web-search
```

The lightweight web parser keeps normal result links and safe relative search
links, but unsafe web result links are ignored for schemes such as
`javascript:`, `mailto:`, `data:`, and `vbscript:`.

Run continuous iteration for ten hours. The runner resumes existing
`research_rounds.jsonl` records by default, appends every new round, and rewrites
the DOCX after each round so progress is recoverable if the process stops:

```bash
python3 -m paper_research path/to/paper.txt \
  --language zh \
  --web-search \
  --duration-hours 10 \
  --sleep-seconds 300 \
  --output-dir research_output
```

Add `--no-resume` when you want to ignore existing `research_rounds.jsonl`
records and start a fresh continuous run.

For a short dry run of continuous mode:

```bash
python3 -m paper_research examples/sample_paper.txt \
  --duration-hours 10 \
  --max-rounds 2 \
  --sleep-seconds 0 \
  --output-dir research_output
```

Paper inputs can be `.txt`, `.md`, or `.markdown` files without extra
dependencies. PDF input is supported when the optional `pypdf` package is
installed.

## Library Use

The workflow can also be used from Python:

```python
from pathlib import Path

from paper_research import BenchmarkSearchAgent, ReportScoringAgent
from paper_research import WorkflowConfig, run_research_workflow

paper_text = Path("examples/sample_paper.txt").read_text(encoding="utf-8")
config = WorkflowConfig(rounds=2, language="zh", output_dir=Path("research_output"))
result = run_research_workflow(paper_text, config)

search_agent = BenchmarkSearchAgent(benchmark_dir=Path("benchmarks"), language="zh")
benchmarks = search_agent.search(paper_text, round_number=1, previous_report=None)
scorecard = ReportScoringAgent().score(result.rounds[-1].report, result.rounds[-1].rubric, "zh")
```

## Development

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

The current report writing and scoring are deterministic and local-first. The
agent classes are intentionally separated so a future change can replace the
deterministic writer/scorer with an LLM provider without changing the
persistence format. Continuous mode is intended for long-running LLM/web-search
iterations, but it also works offline through the built-in benchmark fallback.
