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
