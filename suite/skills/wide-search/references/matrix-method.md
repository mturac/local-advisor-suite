# Matrix Method: Fields, Normalization, Cell States

## Field definitions come first

Before filling any cell, write the field's definition. A field definition states:

1. **What is measured**: "process_concurrency — how many independent processes may hold the database open simultaneously".
2. **Unit and form**: "license — SPDX identifier as published by the vendor".
3. **Scope boundaries**: "max_memory — the documented ceiling for a single query, not the process".

Without the definition, two cells that look comparable are not. The report template has a dedicated section for these definitions — fill it before the table.

## Choosing fields

- 4-8 fields for a readable matrix; more belongs in an appendix.
- Fields must be **fillable from public evidence**. "Ease of use" is not a field; "lines of code to first query" is.
- Include at least one field the reader can verify in 30 seconds (license, latest version) — it calibrates trust in the rest.

## Normalization rules

- **Units**: convert only when the source's unit is unambiguous ("$29/user/month" → "29 USD/user/mo" with the source's phrasing in the quote). Never convert across measurement regimes (median vs. mean, p50 vs. p99).
- **Versions and editions**: a field's value names the edition it applies to ("MIT (core; enterprise UI is AGPL)"), not just the headline.
- **Dates**: ISO form in values ("2026-04-05"), the source's own wording in the quote.
- **Booleans**: expand to what is true ("yes, since 1.2.0" with the version in the claim).

## Cell states

| State | Meaning | How it renders | What to do |
|---|---|---|---|
| verified | VERIFIED claim, quote matched in excerpt | value + citation | nothing |
| unverified | claim without quote match (or PROVISIONAL) | value + "(unverified)" | re-register the source with a longer excerpt, or accept and mark |
| conflict | 2+ verified claims with different normalized values | "CONFLICT: a / b" | `research-resolve`, or surface as unstable |
| n.a. | recorded gap | `n.a.` | link appears in the gap register below the table |
| ? (missing) | no claim, no gap | `?` | a hole: search, or declare a gap |

The `?` state is the only unacceptable one in a final deliverable — it means the process stopped without a decision. `wide-table --strict` fails on unverified, conflict and missing.

## Conflicts

A conflict means the field is unstable across sources: different versions, editions, measurement dates or scopes. Resolution options, in order of preference:

1. **Scope the difference**: both values are right in their scope ("single node: X; cluster: Y") — resolve with the winning claim being the scoped statement.
2. **Date the difference**: newer primary wins; record the reason ("C2 cites the 2026 docs; C1 cites the 2024 model").
3. **Leave it open**: surface the conflict in the report's contradiction section. An honest conflict beats a false consensus.

## Scale discipline

- Budget ≈ 1-1.5 queries per cell. A 5x8 matrix (40 cells) with 15 queries will have gaps — plan which cells matter (the ones the reader will decide on) and declare the rest early.
- Register sources once per entity; the source's excerpt can support several fields of that entity.
- Fill the matrix row-major (all fields of one entity per search session) — it keeps the entity's context loaded and reduces fetches.
