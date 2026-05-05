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

## Iteration 21 - 2026-05-04 08:40 PDT

### Current Problems

- `WorkflowConfig` supported custom `jsonl_filename` and `docx_filename`, but the CLI did not expose those fields.
- CLI users could not change output filenames without writing Python code.

### Planned Changes

- Add a CLI regression test for custom output filenames.
- Add `--jsonl-filename` and `--docx-filename` arguments.
- Pass both values into `WorkflowConfig`.

### Changes Made

- Added `--jsonl-filename` with default `research_rounds.jsonl`.
- Added `--docx-filename` with default `research_report.docx`.
- Added a CLI test that verifies both files are created and printed.

### Verification After Changes

- Red test first failed with `unrecognized arguments: --jsonl-filename ... --docx-filename ...`.
- Target test passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 31 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter21 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --language zh --output-dir /tmp/paper_research_iter21_final --jsonl-filename custom-rounds.jsonl --docx-filename custom-report.docx` wrote both custom output files.
- `git diff --check` passed.

## Iteration 22 - 2026-05-04 08:43 PDT

### Current Problems

- The new CLI filename options accepted path segments such as `../outside.jsonl`.
- That allowed output files to escape `--output-dir`.
- The red test confirmed the issue by creating `research_output/../outside.jsonl`.

### Planned Changes

- Add a CLI test that rejects path segments in output filename options.
- Validate both `--jsonl-filename` and `--docx-filename` as filenames, not paths.
- Remove the test-generated `outside.jsonl` pollution.

### Changes Made

- Added validation for `Path(filename).name != filename`.
- Added a no-traceback CLI error for unsafe JSONL filenames.
- Removed the red-test generated `outside.jsonl` file.

### Verification After Changes

- Red test first failed because no `SystemExit` was raised and `outside.jsonl` was written.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_output_filenames_with_path_segments tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 32 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter22 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.
- `git status --short --branch` confirmed no `outside.jsonl` remained.

## Iteration 23 - 2026-05-04 08:45 PDT

### Current Problems

- CLI output filename options accepted misleading extensions such as `rounds.txt` and `report.txt`.
- This could produce JSONL or DOCX content under the wrong file extension.

### Planned Changes

- Add a CLI test that rejects wrong output filename extensions.
- Require JSONL filenames to end in `.jsonl`.
- Require DOCX filenames to end in `.docx`.

### Changes Made

- Added extension validation for `--jsonl-filename`.
- Added extension validation for `--docx-filename`.
- Added a no-traceback CLI regression test.

### Verification After Changes

- Red test first failed because the CLI wrote `research_output/rounds.txt` and `research_output/report.txt`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_output_filenames_with_wrong_extensions tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 33 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter23 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 24 - 2026-05-04 08:48 PDT

### Current Problems

- README did not mention the new `--jsonl-filename` and `--docx-filename` CLI options.
- Users could miss the feature added in Iteration 21 or misunderstand the filename restrictions added in Iterations 22 and 23.

### Planned Changes

- Extend the README documentation regression test.
- Add a custom-output-filename CLI example.
- Document filename/path and extension constraints.

### Changes Made

- README now includes a custom output filename command example.
- README now states output filename options must be plain filenames.
- README now states JSONL filenames must end with `.jsonl` and DOCX filenames must end with `.docx`.

### Verification After Changes

- Red docs test first failed because README did not include `--jsonl-filename`.
- Target test passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import`
- `python3 -m unittest discover -s tests` passed with 33 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter24 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 25 - 2026-05-04 08:50 PDT

### Current Problems

- English reports lacked the explicit claim-evidence ledger already present in Chinese reports.
- English reports also lacked a dedicated assumptions and verification-gaps section.
- This made English report structure less audit-friendly and less symmetric with the Chinese report.

### Planned Changes

- Add a test requiring English reports to include `Claim-Evidence Ledger`.
- Add a test requiring English reports to include `Key Assumptions and Verification Gaps`.
- Ensure DOCX export includes the new sections through normal report rendering.

### Changes Made

- Added an English `Claim-Evidence Ledger` section with `Claim`, `Evidence`, `Interpretation`, and `Verification gap`.
- Added an English `Key Assumptions and Verification Gaps` section.
- Added regression coverage for the new sections.

### Verification After Changes

- Red test first failed because English report sections did not contain `Claim-Evidence Ledger`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 34 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter25 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --output-dir /tmp/paper_research_iter25_final` produced JSONL and DOCX outputs.
- Output inspection confirmed:
  - JSONL report sections include `Claim-Evidence Ledger` and `Key Assumptions and Verification Gaps`.
  - DOCX `word/document.xml` includes both section headings.
  - `workflow.py` remains under the 950-line threshold at 792 lines.

## Iteration 26 - 2026-05-04 08:54 PDT

### Current Problems

- English `Benchmark-Informed Improvements` text could contain punctuation artifacts such as `.;` and `..`.
- The issue came from joining benchmark strengths that already ended in periods, then adding a final period.

### Planned Changes

- Add a regression test for clean English benchmark-improvement punctuation.
- Preserve the existing Chinese punctuation cleanup.
- Add a small English phrase joiner that strips trailing punctuation before joining.

### Changes Made

- Added `join_english_phrases(...)`.
- English benchmark-improvement sections now strip trailing periods/semicolons before joining reusable traits.
- Added test coverage against `..` and `.;`.

### Verification After Changes

- Red test first failed on `Turns critique into testable next-round research questions..`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_benchmark_improvement_has_clean_punctuation tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_has_clean_punctuation`
- `python3 -m unittest discover -s tests` passed with 35 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter26 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --output-dir /tmp/paper_research_iter26_final` produced JSONL and DOCX outputs.
- Output inspection confirmed the English benchmark-improvement section ends cleanly with a single period and no `.;`.

## Iteration 27 - 2026-05-04 08:58 PDT

### Current Problems

- DOCX core metadata title was always `Iterative Paper Research Report`.
- Chinese DOCX files had Chinese body text but English `docProps/core.xml` title metadata.

### Planned Changes

- Add a DOCX writer test for custom core metadata titles.
- Add a workflow export test for Chinese DOCX core title.
- Let `write_docx(...)` pass language-specific document titles to the DOCX writer.

### Changes Made

- `DocxDocument` now accepts a `title` argument.
- `docProps/core.xml` escapes and writes the provided title.
- `write_docx(...)` now uses `迭代式论文研究报告` for Chinese output and keeps `Iterative Paper Research Report` for English output.

### Verification After Changes

- Red test first failed because `DocxDocument(title=...)` was not accepted.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_export_uses_language_specific_core_title tests.test_docx.DocxWriterTest.test_writes_custom_docx_core_title`
- `python3 -m unittest discover -s tests` passed with 37 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter27 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --language zh --output-dir /tmp/paper_research_iter27_final` produced JSONL and DOCX outputs.
- DOCX inspection confirmed `docProps/core.xml` contains `<dc:title>迭代式论文研究报告</dc:title>`.
- `git diff --check` passed.

## Iteration 28 - 2026-05-04 09:00 PDT

### Current Problems

- Chinese section parsing recognized `摘要`, `方法`, `实验`, and `局限`, but not numbered headings such as `一、摘要` and `二、方法`.
- Numbered Chinese papers therefore fell back to generic method/evidence summaries.

### Planned Changes

- Add a Chinese fixture with numbered headings.
- Normalize Chinese numeral prefixes and Arabic numeric prefixes before heading lookup.
- Preserve existing non-numbered Chinese heading parsing.

### Changes Made

- Added `NUMBERED_CHINESE_PAPER_TEXT`.
- `normalize_chinese_heading(...)` now strips prefixes like `一、` and `1.`.
- Added regression coverage for numbered Chinese headings.

### Verification After Changes

- Red test first failed because `方法与证据` did not include `多角色流程`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed`
- `python3 -m unittest discover -s tests` passed with 38 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter28 python3 -m compileall -q paper_research` passed.
- `python3 -m paper_research examples/sample_paper.txt --rounds 1 --language zh --output-dir /tmp/paper_research_iter28_final` produced JSONL and DOCX outputs.
- `git diff --check` passed.

## Iteration 29 - 2026-05-04 09:03 PDT

### Current Problems

- Chinese heading parsing handled `一、摘要`, but not parenthesized numbering such as `（一）摘要` or `(三) 实验`.
- This is a common Chinese document structure and caused method/evidence fallback summaries.

### Planned Changes

- Add a fixture using full-width and half-width parenthesized Chinese numbering.
- Strip parenthesized Chinese or Arabic numeric prefixes before heading lookup.
- Preserve the numbered-heading support added in Iteration 28.

### Changes Made

- Added `PAREN_NUMBERED_CHINESE_PAPER_TEXT`.
- `normalize_chinese_heading(...)` now strips prefixes like `（一）` and `(3)`.
- Added regression coverage for the parenthesized form.

### Verification After Changes

- Red test first failed because `方法与证据` did not include `多角色流程`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parenthesized_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_numbered_chinese_headings_are_parsed`
- `python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter29 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 30 - 2026-05-04 09:06 PDT

### Current Problems

- Chinese web benchmark search still used English query terms: `excellent research report paper analysis`.
- This made Chinese mode less likely to retrieve Chinese benchmark reports.

### Planned Changes

- Add a web-search test that captures and decodes the DuckDuckGo query URL in Chinese mode.
- Require Chinese query terms such as `优秀`, `论文`, and `研究报告`.
- Preserve the English web-search query behavior.

### Changes Made

- `_search_web_benchmarks(...)` now builds language-specific query text.
- Chinese query text now uses `{title} 优秀 论文 研究报告 分析`.
- English query text still uses `{title} excellent research report paper analysis`.

### Verification After Changes

- Red test first failed because the decoded query was `多智能体论文审查系统 excellent research report paper analysis`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_uses_chinese_query_terms tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 40 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter30 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 31 - 2026-05-04 09:08 PDT

### Current Problems

- Web benchmark `search_note` recorded the percent-encoded DuckDuckGo URL.
- Chinese search provenance was technically present but hard to read in JSONL and DOCX.

### Planned Changes

- Extend the Chinese web-search test to require readable Chinese query terms in `search_note`.
- Keep the actual request URL encoded.
- Preserve existing English web-search behavior.

### Changes Made

- Web benchmark `search_note` now stores the raw query text instead of the encoded URL.
- Chinese notes now include phrases such as `优秀 论文 研究报告`.

### Verification After Changes

- Red test first failed because `search_note` contained only the encoded URL.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_uses_chinese_query_terms tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 40 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter31 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 32 - 2026-05-04 09:12 PDT

### Current Problems

- Chinese local benchmark provenance still used the English fallback phrase `no direct keyword overlap` when no local keyword matched.
- This made Chinese JSONL and DOCX benchmark notes look partially untranslated.

### Planned Changes

- Add a regression test for the no-keyword-overlap local benchmark path in Chinese mode.
- Localize the unmatched-keyword phrase while preserving English behavior.
- Keep existing matched-keyword ordering and search scoring unchanged.

### Changes Made

- Added coverage for unmatched Chinese local benchmark notes.
- `_local_search_note(...)` now renders unmatched Chinese notes as `无直接关键词命中`.
- Chinese matched keywords are joined with `、` for more natural report text.

### Verification After Changes

- Red test first failed because the note contained `no direct keyword overlap`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_note_localizes_no_keyword_overlap tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches`
- `python3 -m unittest discover -s tests` passed with 41 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter32 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 33 - 2026-05-04 09:14 PDT

### Current Problems

- Chinese `Benchmark 对照质量` used an English comma when listing multiple benchmark source types.
- Mixed punctuation made generated Chinese reports and DOCX output less polished.

### Planned Changes

- Add a regression test with mixed local and web benchmark source types.
- Require the Chinese quality section to join source types with `、`.
- Preserve English comma-separated source-type formatting.

### Changes Made

- Added `test_chinese_benchmark_quality_uses_chinese_source_delimiter`.
- `ReportWriterAgent` benchmark quality summaries now render Chinese source types with `、`.

### Verification After Changes

- Red test first failed because the section contained `本地 benchmark, 网页搜索`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_uses_chinese_source_delimiter tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality`
- `python3 -m unittest discover -s tests` passed with 42 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter33 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 34 - 2026-05-04 09:17 PDT

### Current Problems

- Continuous resume could hydrate legacy JSONL benchmark entries that lacked `search_note`.
- In Chinese mode, the fallback legacy trace note was still English: `Recovered from legacy JSONL...`.

### Planned Changes

- Add a Chinese resume regression test for legacy benchmark metadata.
- Pass the active workflow language into JSONL hydration.
- Keep English legacy hydration output unchanged.

### Changes Made

- Added `test_chinese_resume_hydrates_legacy_benchmark_note_in_chinese`.
- `_load_jsonl_rounds(...)`, `_round_from_dict(...)`, and `_legacy_search_note(...)` now accept language context.
- Chinese legacy trace notes now render as `从缺少 benchmark trace metadata 的旧版 JSONL 恢复：...`。

### Verification After Changes

- Red test first failed because the hydrated note contained `Recovered from legacy JSONL...`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_resume_hydrates_legacy_benchmark_note_in_chinese tests.test_workflow.ResearchWorkflowTest.test_resume_hydrates_legacy_benchmark_metadata tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds`
- `python3 -m unittest discover -s tests` passed with 43 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter34 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 35 - 2026-05-04 09:19 PDT

### Current Problems

- DOCX export could render a `Benchmark 搜索结果` section with no body when a round had no benchmark reports.
- That made recovered or externally constructed reports look structurally incomplete.

### Planned Changes

- Add a DOCX regression test for empty Chinese benchmark results.
- Render a clear empty-state paragraph in DOCX when no benchmark reports are present.
- Preserve normal benchmark rendering for rounds with results.

### Changes Made

- Added `test_chinese_export_explains_empty_benchmark_results`.
- `write_docx(...)` now adds `未记录可用的 benchmark 搜索结果。` for empty Chinese benchmark sections.
- English DOCX export now gets the parallel empty state: `No usable benchmark search results were recorded.`

### Verification After Changes

- Red test first failed because the DOCX moved directly from `Benchmark 搜索结果` to the report title.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_chinese_export_explains_empty_benchmark_results tests.test_docx.DocxWriterTest.test_export_uses_language_specific_core_title tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 44 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter35 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 36 - 2026-05-04 09:21 PDT

### Current Problems

- Continuous mode slept once more after the duration deadline had already been reached.
- A zero-hour dry run still waited for `sleep_seconds`, and a 120-second fake run advanced the clock to 180 seconds.

### Planned Changes

- Add duration-boundary tests around the post-round sleep point.
- Keep the guarantee that continuous mode runs at least one round.
- Stop before sleeping when the deadline is already reached.

### Changes Made

- Added `test_continuous_runner_does_not_sleep_after_duration_deadline`.
- Tightened `test_continuous_runner_uses_duration_without_waiting_in_tests` to assert no oversleep.
- `run_continuous_workflow(...)` now checks `clock() >= deadline` before calling `sleeper(...)`.

### Verification After Changes

- Red tests first failed with fake clock values `60.0` and `180.0`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_does_not_sleep_after_duration_deadline tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_uses_duration_without_waiting_in_tests tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds`
- `python3 -m unittest discover -s tests` passed with 45 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter36 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 37 - 2026-05-04 09:22 PDT

### Current Problems

- English scorecard rationales only reported keyword marker counts.
- Unlike Chinese scorecards, they did not cite a concrete generated-report section or snippet.

### Planned Changes

- Add a regression test requiring `Evidence:` in every English score rationale.
- Reuse the existing report-snippet finder for English scoring.
- Keep score values unchanged while improving rationale traceability.

### Changes Made

- Added `test_english_scorecard_cites_report_evidence`.
- English `ReportScoringAgent` rationales now include `Evidence: <section - snippet>`.
- `_find_evidence_snippet(...)` now has an English fallback message for empty reports.

### Verification After Changes

- Red test first failed because rationales looked like `Found 2 evidence markers...` with no evidence snippet.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_cites_report_evidence tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- `python3 -m unittest discover -s tests` passed with 46 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter37 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 38 - 2026-05-04 09:24 PDT

### Current Problems

- Chinese contribution analysis rendered internal English markers such as `agent、workflow、rubric`.
- This weakened the Chinese report voice even when the user requested `--language zh`.

### Planned Changes

- Add a regression test for localized contribution marker terms.
- Keep English keyword matching for papers written in English.
- Render Chinese labels in Chinese reports.

### Changes Made

- Added `test_chinese_contribution_analysis_localizes_marker_terms`.
- `_extract_contribution(...)` now keeps marker/label pairs.
- Chinese reports now use labels such as `智能体`、`工作流`、`评分标准`、`检索`、`证据`。

### Verification After Changes

- Red test first failed because the contribution section contained `论文强调 agent、workflow、rubric、search`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_localizes_marker_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 47 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter38 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 39 - 2026-05-04 09:26 PDT

### Current Problems

- Chinese papers did not use structured contribution marker extraction.
- The report fell back to long sentence excerpts instead of concise signals such as `多智能体`、`评分标准`、`检索`。

### Planned Changes

- Add a regression test for Chinese marker extraction from Chinese paper text.
- Extend contribution marker matching with Chinese aliases.
- Avoid letting generic `智能体` duplicate and crowd out the more specific `多智能体`.

### Changes Made

- Added `test_chinese_contribution_analysis_extracts_chinese_markers`.
- `_extract_contribution(...)` now supports Chinese aliases such as `多智能体`、`评分标准`、`检索`、`实验`、`可复现性`。
- The extractor now skips generic `智能体` when `多智能体` is already present.

### Verification After Changes

- Red test first failed because the contribution section was a sentence fallback, not `论文强调 ...`.
- During green work, an over-specific test assertion for `证据` was corrected because the fixture text did not contain that signal.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_extracts_chinese_markers tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_localizes_marker_terms tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 48 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter39 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 40 - 2026-05-04 09:28 PDT

### Current Problems

- Chinese section parsing only recognized headings placed on their own line.
- Common inline headings such as `摘要：...` and `方法：...` were treated as body text, causing method and experiment evidence to fall back to generic summaries.

### Planned Changes

- Add a Chinese fixture with inline headings.
- Parse valid `heading：content` and `heading: content` lines before normal heading detection.
- Preserve existing numbered and parenthesized heading support.

### Changes Made

- Added `INLINE_CHINESE_PAPER_TEXT`.
- Added `test_inline_chinese_headings_are_parsed`.
- Added `split_inline_heading(...)` and wired it into `parse_sections(...)`.

### Verification After Changes

- Red test first failed because `方法与证据` did not include `多角色流程`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_inline_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_parenthesized_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed`
- `python3 -m unittest discover -s tests` passed with 49 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter40 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 41 - 2026-05-04 09:30 PDT

### Current Problems

- Chinese heading parsing handled `一、摘要`, but not whitespace-numbered headings such as `一 摘要` or `2 方法`.
- Papers using that style fell back to generic method and experiment summaries.

### Planned Changes

- Add a Chinese fixture with whitespace-numbered headings.
- Extend heading normalization for Chinese numerals and Arabic digits followed by spaces.
- Preserve existing numbered, parenthesized, and inline heading behavior.

### Changes Made

- Added `SPACE_NUMBERED_CHINESE_PAPER_TEXT`.
- Added `test_space_numbered_chinese_headings_are_parsed`.
- `normalize_chinese_heading(...)` now strips Chinese-numeral and digit prefixes followed by whitespace.

### Verification After Changes

- Red test first failed because `方法与证据` did not include `多角色流程`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_space_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_inline_chinese_headings_are_parsed`
- `python3 -m unittest discover -s tests` passed with 50 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter41 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 42 - 2026-05-04 09:31 PDT

### Current Problems

- Markdown inputs with a top-level `# Title` produced report titles containing the literal `#`.
- This made DOCX and JSONL output titles look unpolished for `.md` papers.

### Planned Changes

- Add a Markdown-title fixture and regression test.
- Teach title extraction to recognize Markdown H1-H6 headings.
- Preserve existing `Title:` and Chinese `标题：` handling.

### Changes Made

- Added `MARKDOWN_TITLE_PAPER_TEXT`.
- Added `test_markdown_title_heading_is_cleaned`.
- `paper_title(...)` now strips leading Markdown heading markers.

### Verification After Changes

- Red test first failed with `Deep Research Report - # Markdown Research Paper`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_markdown_title_heading_is_cleaned tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 51 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter42 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 43 - 2026-05-04 09:33 PDT

### Current Problems

- Chinese Markdown titles like `# 标题：Markdown 中文论文` were cleaned only partially.
- Generated report titles still included the label `标题：`.

### Planned Changes

- Add a Chinese Markdown-title regression test.
- Centralize title-label cleanup so Markdown headings reuse the same logic as plain title lines.
- Preserve English Markdown title cleanup.

### Changes Made

- Added `MARKDOWN_CHINESE_TITLE_PAPER_TEXT`.
- Added `test_markdown_chinese_title_label_is_cleaned`.
- Added `clean_title_text(...)` and reused it across `paper_title(...)`.

### Verification After Changes

- Red test first failed with `深度研究报告 - 标题：Markdown 中文论文`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_markdown_chinese_title_label_is_cleaned tests.test_workflow.ResearchWorkflowTest.test_markdown_title_heading_is_cleaned tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed`
- `python3 -m unittest discover -s tests` passed with 52 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter43 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 44 - 2026-05-04 09:35 PDT

### Current Problems

- Chinese web benchmark search used a Chinese query, but still fell back to an English summary when a search result lacked a snippet.
- That English fallback could leak into JSONL and DOCX outputs.

### Planned Changes

- Add a Chinese web-search regression test with a result title but no snippet.
- Localize the missing-snippet fallback summary.
- Preserve existing English web-search behavior.

### Changes Made

- Added `test_chinese_web_search_localizes_missing_snippet_summary`.
- `_search_web_benchmarks(...)` now uses `外部搜索结果：可能包含优秀研究报告样例。` in Chinese mode.

### Verification After Changes

- Red test first failed with `External search result for an excellent research-report example.`
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_localizes_missing_snippet_summary tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_uses_chinese_query_terms tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 53 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter44 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 45 - 2026-05-04 09:37 PDT

### Current Problems

- Chinese web benchmark search still used the English title fallback `External benchmark report N` when a result lacked a title.
- This could leak English headings into Chinese JSONL and DOCX benchmark sections.

### Planned Changes

- Add a Chinese web-search regression test with an empty result title.
- Localize the missing-title fallback.
- Preserve existing English web result titles.

### Changes Made

- Added `test_chinese_web_search_localizes_missing_title`.
- `_search_web_benchmarks(...)` now uses `外部 benchmark 报告 N` in Chinese mode.

### Verification After Changes

- Red test first failed with `External benchmark report 1`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_localizes_missing_title tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_localizes_missing_snippet_summary tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 54 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter45 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 46 - 2026-05-04 09:38 PDT

### Current Problems

- Chinese web benchmark provenance used a Chinese query but kept the English label `DuckDuckGo query:`.
- This left Chinese JSONL and DOCX search notes partially untranslated.

### Planned Changes

- Extend the Chinese web-query regression test to assert the search-note label.
- Localize the query label while preserving English behavior.

### Changes Made

- `test_chinese_web_search_uses_chinese_query_terms` now checks for `DuckDuckGo 查询：`.
- `_search_web_benchmarks(...)` now renders Chinese search notes with `DuckDuckGo 查询：...`.

### Verification After Changes

- Red test first failed because `search_note` was `DuckDuckGo query: 多智能体论文审查系统 优秀 论文 研究报告 分析`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_uses_chinese_query_terms tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 54 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter46 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 47 - 2026-05-04 09:40 PDT

### Current Problems

- Local benchmark strength inference recognized evidence and limitations, but not method-audit signals.
- Reports discussing `baseline`、`数据`、`消融实验` did not feed that quality trait into later rubric/report generation.

### Planned Changes

- Add a Chinese local benchmark test for method-audit strength extraction.
- Add baseline/data/ablation keyword detection to benchmark strength inference.
- Preserve existing evidence and limitations strengths.

### Changes Made

- Added `test_chinese_local_benchmark_extracts_method_audit_strength`.
- `_infer_report_strengths(...)` now emits `检查 baseline、数据和消融实验是否充分。` in Chinese mode.
- English mode gets the parallel strength `Audits baselines, data, and ablation evidence.`

### Verification After Changes

- Red test first failed because strengths only contained `把论文主张连接到实验证据。`
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_extracts_method_audit_strength tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality`
- `python3 -m unittest discover -s tests` passed with 55 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter47 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 48 - 2026-05-04 09:42 PDT

### Current Problems

- When `ReportWriterAgent` was called with no benchmark reports, Chinese benchmark quality rendered `来源类型：。`
- That empty punctuation made externally constructed or recovered reports look broken.

### Planned Changes

- Add a Chinese regression test for empty benchmark quality summaries.
- Render an explicit empty source-type placeholder.
- Mirror the empty placeholder in English summaries.

### Changes Made

- Added `test_chinese_benchmark_quality_handles_empty_sources_readably`.
- `_benchmark_quality_summary(...)` now uses `来源类型：无` when no Chinese source types exist.
- English output now uses `Source types: none`.

### Verification After Changes

- Red test first failed because the section contained `来源类型：。`
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_handles_empty_sources_readably tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_uses_chinese_source_delimiter tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality`
- `python3 -m unittest discover -s tests` passed with 56 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter48 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 49 - 2026-05-04 09:44 PDT

### Current Problems

- Empty `.txt` or `.md` paper files were loaded successfully.
- The workflow then raised `ValueError("paper_text cannot be empty.")` outside the CLI input-error handling path, causing a traceback.

### Planned Changes

- Add a CLI regression test for empty paper files.
- Reject empty text inputs inside `load_paper_text(...)`.
- Preserve existing missing-file and valid-input behavior.

### Changes Made

- Added `test_cli_rejects_empty_paper_without_traceback`.
- `load_paper_text(...)` now raises `ValueError("Paper file is empty: ...")` for whitespace-only text/Markdown files.

### Verification After Changes

- Red test first errored with an uncaught traceback from `run_research_workflow(...)`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_empty_paper_without_traceback tests.test_cli_io.InputAndCliTest.test_load_paper_text_reports_missing_file_clearly tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 57 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter49 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 50 - 2026-05-04 09:46 PDT

### Current Problems

- Unsupported paper input errors only said `Unsupported paper file type: .docx`.
- The message did not tell users which input types are accepted.

### Planned Changes

- Add an input-helper regression test for unsupported file types.
- Include the supported extension list in the error message.
- Preserve existing empty-file and CLI validation behavior.

### Changes Made

- Added `test_load_paper_text_lists_supported_types_for_unsupported_file`.
- `load_paper_text(...)` now reports: `Supported types: .txt, .md, .pdf.`

### Verification After Changes

- Red test first failed because the error message lacked the supported type list.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_load_paper_text_lists_supported_types_for_unsupported_file tests.test_cli_io.InputAndCliTest.test_cli_rejects_empty_paper_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_rejects_output_filenames_with_wrong_extensions`
- `python3 -m unittest discover -s tests` passed with 58 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter50 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 51 - 2026-05-04 18:42 PDT

### Current Problems

- `--benchmark-dir` silently fell back to built-in benchmark patterns when the supplied directory did not exist.
- In long runs this could make users believe their own benchmark corpus was being used when it was not.

### Planned Changes

- Add a CLI regression test for a missing benchmark directory.
- Reject missing benchmark directories before reading the paper or writing outputs.
- Preserve successful runs with valid arguments.

### Changes Made

- Added `test_cli_rejects_missing_benchmark_dir_without_traceback`.
- `main(...)` now emits `--benchmark-dir does not exist: ...` through `argparse` when the directory is missing.

### Verification After Changes

- Red test first failed because no `SystemExit` was raised and the CLI wrote default outputs.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_missing_benchmark_dir_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 59 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter51 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 52 - 2026-05-04 18:44 PDT

### Current Problems

- `--benchmark-dir` accepted ordinary files.
- The workflow then treated the path as unusable and silently fell back to built-in benchmark patterns.

### Planned Changes

- Add a CLI regression test for file paths passed as `--benchmark-dir`.
- Reject non-directory benchmark paths with a clear argparse error.
- Preserve missing-directory validation from Iteration 51.

### Changes Made

- Added `test_cli_rejects_file_benchmark_dir_without_traceback`.
- `main(...)` now emits `--benchmark-dir must be a directory: ...` when the path exists but is not a directory.

### Verification After Changes

- Red test first failed because no `SystemExit` was raised and default outputs were written.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_file_benchmark_dir_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_rejects_missing_benchmark_dir_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 60 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter52 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 53 - 2026-05-04 18:47 PDT

### Current Problems

- `--output-dir` could point to an existing regular file.
- The workflow then raised `FileExistsError` while trying to create the output directory, producing a traceback.

### Planned Changes

- Add a CLI regression test for file paths passed as `--output-dir`.
- Reject non-directory output paths during argument validation.
- Preserve normal output directory creation for missing directories.

### Changes Made

- Added `test_cli_rejects_file_output_dir_without_traceback`.
- `main(...)` now emits `--output-dir must be a directory: ...` when the output path exists but is not a directory.

### Verification After Changes

- Red test first errored with `FileExistsError`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_rejects_file_output_dir_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- `python3 -m unittest discover -s tests` passed with 61 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter53 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 54 - 2026-05-04 18:49 PDT

### Current Problems

- Continuous resume failed with a raw `JSONDecodeError` traceback when an existing `research_rounds.jsonl` file was corrupt.
- This made recovery from interrupted or manually edited long runs hard to diagnose.

### Planned Changes

- Add a CLI regression test for corrupt resume JSONL.
- Wrap JSON decode failures with a clear file and line number message.
- Route workflow `ValueError`s through argparse so CLI output stays traceback-free.

### Changes Made

- Added `test_cli_reports_corrupt_resume_jsonl_without_traceback`.
- `_load_jsonl_rounds(...)` now raises `Could not load existing JSONL ... invalid JSON on line N`.
- `main(...)` now catches workflow `ValueError` and reports it through `parser.error(...)`.

### Verification After Changes

- Red test first errored with `json.decoder.JSONDecodeError`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_reports_corrupt_resume_jsonl_without_traceback tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds`
- `python3 -m unittest discover -s tests` passed with 62 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter54 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 55 - 2026-05-04 18:52 PDT

### Current Problems

- Resume JSONL with valid JSON but invalid round structure still failed with raw `KeyError` tracebacks.
- Users could not tell which line in the existing JSONL needed repair.

### Planned Changes

- Add a CLI regression test for structurally invalid resume records.
- Wrap round hydration failures with a file and line number.
- Preserve legacy metadata hydration for valid older records.

### Changes Made

- Added `test_cli_reports_invalid_resume_record_without_traceback`.
- `_load_jsonl_rounds(...)` now wraps `KeyError`, `TypeError`, and `ValueError` from `_round_from_dict(...)`.
- The error now reports `invalid round record on line N`.

### Verification After Changes

- Initial test run exposed a missing test import for `json`; after fixing the test, the red test failed with `KeyError: 'benchmark_reports'`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_reports_invalid_resume_record_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_reports_corrupt_resume_jsonl_without_traceback tests.test_workflow.ResearchWorkflowTest.test_resume_hydrates_legacy_benchmark_metadata`
- `python3 -m unittest discover -s tests` passed with 63 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter55 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 56 - 2026-05-04 18:55 PDT

### Current Problems

- Legacy JSONL could store benchmark `strengths` as a scalar string.
- Hydration used `list(value)`, which split that string into individual characters and silently corrupted benchmark strengths.

### Planned Changes

- Add a resume regression test for scalar legacy benchmark strengths.
- Wrap scalar strings as single-item lists.
- Preserve normal list hydration and invalid-record detection.

### Changes Made

- Added `test_resume_keeps_scalar_legacy_benchmark_strength_as_single_item`.
- Added `_string_list(...)` for string-list hydration.
- Benchmark strengths now hydrate from either `["..."]` or `"..."` safely.

### Verification After Changes

- Red test first failed because strengths became a character list.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_resume_keeps_scalar_legacy_benchmark_strength_as_single_item tests.test_workflow.ResearchWorkflowTest.test_resume_hydrates_legacy_benchmark_metadata tests.test_cli_io.InputAndCliTest.test_cli_reports_invalid_resume_record_without_traceback`
- `python3 -m unittest discover -s tests` passed with 64 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter56 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 57 - 2026-05-04 18:57 PDT

### Current Problems

- Legacy JSONL could store `critic_review.issues` or `critic_review.recommendations` as scalar strings.
- Hydration used `list(value)`, which split those strings into characters.

### Planned Changes

- Add a resume regression test for scalar critic issue/recommendation fields.
- Reuse the string-list hydration helper from Iteration 56.
- Preserve invalid-record detection for genuinely malformed objects.

### Changes Made

- Added `test_resume_keeps_scalar_legacy_critic_lists_as_single_items`.
- `_round_from_dict(...)` now hydrates critic issues and recommendations with `_string_list(...)`.

### Verification After Changes

- Red test first failed because `critic.issues` became a list of characters.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_resume_keeps_scalar_legacy_critic_lists_as_single_items tests.test_workflow.ResearchWorkflowTest.test_resume_keeps_scalar_legacy_benchmark_strength_as_single_item tests.test_cli_io.InputAndCliTest.test_cli_reports_invalid_resume_record_without_traceback`
- `python3 -m unittest discover -s tests` passed with 65 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter57 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 58 - 2026-05-04 18:59 PDT

### Current Problems

- `ReportWriterAgent` only used the first two strengths from each benchmark report.
- Newly inferred method-audit strengths such as baseline/data/ablation checks could be omitted from `基于 Benchmark 的改进`.

### Planned Changes

- Add a regression test where method-audit guidance is the third benchmark strength.
- Include one more strength per benchmark while keeping the section concise.
- Preserve punctuation cleanup for English and Chinese benchmark improvement sections.

### Changes Made

- Added `test_chinese_benchmark_improvement_includes_method_audit_lessons`.
- `ReportWriterAgent` now includes up to three strengths from each benchmark in benchmark-informed improvement text.

### Verification After Changes

- Red test first failed because the section only contained the first two benchmark strengths.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_method_audit_lessons tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_has_clean_punctuation tests.test_workflow.ResearchWorkflowTest.test_english_benchmark_improvement_has_clean_punctuation`
- `python3 -m unittest discover -s tests` passed with 66 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter58 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 59 - 2026-05-04 19:02 PDT

### Current Problems

- If multiple benchmark reports shared the same strength, `基于 Benchmark 的改进` repeated identical lessons.
- Repetition made the generated report less concise and less useful for later scoring.

### Planned Changes

- Add a regression test for duplicate benchmark lessons.
- Deduplicate lessons while preserving the first occurrence order.
- Preserve method-audit lesson inclusion from Iteration 58.

### Changes Made

- Added `test_chinese_benchmark_improvement_deduplicates_repeated_lessons`.
- `ReportWriterAgent` now builds benchmark lessons through ordered deduplication.

### Verification After Changes

- Red test first failed because the repeated lesson appeared twice.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_deduplicates_repeated_lessons tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_method_audit_lessons tests.test_workflow.ResearchWorkflowTest.test_english_benchmark_improvement_has_clean_punctuation`
- `python3 -m unittest discover -s tests` passed with 67 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter59 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 60 - 2026-05-04 19:04 PDT

### Current Problems

- CLI now rejects missing or non-directory `--benchmark-dir` paths, but README did not document that stricter requirement.
- Users could still expect nonexistent paths to silently fall back.

### Planned Changes

- Add a documentation regression assertion.
- Document that `--benchmark-dir` must be an existing directory.
- Preserve existing traceability and custom filename docs.

### Changes Made

- Extended `test_readme_documents_benchmark_traceability_and_library_import`.
- README now says `--benchmark-dir` must point to an existing directory containing `.txt` or `.md` benchmark reports.

### Verification After Changes

- Red docs test first failed because README lacked the new benchmark-dir requirement.
- Target tests passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import tests.test_cli_io.InputAndCliTest.test_cli_rejects_missing_benchmark_dir_without_traceback tests.test_cli_io.InputAndCliTest.test_cli_rejects_file_benchmark_dir_without_traceback`
- `python3 -m unittest discover -s tests` passed with 67 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter60 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 61 - 2026-05-04 19:06 PDT

### Current Problems

- CLI supports `--no-resume`, but README did not document how to start a fresh continuous run.
- Users reading only README could miss how to ignore existing JSONL records.

### Planned Changes

- Add a README regression assertion for `--no-resume`.
- Document the option in the continuous-run section.
- Preserve existing traceability and benchmark-dir documentation.

### Changes Made

- Extended `test_readme_documents_benchmark_traceability_and_library_import`.
- README now explains that `--no-resume` ignores existing `research_rounds.jsonl` records and starts fresh.

### Verification After Changes

- Red docs test first failed because README lacked `--no-resume`.
- Target tests passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds`
- `python3 -m unittest discover -s tests` passed with 67 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter61 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 62 - 2026-05-04 19:08 PDT

### Current Problems

- Chinese `后续研究议程` still used English terms: `baseline`, `ablation`, and `agent`.
- This weakened Chinese output quality in the final report and DOCX.

### Planned Changes

- Add a Chinese report regression test for the research agenda section.
- Replace those English terms with natural Chinese equivalents.
- Preserve existing Chinese DOCX generation behavior.

### Changes Made

- Added `test_chinese_research_agenda_localizes_agent_terms`.
- `后续研究议程` now says `基线方法`、`消融实验`、`智能体角色`.

### Verification After Changes

- Red test first failed because the agenda contained `baseline`, `ablation`, and `agent`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_research_agenda_localizes_agent_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- `python3 -m unittest discover -s tests` passed with 68 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter62 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 63 - 2026-05-04 19:11 PDT

### Current Problems

- Chinese `关键假设与验证缺口` still contained framework terms `benchmark`, `agent`, and `rubric`.
- This made the Chinese report feel partially untranslated.

### Planned Changes

- Add a regression test for the assumptions/gaps section.
- Replace the remaining English framework terms with natural Chinese terms.
- Preserve scorecard evidence behavior that references the section.

### Changes Made

- Added `test_chinese_assumption_gap_section_localizes_framework_terms`.
- The section now uses `对照报告`、`智能体`、`评分标准`.

### Verification After Changes

- Red test first failed because the section did not include `对照报告` and still contained English framework terms.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_assumption_gap_section_localizes_framework_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- `python3 -m unittest discover -s tests` passed with 69 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter63 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 64 - 2026-05-04 19:13 PDT

### Current Problems

- Chinese `执行摘要` still used `外部 benchmark`.
- This was another untranslated framework term in a high-visibility report section.

### Planned Changes

- Add a regression test for the Chinese executive summary.
- Replace `外部 benchmark` with a natural Chinese phrase.
- Preserve existing Chinese DOCX generation and evidence-ledger behavior.

### Changes Made

- Added `test_chinese_executive_summary_localizes_benchmark_term`.
- `执行摘要` now uses `外部对照报告`.

### Verification After Changes

- Red test first failed because the summary did not contain `外部对照报告` and still contained `benchmark`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_executive_summary_localizes_benchmark_term tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- `python3 -m unittest discover -s tests` passed with 70 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter64 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 65 - 2026-05-04 19:15 PDT

### Current Problems

- The Chinese report section title `基于 Benchmark 的改进` still mixed English into a visible heading.
- This affected JSONL structure and DOCX headings.

### Planned Changes

- Add a regression test requiring the localized section title.
- Rename the Chinese section to `基于对照报告的改进`.
- Update existing tests to use the new section title.

### Changes Made

- Added `test_chinese_benchmark_improvement_section_title_is_localized`.
- Renamed the Chinese report section from `基于 Benchmark 的改进` to `基于对照报告的改进`.

### Verification After Changes

- Red test first failed because report sections still contained `基于 Benchmark 的改进`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_section_title_is_localized tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_has_clean_punctuation tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_method_audit_lessons tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_deduplicates_repeated_lessons`
- `python3 -m unittest discover -s tests` passed with 71 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter65 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 66 - 2026-05-04 19:26 PDT

### Current Problems

- The Chinese report still used the section title `Benchmark 对照质量`.
- This left English framework vocabulary in a visible heading and the DOCX export.

### Planned Changes

- Update the existing benchmark-quality tests to expect the localized Chinese title.
- Rename the Chinese section to `对照报告质量`.
- Verify the report JSON and DOCX output still expose the quality summary.

### Changes Made

- Renamed the Chinese benchmark-quality section from `Benchmark 对照质量` to `对照报告质量`.
- Updated related workflow tests and DOCX XML assertions to use the localized title.

### Verification After Changes

- Red target tests first failed because the report still emitted `Benchmark 对照质量`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_uses_chinese_source_delimiter tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_handles_empty_sources_readably`
- `python3 -m unittest discover -s tests` passed with 71 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter66 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 67 - 2026-05-04 19:29 PDT

### Current Problems

- The Chinese `限制与风险` section still emitted `benchmark 敏感性` and `批评 agent`.
- The limitation summarizer did not recognize already-localized input such as `对照报告质量`.
- Several Chinese heading parser tests still normalized around English `benchmark` wording.

### Planned Changes

- Add a regression test that mixes `benchmark`、`rubric`、`critic` into a Chinese limitations paragraph.
- Localize the limitation summary output to `对照报告质量`、`评分标准`、`批评智能体`.
- Make the fixed review guidance use `对照报告敏感性`.

### Changes Made

- Added `test_chinese_limitation_section_localizes_framework_terms`.
- Updated Chinese limitation fixtures and assertions to expect `对照报告质量`.
- `zh_limitation_summary` now recognizes both legacy English framework terms and localized Chinese terms.
- The Chinese report guidance now says `对照报告敏感性`.

### Verification After Changes

- Red target tests first failed because limitations still contained `benchmark 敏感性`, `批评 agent`, and missed localized `对照报告质量` inputs.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_limitation_section_localizes_framework_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed tests.test_workflow.ResearchWorkflowTest.test_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_parenthesized_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_inline_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_space_numbered_chinese_headings_are_parsed`
- `python3 -m unittest discover -s tests` passed with 72 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter67 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 68 - 2026-05-04 19:31 PDT

### Current Problems

- The Chinese `对照报告质量` section still described source types as `内置 fallback` and `本地 benchmark`.
- Its follow-up sentence also said `本地 benchmark`, leaving English framework vocabulary in a reader-facing paragraph.

### Planned Changes

- Update benchmark-quality tests to require localized source-type labels.
- Keep the Chinese source delimiter behavior unchanged.
- Localize only the Chinese report text while preserving English report wording.

### Changes Made

- Changed Chinese built-in source type from `内置 fallback` to `内置回退模式`.
- Changed Chinese local source type from `本地 benchmark` to `本地对照报告`.
- Updated the benchmark-quality summary tail sentence to say `本地对照报告`.

### Verification After Changes

- Red target tests first failed because source types still emitted `内置 fallback` and `本地 benchmark`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_uses_chinese_source_delimiter`
- `python3 -m unittest discover -s tests` passed with 72 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter68 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 69 - 2026-05-04 19:33 PDT

### Current Problems

- Chinese benchmark search provenance still used `内置 fallback` and `本地 benchmark`.
- Local search notes also used `keyword 命中`, which made DOCX/search trace text feel partly untranslated.

### Planned Changes

- Add stricter tests for Chinese local search notes and built-in fallback notes.
- Rename the Chinese local note to `本地对照报告文件` and `关键词命中`.
- Rename the Chinese fallback note to `内置回退` and remove `benchmark` from the note body.

### Changes Made

- Updated `_fallback_search_note` for Chinese to use `内置回退` and `网页对照报告`.
- Updated `_local_search_note` for Chinese to use `本地对照报告文件` and `关键词命中`.
- Expanded tests to reject `fallback`、`benchmark`、`keyword` in Chinese search notes.

### Verification After Changes

- Red target tests first failed because search notes still emitted `内置 fallback`, `本地 benchmark`, and `keyword 命中`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_note_localizes_no_keyword_overlap tests.test_workflow.ResearchWorkflowTest.test_builtin_benchmark_fallback_returns_diverse_report_archetypes`
- `python3 -m unittest discover -s tests` passed with 72 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter69 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 70 - 2026-05-04 19:35 PDT

### Current Problems

- Chinese web-search results with missing titles defaulted to `外部 benchmark 报告 N`.
- This left English framework vocabulary in a generated result title that appears in reports and DOCX exports.

### Planned Changes

- Update the missing-title web-search regression test to require `外部对照报告 N`.
- Keep English web-search fallback titles unchanged.
- Verify the full workflow still passes.

### Changes Made

- Changed the Chinese missing-title fallback from `外部 benchmark 报告 {index}` to `外部对照报告 {index}`.
- Added an assertion that the Chinese fallback title does not contain `benchmark`.

### Verification After Changes

- Red target test first failed because the title was still `外部 benchmark 报告 1`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_localizes_missing_title`
- `python3 -m unittest discover -s tests` passed with 72 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter70 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 71 - 2026-05-04 19:37 PDT

### Current Problems

- Chinese rubric `source_notes` still said `benchmark 报告` and `Benchmark 数量`.
- The generated phrase also had an awkward space after `基于`.

### Planned Changes

- Update the source-notes punctuation test to require `对照报告` wording.
- Rename the Chinese benchmark count label to `对照报告数量`.
- Remove the extra space after `基于`.

### Changes Made

- Chinese rubric source notes now start with `基于对照报告、当前报告生成`.
- Second-round source notes now use `基于对照报告、当前报告、上一轮报告、上一轮评分标准批评生成`.
- The benchmark count label is now `对照报告数量`.

### Verification After Changes

- Red target test first failed because source notes still emitted `benchmark 报告` and then exposed the extra `基于 ` spacing.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_source_notes_use_readable_punctuation`
- `python3 -m unittest discover -s tests` passed with 72 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter71 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 72 - 2026-05-04 19:39 PDT

### Current Problems

- Chinese rubric critic issues and recommendations still used `benchmark`.
- The no-results recommendation also said `benchmark 搜索`, so Chinese DOCX/JSON traces were not fully localized.

### Planned Changes

- Add a focused regression test for Chinese critic issue and recommendation text.
- Replace `benchmark 报告` with `对照报告`.
- Replace `benchmark 搜索` with `对照报告搜索`.

### Changes Made

- Added `test_chinese_rubric_critic_localizes_benchmark_terms`.
- Chinese critic issues now describe `对照报告` style/domain bias.
- Chinese critic recommendations now track `对照报告` metadata and handle missing `对照报告搜索` results.

### Verification After Changes

- Red target test first failed because critic text still contained three `benchmark` phrases.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_critic_localizes_benchmark_terms`
- `python3 -m unittest discover -s tests` passed with 73 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter72 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 73 - 2026-05-04 19:41 PDT

### Current Problems

- Chinese DOCX intro text still said `benchmark 搜索`.
- The benchmark-results heading was `Benchmark 搜索结果`.
- Empty benchmark-search output said `未记录可用的 benchmark 搜索结果。`

### Planned Changes

- Strengthen the DOCX regression test to inspect the Chinese intro, heading, and empty-state text.
- Replace all three reader-facing DOCX strings with `对照报告搜索`.
- Preserve English DOCX wording.

### Changes Made

- Chinese DOCX intro now says `对照报告搜索`.
- Chinese round heading now says `对照报告搜索结果`.
- Chinese empty search state now says `未记录可用的对照报告搜索结果。`

### Verification After Changes

- Red target test first failed because the generated DOCX still contained all three `benchmark 搜索` strings.
- Target test passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_chinese_export_explains_empty_benchmark_results`
- `python3 -m unittest discover -s tests` passed with 73 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter73 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 74 - 2026-05-04 19:43 PDT

### Current Problems

- Chinese resume hydration for legacy JSONL search notes still said `benchmark trace metadata`.
- This affected old-run compatibility paths and could surface in regenerated reports.

### Planned Changes

- Strengthen the Chinese legacy-resume test to require localized metadata wording.
- Replace `benchmark trace metadata` with `对照报告追踪元数据` in Chinese recovery notes.
- Keep English recovery wording unchanged.

### Changes Made

- Chinese `_legacy_search_note` now returns `从缺少对照报告追踪元数据的旧版 JSONL 恢复：...`.
- The resume regression test now rejects `benchmark` and `trace metadata` in the Chinese search note.

### Verification After Changes

- Red target test first failed because the legacy search note still said `benchmark trace metadata`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_resume_hydrates_legacy_benchmark_note_in_chinese`
- `python3 -m unittest discover -s tests` passed with 73 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter74 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 75 - 2026-05-04 19:45 PDT

### Current Problems

- Chinese evidence-ledger output copied `baseline` from the paper text into the generated report.
- The fixed verification-gap sentence also said `baseline 设置`.

### Planned Changes

- Update Chinese report tests to require `基线方法` in the evidence ledger.
- Ensure generated Chinese evidence summaries translate `baseline`.
- Localize the fixed verification-gap wording.

### Changes Made

- `zh_evidence_summary` now emits `基线方法` instead of `baseline`.
- The Chinese evidence-ledger verification gap now says `基线方法设置`.
- Heading/parser tests now reject `baseline` in the generated Chinese evidence ledger while leaving source-paper fixtures unchanged.

### Verification After Changes

- Red target tests first failed because the evidence ledger still contained `baseline`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed tests.test_workflow.ResearchWorkflowTest.test_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_parenthesized_numbered_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_inline_chinese_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_space_numbered_chinese_headings_are_parsed`
- `python3 -m unittest discover -s tests` passed with 73 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter75 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 76 - 2026-05-04 19:47 PDT

### Current Problems

- Chinese benchmark method-audit strengths still emitted `检查 baseline、数据和消融实验是否充分`.
- Built-in Chinese benchmark summaries and strengths also used `baseline`.
- The `基于对照报告的改进` section could therefore reintroduce English terminology.

### Planned Changes

- Update local benchmark extraction tests to require `基线方法`.
- Update report-improvement tests to reject `baseline` in Chinese benchmark lessons.
- Localize both built-in and inferred Chinese benchmark strengths.

### Changes Made

- Chinese built-in methodology benchmark summary now says `基线方法`.
- Chinese built-in methodology benchmark strength now says `追问基线方法、数据和消融实验是否充分`.
- `_infer_report_strengths` now emits `检查基线方法、数据和消融实验是否充分。` for Chinese.

### Verification After Changes

- Red target test first failed because extracted Chinese strengths still contained `baseline`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_extracts_method_audit_strength tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_method_audit_lessons`
- `python3 -m unittest discover -s tests` passed with 73 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter76 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 77 - 2026-05-04 19:52 PDT

### Current Problems

- Chinese rubric criterion descriptions still contained `baseline`.
- This appeared in the DOCX scoring-standard section, even after report body and benchmark lessons were localized.

### Planned Changes

- Add a regression test that inspects all Chinese rubric criterion descriptions across two rounds.
- Replace visible Chinese rubric descriptions with `基线方法`.
- Keep internal scoring keyword compatibility unchanged.

### Changes Made

- Added `test_chinese_rubric_descriptions_localize_baseline_terms`.
- The `证据质量` criterion now says `评价实验、基线方法、测量方式和主张支撑`.
- The second-round reproducibility criterion now says `复现实验、数据、基线方法和评估缺口`.

### Verification After Changes

- Red target test first failed because descriptions still contained two `baseline` occurrences.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_descriptions_localize_baseline_terms`
- `python3 -m unittest discover -s tests` passed with 74 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter77 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 78 - 2026-05-04 19:53 PDT

### Current Problems

- The Chinese `限制与失败模式` rubric description still ended with the English word `caveat`.
- This showed up in Chinese DOCX rubric output.

### Planned Changes

- Expand the Chinese rubric-description regression test to require `注意事项`.
- Reject `caveat` in generated Chinese rubric descriptions.
- Keep the English rubric description unchanged.

### Changes Made

- Updated `限制与失败模式` description to `揭示弱点、缺失控制、可复现性风险和注意事项。`
- The rubric-description test now rejects both `baseline` and `caveat`.

### Verification After Changes

- Red target test first failed because descriptions still contained `caveat`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_descriptions_localize_baseline_terms`
- `python3 -m unittest discover -s tests` passed with 74 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter78 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 79 - 2026-05-04 19:56 PDT

### Current Problems

- Chinese scoring still used the internal keyword `baseline` for evidence-quality and reproducibility scoring.
- After report text was localized to `基线方法`, the evidence snippet for `证据质量` could jump to the wrong section instead of citing the evidence ledger.

### Planned Changes

- Add a regression test requiring Chinese evidence scoring to cite `基线方法`.
- Replace Chinese scoring keywords with localized terms.
- Preserve English scoring keywords unchanged.

### Changes Made

- Added `test_chinese_scoring_counts_localized_baseline_marker`.
- Chinese `证据质量` scoring now uses `基线方法` instead of `baseline`.
- Chinese `可复现性与证据引用` scoring also uses `基线方法`.

### Verification After Changes

- Red target test first failed because the evidence rationale cited `关键假设与验证缺口` and did not include `基线方法`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker`
- `python3 -m unittest discover -s tests` passed with 75 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter79 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 80 - 2026-05-04 19:59 PDT

### Current Problems

- Chinese technical-contribution scoring still used the English keyword `agent`.
- The generated report had already localized this concept to `智能体`, so contribution scoring undercounted one relevant marker.

### Planned Changes

- Add a regression test requiring Chinese `技术贡献` scoring to count localized agent terminology.
- Replace the Chinese scoring keyword `agent` with `智能体`.
- Keep English scoring keywords unchanged.

### Changes Made

- Added `test_chinese_scoring_counts_localized_agent_marker`.
- Chinese `技术贡献` scoring now uses `智能体`.
- The test now requires the contribution score to reach the 5-marker band while citing `多智能体` without `agent`.

### Verification After Changes

- Tightened red target test first failed because `技术贡献` scored 14 instead of the expected localized-marker score band.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_agent_marker`
- `python3 -m unittest discover -s tests` passed with 76 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter80 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 81 - 2026-05-04 20:01 PDT

### Current Problems

- Chinese research-usefulness scoring still used the English keyword `ablation`.
- The generated Chinese agenda uses `消融实验`, so the scorer undercounted one relevant marker.

### Planned Changes

- Add a regression test requiring `研究价值` scoring to count `消融实验`.
- Replace the Chinese scoring keyword `ablation` with `消融实验`.
- Keep English scoring unchanged.

### Changes Made

- Added `test_chinese_scoring_counts_localized_ablation_marker`.
- Chinese `研究价值` scoring now uses `消融实验`.
- The test verifies the score reaches the expected band and the rationale does not contain `ablation`.

### Verification After Changes

- Red target test first failed because `研究价值` scored 12 instead of counting the localized ablation marker.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_ablation_marker`
- `python3 -m unittest discover -s tests` passed with 77 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter81 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 82 - 2026-05-04 20:04 PDT

### Current Problems

- Chinese `对照报告质量` coverage detection recognized method-audit coverage via `baseline` or `消融`.
- A localized strength that only said `基线方法` fell back to `通用研究报告模式`.

### Planned Changes

- Add a regression test for localized baseline-only benchmark strengths.
- Count `基线` as method-audit coverage in Chinese benchmark-quality summaries.
- Preserve English coverage detection.

### Changes Made

- Added `test_chinese_benchmark_quality_counts_localized_baseline_coverage`.
- Chinese benchmark-quality coverage now treats `基线` as `方法审计`.

### Verification After Changes

- Red target test first failed because the quality summary returned `通用研究报告模式`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_counts_localized_baseline_coverage`
- `python3 -m unittest discover -s tests` passed with 78 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter82 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 83 - 2026-05-04 20:07 PDT

### Current Problems

- Chinese contribution analysis emitted `论文强调 多智能体` with an unnatural extra space after `强调`.
- This affected a high-visibility report section.

### Planned Changes

- Update the Chinese contribution-marker test to require natural spacing.
- Remove the extra space in `_extract_contribution`.
- Preserve English contribution phrasing.

### Changes Made

- Chinese contribution extraction now returns `论文强调多智能体、...`.
- The regression test now rejects `论文强调 多智能体`.

### Verification After Changes

- Red target test first failed because contribution text still contained `论文强调 多智能体`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_extracts_chinese_markers`
- `python3 -m unittest discover -s tests` passed with 78 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter83 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 84 - 2026-05-04 20:10 PDT

### Current Problems

- The Chinese evidence ledger repeated the same evidence summary in both `证据` and `解释`.
- This reduced information density in a core report section.

### Planned Changes

- Add a regression test requiring the core evidence sentence to appear only once.
- Rewrite the explanation line to connect method and experiment interpretation without repeating the full evidence sentence.
- Preserve the evidence line itself for scoring and citation.

### Changes Made

- Added `test_chinese_evidence_ledger_avoids_repeating_evidence_summary`.
- The explanation line now says `实验部分提供了覆盖提升的方向性证据`.
- The evidence summary remains in the `证据` line, so scoring still has a concrete snippet to cite.

### Verification After Changes

- Red target test first failed because the evidence sentence appeared twice.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_evidence_ledger_avoids_repeating_evidence_summary`
- `python3 -m unittest discover -s tests` passed with 79 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter84 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 85 - 2026-05-04 20:14 PDT

### Current Problems

- The Chinese `贡献分析` section emitted `。 本报告...` with an English-style space after the Chinese full stop.
- This made a high-visibility paragraph feel mechanically concatenated.

### Planned Changes

- Add a regression assertion rejecting `。 ` in Chinese contribution analysis.
- Remove the extra space from the section concatenation.
- Preserve English report spacing.

### Changes Made

- Updated `test_chinese_contribution_analysis_localizes_marker_terms`.
- Removed the extra space between the extracted contribution sentence and the follow-up sentence.

### Verification After Changes

- Red target test first failed because contribution analysis contained `。 本报告`.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_localizes_marker_terms`
- `python3 -m unittest discover -s tests` passed with 79 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter85 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 86 - 2026-05-04 20:18 PDT

### Current Problems

- Local benchmark search sorted reports with equal keyword matches by filename.
- A thin note could outrank a more structured report if its filename sorted earlier.

### Planned Changes

- Add a regression test where two local reports have identical keyword matches but different report structure.
- Add a lightweight structure score for local benchmark tie-breaking.
- Keep keyword match count as the primary ranking signal.

### Changes Made

- Added `test_local_benchmark_search_tiebreaks_on_report_structure`.
- Local search now records a structure score based on claim/evidence/limitations/follow-up style markers.
- Sorting now uses keyword score, then structure score, then filename.

### Verification After Changes

- Red target test first failed because `aaa_thin.md` outranked `zzz_structured.md`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_tiebreaks_on_report_structure tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_scores_more_than_first_five_files`
- `python3 -m unittest discover -s tests` passed with 80 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter86 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 87 - 2026-05-04 20:21 PDT

### Current Problems

- When no local benchmark file matched paper keywords, fallback selection used the first two files by filename.
- This could ignore a more structured local report if it appeared later alphabetically.

### Planned Changes

- Add a regression test with no keyword matches and one structured local report.
- Use structure score for fallback selection as well as keyword-tie sorting.
- Preserve the existing no-keyword search-note behavior.

### Changes Made

- Added `test_local_benchmark_fallback_prefers_structured_reports_without_keyword_matches`.
- No-keyword local fallback now sorts by structure score before filename.

### Verification After Changes

- Red target test first failed because `aaa_plain.md` was selected before `zzz_structured.md`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_fallback_prefers_structured_reports_without_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_note_localizes_no_keyword_overlap`
- `python3 -m unittest discover -s tests` passed with 81 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter87 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 88 - 2026-05-04 20:23 PDT

### Current Problems

- Local benchmark search only loaded `.txt` and `.md` files.
- `.markdown` benchmark reports were skipped, causing unnecessary fallback to built-in reports.

### Planned Changes

- Add a regression test for `.markdown` local benchmark files.
- Include `.markdown` in the local benchmark file suffix allow-list.
- Verify existing `.md` local search still works.

### Changes Made

- Added `test_searches_local_markdown_extension_benchmark_reports`.
- Local search now accepts `.markdown` files.

### Verification After Changes

- Red target test first failed because search fell back to `built-in://claim-evidence-round-1`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_searches_local_markdown_extension_benchmark_reports tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided`
- `python3 -m unittest discover -s tests` passed with 82 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter88 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 89 - 2026-05-04 20:25 PDT

### Current Problems

- Local benchmark search included hidden files such as `.draft.md`.
- A hidden draft with strong keyword overlap could outrank published benchmark reports.

### Planned Changes

- Add a regression test with a hidden draft and a visible published report.
- Skip local files when any path segment is hidden.
- Preserve normal `.md` and `.markdown` local search behavior.

### Changes Made

- Added `test_local_benchmark_search_ignores_hidden_files`.
- Local search now skips hidden files and files under hidden directories.

### Verification After Changes

- Red target test first failed because `.draft.md` was selected first.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_ignores_hidden_files tests.test_workflow.ResearchWorkflowTest.test_searches_local_markdown_extension_benchmark_reports`
- `python3 -m unittest discover -s tests` passed with 83 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter89 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 90 - 2026-05-04 20:28 PDT

### Current Problems

- A benchmark directory containing only blank files produced empty local benchmark reports.
- This prevented the workflow from falling back to useful built-in benchmark archetypes.

### Planned Changes

- Add a regression test for blank local benchmark files.
- Skip blank local files during benchmark search.
- Verify hidden-file filtering still works.

### Changes Made

- Added `test_local_benchmark_search_ignores_empty_files_and_uses_fallback`.
- Local search now skips files whose content is empty after trimming whitespace.

### Verification After Changes

- Red target test first failed because an empty file produced a `local` benchmark result.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_ignores_empty_files_and_uses_fallback tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_ignores_hidden_files`
- `python3 -m unittest discover -s tests` passed with 84 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter90 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 91 - 2026-05-04 20:30 PDT

### Current Problems

- Very short placeholder files such as `TBD` could still produce local benchmark reports.
- This polluted fallback behavior when a benchmark directory only contained placeholders.

### Planned Changes

- Add a regression test for placeholder local benchmark files.
- Skip only extremely short local file content to avoid dropping legitimate short Chinese notes.
- Re-run the no-keyword Chinese note test to guard against over-filtering.

### Changes Made

- Added `test_local_benchmark_search_ignores_placeholder_files`.
- Local search now skips files with fewer than 10 non-whitespace characters.

### Verification After Changes

- Red target test first failed because `placeholder.md` produced a `local` benchmark report.
- Initial threshold was too high and full tests caught an over-filtering regression; threshold was lowered to preserve short valid notes.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_ignores_placeholder_files tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_note_localizes_no_keyword_overlap`
- `python3 -m unittest discover -s tests` passed with 85 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter91 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 92 - 2026-05-04 20:33 PDT

### Current Problems

- README still documented local benchmark directories as `.txt` or `.md` only.
- It did not mention `.markdown` support or hidden/placeholder file filtering.

### Planned Changes

- Add documentation assertions for `.markdown` and ignored hidden/placeholder files.
- Update README local benchmark documentation.
- Keep existing traceability and CLI filename documentation intact.

### Changes Made

- README now says local benchmark directories can contain `.txt`, `.md`, or `.markdown` reports.
- README now says hidden files and placeholder files are ignored.
- Documentation test now covers both behaviors.

### Verification After Changes

- Red documentation test first failed because README did not mention `.markdown`.
- After updating README, the same test passed.
- `python3 -m unittest discover -s tests` passed with 85 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter92 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 93 - 2026-05-04 20:36 PDT

### Current Problems

- DOCX bullet paragraphs used a `ListBullet` style name but the package had no numbering part.
- Some DOCX readers may not render bullets reliably without `word/numbering.xml` and a document relationship.

### Planned Changes

- Add a DOCX structure regression test for numbering support.
- Add `word/numbering.xml` and `word/_rels/document.xml.rels`.
- Bind the `ListBullet` style to numbering ID 1.

### Changes Made

- Added `test_writes_numbering_part_for_bullets`.
- DOCX exports now include a numbering content type override, numbering relationship, and bullet numbering definition.
- `ListBullet` style now includes `w:numPr`.

### Verification After Changes

- Red target test first failed because `word/numbering.xml` was missing.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_writes_numbering_part_for_bullets tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections`
- `python3 -m unittest discover -s tests` passed with 86 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter93 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 94 - 2026-05-04 20:39 PDT

### Current Problems

- DuckDuckGo result parsing only recognized double-quoted HTML attributes.
- Search pages using single quotes for `class` or `href` attributes fell back to built-in reports.

### Planned Changes

- Add a regression test for single-quoted web result attributes.
- Extend result and snippet regexes to support both single and double quotes.
- Verify existing double-quoted English and Chinese web tests still pass.

### Changes Made

- Added `test_web_search_agent_handles_single_quoted_result_attributes`.
- `_extract_duckduckgo_results` now supports single-quoted and double-quoted attributes.

### Verification After Changes

- Red target test first failed because search fell back to `built-in://claim-evidence-round-1`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_single_quoted_result_attributes tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_chinese_web_search_uses_chinese_query_terms`
- `python3 -m unittest discover -s tests` passed with 87 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter94 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 95 - 2026-05-04 20:41 PDT

### Current Problems

- DuckDuckGo result parsing required `class` to appear before `href` on result links.
- If the HTML emitted `href` first, the workflow missed web results and used built-in fallback reports.

### Planned Changes

- Add a regression test for reversed `href`/`class` attribute order.
- Parse anchor tags into attributes first, then inspect `class` and `href`.
- Preserve support for single-quoted and double-quoted attributes.

### Changes Made

- Added `test_web_search_agent_handles_href_before_class`.
- `_extract_duckduckgo_results` now parses generic anchor attributes and no longer depends on attribute order.
- Added `_parse_html_attrs` for simple quoted attribute extraction.

### Verification After Changes

- Red target test first failed because search fell back to `built-in://claim-evidence-round-1`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_href_before_class tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_single_quoted_result_attributes tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 88 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter95 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 96 - 2026-05-04 20:44 PDT

### Current Problems

- Web result snippet parsing only checked anchor tags.
- Search pages using `<div class="result__snippet">` lost their snippets and used generic fallback summaries.

### Planned Changes

- Add a regression test for `div` snippets.
- Parse simple HTML elements with `result__snippet` class regardless of tag name.
- Verify existing anchor result parsing still works.

### Changes Made

- Added `test_web_search_agent_extracts_div_snippets`.
- `_extract_duckduckgo_results` now extracts snippets from any simple element with class `result__snippet`.

### Verification After Changes

- Red target test first failed because the summary fell back to `External search result...`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_div_snippets tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_href_before_class`
- `python3 -m unittest discover -s tests` passed with 89 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter96 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 97 - 2026-05-04 20:46 PDT

### Current Problems

- Web result attribute parsing only supported quoted attribute values.
- Simplified HTML with `class=result__a` or `href=https://...` was missed and triggered built-in fallback.

### Planned Changes

- Add a regression test for unquoted result and snippet attributes.
- Extend HTML attribute parsing to support double-quoted, single-quoted, and unquoted values.
- Verify quoted-attribute parsing still works.

### Changes Made

- Added `test_web_search_agent_handles_unquoted_attributes`.
- `_parse_html_attrs` now parses quoted and unquoted attribute values.

### Verification After Changes

- Red target test first failed because search fell back to `built-in://claim-evidence-round-1`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_unquoted_attributes tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_single_quoted_result_attributes tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_href_before_class`
- `python3 -m unittest discover -s tests` passed with 90 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter97 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 98 - 2026-05-04 20:48 PDT

### Current Problems

- Web result URL cleaning only recognized DuckDuckGo `uddg` redirect parameters.
- Redirect links using a `q` parameter were preserved as intermediate URLs.

### Planned Changes

- Add a regression test for `?q=` redirect URLs.
- Clean both `uddg` and `q` redirect parameters.
- Verify existing direct web result extraction still works.

### Changes Made

- Added `test_web_search_agent_cleans_q_redirect_urls`.
- `_clean_result_url` now unwraps `uddg` and `q` redirect parameters.

### Verification After Changes

- Red target test first failed because the source stayed `/url?q=...`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 91 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter98 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 99 - 2026-05-04 20:51 PDT

### Current Problems

- URL cleaning unwrapped any `q` parameter, even if it was a normal search term.
- A link like `/search?q=paper-analysis` became `paper-analysis`, which is not a usable source URL.

### Planned Changes

- Add a regression test for non-URL `q` values.
- Only unwrap `uddg` or `q` parameters when the decoded value is an HTTP(S) URL.
- Preserve the new `q` redirect URL cleaning behavior for real URLs.

### Changes Made

- Added `test_web_search_agent_keeps_non_url_q_values_as_original_href`.
- `_clean_result_url` now validates decoded redirect candidates before returning them.

### Verification After Changes

- Red target test first failed because `/search?q=paper-analysis` became `paper-analysis`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls`
- `python3 -m unittest discover -s tests` passed with 92 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter99 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 100 - 2026-05-04 20:54 PDT

### Current Problems

- DuckDuckGo result parsing matched CSS class names by substring.
- A class like `not-result__a` could be treated as a real search result, producing false-positive benchmark sources.

### Planned Changes

- Add a regression test for false-positive result class names.
- Match DuckDuckGo anchor and snippet classes as exact class tokens.
- Preserve existing parsing for normal anchors and `<div class="result__snippet">` snippets.

### Changes Made

- Added `test_web_search_agent_requires_result_class_tokens`.
- Added `_has_class` and used it for result anchors and snippets.

### Verification After Changes

- Red target test first failed because `not-result__a` was parsed as a web result.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_requires_result_class_tokens tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_div_snippets`
- `python3 -m unittest discover -s tests` passed with 93 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter100 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 101 - 2026-05-04 20:56 PDT

### Current Problems

- Redirect URL cleaning only accepted lowercase `http://` and `https://` schemes.
- A valid `HTTPS://...` redirect stayed wrapped as `/url?q=...`, reducing source quality in benchmark results.

### Planned Changes

- Add a regression test for uppercase-scheme redirect URLs.
- Make redirect candidate scheme validation case-insensitive.
- Preserve the original decoded candidate text after validation.

### Changes Made

- Added `test_web_search_agent_cleans_uppercase_scheme_redirect_urls`.
- `_clean_result_url` now checks redirect candidates with `candidate.lower().startswith(...)`.

### Verification After Changes

- Red target test first failed because the source stayed `/url?q=HTTPS...`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_uppercase_scheme_redirect_urls tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href`
- `python3 -m unittest discover -s tests` passed with 94 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter101 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 102 - 2026-05-04 20:58 PDT

### Current Problems

- Web result extraction accepted `result__a` anchors even when they had no `href`.
- Those entries became synthetic `web-search://...` sources, which looked like external benchmark evidence but had no real URL.

### Planned Changes

- Add a regression test for result anchors without `href`.
- Require a non-empty cleaned source URL before accepting a web result.
- Preserve normal web result parsing with real links.

### Changes Made

- Added `test_web_search_agent_ignores_result_anchors_without_href`.
- `_extract_duckduckgo_results` now skips result anchors that do not provide a source.

### Verification After Changes

- Red target test first failed because the missing-`href` anchor produced a web result.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_result_anchors_without_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 95 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter102 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 103 - 2026-05-04 21:01 PDT

### Current Problems

- The Chinese rubric already evolved when the prior critic asked for an explicit reproducibility criterion.
- The English rubric ignored the same critic signal and kept the generic `Research Usefulness` criterion in round 2.

### Planned Changes

- Add a regression test for second-round English rubric evolution.
- Replace the generic English final criterion with `Reproducibility and Evidence Citation` when prior critic feedback mentions reproducibility.
- Add scoring keywords for the new English criterion.

### Changes Made

- Added `test_second_round_english_rubric_evolves_from_critic_feedback`.
- Updated English `RubricBuilderAgent` logic to mirror the Chinese critic-feedback path.
- Added a keyword map entry for `Reproducibility and Evidence Citation`.

### Verification After Changes

- Red target test first failed because the second-round English rubric still used `Research Usefulness`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_second_round_english_rubric_evolves_from_critic_feedback tests.test_workflow.ResearchWorkflowTest.test_second_round_chinese_rubric_evolves_from_critic_feedback`
- `python3 -m unittest discover -s tests` passed with 96 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter103 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 104 - 2026-05-04 21:03 PDT

### Current Problems

- DOCX styles did not define explicit fonts for Latin or East Asian text.
- Chinese reports could render with unpredictable fallback fonts in Word-compatible readers.

### Planned Changes

- Add a DOCX regression test that inspects `word/styles.xml`.
- Define default Latin and East Asian fonts in the Normal style.
- Preserve existing Chinese title metadata and document export behavior.

### Changes Made

- Added `test_styles_define_multilingual_fonts`.
- Added `w:rFonts` to the DOCX Normal style with `Aptos` and `Microsoft YaHei`.

### Verification After Changes

- Red target test first failed because styles XML had no `w:rFonts` entry.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_styles_define_multilingual_fonts tests.test_docx.DocxWriterTest.test_export_uses_language_specific_core_title`
- `python3 -m unittest discover -s tests` passed with 97 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter104 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 105 - 2026-05-04 21:05 PDT

### Current Problems

- DOCX bullet numbering had a bullet glyph but no indentation settings.
- Long benchmark, rubric, or scorecard bullets could render too close to the page margin in Word-compatible readers.

### Planned Changes

- Add a DOCX regression test for bullet indentation in `word/numbering.xml`.
- Add a left indent and hanging indent to the bullet level definition.
- Preserve the existing numbering part and ListBullet style relationship.

### Changes Made

- Added `test_bullet_numbering_defines_indentation`.
- Added `<w:ind w:left="720" w:hanging="360"/>` to the bullet numbering level.

### Verification After Changes

- Red target test first failed because `word/numbering.xml` had no bullet indentation.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_bullet_numbering_defines_indentation tests.test_docx.DocxWriterTest.test_writes_numbering_part_for_bullets`
- `python3 -m unittest discover -s tests` passed with 98 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter105 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 106 - 2026-05-04 21:07 PDT

### Current Problems

- DOCX heading styles used visual formatting but did not define outline levels.
- Word-compatible readers could fail to expose the report hierarchy cleanly in navigation or outline views.

### Planned Changes

- Add a regression test for Heading1/2/3 outline levels in `word/styles.xml`.
- Add `w:outlineLvl` to each heading style.
- Preserve nested heading export behavior for report sections.

### Changes Made

- Added `test_heading_styles_define_outline_levels`.
- Added outline levels 0, 1, and 2 to Heading1, Heading2, and Heading3 styles.

### Verification After Changes

- Red target test first failed because no heading style had `w:outlineLvl`.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_heading_styles_define_outline_levels tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections`
- `python3 -m unittest discover -s tests` passed with 99 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter106 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 107 - 2026-05-04 21:10 PDT

### Current Problems

- Chinese benchmark keyword extraction did not include `基线`, `数据`, or `消融`.
- Local benchmark search could describe an experiment-audit match only as `方法、实验`, losing the more useful scoring dimensions.

### Planned Changes

- Add a regression test for Chinese baseline/data/ablation benchmark matching.
- Extend the Chinese keyword list with experiment-audit terms.
- Preserve existing Chinese keyword matching behavior for multi-agent and rubric reports.

### Changes Made

- Added `test_chinese_local_benchmark_matches_baseline_data_ablation_terms`.
- Added `基线`, `数据`, and `消融` to `_keywords`.

### Verification After Changes

- Red target test first failed because the search note only listed `方法、实验`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_matches_baseline_data_ablation_terms tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches`
- `python3 -m unittest discover -s tests` passed with 100 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter107 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 108 - 2026-05-04 21:12 PDT

### Current Problems

- Benchmark quality summaries counted built-in fallback archetypes as sources without separating real external sources.
- Chinese reports could say `来源数量：3` while all three entries were internal fallback patterns.

### Planned Changes

- Add a regression assertion for external source count and built-in-only warning text.
- Compute external benchmark count separately from total benchmark entries.
- Preserve readable handling for empty benchmark lists and mixed local/web source types.

### Changes Made

- Updated `test_chinese_report_records_benchmark_source_quality`.
- Added external source counting and a built-in-only note to `_benchmark_quality_summary`.
- Added `_raw_benchmark_source_type` to avoid duplicating source-type inference.

### Verification After Changes

- Red target test first failed because the Chinese quality section had no external source count.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_handles_empty_sources_readably tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_uses_chinese_source_delimiter`
- `python3 -m unittest discover -s tests` passed with 100 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter108 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 109 - 2026-05-04 21:14 PDT

### Current Problems

- English benchmark quality summaries still lacked external source counts after the Chinese path was improved.
- The English report could also overstate built-in fallback archetypes as if they were external benchmark evidence.

### Planned Changes

- Add an English regression test for external benchmark source counts.
- Add external source count and built-in-only warning text to English benchmark quality summaries.
- Preserve the Chinese behavior added in the previous iteration.

### Changes Made

- Added `test_english_report_records_external_benchmark_source_count`.
- Updated the English `_benchmark_quality_summary` text to include external source count and fallback-only warning.

### Verification After Changes

- Red target test first failed because the English section had no `External source count`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_report_records_external_benchmark_source_count tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality`
- `python3 -m unittest discover -s tests` passed with 101 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter109 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 110 - 2026-05-04 21:17 PDT

### Current Problems

- A real two-round Chinese sample run showed stale critic feedback.
- Round 2 added `可复现性与证据引用`, but the critic still complained that reproducibility was only embedded in limitations.

### Planned Changes

- Add a regression test for the second-round Chinese critic.
- Treat criterion names containing `可复现性` as explicit reproducibility criteria.
- Apply the same containment check to English `Reproducibility` criterion names.

### Changes Made

- Added `test_second_round_chinese_critic_recognizes_explicit_reproducibility_criterion`.
- Updated `RubricCriticAgent` criterion-name checks from exact membership to substring matching.

### Verification After Changes

- Ran a two-round Chinese sample command:
  - `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter110_zh`
- Red target test first failed because round 2 still emitted the stale reproducibility issue.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_second_round_chinese_critic_recognizes_explicit_reproducibility_criterion tests.test_workflow.ResearchWorkflowTest.test_second_round_chinese_rubric_evolves_from_critic_feedback`
- `python3 -m unittest discover -s tests` passed with 102 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter110 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 111 - 2026-05-04 21:20 PDT

### Current Problems

- When benchmark search returned only built-in fallback archetypes, the Chinese critic did not recommend adding real external comparisons.
- This left the benchmark quality warning isolated in the report instead of feeding into the improvement loop.

### Planned Changes

- Add a regression test for built-in-only benchmark critic recommendations.
- Keep the existing empty-search warning separate from the built-in-only warning.
- Localize the recommendation without using `benchmark` terminology.

### Changes Made

- Added `test_chinese_critic_flags_builtin_only_benchmark_sources`.
- `RubricCriticAgent` now recommends real external comparison reports when all benchmark reports are built-in fallback entries.

### Verification After Changes

- Red target test first failed because critic recommendations did not mention `内置回退` or `外部对照报告`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_critic_flags_builtin_only_benchmark_sources tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_critic_localizes_benchmark_terms`
- `python3 -m unittest discover -s tests` passed with 103 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter111 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 112 - 2026-05-04 21:23 PDT

### Current Problems

- The English critic did not flag rounds that relied only on built-in fallback benchmark patterns.
- This made the English feedback loop weaker than the Chinese one for source-quality remediation.

### Planned Changes

- Add an English regression test for built-in-only benchmark critic recommendations.
- Add an English recommendation that prioritizes real external benchmark reports after built-in-only rounds.
- Preserve the Chinese recommendation added in the previous iteration.

### Changes Made

- Added `test_english_critic_flags_builtin_only_benchmark_sources`.
- Updated the English `RubricCriticAgent` branch to detect built-in-only benchmark reports.

### Verification After Changes

- Red target test first failed because English recommendations did not mention `built-in fallback`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_critic_flags_builtin_only_benchmark_sources tests.test_workflow.ResearchWorkflowTest.test_chinese_critic_flags_builtin_only_benchmark_sources`
- `python3 -m unittest discover -s tests` passed with 104 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter112 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 113 - 2026-05-04 21:27 PDT

### Current Problems

- Continuous-mode resume accepted JSONL files with non-contiguous `round_number` values.
- A corrupted file starting at round 2 could be loaded, after which the runner would append another round 2 and produce ambiguous output.

### Planned Changes

- Add a resume regression test for non-contiguous round numbers.
- Validate loaded JSONL rounds are numbered from 1 without gaps.
- Preserve normal resume behavior and legacy metadata hydration.

### Changes Made

- Added `test_resume_rejects_non_contiguous_round_numbers`.
- `_load_jsonl_rounds` now raises a clear `ValueError` when line order and `round_number` do not match.

### Verification After Changes

- Re-ran a two-round Chinese sample:
  - `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter113_zh`
- Confirmed the second-round stale reproducibility critic issue stayed fixed in the real JSONL output.
- Red target test first failed because non-contiguous round numbers were accepted.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_resume_rejects_non_contiguous_round_numbers tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds tests.test_workflow.ResearchWorkflowTest.test_resume_hydrates_legacy_benchmark_metadata`
- `python3 -m unittest discover -s tests` passed with 105 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter113 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 114 - 2026-05-04 21:30 PDT

### Current Problems

- Paper input accepted `.md` but rejected `.markdown`.
- Benchmark search already accepted `.markdown`, so Markdown support was inconsistent across input paths.

### Planned Changes

- Add an input regression test for `.markdown` paper files.
- Accept `.markdown` in `load_paper_text`.
- Update the unsupported-file error message to list `.markdown`.

### Changes Made

- Added `test_load_paper_text_accepts_markdown_extension`.
- Updated `load_paper_text` suffix handling and the supported-types message.
- Updated the unsupported-file test expectation.

### Verification After Changes

- Red target test first failed because `.markdown` raised `Unsupported paper file type`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_load_paper_text_accepts_markdown_extension tests.test_cli_io.InputAndCliTest.test_load_paper_text_lists_supported_types_for_unsupported_file`
- `python3 -m unittest discover -s tests` passed with 106 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter114 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 115 - 2026-05-04 21:32 PDT

### Current Problems

- README described Markdown input generally but did not list `.markdown` paper inputs.
- This lagged behind the input loader behavior added in Iteration 114.

### Planned Changes

- Add a documentation regression assertion for `.txt`, `.md`, and `.markdown` paper input support.
- Update README usage notes to list supported paper input extensions explicitly.
- Preserve existing benchmark traceability documentation checks.

### Changes Made

- Updated `test_readme_documents_benchmark_traceability_and_library_import`.
- Updated README to state that paper inputs can be `.txt`, `.md`, or `.markdown` files.

### Verification After Changes

- Red documentation test first failed because README did not contain the explicit paper input extension sentence.
- Target tests passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import tests.test_cli_io.InputAndCliTest.test_load_paper_text_accepts_markdown_extension`
- `python3 -m unittest discover -s tests` passed with 106 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter115 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 116 - 2026-05-04 21:35 PDT

### Current Problems

- `run_research_workflow` rejected `WorkflowConfig(rounds=0)`, but `run_continuous_workflow` accepted it.
- Library callers could pass an invalid shared config and get different behavior depending on run mode.

### Planned Changes

- Add a continuous-mode regression test for invalid `WorkflowConfig.rounds`.
- Reuse the same `WorkflowConfig.rounds must be at least 1` validation in continuous mode.
- Preserve normal continuous resume behavior.

### Changes Made

- Added `test_continuous_runner_rejects_invalid_workflow_rounds`.
- Added a `config.rounds` validation check to `run_continuous_workflow`.

### Verification After Changes

- Red target test first failed because continuous mode accepted `rounds=0`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_rejects_invalid_workflow_rounds tests.test_workflow.ResearchWorkflowTest.test_continuous_runner_resumes_and_keeps_appending_rounds`
- `python3 -m unittest discover -s tests` passed with 107 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter116 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 117 - 2026-05-04 21:38 PDT

### Current Problems

- Web result snippets were paired by raw result-anchor index.
- If a skipped `result__a` anchor had no `href` and no snippet, the next valid result lost its actual snippet.

### Planned Changes

- Add a regression test with a skipped anchor before a valid result.
- Advance the snippet cursor only when a web result is accepted.
- Preserve behavior for normal results and missing-`href` fallback handling.

### Changes Made

- Added `test_web_search_agent_keeps_snippet_after_skipped_anchor_without_snippet`.
- `_extract_duckduckgo_results` now advances snippet assignment only for accepted source-bearing results.

### Verification After Changes

- Red target test first failed because the real result fell back to the generic external-result summary.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_snippet_after_skipped_anchor_without_snippet tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_result_anchors_without_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- `python3 -m unittest discover -s tests` passed with 108 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter117 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 118 - 2026-05-04 21:42 PDT

### Current Problems

- The Iteration 117 snippet cursor fix handled skipped anchors without snippets.
- It still reused a skipped anchor's own snippet for the next accepted result when the skipped anchor did have a snippet.

### Planned Changes

- Add a regression test for a skipped no-`href` result that has its own snippet.
- Parse result anchors and snippets as ordered events.
- Attach snippets only to the most recent accepted source-bearing result.

### Changes Made

- Added `test_web_search_agent_does_not_reuse_snippet_from_skipped_anchor`.
- Reworked `_extract_duckduckgo_results` to pair snippets in HTML order instead of by raw list index.

### Verification After Changes

- Red target test first failed because the real result summary contained the skipped anchor's snippet.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_does_not_reuse_snippet_from_skipped_anchor tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_snippet_after_skipped_anchor_without_snippet tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_div_snippets`
- `python3 -m unittest discover -s tests` passed with 109 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter118 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 119 - 2026-05-04 21:44 PDT

### Current Problems

- The ordered snippet parser still used a broad element regex.
- When a search result was wrapped in an outer container, the regex could consume that container and miss an inner `result__snippet` element.

### Planned Changes

- Add a regression test for snippets nested inside a result container.
- Use a dedicated snippet-element pattern that only matches elements whose opening tag mentions `result__snippet`.
- Keep exact class-token filtering after the regex match.

### Changes Made

- Added `test_web_search_agent_extracts_nested_result_snippets`.
- Replaced the broad snippet element scan with a dedicated `snippet_pattern`.

### Verification After Changes

- Red target test first failed because the nested result fell back to the generic summary.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_nested_result_snippets tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_does_not_reuse_snippet_from_skipped_anchor tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_div_snippets tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_requires_result_class_tokens`
- `python3 -m unittest discover -s tests` passed with 110 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter119 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 120 - 2026-05-04 21:49 PDT

### Current Problems

- Chinese Markdown section headings such as `## 摘要` and `## 方法` were not normalized.
- Reports generated from Chinese Markdown papers could lose method and experiment sections and fall back to generic summaries.

### Planned Changes

- Add a regression test for Chinese Markdown section headings.
- Strip Markdown heading markers before Chinese heading normalization.
- Preserve existing Chinese plain-heading and Markdown title behavior.

### Changes Made

- Added `MARKDOWN_CHINESE_SECTION_PAPER_TEXT`.
- Added `test_chinese_markdown_section_headings_are_parsed`.
- Updated `normalize_chinese_heading` to remove leading Markdown heading markers.

### Verification After Changes

- Red target test first failed because the method section fell back to a generic technical-process summary.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_markdown_section_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed tests.test_workflow.ResearchWorkflowTest.test_markdown_chinese_title_label_is_cleaned`
- `python3 -m unittest discover -s tests` passed with 111 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter120 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 121 - 2026-05-04 21:52 PDT

### Current Problems

- Chinese papers using `评估` or `评价` headings were not mapped to experiment evidence.
- Even when Chinese evidence mentioned `基线方法` and `可复现性`, the summary could fall back to a generic experiment statement.

### Planned Changes

- Add a regression test for a Chinese `评估` heading.
- Map `评估` and `评价` to the experiments section.
- Preserve Chinese baseline/reproducibility evidence in the generated evidence ledger.

### Changes Made

- Added `CHINESE_EVALUATION_HEADING_PAPER_TEXT`.
- Added `test_chinese_evaluation_heading_is_parsed_as_experiments`.
- Updated Chinese heading normalization and `zh_evidence_summary`.

### Verification After Changes

- Red target test first failed because the evidence ledger did not include `评估显示`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_evaluation_heading_is_parsed_as_experiments tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker`
- `python3 -m unittest discover -s tests` passed with 112 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter121 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 122 - 2026-05-04 21:55 PDT

### Current Problems

- Chinese papers using `不足` or `局限性` headings were not mapped to limitations.
- The generated limitations section could fall back to a generic warning even when the paper stated concrete risks.

### Planned Changes

- Add a regression test for the `不足` heading.
- Map common Chinese limitations aliases to the `limitations` section.
- Preserve existing localized limitations behavior.

### Changes Made

- Added `test_chinese_shortcoming_heading_is_parsed_as_limitations`.
- Added `局限性`, `不足`, and `不足与展望` to Chinese heading normalization.

### Verification After Changes

- Red target test first failed because the limitations section used the generic fallback.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_shortcoming_heading_is_parsed_as_limitations tests.test_workflow.ResearchWorkflowTest.test_chinese_limitation_section_localizes_framework_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed`
- `python3 -m unittest discover -s tests` passed with 113 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter122 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 123 - 2026-05-04 21:58 PDT

### Current Problems

- `first_sentences` split only on English punctuation.
- Chinese summaries using `。`, `！`, or `？` could keep too much text instead of selecting the requested number of sentences.

### Planned Changes

- Add a regression test for Chinese sentence punctuation.
- Extend sentence splitting to Chinese sentence-ending punctuation.
- Preserve existing English report and benchmark behavior.

### Changes Made

- Added `test_first_sentences_splits_chinese_punctuation`.
- Updated `first_sentences` to split on `.`, `!`, `?`, `。`, `！`, and `？`.

### Verification After Changes

- Red target test first failed because all three Chinese sentences stayed together.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_first_sentences_splits_chinese_punctuation tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_extracts_method_audit_strength tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 114 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter123 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 124 - 2026-05-04 22:50 PDT

### Current Problems

- The Chinese punctuation split from Iteration 123 introduced an English abbreviation regression.
- `first_sentences("... e.g. retrieval ...", count=1)` stopped at `e.` or `e.g.` instead of the real sentence boundary.

### Planned Changes

- Add a regression test for English abbreviations without internal spaces.
- Keep Chinese punctuation splitting.
- Protect common abbreviations before sentence splitting.

### Changes Made

- Added `test_first_sentences_preserves_english_abbreviations_without_space`.
- Updated `first_sentences` to protect `e.g.` and `i.e.` before splitting, then restore them.

### Verification After Changes

- Red target test first failed because the summary stopped at `The system uses e.`.
- An intermediate regex-only fix still stopped at `The system uses e.g.`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_first_sentences_preserves_english_abbreviations_without_space tests.test_workflow.ResearchWorkflowTest.test_first_sentences_splits_chinese_punctuation tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 115 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter124 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 125 - 2026-05-04 22:54 PDT

### Current Problems

- Iteration 124 protected lowercase `e.g.` and `i.e.` but not sentence-initial capitalized forms.
- `E.g. retrieval filtering...` was truncated to `E.g.`.

### Planned Changes

- Add a regression test for capitalized English abbreviations.
- Protect `E.g.` and `I.e.` alongside lowercase forms.
- Preserve Chinese punctuation splitting.

### Changes Made

- Added `test_first_sentences_preserves_capitalized_english_abbreviations`.
- Extended abbreviation protection in `first_sentences`.

### Verification After Changes

- Red target test first failed because the summary stopped at `E.g.`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_first_sentences_preserves_capitalized_english_abbreviations tests.test_workflow.ResearchWorkflowTest.test_first_sentences_preserves_english_abbreviations_without_space tests.test_workflow.ResearchWorkflowTest.test_first_sentences_splits_chinese_punctuation`
- `python3 -m unittest discover -s tests` passed with 116 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter125 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 126 - 2026-05-04 22:57 PDT

### Current Problems

- `first_sentences` still split on common paper abbreviations like `Fig. 1`.
- Summaries could truncate to `Fig.` instead of keeping the actual evidence sentence.

### Planned Changes

- Add a regression test for figure abbreviations.
- Protect common figure/table abbreviations before sentence splitting.
- Preserve the abbreviation and Chinese punctuation behavior from prior iterations.

### Changes Made

- Added `test_first_sentences_preserves_figure_abbreviations`.
- Added `Fig.`, `fig.`, `Tab.`, and `tab.` to abbreviation protection.

### Verification After Changes

- Red target test first failed because the summary stopped at `Fig.`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_first_sentences_preserves_figure_abbreviations tests.test_workflow.ResearchWorkflowTest.test_first_sentences_preserves_capitalized_english_abbreviations tests.test_workflow.ResearchWorkflowTest.test_first_sentences_splits_chinese_punctuation`
- `python3 -m unittest discover -s tests` passed with 117 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter126 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 127 - 2026-05-04 23:00 PDT

### Current Problems

- Multi-round DOCX exports placed every round back-to-back without page breaks.
- Long continuous-run reports were harder to skim because each round did not start on a clean page.

### Planned Changes

- Add a DOCX export regression test for page breaks between rounds.
- Add a page-break paragraph primitive to the lightweight DOCX writer.
- Insert a page break before round 2 and later rounds.

### Changes Made

- Added `test_export_inserts_page_break_between_rounds`.
- Added `page_break()` and `PageBreak` XML rendering in `docx.py`.
- Updated `write_docx` to insert page breaks between rounds.

### Verification After Changes

- Red target test first failed because the document XML had no `<w:br w:type="page"/>`.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_export_inserts_page_break_between_rounds tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections`
- `python3 -m unittest discover -s tests` passed with 118 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter127 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 128 - 2026-05-04 23:03 PDT

### Current Problems

- Rubric `source_notes` counted benchmark reports but did not distinguish built-in fallback entries from real external sources.
- This was less traceable than the benchmark quality section added earlier.

### Planned Changes

- Add regression assertions for external source counts in Chinese rubric source notes.
- Compute external benchmark count inside `RubricBuilderAgent`.
- Add the same count to English rubric source notes.

### Changes Made

- Updated `test_chinese_rubric_source_notes_use_readable_punctuation`.
- Added external source count to Chinese and English rubric `source_notes`.

### Verification After Changes

- Red target test first failed because Chinese rubric notes had no `外部来源数量`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_rubric_source_notes_use_readable_punctuation tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round tests.test_workflow.ResearchWorkflowTest.test_english_report_records_external_benchmark_source_count`
- `python3 -m unittest discover -s tests` passed with 118 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter128 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 129 - 2026-05-04 23:08 PDT

### Current Problems

- The English deterministic scorecard gave the sample report 91/100.
- This over-rewarded keyword coverage and was inconsistent with the stricter Chinese scoring behavior.

### Planned Changes

- Add an English regression test that caps the sample score at a non-inflated level.
- Reduce English keyword-hit reward while preserving evidence citations.
- Verify the sample score and quality band after the change.

### Changes Made

- Added `test_english_scorecard_avoids_inflated_sample_score`.
- Changed English scoring from `8 + hits * 3` to `8 + min(hits, 5) * 2`.

### Verification After Changes

- Ran a two-round Chinese sample:
  - `python3 -m paper_research examples/sample_paper.txt --rounds 2 --language zh --output-dir /tmp/paper_research_iter129_zh`
- Confirmed rubric source notes included `外部来源数量：0` and DOCX had one page break between two rounds.
- Red target test first failed because the English sample score was 91/100.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_avoids_inflated_sample_score tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_cites_report_evidence tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- Manual score check now reports 78/100 with quality band `good`.
- `python3 -m unittest discover -s tests` passed with 119 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter129 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 130 - 2026-05-04 23:12 PDT

### Current Problems

- English scorecard summaries used a lower risk threshold than the second-round low-score refinement logic.
- A 14/20 `Research Usefulness` score appeared in the next round's low-score list but not in the first round's `Main risks`.

### Planned Changes

- Add a regression test that compares first-round summary risks with second-round low-score refinement.
- Use the same 14-point threshold for English risk summaries.
- Preserve the Chinese 12-point threshold.

### Changes Made

- Added `test_english_scorecard_summary_matches_low_score_threshold`.
- Updated `_score_risk_summary` to use language-specific thresholds.

### Verification After Changes

- Red target test first failed because the first-round summary omitted `Research Usefulness`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_summary_matches_low_score_threshold tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_avoids_inflated_sample_score tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- `python3 -m unittest discover -s tests` passed with 120 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter130 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 131 - 2026-05-04 23:15 PDT

### Current Problems

- Chinese papers using `技术路线`, `系统设计`, or `方案` headings were not parsed as method sections.
- Generated method analysis could fall back to `需要进一步拆解的技术流程` despite concrete method text being present.

### Planned Changes

- Add a regression test for the `技术路线` heading.
- Map common Chinese method aliases to the `method` section.
- Preserve existing Chinese evaluation and plain method heading behavior.

### Changes Made

- Added `CHINESE_TECHNICAL_ROUTE_PAPER_TEXT`.
- Added `test_chinese_technical_route_heading_is_parsed_as_method`.
- Added `技术路线`, `系统设计`, and `方案` to Chinese heading normalization.

### Verification After Changes

- Red target test first failed because the method section used the generic technical-process fallback.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_technical_route_heading_is_parsed_as_method tests.test_workflow.ResearchWorkflowTest.test_chinese_evaluation_heading_is_parsed_as_experiments tests.test_workflow.ResearchWorkflowTest.test_chinese_paper_headings_and_title_are_parsed`
- `python3 -m unittest discover -s tests` passed with 121 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter131 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 132 - 2026-05-04 23:19 PDT

### Current Problems

- English section headings with Roman numeral prefixes such as `II. Method` were not normalized.
- Method and evaluation sections could be missed in papers using traditional numbered headings.

### Planned Changes

- Add a regression test for Roman-numbered English headings.
- Strip leading Roman numerals before English heading lookup.
- Preserve existing approach/evaluation and Markdown title parsing.

### Changes Made

- Added `ROMAN_NUMBERED_ENGLISH_PAPER_TEXT`.
- Added `test_parses_roman_numbered_english_headings`.
- Updated `normalize_english_heading` to remove leading Roman numeral prefixes.

### Verification After Changes

- Red target test first failed because method and evaluation fell back to explicit-missing defaults.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parses_roman_numbered_english_headings tests.test_workflow.ResearchWorkflowTest.test_parses_approach_and_evaluation_headings tests.test_workflow.ResearchWorkflowTest.test_markdown_title_heading_is_cleaned`
- `python3 -m unittest discover -s tests` passed with 122 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter132 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 133 - 2026-05-04 23:22 PDT

### Current Problems

- English `Ablation Study` headings were not mapped to evaluation evidence.
- Ablation content could be appended to the method section while the evidence section still claimed experiments/results were missing.

### Planned Changes

- Add a regression test for ablation headings.
- Map `ablation` and `ablation study` to experiments.
- Preserve existing approach/evaluation and Roman-numbered heading parsing.

### Changes Made

- Added `ABLATION_HEADING_PAPER_TEXT`.
- Added `test_parses_ablation_heading_as_evaluation_evidence`.
- Updated English heading normalization for ablation sections.

### Verification After Changes

- Red target test first failed because evidence reading used the explicit missing-results fallback.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parses_ablation_heading_as_evaluation_evidence tests.test_workflow.ResearchWorkflowTest.test_parses_approach_and_evaluation_headings tests.test_workflow.ResearchWorkflowTest.test_parses_roman_numbered_english_headings`
- `python3 -m unittest discover -s tests` passed with 123 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter133 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 134 - 2026-05-04 23:26 PDT

### Current Problems

- Chinese `消融实验` headings were not mapped to the experiments section.
- Ablation evidence could be missed and replaced with the generic experiment fallback.

### Planned Changes

- Add a regression test for Chinese ablation headings.
- Map `消融实验` and `消融` to experiments.
- Preserve ablation-specific language in Chinese evidence summaries.

### Changes Made

- Added `CHINESE_ABLATION_HEADING_PAPER_TEXT`.
- Added `test_chinese_ablation_heading_is_parsed_as_experiments`.
- Updated Chinese heading normalization and `zh_evidence_summary`.

### Verification After Changes

- Red target test first failed because the ledger used the generic experiment statement.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_ablation_heading_is_parsed_as_experiments tests.test_workflow.ResearchWorkflowTest.test_chinese_evaluation_heading_is_parsed_as_experiments tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_ablation_marker`
- `python3 -m unittest discover -s tests` passed with 124 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter134 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 135 - 2026-05-04 23:30 PDT

### Current Problems

- Score rationales reported only how many markers were found.
- Reviewers could not see which rubric markers caused a score without inspecting the code.

### Planned Changes

- Add a regression test for listed matched markers in English score rationale.
- Include matched keyword names in English rationale.
- Include matched keyword names in Chinese rationale as well.

### Changes Made

- Added `test_english_scorecard_lists_matched_markers`.
- `ReportScoringAgent` now stores `matched_keywords` and includes them in rationale text.

### Verification After Changes

- Red target test first failed because rationale had no `Matched markers:` text.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_lists_matched_markers tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_cites_report_evidence tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker`
- `python3 -m unittest discover -s tests` passed with 125 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter135 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 136 - 2026-05-04 23:35 PDT

### Current Problems

- English scoring marker matching used raw substring checks.
- `metadata` incorrectly matched the `data` rubric marker and inflated reproducibility/evidence scoring.

### Planned Changes

- Add a regression test for `data` inside `metadata`.
- Use word-boundary matching for normal English markers.
- Preserve intentional stem matching for markers like `reproduc`, `result`, and `experiment`.

### Changes Made

- Added `test_english_scoring_does_not_match_data_inside_metadata`.
- Added `_contains_marker` and routed scoring/evidence lookup through it.
- Imported `re` in `workflow.py`.

### Verification After Changes

- Red target test first failed because rationale reported `Matched markers: data`.
- Initial implementation raised `NameError` until `re` was imported.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scoring_does_not_match_data_inside_metadata tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_lists_matched_markers tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_avoids_inflated_sample_score tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker`
- Manual English sample score check now reports 72/100 with explicit matched marker lists.
- First full-suite run exposed an evidence-snippet regression where English scoring selected `Executive Thesis` instead of `Claim-Evidence Ledger`; added English preferred-section mappings and retested the affected cases.
- `python3 -m unittest discover -s tests` passed with 126 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter136 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 137 - 2026-05-04 23:43 PDT

### Current Problems

- `workflow.py` was 915 lines and had accumulated report writing, rubric building, scoring, critique, persistence, and resume logic in one module.
- `ReportScoringAgent` lived in `workflow.py`, even though scoring helpers already had a dedicated `scoring.py` module.

### Planned Changes

- Tighten the workflow maintainability threshold so the structure problem is caught by tests.
- Move `ReportScoringAgent` and its scoring-only helper functions into `paper_research.scoring`.
- Keep `paper_research.workflow.ReportScoringAgent` import-compatible through a module import.

### Changes Made

- Lowered the workflow structure threshold from 950 to 900 lines.
- Added `test_report_scoring_agent_has_dedicated_module`.
- Moved `ReportScoringAgent`, marker-aware evidence lookup, quality banding, and risk-summary helpers to `scoring.py`.
- Updated `workflow.py` to import `ReportScoringAgent` from `scoring.py`; `workflow.py` is now 746 lines.

### Verification After Changes

- Red target tests first failed because `workflow.py` had 915 lines and `paper_research.scoring` did not expose `ReportScoringAgent`.
- Target structure tests passed:
  - `python3 -m unittest tests.test_structure.CodeStructureTest.test_workflow_module_stays_below_maintainability_threshold tests.test_structure.CodeStructureTest.test_report_scoring_agent_has_dedicated_module`
- Target scoring regressions passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scoring_does_not_match_data_inside_metadata tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_lists_matched_markers tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 127 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter137 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 138 - 2026-05-04 23:45 PDT

### Current Problems

- After `ReportScoringAgent` moved into its own module, `score()` became a clearer standalone API surface.
- Direct calls with an unsupported language silently used English scoring rules instead of failing fast.

### Planned Changes

- Add a focused scoring-module regression test.
- Reject languages outside `en` and `zh` inside `ReportScoringAgent.score()`.
- Preserve existing English and Chinese scoring behavior.

### Changes Made

- Added `tests/test_scoring.py`.
- Added `test_score_rejects_unknown_language`.
- Added scoring-module language validation with the same `en`/`zh` contract as the workflow.

### Verification After Changes

- Red target test first failed because `ValueError` was not raised.
- Target tests passed:
  - `python3 -m unittest tests.test_scoring.ReportScoringAgentTest.test_score_rejects_unknown_language`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_scoring_does_not_match_data_inside_metadata tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_baseline_marker`
- `python3 -m unittest discover -s tests` passed with 128 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter138 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 139 - 2026-05-04 23:48 PDT

### Current Problems

- A fresh Chinese sample run showed the report had a research problem, but the executive summary did not explicitly state problem scope or importance.
- The missing terms caused `问题定义` to remain a low score even when the report content was otherwise clear.

### Planned Changes

- Add a regression test that Chinese executive summaries state problem scope and importance.
- Improve the Chinese executive summary template without changing scoring rules.
- Update score-dependent assertions to reflect the improved quality baseline.

### Changes Made

- Added `test_chinese_executive_summary_states_problem_scope_and_importance`.
- Updated the Chinese `执行摘要` to include `问题范围` and `重要性`.
- Updated Chinese DOCX and second-round low-score assertions from the old `问题定义：12/20` baseline to the new `问题定义：16/20` behavior.

### Verification After Changes

- Red target test first failed because `问题范围` was missing from the Chinese executive summary.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_executive_summary_states_problem_scope_and_importance tests.test_workflow.ResearchWorkflowTest.test_chinese_executive_summary_localizes_benchmark_term tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections`
- Manual Chinese sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 2 --output-dir /tmp/paper_research_iter139_zh_after`
- Manual sample quality check: round 2 total improved from 72/100 to 76/100; `问题定义` improved from 12/20 to 16/20 with matched markers `问题、范围、假设、重要、研究`.
- `python3 -m unittest discover -s tests` passed with 129 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter139 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 140 - 2026-05-04 23:51 PDT

### Current Problems

- The Chinese `限制与风险` section listed limitations but did not explicitly name failure modes or fragile points.
- The sample report therefore still under-expressed the `限制与失败模式` rubric criterion.

### Planned Changes

- Add assertions that the Chinese limitation section includes `失败模式` and `脆弱点`.
- Improve the limitation section language without changing the scoring rules.
- Update second-round refinement expectations now that the first-round low-score set is genuinely empty.

### Changes Made

- Extended `test_chinese_limitation_section_localizes_framework_terms`.
- Updated the Chinese `限制与风险` template to include explicit failure modes and fragile points.
- Renamed the second-round refinement test to `test_second_round_report_summarizes_prior_score_status` and updated its expectation to `没有明显低分项`.

### Verification After Changes

- Red target test first failed because `失败模式` was absent from the limitation section.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_limitation_section_localizes_framework_terms tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_second_round_report_summarizes_prior_score_status tests.test_workflow.ResearchWorkflowTest.test_chinese_scorecard_cites_evidence_and_avoids_inflated_sample_score`
- Manual Chinese sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 2 --output-dir /tmp/paper_research_iter140_zh_after`
- Manual sample quality check: round 2 total improved to 78/100; `限制与失败模式` improved to 16/20 with matched markers `限制、风险、脆弱、失败、复现`.
- `python3 -m unittest discover -s tests` passed with 129 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter140 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 141 - 2026-05-04 23:54 PDT

### Current Problems

- A fresh English sample run showed `Problem Framing` stayed at 12/20.
- The `Executive Thesis` described the paper generally but did not explicitly state the research question, scope, or why the problem matters.

### Planned Changes

- Add a regression test for English executive-thesis problem framing.
- Improve the English opening section with explicit question, scope, and importance language.
- Preserve claim/evidence ledger behavior and prior anti-inflation scoring regression tests.

### Changes Made

- Added `test_english_executive_thesis_states_question_scope_and_importance`.
- Updated `Executive Thesis` to include `Research question:`, `Scope:`, and `Why it matters:`.

### Verification After Changes

- Red target test first failed because `Research question:` was absent from the English executive thesis.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_executive_thesis_states_question_scope_and_importance tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_avoids_inflated_sample_score`
- Manual English sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 2 --output-dir /tmp/paper_research_iter141_en_after`
- Manual sample quality check: round 2 `Problem Framing` improved from 12/20 to 18/20. The total rose to 90/100, which suggests the next scoring-calibration iteration should cap high scores when only built-in benchmark patterns are available.
- `python3 -m unittest discover -s tests` passed with 130 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter141 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 142 - 2026-05-04 23:58 PDT

### Current Problems

- After English problem framing improved, the two-round English sample reached 90/100 even though benchmark search used only built-in fallback patterns.
- Keyword-complete reports could therefore receive a high score without external benchmark evidence.

### Planned Changes

- Add scoring-level coverage for a source-confidence cap when `External source count: 0`.
- Add workflow-level coverage that a built-in-only English second round does not reach the high band.
- Apply the cap per criterion and explain it in score rationales.

### Changes Made

- Added `test_builtin_only_rubric_caps_high_english_scores`.
- Added `test_english_builtin_only_second_round_does_not_reach_high_band`.
- Added source-note detection for `External source count: 0` / `外部来源数量：0`.
- Applied an 80% per-criterion source-confidence cap when no external benchmark sources are present.
- Added cap notes to affected score rationales.

### Verification After Changes

- Red scoring test first failed because the full-marker score remained 18/20.
- Red workflow test first failed because the built-in-only second round scored 85/100 and still reached `high`.
- Target tests passed:
  - `python3 -m unittest tests.test_scoring.ReportScoringAgentTest.test_builtin_only_rubric_caps_high_english_scores tests.test_workflow.ResearchWorkflowTest.test_english_builtin_only_second_round_does_not_reach_high_band tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_avoids_inflated_sample_score`
- Manual English sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 2 --output-dir /tmp/paper_research_iter142_en_after2`
- Manual sample quality check: built-in-only round 2 now scores 80/100 with `Quality band: good`; each fully matched criterion is capped at 16/20 with a source-confidence rationale note.
- `python3 -m unittest discover -s tests` passed with 132 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter142 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 143 - 2026-05-05 00:02 PDT

### Current Problems

- Source-confidence caps were visible in individual score rationales, but the scorecard summary could still report no obvious risks.
- Chinese built-in-only runs often landed exactly at the cap, so no per-score cap note appeared even though external benchmark evidence was still absent.

### Planned Changes

- Require source-confidence risk to appear in the overall summary for built-in-only scoring.
- Treat external source count 0 as a summary-level risk, independent of whether a particular score was reduced.
- Preserve the per-criterion cap rationale when points are actually capped.

### Changes Made

- Extended `test_builtin_only_rubric_caps_high_english_scores` to check the scorecard summary.
- Added `test_builtin_only_rubric_notes_chinese_source_confidence_risk`.
- Changed scoring summary risk calculation to use source-confidence limitation whenever external source count is 0.

### Verification After Changes

- Red English scoring test first failed because the summary did not mention `source confidence`.
- Red Chinese scoring test first failed because the summary did not mention `来源置信度`.
- Target tests passed:
  - `python3 -m unittest tests.test_scoring.ReportScoringAgentTest.test_builtin_only_rubric_caps_high_english_scores tests.test_scoring.ReportScoringAgentTest.test_builtin_only_rubric_notes_chinese_source_confidence_risk tests.test_workflow.ResearchWorkflowTest.test_english_builtin_only_second_round_does_not_reach_high_band`
- Manual Chinese sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 2 --output-dir /tmp/paper_research_iter143_zh_after2`
- Manual sample quality check: Chinese round 2 summary now reports `主要风险：来源置信度受限：外部对照报告数量为 0`.
- `python3 -m unittest discover -s tests` passed with 133 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter143 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 144 - 2026-05-05 00:04 PDT

### Current Problems

- The standalone scoring API always wrote summaries as `x/100`.
- Custom rubrics with a non-100 max score, such as a one-criterion 20-point rubric, produced misleading summaries like `16/100` and an incorrect low quality band.

### Planned Changes

- Add a regression check for the scoring summary denominator.
- Use the sum of rubric criterion max points as the summary denominator.
- Normalize the total to a percentage only for quality-band calculation.

### Changes Made

- Extended `test_builtin_only_rubric_caps_high_english_scores` to require `16/20` and `Quality band: good`.
- Added `_normalized_total`.
- Updated English and Chinese scorecard summaries to use dynamic denominators while preserving standard `x/100` output for normal five-criterion rubrics.

### Verification After Changes

- Red target test first failed because the summary still said `16/100`.
- Target tests passed:
  - `python3 -m unittest tests.test_scoring.ReportScoringAgentTest.test_builtin_only_rubric_caps_high_english_scores tests.test_scoring.ReportScoringAgentTest.test_builtin_only_rubric_notes_chinese_source_confidence_risk tests.test_workflow.ResearchWorkflowTest.test_english_builtin_only_second_round_does_not_reach_high_band`
- Manual English sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 2 --output-dir /tmp/paper_research_iter144_en_after`
- Manual sample quality check: standard workflow still reports `80/100` and `Quality band: good`.
- `python3 -m unittest discover -s tests` passed with 133 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter144 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 145 - 2026-05-05 00:08 PDT

### Current Problems

- The English executive thesis generated an awkward phrase: `how should we evaluate we study ...`.
- After stripping the leading phrase, the claim-evidence ledger still produced `iteration. can be improved`.

### Planned Changes

- Add regression assertions against the awkward English phrasing.
- Clean common English abstract preambles before using them as problem statements.
- Remove trailing sentence punctuation from generated problem statements so they compose cleanly inside claim sentences.

### Changes Made

- Extended the English executive-thesis test to reject `evaluate we study` and `argues that we study`.
- Extended the claim-evidence ledger test to reject `. can be improved`.
- Updated `problem_statement` to strip common English preambles such as `we study`, `we present`, and `this paper proposes`.
- Trimmed trailing punctuation from generated problem statements.

### Verification After Changes

- Red executive-thesis test first failed because `evaluate we study` was present.
- Red ledger test first failed because `. can be improved` was present.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_executive_thesis_states_question_scope_and_importance tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_english_builtin_only_second_round_does_not_reach_high_band`
- Manual English sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 2 --output-dir /tmp/paper_research_iter145_en_after2`
- Manual sample quality check: the claim now reads `the paper argues that an agent workflow ... can be improved` without the stray period.
- `python3 -m unittest discover -s tests` passed with 133 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter145 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 146 - 2026-05-05 00:11 PDT

### Current Problems

- The English claim-evidence ledger used the phrase `method evidence shows The system ...`.
- The capitalized sentence splice made the interpretation read like a template join rather than a polished report sentence.

### Planned Changes

- Add regression assertions against `shows The`.
- Rewrite the interpretation sentence as a natural clause.
- Lowercase only the first character of the inserted method summary when embedding it inside that clause.

### Changes Made

- Extended `test_english_report_uses_claim_evidence_ledger_sections`.
- Updated the English ledger interpretation to `the method section shows that ...`.
- Added `_lower_initial` for clause embedding.

### Verification After Changes

- Red target test first failed because `shows The` was present.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_english_builtin_only_second_round_does_not_reach_high_band`
- Manual English sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 2 --output-dir /tmp/paper_research_iter146_en_after`
- Manual sample quality check: the ledger now reads `Interpretation: the method section shows that the system separates ...`.
- `python3 -m unittest discover -s tests` passed with 133 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter146 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 147 - 2026-05-05 00:14 PDT

### Current Problems

- Local benchmark search ignored very short placeholders like `TBD`, but a longer `TODO: fill later ...` file could still be selected as a usable local benchmark.
- Placeholder local files can pollute benchmark-informed report generation and hide the fact that no real external comparison was found.

### Planned Changes

- Extend placeholder-file regression coverage.
- Add a local benchmark placeholder detector for TODO/TBD/fill-later content.
- Preserve valid local benchmark selection and structured fallback behavior.

### Changes Made

- Extended `test_local_benchmark_search_ignores_placeholder_files` with a longer TODO file.
- Added `_is_placeholder_benchmark`.
- Skipped local benchmark files whose normalized content is `todo`, `tbd`, `placeholder`, `draft`, starts with `todo:` / `tbd:`, or contains `fill later`.

### Verification After Changes

- Red target test first failed because `todo.md` was selected as a local benchmark.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_ignores_placeholder_files tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_fallback_prefers_structured_reports_without_keyword_matches`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter147_en_after`
- `python3 -m unittest discover -s tests` passed with 133 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter147 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 148 - 2026-05-05 00:17 PDT

### Current Problems

- Web benchmark parsing accepted any non-empty result href.
- `javascript:` and `mailto:` anchors could be treated as usable web benchmark sources.

### Planned Changes

- Add regression coverage for unsafe result links.
- Reject obvious non-content schemes while preserving existing relative URL behavior.
- Recheck normal web extraction and non-URL query fallback behavior.

### Changes Made

- Added `test_web_search_agent_ignores_unsafe_result_links`.
- Added `_is_unsafe_result_href`.
- Updated `_clean_result_url` to return an empty URL for `javascript`, `mailto`, `data`, and `vbscript` schemes.

### Verification After Changes

- Red target test first failed because a `javascript:void(0)` result was treated as `source_type='web'`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_result_links tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter148_en_after`
- `python3 -m unittest discover -s tests` passed with 134 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter148 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 149 - 2026-05-05 00:19 PDT

### Current Problems

- README did not document the new source-confidence scoring behavior.
- README did not document unsafe web result link filtering.

### Planned Changes

- Add documentation regression coverage for source-confidence scoring and unsafe link filtering.
- Update README in the benchmark traceability and web-search sections.
- Preserve existing usage and library examples.

### Changes Made

- Extended `test_readme_documents_benchmark_traceability_and_library_import`.
- Documented that `External source count: 0` triggers source-confidence caps and summary risk notes.
- Documented that unsafe web result links are ignored for `javascript:`, `mailto:`, `data:`, and `vbscript:` schemes.

### Verification After Changes

- Red documentation test first failed because README did not mention unsafe web result links or source confidence.
- The first README update split `External source count: 0` across lines; the documentation test caught that searchability issue.
- Target documentation test passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter149_en_after`
- `python3 -m unittest discover -s tests` passed with 134 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter149 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 150 - 2026-05-05 00:24 PDT

### Current Problems

- `ReportScoringAgent` had a dedicated module but was not exported from the top-level `paper_research` package.
- README library-use examples did not show the scoring agent as an independently reusable API.

### Planned Changes

- Add public API coverage for top-level `ReportScoringAgent` import.
- Export the scoring agent from `paper_research.__init__`.
- Update README library-use examples to show top-level scoring usage.

### Changes Made

- Updated `test_public_api_and_models_remain_importable`.
- Added `ReportScoringAgent` to `paper_research.__all__`.
- Updated README to import `BenchmarkSearchAgent` and `ReportScoringAgent` together and show a direct `.score(...)` call.

### Verification After Changes

- Red structure test first failed because `ReportScoringAgent` could not be imported from `paper_research`.
- Red documentation test first failed because README did not show the top-level scoring import.
- Target tests passed:
  - `python3 -m unittest tests.test_structure.CodeStructureTest.test_public_api_and_models_remain_importable tests.test_structure.CodeStructureTest.test_report_scoring_agent_has_dedicated_module`
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter150_zh_after`
- `python3 -m unittest discover -s tests` passed with 134 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter150 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 151 - 2026-05-05 00:36 PDT

### Current Problems

- Direct unsafe web result links were ignored, but unsafe targets inside redirect query parameters were still preserved as relative `/url?q=...` results.
- A `javascript:` redirect target could therefore still enter benchmark search results.

### Planned Changes

- Add regression coverage for unsafe redirect targets.
- Reject redirect candidates with unsafe schemes.
- Preserve existing safe redirect cleanup and non-URL query fallback behavior.

### Changes Made

- Added `test_web_search_agent_ignores_unsafe_redirect_targets`.
- Updated `_clean_result_url` to inspect decoded redirect candidates with `_is_unsafe_result_href`.

### Verification After Changes

- Red target test first failed because the unsafe redirect was treated as a web benchmark.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_redirect_targets tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_result_links tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter151_en_after`
- `python3 -m unittest discover -s tests` passed with 135 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter151 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 152 - 2026-05-05 00:39 PDT

### Current Problems

- Local benchmark keyword matching used raw substring checks.
- An English paper keyword like `data` could match `metadata`, causing an irrelevant local benchmark to outrank a direct `data` benchmark by filename order.

### Planned Changes

- Add a regression test for `data` versus `metadata` local benchmark ranking.
- Use word-boundary matching for simple English benchmark keywords.
- Preserve Chinese and mixed-token substring matching behavior.

### Changes Made

- Added `test_local_benchmark_search_avoids_substring_keyword_matches`.
- Added `_contains_keyword` to benchmark search.
- Routed local benchmark matched-term detection through `_contains_keyword`.

### Verification After Changes

- Red target test first failed because `aaa_metadata.md` ranked above `zzz_data.md`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_avoids_substring_keyword_matches tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_matches_baseline_data_ablation_terms tests.test_workflow.ResearchWorkflowTest.test_searches_local_benchmark_reports_when_provided`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter152_en_after`
- `python3 -m unittest discover -s tests` passed with 136 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter152 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 153 - 2026-05-05 00:42 PDT

### Current Problems

- DOCX exports showed a generic `Scoring Rubric` / `评分标准` section heading.
- The actual per-round rubric title, such as `Round 1 Scoring Rubric`, was not rendered in the document body.

### Planned Changes

- Add a DOCX regression test requiring the concrete rubric title to appear.
- Render rubric title before rubric source notes.
- Preserve existing heading levels and Chinese DOCX formatting.

### Changes Made

- Extended `test_export_uses_nested_heading_levels_for_report_sections`.
- Updated `write_docx` to add `round_result.rubric.title` under the scoring rubric heading.

### Verification After Changes

- Red target test first failed because `Custom Round Rubric Title` was missing from `word/document.xml`.
- Target tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter153_zh_after`
- `python3 -m unittest discover -s tests` passed with 136 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter153 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 154 - 2026-05-05 00:46 PDT

### Current Problems

- Local benchmark strength inference did not recognize reproducibility-only reports.
- A report focused on reproducibility setup and replication details fell back to the generic `Provides a reusable external comparison point.` strength.

### Planned Changes

- Add regression coverage for reproducibility benchmark strength extraction.
- Recognize English `reproduc...` / `replication` and Chinese `复现` signals.
- Preserve existing method-audit and Chinese keyword behavior.

### Changes Made

- Added `test_local_benchmark_extracts_reproducibility_strength`.
- Updated `_infer_report_strengths` to emit:
  - `Checks reproducibility and replication details.`
  - `检查可复现性和复现实验细节。`

### Verification After Changes

- Red target test first failed because the reproducibility report only received the generic default strength.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_extracts_reproducibility_strength tests.test_workflow.ResearchWorkflowTest.test_chinese_local_benchmark_extracts_method_audit_strength tests.test_workflow.ResearchWorkflowTest.test_local_benchmark_search_prioritizes_chinese_keyword_matches`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter154_en_after`
- `python3 -m unittest discover -s tests` passed with 137 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter154 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 155 - 2026-05-05 00:49 PDT

### Current Problems

- Benchmark search could now infer reproducibility strengths.
- Report writing still copied only the first three strengths from each benchmark, so reproducibility lessons could be dropped when a benchmark also covered limitations, evidence, and baseline/data/ablation checks.

### Planned Changes

- Add a regression test that places reproducibility as the fourth benchmark strength.
- Allow report writing to carry the fourth strength into benchmark-informed improvement text.
- Preserve existing de-duplication and method-audit lesson behavior.

### Changes Made

- Added `test_chinese_benchmark_improvement_includes_reproducibility_lesson`.
- Increased per-benchmark lesson intake from three strengths to four strengths.

### Verification After Changes

- Red target test first failed because the benchmark improvement section omitted `检查可复现性和复现实验细节`.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_reproducibility_lesson tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_includes_method_audit_lessons tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_improvement_deduplicates_repeated_lessons`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter155_zh_after`
- `python3 -m unittest discover -s tests` passed with 138 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter155 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 156 - 2026-05-05 00:53 PDT

### Current Problems

- The CLI success path printed only JSONL and DOCX paths.
- Users had to open generated files to see the final score summary and source-confidence risks.

### Planned Changes

- Add CLI regression coverage for final score summary output.
- Print the final round scorecard summary after output paths.
- Preserve existing custom filename output behavior.

### Changes Made

- Added `test_cli_prints_final_score_summary`.
- Updated `main(...)` to print `Final score summary: ...` when at least one round exists.

### Verification After Changes

- Red target test first failed because stdout only contained `Wrote ...` lines.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_prints_final_score_summary tests.test_cli_io.InputAndCliTest.test_cli_accepts_custom_output_filenames`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter156_en_after`
- Manual CLI output now includes the final score summary and source-confidence risk text.
- `python3 -m unittest discover -s tests` passed with 139 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter156 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 157 - 2026-05-05 00:55 PDT

### Current Problems

- CLI output now included `Final score summary`, but README did not document that behavior.
- Users reading Usage would not know they can see the latest score and source-confidence risk directly in terminal output.

### Planned Changes

- Add documentation coverage for `Final score summary`.
- Update README Usage near the basic command.
- Preserve CLI behavior and sample execution.

### Changes Made

- Extended `test_readme_documents_benchmark_traceability_and_library_import`.
- Added README text explaining that successful CLI runs print output paths plus a `Final score summary` line.

### Verification After Changes

- Red documentation test first failed because README did not mention `Final score summary`.
- Target tests passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import tests.test_cli_io.InputAndCliTest.test_cli_prints_final_score_summary`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter157_zh_after`
- Manual CLI output includes the Chinese final score summary and source-confidence risk.
- `python3 -m unittest discover -s tests` passed with 139 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter157 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 158 - 2026-05-05 00:58 PDT

### Current Problems

- Chinese CLI runs printed an English `Final score summary:` label before a Chinese scorecard summary.
- This made terminal output less consistent with `--language zh` output elsewhere.

### Planned Changes

- Add CLI regression coverage for the Chinese final score label.
- Localize the final score summary label based on `--language`.
- Preserve the existing English CLI label.

### Changes Made

- Added `test_cli_localizes_chinese_final_score_summary_label`.
- Updated CLI output to use `最终评分摘要：` in Chinese mode and `Final score summary:` in English mode.

### Verification After Changes

- Red target test first failed because Chinese stdout still contained `Final score summary:`.
- Target tests passed:
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_cli_localizes_chinese_final_score_summary_label tests.test_cli_io.InputAndCliTest.test_cli_prints_final_score_summary`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter158_zh_after`
- Manual CLI output now starts the final score line with `最终评分摘要：`.
- `python3 -m unittest discover -s tests` passed with 140 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter158 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 159 - 2026-05-05 01:01 PDT

### Current Problems

- README documented `Final score summary` after the CLI change.
- It did not document the localized Chinese label `最终评分摘要`, even though `--language zh` now uses it.

### Planned Changes

- Add documentation coverage for the Chinese CLI score-summary label.
- Update README's CLI output description.
- Preserve the localized CLI behavior.

### Changes Made

- Extended `test_readme_documents_benchmark_traceability_and_library_import`.
- Added README text saying Chinese runs use `最终评分摘要`.

### Verification After Changes

- Red documentation test first failed because README did not mention `最终评分摘要`.
- Target tests passed:
  - `python3 -m unittest tests.test_docs.DocumentationTest.test_readme_documents_benchmark_traceability_and_library_import tests.test_cli_io.InputAndCliTest.test_cli_localizes_chinese_final_score_summary_label`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter159_zh_after`
- Manual CLI output starts with `最终评分摘要：` for the final score line.
- `python3 -m unittest discover -s tests` passed with 140 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter159 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 160 - 2026-05-05 01:06 PDT

### Current Problems

- `benchmark.py` had grown to 451 lines and mixed benchmark agent logic with web fetching, DuckDuckGo HTML parsing, attribute parsing, and result URL cleaning.
- Future web parsing fixes would continue to bloat the benchmark module.

### Planned Changes

- Add a structure test requiring a dedicated web-search parsing module.
- Move web fetch and DuckDuckGo parsing helpers into `paper_research.web_search`.
- Keep `BenchmarkSearchAgent` behavior and existing web parsing regressions intact.

### Changes Made

- Added `test_web_search_parsing_has_dedicated_module`.
- Added `paper_research/web_search.py`.
- Moved `fetch_url`, `extract_duckduckgo_results`, HTML attr parsing, class-token checks, HTML stripping, redirect URL cleaning, and unsafe href filtering into the new module.
- Updated `benchmark.py` to import those helpers; `benchmark.py` dropped from 451 lines to 363 lines.

### Verification After Changes

- Red structure test first failed because `paper_research.web_search` did not exist.
- Target tests passed:
  - `python3 -m unittest tests.test_structure.CodeStructureTest.test_web_search_parsing_has_dedicated_module tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_redirect_targets tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_handles_unquoted_attributes`
- First full verification pass caught a trailing blank line at EOF in `benchmark.py`; fixed it and reran.
- `python3 -m unittest discover -s tests` passed with 141 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter160 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 161 - 2026-05-05 03:06 PDT

### Current Problems

- Web benchmark parsing rejected clearly unsafe schemes such as `javascript:` and `mailto:`.
- Other absolute non-HTTP schemes such as `ftp://` and `file://` could still be treated as usable web benchmark sources.

### Planned Changes

- Add regression coverage for unsupported absolute result links.
- Allow only `http`, `https`, and relative result links.
- Preserve existing redirect cleanup and relative query behavior.

### Changes Made

- Added `test_web_search_agent_ignores_unsupported_absolute_result_links`.
- Replaced scheme filtering with `_has_unsupported_scheme`, which rejects any non-empty scheme outside `http` and `https`.
- Applied the same check to decoded redirect candidates.

### Verification After Changes

- Red target test first failed because an `ftp://` result was treated as a web benchmark.
- Target tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsupported_absolute_result_links tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_result_links tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter161_en_after`
- `python3 -m unittest discover -s tests` passed with 142 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter161 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 162 - 2026-05-05 03:09 PDT

### Current Problems

- `paper_research.web_search` had no direct module-level tests after extraction.
- Redirect target URLs with leading/trailing whitespace were not cleaned to their HTTP(S) target.

### Planned Changes

- Add a focused `tests/test_web_search.py`.
- Add regression coverage for whitespace around decoded redirect targets.
- Preserve existing BenchmarkSearchAgent web parsing behavior.

### Changes Made

- Added `WebSearchParsingTest`.
- Added `test_redirect_target_whitespace_is_ignored`.
- Stripped decoded redirect candidates before scheme validation and HTTP(S) target detection.

### Verification After Changes

- Red target test first failed because the URL stayed as `/url?q=...` instead of `https://example.com/spaced-report`.
- Target tests passed:
  - `python3 -m unittest tests.test_web_search.WebSearchParsingTest.test_redirect_target_whitespace_is_ignored tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsupported_absolute_result_links`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter162_en_after`
- `python3 -m unittest discover -s tests` passed with 143 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter162 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 163 - 2026-05-05 03:12 PDT

### Current Problems

- Protocol-relative redirect targets such as `//example.com/report` were not normalized into usable benchmark URLs.
- The parser kept the original `/url?q=...` redirect instead of the intended target.

### Planned Changes

- Add module-level web search parsing coverage for protocol-relative redirect targets.
- Normalize protocol-relative targets to HTTPS.
- Preserve non-URL query fallback behavior.

### Changes Made

- Added `test_protocol_relative_redirect_target_becomes_https`.
- Added `test_skipped_anchor_does_not_steal_next_snippet` as module-level coverage for skipped anchors.
- Updated redirect target cleaning to return `https://...` for decoded `//...` candidates.

### Verification After Changes

- Red target test first failed because the URL stayed as `/url?q=...`.
- Target tests passed:
  - `python3 -m unittest tests.test_web_search.WebSearchParsingTest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_cleans_q_redirect_urls tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_keeps_non_url_q_values_as_original_href`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language en --rounds 1 --output-dir /tmp/paper_research_iter163_en_after`
- `python3 -m unittest discover -s tests` passed with 145 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter163 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 164 - 2026-05-05 03:17 PDT

### Current Problems

- Chinese reports still injected the project-specific multi-agent review workflow into unrelated Chinese papers.
- Generic Chinese abstracts fell back to `论文自动分析流程`, losing domain terms such as reliable reasoning, contrastive pretraining, and retrieval filtering.

### Planned Changes

- Add a regression test with a general Chinese AI paper outside the paper-research project domain.
- Preserve domain-specific Chinese problem, method, evidence, and limitation text when no specialized heuristic applies.
- Replace the Chinese claim/evidence template text that implied every paper proves multi-role iterative improvement.

### Changes Made

- Added `GENERAL_CHINESE_PAPER_TEXT` and `test_chinese_report_preserves_domain_specific_topic`.
- Updated `zh_problem_summary` to fall back to a cleaned first abstract sentence instead of a fixed project-domain label.
- Updated Chinese method, evidence, and limitation fallback summaries to compact the source section content.
- Revised the Chinese executive summary scope and claim text to avoid hardcoding `论文长文本理解` and `多角色流程持续改进`.
- Updated scoring evidence selection so Chinese technical contribution scores prefer `贡献分析` over the broader executive summary when citing `多智能体`.

### Verification After Changes

- Red target test first failed because the generated report did not include `检索过滤` and still contained project-specific report wording.
- Target test passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_preserves_domain_specific_topic`
- Related Chinese workflow and DOCX tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_chinese_evidence_ledger_avoids_repeating_evidence_summary tests.test_workflow.ResearchWorkflowTest.test_chinese_executive_summary_states_problem_scope_and_importance tests.test_workflow.ResearchWorkflowTest.test_chinese_limitation_section_localizes_framework_terms`
  - `python3 -m unittest tests.test_docx.DocxWriterTest`
- Full test run initially failed on `test_chinese_scoring_counts_localized_agent_marker`; fixing preferred scoring evidence sections restored the expected `多智能体` citation.
- Regression tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_agent_marker`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_preserves_domain_specific_topic`
- Manual Chinese sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --language zh --rounds 1 --output-dir /tmp/paper_research_iter164_zh_after`
- `python3 -m unittest discover -s tests` passed with 146 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter164 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 165 - 2026-05-05 03:20 PDT

### Current Problems

- Direct protocol-relative web result links such as `//example.com/report` were preserved as non-normalized sources.
- Direct web result links with surrounding whitespace were not trimmed before scheme checks and downstream source recording.

### Planned Changes

- Add module-level web parser coverage for direct protocol-relative result links.
- Normalize direct protocol-relative links to HTTPS before unsupported-scheme filtering.
- Keep existing redirect, unsafe-link, and unsupported-scheme behavior intact.

### Changes Made

- Added `test_direct_protocol_relative_result_becomes_https`.
- Updated `_clean_result_url` to unescape and trim `href` values before parsing.
- Normalized direct `//...` result URLs to `https://...`.

### Verification After Changes

- Red target test first failed because the result URL remained ` //example.com/direct-report `.
- Target and related tests passed:
  - `python3 -m unittest tests.test_web_search.WebSearchParsingTest`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_extracts_external_report_results tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsupported_absolute_result_links tests.test_workflow.ResearchWorkflowTest.test_web_search_agent_ignores_unsafe_result_links`
- `python3 -m unittest discover -s tests` passed with 147 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter165 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 166 - 2026-05-05 03:22 PDT

### Current Problems

- DOCX exports rendered the rubric title as a plain paragraph below `Scoring Rubric`.
- This made per-round rubric titles less visible in Word's document outline/navigation structure.

### Planned Changes

- Add DOCX XML coverage that requires the rubric title to use the nested heading style.
- Render rubric titles as level-3 headings under the level-2 scoring rubric section.
- Verify existing English and Chinese exports still include expected sections and scorecards.

### Changes Made

- Added `test_export_renders_rubric_title_as_nested_heading`.
- Changed `write_docx` to render `round_result.rubric.title` with `Heading3`.

### Verification After Changes

- Red target test first failed because `Round 1 Evidence Rubric` was emitted as a normal paragraph.
- Target and related tests passed:
  - `python3 -m unittest tests.test_docx.DocxWriterTest.test_export_renders_rubric_title_as_nested_heading tests.test_docx.DocxWriterTest.test_export_uses_nested_heading_levels_for_report_sections`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- Manual sample run passed:
  - `python3 -m paper_research examples/sample_paper.txt --rounds 1 --output-dir /tmp/paper_research_iter166_docx_after`
- `python3 -m unittest discover -s tests` passed with 148 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter166 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 167 - 2026-05-05 03:25 PDT

### Current Problems

- Chinese contribution analysis for a general AI paper collapsed the core contribution to `检索`.
- Domain markers such as `对比预训练`, `可靠推理`, and `验证器` were present in the paper text but absent from the contribution section.

### Planned Changes

- Add a focused regression test for Chinese contribution extraction on a non-project-domain AI paper.
- Extend contribution marker extraction with common AI method/task terms.
- Verify the change does not break existing Chinese scoring evidence or English report behavior.

### Changes Made

- Added `test_chinese_contribution_analysis_keeps_domain_markers`.
- Extended `_extract_contribution` with markers for contrastive pretraining, reliable reasoning, verifier, and reranking concepts.

### Verification After Changes

- Red target test first failed because `贡献分析` only contained `论文强调检索`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_keeps_domain_markers tests.test_workflow.ResearchWorkflowTest.test_chinese_report_preserves_domain_specific_topic`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_scoring_counts_localized_agent_marker tests.test_workflow.ResearchWorkflowTest.test_english_executive_thesis_states_question_scope_and_importance`
- `python3 -m unittest discover -s tests` passed with 149 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter167 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 168 - 2026-05-05 03:27 PDT

### Current Problems

- English abstracts beginning with `We introduce ...` produced awkward report text such as `evaluate we introduce`.
- The English claim template still implied every paper's claim was about improving a workflow or method.

### Planned Changes

- Add a regression test for `We introduce ...` problem-statement cleanup.
- Extend English lead-verb removal beyond study/present/propose.
- Make the English claim/evidence ledger use a general feasibility/effectiveness claim.

### Changes Made

- Added `test_english_problem_statement_cleans_we_introduce`.
- Updated `problem_statement` to strip `we introduce/develop/design` and matching `this paper ...` variants.
- Reworded the English claim line to `is feasible or effective`.

### Verification After Changes

- Red target test first failed because the generated report contained `evaluate we introduce` and `argues that we introduce`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_problem_statement_cleans_we_introduce tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_english_executive_thesis_states_question_scope_and_importance`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parses_approach_and_evaluation_headings tests.test_workflow.ResearchWorkflowTest.test_english_scorecard_cites_report_evidence`
- `python3 -m unittest discover -s tests` passed with 150 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter168 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 169 - 2026-05-05 03:29 PDT

### Current Problems

- English `Benchmark Quality` text could produce the broken sentence fragment `Future web or local benchmarks should Only built-in...`.
- The built-in-only risk note was inserted between `should` and `continue`, reducing report readability.

### Planned Changes

- Add a regression test for the malformed built-in fallback sentence.
- Move the built-in-only risk note into its own sentence before the future benchmark guidance.
- Verify Chinese benchmark quality output remains unaffected.

### Changes Made

- Added `test_english_benchmark_quality_avoids_broken_builtin_sentence`.
- Reordered the English `_benchmark_quality_summary` sentence assembly.

### Verification After Changes

- Red target test first failed because `should Only built-in` appeared in the generated section.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_benchmark_quality_avoids_broken_builtin_sentence tests.test_workflow.ResearchWorkflowTest.test_english_report_records_external_benchmark_source_count`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_report_records_benchmark_source_quality tests.test_workflow.ResearchWorkflowTest.test_chinese_benchmark_quality_handles_empty_sources_readably`
- `python3 -m unittest discover -s tests` passed with 151 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter169 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 170 - 2026-05-05 03:32 PDT

### Current Problems

- Markdown titles wrapped in emphasis markup, such as `# **Title: Paper**`, leaked `**Title:` into generated report titles.
- This made the final report title look like raw Markdown instead of a cleaned paper title.

### Planned Changes

- Add a regression test for emphasized Markdown title headings.
- Strip common Markdown wrapper characters before and after title label cleanup.
- Verify existing Markdown and Chinese title cleanup still works.

### Changes Made

- Added `MARKDOWN_BOLD_TITLE_PAPER_TEXT` and `test_markdown_bold_title_markup_is_cleaned`.
- Added `_strip_title_markup` and used it inside `clean_title_text`.

### Verification After Changes

- Red target test first failed because the report title was `Deep Research Report - **Title: Bold Markdown Paper**`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_markdown_bold_title_markup_is_cleaned tests.test_workflow.ResearchWorkflowTest.test_markdown_title_heading_is_cleaned tests.test_workflow.ResearchWorkflowTest.test_markdown_chinese_title_label_is_cleaned`
  - `python3 -m unittest tests.test_cli_io.InputAndCliTest.test_load_paper_text_accepts_markdown_extension`
- `python3 -m unittest discover -s tests` passed with 152 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter170 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 171 - 2026-05-05 03:34 PDT

### Current Problems

- Chinese abstracts beginning with `本文提出了一种...` kept the auxiliary `了` after lead-verb stripping.
- Generated executive summaries could say `关于了一种...`, which is visibly ungrammatical.

### Planned Changes

- Add a regression test covering `本文提出了...` style abstracts.
- Strip optional `了` after common Chinese lead verbs.
- Verify existing Chinese report grounding and DOCX generation still pass.

### Changes Made

- Added `CHINESE_INTRO_LE_PAPER_TEXT` and `test_chinese_problem_summary_strips_le_after_intro_verb`.
- Updated `zh_problem_summary` lead-verb cleanup to consume optional `了`.

### Verification After Changes

- Red target test first failed because the executive summary contained `关于了一种图神经网络方法`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_problem_summary_strips_le_after_intro_verb tests.test_workflow.ResearchWorkflowTest.test_chinese_report_preserves_domain_specific_topic`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_contribution_analysis_keeps_domain_markers tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- `python3 -m unittest discover -s tests` passed with 153 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter171 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 172 - 2026-05-05 03:36 PDT

### Current Problems

- Chinese Markdown section headings wrapped in emphasis markup, such as `## **摘要**`, were not recognized.
- When headings were missed, Chinese reports fell back to generic method/evidence text instead of using the paper's actual sections.

### Planned Changes

- Add a regression test for emphasized Chinese Markdown section headings.
- Strip common Markdown wrapper characters during Chinese heading normalization.
- Verify existing Markdown title cleanup and English heading parsing remain intact.

### Changes Made

- Added `MARKDOWN_CHINESE_BOLD_SECTION_PAPER_TEXT` and `test_markdown_chinese_bold_section_headings_are_parsed`.
- Updated `normalize_chinese_heading` to strip Markdown wrapper characters before and after numbering cleanup.

### Verification After Changes

- Red target test first failed because `方法与证据` did not include `结构编码`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_markdown_chinese_bold_section_headings_are_parsed tests.test_workflow.ResearchWorkflowTest.test_markdown_chinese_title_label_is_cleaned`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_parses_roman_numbered_english_headings tests.test_workflow.ResearchWorkflowTest.test_parses_approach_and_evaluation_headings`
- `python3 -m unittest discover -s tests` passed with 154 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter172 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 173 - 2026-05-05 03:38 PDT

### Current Problems

- Chinese reports with missing method or experiment sections could include English fallback sentences.
- The output mixed phrases such as `The method section was not explicit` into otherwise Chinese reports.

### Planned Changes

- Add a regression test for Chinese papers that only provide a title and abstract.
- Route missing Chinese sections through localized summary helpers instead of English defaults.
- Verify English report defaults and Chinese DOCX generation remain intact.

### Changes Made

- Added `test_chinese_missing_sections_use_chinese_defaults`.
- Changed `ReportWriterAgent.write` to use empty defaults for missing method, experiment, and limitation text when `language="zh"`.

### Verification After Changes

- Red target test first failed because the report contained English fallback method and experiment sentences.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_missing_sections_use_chinese_defaults tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_english_report_uses_claim_evidence_ledger_sections tests.test_workflow.ResearchWorkflowTest.test_runs_iterative_agents_and_records_every_round`
- `python3 -m unittest discover -s tests` passed with 155 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter173 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.

## Iteration 174 - 2026-05-05 03:41 PDT

### Current Problems

- Chinese reports without an experiment/results section still said the experiment section provided directional coverage evidence.
- This contradicted the localized `实验或结果部分不够明确` evidence summary.

### Planned Changes

- Extend the missing-section regression test to reject unsupported positive evidence claims.
- Make the Chinese claim-evidence ledger explanation conditional on whether experiment text exists.
- Verify existing Chinese evidence-ledger behavior still passes.

### Changes Made

- Updated `test_chinese_missing_sections_use_chinese_defaults` to require `实验部分尚未提供足够的结果细节`.
- Added an `evidence_interpretation` branch in the Chinese report writer.

### Verification After Changes

- Red target test first failed because the report still contained `实验部分提供了覆盖提升的方向性证据`.
- Target and related tests passed:
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_missing_sections_use_chinese_defaults tests.test_workflow.ResearchWorkflowTest.test_chinese_report_uses_evidence_ledger_sections`
  - `python3 -m unittest tests.test_workflow.ResearchWorkflowTest.test_chinese_evidence_ledger_avoids_repeating_evidence_summary tests.test_workflow.ResearchWorkflowTest.test_can_generate_chinese_report_and_docx`
- `python3 -m unittest discover -s tests` passed with 155 tests.
- `PYTHONPYCACHEPREFIX=/tmp/paper_research_pycache_iter174 python3 -m compileall -q paper_research` passed.
- `git diff --check` passed.
