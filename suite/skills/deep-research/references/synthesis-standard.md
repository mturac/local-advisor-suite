# Synthesis Standard

How to write the final report from the evidence pack without drifting beyond the evidence.

## The pack is the boundary

`research-pack` renders exactly what you may use: claims with citations, verbatim quotes, gaps, resolutions. The report may:

- **Combine** claims across sub-questions into a narrative.
- **Interpret** what the claims mean for the reader's question.
- **Recommend**, with the reasoning attached to evidence.

The report may NOT:

- State a number that is not in a claim (audit flag: `UNSUPPORTED_NUMBER`).
- Cite a URL that is not in the ledger (audit flag: `UNREGISTERED_REPORT_URL`).
- Use a superseded claim (the pack marks them: "do not use").
- Present a gap's topic as if it were answered. Gaps get their own section.

## Structure

1. **Executive summary** — the answer to the topic question in 3-5 cited sentences. If the evidence does not support a summary this short, say what is missing instead of padding.
2. **Findings by sub-question** — one section per sub-question, claims woven into prose with inline citations after each fact.
3. **Comparison table** (if entities were tracked) — built from verified claims; every cell carries its citation, missing cells are `n.a.`.
4. **Contradictions and resolutions** — each resolved contradiction with its reason; each unresolved one stated as open.
5. **Gaps** — a table of what could not be verified, the queries tried, and the reason. This section is a deliverable, not a confession.
6. **Recommendations** — only actions the evidence supports, each with its justification linked.

## Citation form

- Inline, immediately after the fact: `([Publisher](url))`.
- Anchor names the publisher or document: `[DuckDB docs]`, `[SQLite Architecture]`, `[OECD 2025 report]`.
- Never `[source]`, `[link]`, `[here]`, or a bare URL — the audit flags each of these.
- One citation per fact, not one per paragraph.

## Calibration language

- Match the evidence: "DuckDB documents a single-writer model ([DuckDB docs](...))", not "DuckDB is single-writer" — unless multiple independent sources agree, in which case say so.
- Absolute terms ("best", "always", "guaranteed", "proven") require 2+ independent domains AND a primary source; otherwise the audit flags `OVERCLAIM_LANGUAGE` and the fix is softer wording or more evidence.
- Volatile facts are dated: "as of 2026-11".

## Numbers

- Use the source's number, not a recomputation. If you must compute (e.g. converting units), show the computation next to the cited inputs.
- The audit checks numbers digit-level: every digit in your sentence should appear in the cited evidence. "about a third" instead of "33%" when the source says "roughly one-third" is the correct call.

## Before delivering

Run `audit-report --report-file <report.md>`. Every issue it raises names its line and fix. Fix them all (PASS), or `--strict` will also fail on warnings. The report that ships is the report that passed.
