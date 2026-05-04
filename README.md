# paper-research

`paper-research` is a dependency-light Python workflow for iterative deep
paper interpretation. It reads a paper, runs multiple analysis rounds, and
records every round in both JSONL and DOCX.

## What It Does

Each round follows the same agent pipeline:

1. `BenchmarkSearchAgent` searches for strong external research-report examples.
   It can search a local benchmark directory of `.txt` or `.md` reports, and
   `--web-search` enables a lightweight web search fallback. If neither returns
   results, it uses a built-in benchmark pattern so the workflow still runs from
   an empty repo.
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

## Usage

Run from the repository root:

```bash
python3 -m paper_research examples/sample_paper.txt --rounds 2 --output-dir research_output
```

Generate a Chinese report:

```bash
python3 -m paper_research examples/sample_paper.txt \
  --rounds 2 \
  --language zh \
  --output-dir research_output
```

With your own benchmark report folder:

```bash
python3 -m paper_research path/to/paper.txt \
  --rounds 3 \
  --benchmark-dir path/to/excellent-reports \
  --output-dir research_output
```

With web search fallback enabled:

```bash
python3 -m paper_research path/to/paper.txt --rounds 3 --web-search
```

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

For a short dry run of continuous mode:

```bash
python3 -m paper_research examples/sample_paper.txt \
  --duration-hours 10 \
  --max-rounds 2 \
  --sleep-seconds 0 \
  --output-dir research_output
```

Text and Markdown inputs work without extra dependencies. PDF input is supported
when the optional `pypdf` package is installed.

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
