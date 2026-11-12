---
name: wide-search
description: Entity-by-field comparison tables where every cell is backed by a verified claim with a citation and missing facts are explicit n.a. gaps; use when the user wants to compare several products, tools, libraries or vendors across the same attributes and demands a trustworthy matrix.
license: Apache-2.0
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.3"
---

# Wide Search

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Compare N entities across M fields in a matrix where every cell is either verified against an opened source or explicitly `n.a.` Nothing in the table comes from memory.

## When to use

- "Compare these 5 databases / CI tools / frameworks / vendors as a table."
- The user needs a decision-grade comparison for `decision-review` scoring.

Do NOT use for a single entity's deep dive (`deep-research`) or a single fact (`web-search`) — though all three share the same ledger and runtime.

## Workflow

1. **Define the matrix before filling it.**

   ```bash
   $WB research-init --mode wide-matrix \
     --topic "Embedded analytical DBs compared" \
     --entity DuckDB --entity SQLite --entity Polars \
     --field license --field process_concurrency --field max_memory --field python_api \
     --max-queries 15
   ```

   Field names are snake_case keys, stable across entities. Every field needs a definition in the report (unit, scope, normalization) — see `references/matrix-method.md`.

2. **Search per (entity, field) cell**, on the host's tools, logging queries:

   ```bash
   $WB research-log-query --query "DuckDB license" 
   $WB research-add-source --url https://duckdb.org/license --title "License" --tier PRIMARY --content-file page.txt
   $WB research-add-claim --entity DuckDB --field license \
     --statement "DuckDB is MIT licensed" --value "MIT" --source-id S1 --quote "DuckDB is MIT licensed"
   ```

   The `--entity`/`--field` pair is what routes a claim into its cell.

3. **Declare cells you cannot verify.** After honest attempts (record the queries):

   ```bash
   $WB research-add-gap --entity Polars --field max_memory \
     --description "No documented hard memory ceiling; depends on spilling config" \
     --query-tried "Polars max memory limit" --reason NO_PUBLIC_SOURCE
   ```

4. **Render the matrix.**

   ```bash
   $WB wide-table --output .local-workbench/matrix.md --csv .local-workbench/matrix.csv
   ```

   Cell states: **verified** (claim with quote match, citation shown), **unverified** (claim without quote match), **conflict** (contradicting verified values — run `research-resolve`), **n.a.** (recorded gap), **?** (nothing — this is a hole in your process; fill or declare it).

5. **Gate on quality.**

   ```bash
   $WB wide-table --strict    # FAIL if any cell is unverified, conflicting or missing
   ```

   For a decision-grade table, iterate until strict passes or the remaining cells are declared gaps.

6. **Deliver with the report** built on `templates/wide-comparison-matrix.md`: field definitions, the table, the gap register, and the query trail. Run `evidence-audit` on the final document.

## Guardrails

- **No memory cells.** An unverifiable cell is `n.a.` with a gap entry. A remembered "MIT license" is a liability, not a shortcut.
- **Normalization discipline.** "$29/user/mo" and "29 USD" are the same value only after you say so in the field definition; state units.
- **Conflicts are findings.** Two sources disagreeing on a cell is information about the field's instability — resolve with `research-resolve` or surface it, never average it.
- **Budget honesty.** With a 15-query budget and 12 cells, some cells will not make it. Declare them rather than stretching.

## Commands

| Command | Purpose |
|---|---|
| `research-init --mode wide-matrix` | Create the ledger with entities and fields |
| `research-log-query` / `research-add-source` / `research-add-claim` | Same ledger discipline as deep-research, with `--entity`/`--field` routing |
| `research-add-gap` | Declare a cell `n.a.` with the attempted queries |
| `research-resolve` | Resolve a cell conflict on the record |
| `wide-table [--strict] [--csv]` | Render the matrix with per-cell states and a gap register |

## Output expectation

A table where a reader can click any non-`n.a.` cell's citation and find the quoted fact on the opened page, plus a gap register explaining every `n.a.`

## References

- `references/matrix-method.md` — field definition, normalization and cell-state rules.

## Example

- `examples/db-matrix.md` — a 3-entity matrix including a conflict, its resolution, and a declared gap.
