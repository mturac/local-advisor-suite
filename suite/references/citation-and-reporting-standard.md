# Citation & Reporting Standard

When writing research syntheses, decision memos, or wide comparison tables:

1. **Natural Inline Citations**:
   - Every factual claim derived from a source must carry an inline Markdown link immediately after the sentence or table cell.
   - Anchor text must name the specific publisher, documentation, or paper — never generic words like `[source](...)`, `[link](...)`, `[here](...)`, or raw URLs.
   - Example: `SQLite runs in-process without a separate server daemon ([SQLite Architecture Docs](https://www.sqlite.org/arch.html)).`

2. **Ledger Grounding**:
   - Every URL cited in a Markdown report must exist in `.local-workbench/research_ledger.json` under `sources`.
   - Run `python3 scripts/workbench.py audit-report --report-file <report.md>` before delivering any research report.

3. **Missing Data (`n.a.`)**:
   - In wide entity comparisons, if a field cannot be verified from a fetched primary or reputable secondary source within the query budget, write `n.a.` in the table cell and log a gap with `research-add-gap`.
   - Never guess or interpolate missing numbers from model training memory.

4. **Contradiction Handling**:
   - When two reputable sources disagree on a figure or policy, register both sources and claims, then explain the discrepancy (e.g., different benchmark dates, editions, or scope definitions) instead of silently picking one.

5. **Verification Wording** (v3.0):
   - Delivery wording is level-bound to the L0-L4 ladder; never claim above the level `verify-delivery` recorded.
   - Spec work is criterion-bound: a task is done when its acceptance criterion's observable outcome is demonstrated, not when the code is written.
   - Assumptions are marked: knowledge entries added with `--assumed` export as **ASSUMPTION (unverified)** and must never be cited as fact.
