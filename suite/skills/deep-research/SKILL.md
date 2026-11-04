---
name: deep-research
description: Multi-step research with a local evidence ledger; decomposes the topic into sub-questions, enforces a query budget, registers every opened source with a hash, verifies claims against verbatim quotes, scores sources 0-5, detects and resolves contradictions, records knowledge gaps and audits the final report; use for any question needing several sources and a synthesis.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.0.0"
---

# Deep Research

Research that leaves an auditable trail: every claim in the final report traces to an opened source and a verbatim quote, every gap is explicit, and contradictions are resolved on the record.

## When to use

- The question needs several sources and a synthesis ("How do these databases handle concurrency? What are the trade-offs?").
- A decision (`decision-review`) needs verified facts as scores.
- A previous quick lookup (`web-search`) hit contradictions or missing pieces.

Do NOT use for a single fact — that is `web-search`. For entity-by-field tables — that is `wide-search` (same ledger, matrix mode).

## Workflow

1. **Decompose before searching.** Write the topic as 3-6 sub-questions that together answer it, and set a query budget.

   ```bash
   $WB research-init --topic "Embedded analytical DBs for local Python workloads" \
     --sub-question "What are the licensing models?" \
     --sub-question "What are the concurrency limitations?" \
     --sub-question "What are the memory limits under spill-to-disk?" \
     --max-queries 12 --time-sensitive
   ```

   `--time-sensitive` enables recency penalties in scoring. Good decomposition is the research: two sub-questions that always answer together are one question.

2. **Search inside the budget, on the host's tools.** Log every query:

   ```bash
   $WB research-log-query --query "DuckDB concurrency multiprocess file locking" --sub-question-id Q2
   ```

   Duplicate queries are rejected; the budget exhausted is a stop signal, not a suggestion. When it trips, record gaps and synthesize.

3. **Register sources from opened pages only.** Fetch with the host tool (or `fetch-url --allow-network`), then:

   ```bash
   $WB research-add-source --url https://duckdb.org/docs/connect/concurrency \
     --title "Concurrency - DuckDB Documentation" --publisher "DuckDB Foundation" \
     --tier PRIMARY --published-date 2026 --content-file page.txt
   ```

   Sources are deduplicated by canonical URL and content-hashed. A search snippet is never a source.

4. **Extract atomic claims with verbatim quotes.**

   ```bash
   $WB research-add-claim --sub-question-id Q2 --entity DuckDB --field process_concurrency \
     --statement "DuckDB allows one read-write process or multiple read-only processes" \
     --value "1 RW or N RO" --source-id S1 \
     --quote "one process with read-write access, or multiple processes with read-only access"
   ```

   The quote must appear in the stored excerpt, or the claim is rejected (or forced LOW/PROVISIONAL with `--allow-unverified-quote`). One claim = one fact; do not bundle.

5. **Check status and coverage.**

   ```bash
   $WB research-status     # contradictions, unresolved sub-questions, budget
   $WB research-gaps       # per-sub-question coverage: STRONG / WEAK / OPEN + next actions
   $WB research-score      # 0-5 source quality with reasons
   ```

   Fix what they flag: find an independent domain (`research-gaps` says how many), upgrade to a primary source, or re-register with a longer excerpt so the quote verifies.

6. **Resolve contradictions explicitly.**

   ```bash
   $WB research-resolve --entity DuckDB --field process_concurrency --winner-claim C2 \
     --reason "C2 cites the 2026 docs; C1 cites a 2024 blog describing the old single-writer model"
   ```

   Never silently pick a side. The resolution reason is part of the record.

7. **Record gaps honestly.** What you could not verify within budget:

   ```bash
   $WB research-add-gap --sub-question-id Q3 --entity DuckDB --field encrypted_swap_overhead \
     --description "No published fixed overhead percentage for encrypted spill-to-disk" \
     --query-tried "DuckDB encrypted spill benchmark" --reason NO_PUBLIC_SOURCE
   ```

8. **Build the evidence pack and synthesize from it only.**

   ```bash
   $WB research-pack --output .local-workbench/evidence_pack.md
   ```

   Write the synthesis using only the pack's claims and citations. Superseded claims are marked and must not be used.

9. **Audit before delivering.**

   ```bash
   $WB audit-report --report-file report.md
   ```

   Deliver only on PASS (see `evidence-audit`). Then run `delivery-verify --artifact report.md` to record what was actually produced.

## Guardrails

- **Ledger-first**: nothing enters the report that is not a claim in the ledger.
- **Budget discipline**: the query budget exists to force synthesis over infinite drift.
- **No memory gaps**: an unverifiable cell is `n.a.` plus a recorded gap, never a remembered number.
- **Independent domains**: a sub-question is STRONG only with 2+ independent domains or a primary source.

## Commands

| Command | Purpose |
|---|---|
| `research-init` | Create the ledger: sub-questions, entities, budget, time-sensitivity |
| `research-log-query` | Spend a query against the budget |
| `research-add-source` | Register an opened page (hash, excerpt, tier, date) |
| `research-add-claim` | Atomic fact with a verbatim quote, verified against the excerpt |
| `research-add-gap` | Record what could not be verified and why |
| `research-status` | Contradictions, unresolved sub-questions, readiness |
| `research-score` / `research-gaps` | Source quality 0-5; per-sub-question coverage |
| `research-resolve` | Record the winning claim of a contradiction and why |
| `research-pack` | Markdown evidence pack for synthesis |
| `audit-report` | Full audit of ledger + report (delegates to the `evidence-audit` rules) |

## Output expectation

A report where every fact carries a named inline citation, gaps have their own section, contradictions have recorded resolutions, and `audit-report` returns PASS.

## References

- `references/research-protocol.md` — the full loop with decision points and stop rules.
- `references/source-quality.md` — the exact 0-5 scoring rules the runtime applies.
- `references/synthesis-standard.md` — how to write from the evidence pack without drifting.

## Example

- `examples/duckdb-concurrency.md` — a real ledger run: init, sources, claims, a contradiction, its resolution, and the pack.
