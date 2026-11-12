---
name: data-analysis
description: Grounded analysis of a data file the user names (CSV, TSV, JSON, logs); registers the dataset with a SHA-256 content hash, logs every number as a finding that carries the exact command or formula which produced it, declares gaps instead of guessing, and renders a report whose figures all trace to the ledger; use for analyze this file, dataset questions, row counts, trends and summaries.
license: Apache-2.0
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.3"
---

# Data Analysis

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Answer a question about a data file the user provides — with the dataset pinned by hash, every number logged with the command that produced it, and gaps declared instead of guessed.

## When to use

- The user names a data file (CSV, TSV, JSON, log) and asks a question about its contents: "analyze this", "what's the trend", "how many rows", "summarize the sales data".
- The user asks for aggregates, counts, comparisons or anomalies inside a specific file.

Do NOT use when:

- The question is about the web or external facts, not a local file — that is `web-search` or `deep-research`.
- The user wants entities compared across sources as a table — that is `wide-search`.
- No file is named — ask for one; do not go hunting through the project for data.
- The file is code with a bug — that is `local-debug`.

## Workflow

1. **Intake.** Ask for the file path and the analytical question if either is missing. Register both before computing anything:
   `$WB data-register --path FILE --question "..."` — this records path, size and SHA-256 so every later number is bound to an exact dataset version.
2. **Profile before interpreting.** Establish the shape of the data first (row count, columns, date ranges, missing values) and log each check as a finding. Read `references/dataset-intake.md`.
3. **Compute with methods, log as findings.** For every number you will present: run the real command (or apply the formula), then log it:
   `$WB data-finding --statement "..." --method "exact command" --result "..."`
   The method must be re-runnable by the user. A number without a method is a guess — never log one. Read `references/computation-ledger.md`.
4. **Declare what you cannot compute.** Missing columns, ambiguous definitions, out-of-scope asks:
   `$WB data-gap --description "..." --reason "NO_DATA | AMBIGUOUS_DEFINITION | OUT_OF_SCOPE | ..."`
5. **Watch for drift.** `data-finding` and `data-report` refuse to run when the file no longer matches its registered hash; re-run `data-register --path FILE` (same path refreshes the hash) and redo affected findings.
6. **Report.** Render the deliverable from the ledger:
   `$WB data-report --answer "..."` — writes `ANALYSIS.md` (or `--output`). Numbers in the answer that no finding supports are rejected (`UNLEDGERED_NUMBERS`); either log the finding or pass `--allow-unverified-numbers` to publish them visibly marked UNVERIFIED.

## Stop rules

- Never present a number that is not a logged finding — compute it, or declare a gap.
- Check the pitfalls in `references/pitfalls.md` (missing data, unit confusion, aggregation traps, small samples) before writing the answer.
- The report answers the registered question and names its dataset; anything beyond that scope is a new question.

## Files

- `references/dataset-intake.md` — profiling checks to run before interpreting anything.
- `references/computation-ledger.md` — the finding discipline: methods, results, rounding, units.
- `references/pitfalls.md` — the recurring traps that make file analyses wrong.
- `templates/analysis-report.md` — fillable report skeleton (same fields the CLI emits).
- `examples/sales-trend.md` — a real run: register, findings, gap, report.
