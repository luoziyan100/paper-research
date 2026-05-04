# Iteration Log

## Iteration 1 - 2026-05-04 07:27 PDT

### Current Problems

- Chinese reports still embed long English paper sentences directly in the main analysis, which makes the report feel like a translated template rather than a Chinese research report.
- Scorecards mostly count keywords and produce inflated totals such as 91/100 on the sample paper.
- The rubric critic correctly says reproducibility should be explicit, but the next round rubric does not yet evolve to include it.
- The generated report lacks a clear evidence ledger that separates paper claims, paper evidence, evaluator interpretation, and verification gaps.
- DOCX output records the sections, but the content is not yet structured enough for a serious research review.

### Planned Changes

- Add tests for richer Chinese report sections, evidence-backed scoring rationales, and rubric evolution after critic feedback.
- Improve the report writer with evidence-ledger sections and clearer Chinese framing.
- Make second-round rubrics react to prior critic feedback by including reproducibility/evidence citation criteria.
- Lower scoring confidence when concrete evidence is thin, and require rationales to name evidence snippets rather than only keyword counts.

### Verification

- Baseline command run: `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter1_audit`
- Baseline output inspected from `/tmp/paper_research_iter1_audit/research_rounds.jsonl`.

### Changes Made

- Added Chinese report sections for `论文主张与证据账本` and `关键假设与验证缺口`.
- Rewrote Chinese executive summaries so they synthesize the paper problem instead of embedding long English source sentences.
- Made Chinese scoring rationales cite concrete report evidence with `证据：...` instead of only reporting keyword counts.
- Reduced Chinese score inflation by using a stricter scoring formula and caps when validation gaps are present.
- Made second-round Chinese rubrics react to prior critic feedback by replacing `研究价值` with `可复现性与证据引用` when reproducibility is criticized.
- Cleaned Chinese benchmark-improvement punctuation.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 11 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter1_final python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter1_final` produced `research_rounds.jsonl` and `research_report.docx`.
- Final sample output inspected from `/tmp/paper_research_iter1_final/research_rounds.jsonl`.
- Observed improvements:
  - Round 1 score changed from `91/100` to `64/100`.
  - Round 2 rubric includes `可复现性与证据引用`.
  - DOCX contains `word/document.xml` with 20,858 bytes.

## Iteration 2 - 2026-05-04 07:31 PDT

### Current Problems

- When no local or web benchmark reports are available, the built-in fallback returns only one benchmark pattern, which is too thin to simulate searching multiple excellent reports.
- The generated report uses benchmark strengths but does not explicitly record benchmark source diversity, source count, or fallback status.
- The DOCX includes benchmark entries, but readers cannot quickly tell whether the report was based on real local/web benchmarks or internal fallback examples.

### Planned Changes

- Add tests requiring multiple diverse built-in benchmark archetypes.
- Add a Chinese `Benchmark 对照质量` section that reports benchmark count, source type, and coverage traits.
- Ensure the generated DOCX includes this benchmark quality section through the normal report section rendering.

### Changes Made

- Expanded built-in benchmark fallback from one generic pattern to three archetypes:
  - `claim-evidence`
  - `methodology`
  - `limitations`
- Added English and Chinese fallback content for those benchmark archetypes.
- Added `Benchmark 对照质量` / `Benchmark Quality` report sections that summarize source count, source type, and coverage dimensions.
- Added tests that verify benchmark diversity and DOCX inclusion of the benchmark quality section.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 13 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter2 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter2_final` produced JSONL and DOCX outputs.
- Final output inspected from `/tmp/paper_research_iter2_final/research_rounds.jsonl`.
- Observed improvements:
  - Each round now records 3 built-in benchmark archetypes.
  - `Benchmark 对照质量` reports `来源数量：3` and `来源类型：内置 fallback`.
  - DOCX `word/document.xml` grew to 24,620 bytes and includes the new section.
