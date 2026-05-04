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

## Iteration 3 - 2026-05-04 07:35 PDT

### Current Problems

- Evidence-ledger sections contain multiple lines, but the DOCX writer stored embedded newline characters inside one text node rather than using Word line breaks.
- DOCX packages lacked `docProps/core.xml` and `docProps/app.xml`, making generated documents less complete for real Word processors and document indexing.

### Planned Changes

- Add tests for Word-compatible line break preservation.
- Add tests for basic DOCX metadata parts.
- Update the dependency-free DOCX writer without changing the public report workflow.

### Changes Made

- Converted multiline paragraph text into repeated `<w:t>` runs separated by `<w:br/>`.
- Added `docProps/core.xml` and `docProps/app.xml`.
- Added package relationships and content types for the metadata parts.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 15 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter3 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter3_final` produced JSONL and DOCX outputs.
- DOCX inspection showed:
  - `docProps/core.xml` exists.
  - `docProps/app.xml` exists.
  - `word/document.xml` contains 12 `<w:br/>` line breaks.

## Iteration 4 - 2026-05-04 07:37 PDT

### Current Problems

- `paper_research/workflow.py` had grown to 1,253 lines, mixing data models, agent logic, persistence, and DOCX export.
- This size makes future 10-hour iteration risky because unrelated changes are more likely to conflict in one large file.

### Planned Changes

- Add a structure test that keeps `workflow.py` below a maintainability threshold.
- Move dataclass models to `paper_research/models.py`.
- Move DOCX workflow export code to `paper_research/export.py`.
- Keep public imports compatible through `paper_research.workflow` and `paper_research.__init__`.

### Changes Made

- Added `paper_research/models.py` for workflow configuration, result, report, rubric, scorecard, and critic dataclasses.
- Added `paper_research/export.py` for `write_docx`.
- Reduced `paper_research/workflow.py` from 1,253 lines to 1,094 lines.
- Added `tests/test_structure.py` to enforce the module size threshold and public import compatibility.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 17 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter4 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter4_final` produced JSONL and DOCX outputs.

## Iteration 5 - 2026-05-04 07:41 PDT

### Current Problems

- Invalid CLI options such as `--rounds 0` surfaced as Python exceptions from the workflow layer.
- Continuous-mode invalid sleep settings surfaced as Python exceptions instead of user-facing command-line errors.
- Missing paper files surfaced the default low-level `FileNotFoundError` message.

### Planned Changes

- Add CLI and input tests for invalid rounds, bad continuous sleep configuration, and missing files.
- Validate CLI arguments before constructing workflow configs.
- Convert file loading errors into argparse-style messages without tracebacks.

### Changes Made

- Added `tests/test_cli_io.py`.
- Added explicit missing-file handling in `load_paper_text`.
- Added CLI validation for `--rounds`, `--duration-hours`, `--sleep-seconds`, and `--max-rounds`.
- Wrapped paper loading errors with `parser.error(...)`.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 20 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter5 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter5_final` produced JSONL and DOCX outputs.
- `python3 -m paper_research examples/sample_paper.txt --rounds 0` exited with code 2 and printed `--rounds must be at least 1`.

## Iteration 6 - 2026-05-04 07:45 PDT

### Current Problems

- Round 2 reports said they incorporated the previous report, but did not identify the previous round's low-scoring rubric items.
- This made the score-report-critique loop less actionable because later reports could ignore the concrete weaknesses found by scoring.

### Planned Changes

- Add a test requiring the second Chinese report to mention prior low-score items.
- Pass prior scorecards into report writing.
- Keep `workflow.py` under the structure threshold by extracting scoring helpers if needed.

### Changes Made

- `ReportWriterAgent.write(...)` now accepts `prior_scorecard`.
- Round 2+ report refinement sections include `上一轮低分项`.
- Added `paper_research/scoring.py` for scoring helper functions.
- Kept `paper_research/workflow.py` under the 1,100-line threshold after the new feature.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 21 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter6_final python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter6_final` produced JSONL and DOCX outputs.
- Final output inspected from `/tmp/paper_research_iter6_final/research_rounds.jsonl`.
- Round 2 `本轮改进` now includes `上一轮低分项：问题定义 12/20；限制与失败模式 12/20`.

## Iteration 7 - 2026-05-04 07:49 PDT

### Current Problems

- Chinese paper inputs using headings such as `标题：`, `摘要`, `方法`, `实验`, and `局限` were not parsed as structured paper sections.
- Chinese titles were included with the `标题：` prefix in generated report titles.
- Adding Chinese parsing directly to `workflow.py` would have pushed the module back over the maintainability threshold.

### Planned Changes

- Add a Chinese-paper fixture test.
- Parse common Chinese headings and Chinese title prefixes.
- Extract text parsing and summary helpers into `paper_research/text.py`.
- Keep `workflow.py` under the 1,100-line threshold.

### Changes Made

- Added `CHINESE_PAPER_TEXT` fixture coverage in `tests/test_workflow.py`.
- Added `paper_research/text.py` for section parsing, title extraction, compacting, and Chinese summary helpers.
- Updated Chinese evidence summary wording to avoid duplicated phrasing such as `实验部分声称，实验声称`.
- Reduced `paper_research/workflow.py` to 985 lines.

### Verification After Changes

- `python3 -m unittest discover -s tests` passed with 22 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter7 python3 -m compileall -q paper_research` passed.
- A Chinese input smoke run produced title `深度研究报告 - 多智能体论文审查系统`.
- The generated Chinese report included method evidence with `多角色流程`, evidence text with `baseline`, and limitation text with `benchmark 报告质量`.

## Iteration 8 - 2026-05-04 07:56 PDT

### Current Problems

- Benchmark search results recorded `title`, `source`, `summary`, and `strengths`, but did not explain how each result was found.
- JSONL output could not distinguish local files, web search results, and built-in fallback examples without inferring from URL strings.
- DOCX benchmark sections listed sources but did not show search provenance, making the final report less auditable.
- Adding benchmark metadata risked breaking resume from legacy JSONL files generated by earlier iterations.

### Planned Changes

- Add trace metadata to every `BenchmarkReport`.
- Require local, web, and built-in fallback benchmark results to carry explicit source type and search notes.
- Preserve compatibility with older JSONL records that do not contain the new fields.
- Render search provenance in DOCX benchmark sections.

### Changes Made

- Added `source_type` and `search_note` fields to `BenchmarkReport`.
- Local benchmark results now record `source_type="local"` and the matching keyword note.
- Web benchmark results now record `source_type="web"` and the DuckDuckGo query URL.
- Built-in fallback results now record `source_type="built-in"` and a fallback explanation.
- Legacy JSONL resume hydrates missing benchmark metadata from source strings and marks the note as recovered from legacy JSONL.
- DOCX benchmark result blocks now include `搜索说明` / `Search note` bullets.

### Verification After Changes

- Red tests first failed because `BenchmarkReport` did not yet expose `source_type`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_builtin_benchmark_fallback_returns_diverse_report_archetypes tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality tests.test_workflow.ResearchWorkflowTest.test_resume_hydrates_legacy_benchmark_metadata`
- `python3 -m unittest discover -s tests` passed with 23 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter8 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter8_final` produced JSONL and DOCX outputs.
- Output inspection confirmed:
  - JSONL benchmark rows include `source_type` and `search_note`.
  - DOCX `word/document.xml` includes `搜索说明`.
  - `paper_research/workflow.py` remains under the structure threshold at 1,042 lines.

## Iteration 9 - 2026-05-04 07:58 PDT

### Current Problems

- Chinese evidence-ledger sections still copied an English experiment sentence directly into `证据：...`.
- The Chinese rubric source note used mixed English punctuation and missing spacing: `基于benchmark 报告, 当前报告生成`.
- These issues made the generated Chinese report feel partially templated even after earlier report-quality improvements.

### Planned Changes

- Add tests requiring Chinese evidence-ledger content to use Chinese evidence summaries instead of raw English sample sentences.
- Add tests requiring readable Chinese punctuation in rubric source notes.
- Keep the change scoped to report wording, without changing scoring behavior.

### Changes Made

- Changed Chinese `论文主张与证据账本` evidence lines to use the Chinese evidence summary helper.
- Changed Chinese rubric source notes to use `基于 benchmark 报告、当前报告...生成`.
- Preserved `baseline` in Chinese-paper evidence summaries where it is a meaningful technical term.

### Verification After Changes

- Red tests first failed on `Across three papers` appearing in the evidence ledger and the old `基于benchmark 报告, 当前报告生成` source note.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_source_notes_use_readable_punctuation`
- `python3 -m unittest discover -s tests` passed with 24 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter9 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter9_final` produced JSONL and DOCX outputs.
- Output inspection confirmed:
  - JSONL evidence ledger now says `证据：在三篇论文上，迭代评分提高了假设、限制和可复现性细节的覆盖。`
  - JSONL rubric notes now say `基于 benchmark 报告、当前报告生成`.
  - DOCX `word/document.xml` includes the same Chinese evidence summary and no `Across three papers` match.
  - `paper_research/workflow.py` remains at 1,042 lines.

## Iteration 10 - 2026-05-04 08:00 PDT

### Current Problems

- DOCX export used `Heading2` for both the report title and every report section.
- Word outline/navigation would show `执行摘要`, `贡献分析`, and other report sections as siblings of `评分标准`, instead of nested under the report title.
- The DOCX style sheet did not define `Heading3`, so simply changing style IDs would not be enough for reliable rendering.

### Planned Changes

- Add a DOCX export test that requires report titles to remain `Heading2` while report sections become `Heading3`.
- Add a `Heading3` style definition to the dependency-free DOCX writer.
- Keep top-level round sections, benchmark blocks, scoring rubric, scorecard, and critic review at their existing levels.

### Changes Made

- Report section headings in `write_docx(...)` now use `heading(..., level=3)`.
- Added a `Heading3` paragraph style with smaller bold text and tighter spacing.
- Added a focused DOCX export test using a constructed `RoundResult`.

### Verification After Changes

- Red test first failed because `Executive Thesis` was exported as `Heading2`.
- Target test passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections`
- `python3 -m unittest discover -s tests` passed with 25 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter10 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter10_final` produced JSONL and DOCX outputs.
- DOCX inspection confirmed:
  - `深度研究报告 - Retrieval Augmented Agents for Scientific Analysis` is `Heading2`.
  - `执行摘要` is `Heading3`.
  - `评分标准` and `评分标准批评` remain `Heading2`.
  - `word/styles.xml` defines `Heading3`.

## Iteration 11 - 2026-05-04 08:03 PDT

### Current Problems

- Chinese DOCX rubric entries still used English units and punctuation, such as `(20 pts):`.
- Chinese score bullets used English-style colon and period, such as `问题定义: 12/20.`.
- Benchmark trace bullets used `搜索说明:` and then, after the first fix, still left a space after the Chinese colon.
- Critic issue/recommendation bullets also used English colon spacing.

### Planned Changes

- Add a Chinese DOCX regression test for score units, score punctuation, and benchmark search-note punctuation.
- Keep English DOCX punctuation unchanged.
- Update only export formatting; avoid changing JSONL semantics or score calculations.

### Changes Made

- Chinese rubric bullets now use `问题定义（20 分）：...`.
- Chinese score bullets now use `问题定义：12/20。...`.
- Chinese benchmark, strength, issue, and recommendation bullets now use full-width colons without an extra space.
- Added test assertions that Chinese DOCX output does not contain `20 pts`, `搜索说明:`, or `搜索说明： `.

### Verification After Changes

- Red tests first failed on `问题定义（20 分）：` missing and then on `搜索说明： ` still appearing.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- `python3 -m unittest discover -s tests` passed with 25 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter11_final python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter11_final2` produced JSONL and DOCX outputs.
- DOCX inspection confirmed:
  - `搜索说明：内置 fallback...`
  - `优点：区分论文原始主张和评审者解释。`
  - `问题定义（20 分）：解释研究问题...`
  - `问题定义：12/20。找到 3 个相关标记...`
  - No matches for `20 pts`, `搜索说明:`, or `搜索说明： `.

## Iteration 12 - 2026-05-04 08:05 PDT

### Current Problems

- Local benchmark search mainly extracted English keywords.
- For Chinese papers, a relevant Chinese benchmark file could be ranked behind an irrelevant file just because of filename order.
- Search notes could not show useful Chinese keyword hits when the paper and benchmark were both Chinese.

### Planned Changes

- Add a test with one irrelevant Chinese benchmark file and one relevant Chinese benchmark file.
- Extract common Chinese research-review terms from paper text.
- Sort local benchmark candidates by keyword hit count before filename order.
- Preserve fallback behavior when no local file matches any keyword.

### Changes Made

- `_keywords(...)` now includes Chinese terms such as `多智能体`, `论文审查`, `评分标准`, `可复现性`, and `证据引用` when present.
- Local benchmark search now scores files first and sorts matched files by descending score.
- Search notes now include Chinese matched terms when relevant.
- Added regression coverage requiring the Chinese relevant benchmark file to rank first.

### Verification After Changes

- Red test first failed because `aaa_irrelevant.md` ranked ahead of `zzz_relevant.md`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided`
- `python3 -m unittest discover -s tests` passed with 26 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter12 python3 -m compileall -q paper_research` passed.
- `paper_research/workflow.py` is 1,065 lines, still below the 1,100-line structure threshold.

## Iteration 13 - 2026-05-04 08:09 PDT

### Current Problems

- `paper_research/workflow.py` had grown back to 1,065 lines after search and benchmark improvements.
- Benchmark search mixed local search, web parsing, built-in fallback reports, and workflow orchestration in one module.
- Future search-quality work would be harder to isolate if benchmark code stayed inside the main workflow file.

### Planned Changes

- Add a structure test requiring a dedicated `paper_research.benchmark` module.
- Tighten the `workflow.py` maintainability threshold from 1,100 lines to 950 lines.
- Move benchmark search code and helper functions into the new module while preserving `from paper_research.workflow import BenchmarkSearchAgent` compatibility.

### Changes Made

- Added `paper_research/benchmark.py`.
- Moved `BenchmarkSearchAgent`, local benchmark scoring, web result parsing, fallback benchmark generation, keyword extraction, and benchmark strength inference into the new module.
- Updated `workflow.py` to import and re-export `BenchmarkSearchAgent`.
- Removed benchmark-only URL/HTML parsing imports from `workflow.py`.
- Tightened the structure test threshold to 950 lines and added a direct import check for `paper_research.benchmark`.

### Verification After Changes

- Red tests first failed because `paper_research.benchmark` did not exist and `workflow.py` had 1,065 lines.
- Target tests passed:
  - `python3 -m unittest tests.test_structure.CodeStructureTest`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_builtin_benchmark_fallback_returns_diverse_report_archetypes tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 27 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter13 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter13_final` produced JSONL and DOCX outputs.
- `git diff --check` passed after removing a trailing blank line.
- `paper_research/workflow.py` is now 737 lines; `paper_research/benchmark.py` is 339 lines.

## Iteration 14 - 2026-05-04 08:11 PDT

### Current Problems

- Chinese score rationales still used an English separator between section names and evidence snippets, such as `证据：执行摘要 - ...`.
- This formatting leaked into both JSONL scorecards and DOCX score bullets.

### Planned Changes

- Add a regression test requiring Chinese score rationales to avoid the English ` - ` separator.
- Keep English score rationales unchanged.
- Update the evidence-snippet helper to choose separators by output language.

### Changes Made

- `_find_evidence_snippet(...)` now receives `language`.
- Chinese evidence snippets now use `章节：内容`.
- English evidence snippets continue to use `Section - content`.

### Verification After Changes

- Red test first failed with rationales such as `证据：执行摘要 - 本报告...`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- `python3 -m unittest discover -s tests` passed with 27 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter14 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter14_final` produced JSONL and DOCX outputs.
- Output inspection confirmed:
  - JSONL rationales now include `证据：执行摘要：...`.
  - DOCX score bullets now include `问题定义：12/20。找到 3 个相关标记。证据：执行摘要：...`.
  - No match for `证据：执行摘要 -`.

## Iteration 15 - 2026-05-04 08:13 PDT

### Current Problems

- Local benchmark search only scored the first five `.txt`/`.md` files after filename sorting.
- A relevant benchmark file placed sixth or later could be missed entirely, even if it had strong Chinese keyword matches.

### Planned Changes

- Add a regression test with five irrelevant files before a relevant Chinese benchmark file.
- Score all local benchmark candidates before taking the top results.
- Keep the returned result cap at five after ranking so output size remains controlled.

### Changes Made

- Local benchmark search now iterates over all candidate local files.
- Existing ranking still returns the top five matched reports after scoring.
- Added test coverage for relevant files beyond the first five sorted filenames.

### Verification After Changes

- Red test first failed because `aaa_irrelevant_0.md` ranked first while `zzz_relevant.md` was never scored.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_scores_more_than_first_five_files tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches`
- `python3 -m unittest discover -s tests` passed with 28 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter15 python3 -m compileall -q paper_research` passed.
- Structure check remains within thresholds: `workflow.py` 742 lines and `benchmark.py` 339 lines.

## Iteration 16 - 2026-05-04 08:20 PDT

### Current Problems

- Scorecard summaries only reported a total score and a generic low-score warning.
- Readers had to inspect individual criterion scores to infer whether the report quality was high, moderate, or risky.
- The summary did not name the most important weak criteria.

### Planned Changes

- Add a test requiring Chinese scorecard summaries to include `质量等级` and `主要风险`.
- Derive quality bands from total score.
- Derive main risks from low-scoring criteria.
- Keep score calculations unchanged.

### Changes Made

- Added `_quality_band(...)`.
- Added `_score_risk_summary(...)`.
- Chinese summaries now include total score, quality band, and main weak criteria.
- English summaries now include equivalent quality band and main-risk text.

### Verification After Changes

- Red test first failed because the summary was only `本轮报告总分 68/100。低分项应在下一轮优先修订。`
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- `python3 -m unittest discover -s tests` passed with 28 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter16 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter16_final` produced JSONL and DOCX outputs.
- Output inspection confirmed:
  - Round 1 summary: `本轮报告总分 68/100。质量等级：中等。主要风险：问题定义、限制与失败模式。低分项应在下一轮优先修订。`
  - Round 2 summary: `本轮报告总分 70/100。质量等级：良好。主要风险：问题定义。低分项应在下一轮优先修订。`
  - DOCX `word/document.xml` includes the same summary text.
  - `workflow.py` remains under the 950-line threshold at 777 lines.

## Iteration 17 - 2026-05-04 08:24 PDT

### Current Problems

- English paper parsing recognized `Method` and `Experiments`, but not common alternatives such as `Approach` and `Evaluation`.
- Papers using those headings produced reports that said the method and experiment sections were not explicit.
- This reduced report quality for common ML/NLP paper structures.

### Planned Changes

- Add a test paper using `Approach` and `Evaluation` headings.
- Normalize common English heading aliases into the existing canonical section names.
- Preserve existing parsing for `Method`, `Experiments`, Chinese headings, and the sample paper.

### Changes Made

- Added `normalize_english_heading(...)`.
- Mapped `Approach`, `Methodology`, and `System Design` to `method`.
- Mapped `Evaluation`, `Empirical Evaluation`, and `Experiments and Results` to `experiments`.
- Mapped `Background`, `Findings`, and singular limitation/experiment variants.

### Verification After Changes

- Red test first failed because `Method and Evidence` said `The method section was not explicit`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parses_approach_and_evaluation_headings tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 29 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter17 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter17_final` produced JSONL and DOCX outputs.
- Sample output inspection confirmed the original Chinese `方法与证据` section still uses the expected method/evidence summaries.

## Iteration 18 - 2026-05-04 08:26 PDT

### Current Problems

- After extracting benchmark search into `paper_research.benchmark`, users still could not import `BenchmarkSearchAgent` from the top-level `paper_research` package.
- This made the new public search module harder to discover and reuse.

### Planned Changes

- Add a public API test for top-level `BenchmarkSearchAgent` import.
- Export `BenchmarkSearchAgent` from `paper_research/__init__.py`.
- Verify the package still has no import-cycle issue.

### Changes Made

- Added `BenchmarkSearchAgent` to the package-level imports.
- Added it to `__all__`.
- Extended the public API structure test.

### Verification After Changes

- Red test first failed with `ImportError: cannot import name 'BenchmarkSearchAgent' from 'paper_research'`.
- Target test passed:
  - `python3 -m unittest tests.test_structure.CodeStructureTest.test_public_api_and_models_remain_importable`
- `python3 -m unittest discover -s tests` passed with 29 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter18 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --language zh --output-dir /tmp/paper_research_iter18_final` produced JSONL and DOCX outputs.
- `git diff --check` passed.

## Iteration 19 - 2026-05-04 08:29 PDT

### Current Problems

- README did not document benchmark traceability fields added in earlier iterations.
- README did not show the new top-level `BenchmarkSearchAgent` import path.
- Users would have to inspect JSONL or source code to learn about `source_type`, `search_note`, and library usage.

### Planned Changes

- Add a README regression test for benchmark traceability and library import examples.
- Document JSONL benchmark fields.
- Add a short Python library usage example.

### Changes Made

- Added `tests/test_docs.py`.
- Documented `source_type` and `search_note`.
- Added a `Library Use` section showing:
  - `from paper_research import BenchmarkSearchAgent, WorkflowConfig, run_research_workflow`
  - direct workflow execution from Python
  - direct benchmark search from Python

### Verification After Changes

- Red test first failed because README did not include `source_type`.
- Target test passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import`
- `python3 -m unittest discover -s tests` passed with 30 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter19 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 20 - 2026-05-04 08:32 PDT

### Current Problems

- Chinese local benchmark files containing terms such as `证据引用` and `可复现性` still received only the generic strength `提供可复用的外部对照样例。`
- Benchmark-informed report writing therefore lost useful information from Chinese benchmark reports.

### Planned Changes

- Extend existing Chinese local benchmark test to require evidence-related strengths.
- Teach benchmark strength inference to recognize Chinese keywords.
- Preserve English strength inference behavior.

### Changes Made

- `_infer_report_strengths(...)` now recognizes Chinese `限制`/`风险`/`局限`.
- It now recognizes Chinese `实验`/`证据`.
- It now recognizes Chinese `未来`/`后续`.
- Added a regression assertion that Chinese benchmark content with `证据引用` produces `把论文主张连接到实验证据。`.

### Verification After Changes

- Red test first failed because the relevant Chinese local benchmark returned only `提供可复用的外部对照样例。`
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided`
- `python3 -m unittest discover -s tests` passed with 30 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter20 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.
