# Wide Comparison Matrix — <QUESTION>

> Deliverable skeleton for the wide-search skill. Fill every section; a `?`
> cell in the final table means the process stopped without a decision.
> Cell states and normalization rules: see `references/matrix-method.md`.

- **Question**: <the question this matrix answers, one sentence>
- **Mode**: <single-answer | comparison>
- **Compiled at**: <YYYY-MM-DD> by <agent/session>

## 1 · Entities

| ID | Entity | Notes |
|----|--------|-------|
| E1 | <name> | <edition / version pinned, if any> |
| E2 | <name> | |

## 2 · Field definitions (fill BEFORE the table)

| Field | What is measured | Unit / form | Scope boundaries |
|-------|------------------|-------------|------------------|
| <license> | <what> | <SPDX id as published> | <what counts, what does not> |
| <process_concurrency> | <what> | <count, with version> | <documented ceiling for…, not…> |
| … | | | |

Rules: 4–8 fields; every field fillable from public evidence; include at
least one 30-second-verifiable field (license, latest version).

## 3 · The matrix

| Entity \ Field | <field 1> | <field 2> | <field 3> | <field 4> |
|----------------|-----------|-----------|-----------|-----------|
| **E1** <name> | <value + [C#]> | <value (unverified)> | <CONFLICT: a / b> | <n.a. → gap G#> |
| **E2** <name> | | | | |

Cell states: `verified` value + citation · `unverified` value + "(unverified)"
· `conflict` "CONFLICT: a / b" · `n.a.` recorded gap · `?` unacceptable in a
final deliverable — search, or declare a gap.

## 4 · Claims register

| ID | Entity | Field | Value | Source | Quote (word-for-word) |
|----|--------|-------|-------|--------|-----------------------|
| C1 | E1 | <field> | <normalized value> | S1 | "<exact sentence>" |
| C2 | | | | | |

## 5 · Sources

| ID | URL | Tier | Why this tier |
|----|-----|------|---------------|
| S1 | <https://…> | PRIMARY | <vendor's own docs> |
| S2 | <https://…> | SECONDARY | <learned from someone else> |

## 6 · Conflicts & resolutions

| Entity \ Field | Claims | Resolution | Reason on record |
|----------------|--------|------------|------------------|
| <E1 \ field> | C2 vs C3 | <winner: C# / scoped / dated / left open> | <why, in one sentence> |

## 7 · Gap register

| ID | Entity | Field | What is missing | Declared at |
|----|--------|-------|-----------------|-------------|
| G1 | E2 | <field> | <no public benchmark for …> | <YYYY-MM-DD> |

## 8 · Query trail

| # | Query | Tool | Results kept | At |
|---|-------|------|--------------|----|
| 1 | <query string> | <firecrawl-search / …> | <n> | <time> |

Budget: ≈ 1–1.5 queries per cell. This trail is the proof the matrix did
not surf beyond its budget.
