---
name: evidence-audit
description: Audits a draft report against the research ledger before delivery; flags unregistered links, generic anchors, claims whose numbers are absent from the cited source, overclaim language, stale currentness, undated evidence and single-source reliance; use before delivering any researched document or when asked to check someone else's draft.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Evidence Audit

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

The gate between a draft and a deliverable. `audit-report` checks the ledger's integrity and the report's citations, numbers, dates and language against the recorded evidence — deterministically, offline.

## When to use

- Before delivering any research report, comparison matrix or memo that cites sources.
- After editing a delivered report (re-audit; edits introduce violations).
- When asked to review a document someone else wrote against its claimed evidence.

## Workflow

1. **Audit the draft:**

   ```bash
   $WB audit-report --report-file report.md --max-age-days 365
   ```

2. **Read the issues.** Each issue carries a type, a line number, the offending text and a concrete `fix`. Blocking issues fail the audit; warnings do not unless `--strict` is set.

3. **Fix the document, not the ledger** (unless the ledger is wrong): re-check the source, correct the sentence, add the citation, soften the claim. Re-run until PASS.

4. **Optionally go strict** for decision-grade deliverables:

   ```bash
   $WB audit-report --report-file report.md --strict
   ```

   `--strict` fails on warnings too (overclaim wording, staleness, undated evidence, single-source reliance).

## What is checked

**Ledger integrity (blocking):** claims without sources, dangling source references, missing or weak quotes, HIGH-confidence claims whose quote never matched the stored excerpt.

**Citations (blocking):**
- Every inline URL must be registered in the ledger (`UNREGISTERED_REPORT_URL`) — you cited a page you never opened.
- Anchors must name the publisher/document; `[source]`, `[here]`, raw URLs are flagged (`GENERIC_OR_RAW_ANCHOR`).

**Content (mixed severity):**

| Check | Severity | What it means |
|---|---|---|
| `UNCITED_NUMERIC_CLAIM` | blocking | A number/date in prose with no citation on the sentence |
| `UNSUPPORTED_NUMBER` | blocking | The cited evidence does not contain that number |
| `DATE_AHEAD_OF_EVIDENCE` | blocking | The sentence implies a year newer than any cited source |
| `UNDATED_EVIDENCE` | warning | A dated/current claim resting on an undated source |
| `STALE_CURRENTNESS_CLAIM` | warning | "Currently/latest" on evidence older than `--max-age-days` |
| `OVERCLAIM_LANGUAGE` | warning | "always", "guaranteed", "the best"... without 2+ independent domains and a primary |
| `SINGLE_SOURCE_RELIANCE` | warning | >50% of citations from one domain |

## What is NOT checked (the human part)

The audit is mechanical. These remain your job — the checklist is in `references/audit-rules.md`:

- Whether a number is used in the right context (the source's 30% was about latency, not cost).
- Whether the reasoning from evidence to conclusion is valid.
- Whether the selection of sources is fair (absence of disconfirming evidence is not neutrality).

Run the manual checklist after the mechanical PASS, before delivery.

## Guardrails

- A report that cannot reach PASS is not ready. The fix is always more evidence or softer claims — never editing the ledger to match the report.
- Method, scope, gaps and appendix sections are exempt from number/currentness checks — do not hide claims there.
- Audit the report you will deliver, not an earlier draft.

## Commands

| Command | Purpose |
|---|---|
| `audit-report --report-file F` | Full audit: ledger integrity + citations + content |
| `audit-report --report-file F --strict --max-age-days N` | Decision-grade gate |

## Output expectation

A PASS verdict with zero blocking issues (and zero warnings under `--strict`), or a fix list precise enough that the next pass passes.

## References

- `references/audit-rules.md` — the complete issue taxonomy with examples and the manual post-audit checklist.

## Example

- `examples/report-audit.md` — a draft with five distinct violations, the audit output, and the fixed PASS-ing version.
