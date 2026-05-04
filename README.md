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
persistence format.
