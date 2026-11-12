---
name: knowledge-capture
description: Saves reusable project knowledge as sourced question-and-answer entries with tags, retrieves it later with deterministic offline search, and exports a browsable knowledge base; use to record hard-won answers and decisions during or after research and debugging, and to look them up before re-researching.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Knowledge Capture

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

The project's memory of hard-won answers: every entry is a question, an answer, and a source (or an explicit assumption marker). Search is offline and deterministic; nothing here is improvised.

## When to use

- A research or debugging session produced an answer the project will need again ("Which port does the sandbox proxy actually use?").
- Before starting research, check whether the question is already answered.
- At session end, distill the durable Q&A out of the ledgers so the next session starts warm.

Do NOT use as a general notebook: entries are question-shaped, answer-complete, and sourced — or they do not belong.

## Workflow

1. **Check before researching:**

   ```bash
   $WB kb-search --query "csv export tax rounding"
   ```

   Token-overlap scoring (tags x3, question x2, answer x1) ranks entries deterministically; filter with `--tag billing`.

2. **Capture with a source:**

   ```bash
   $WB kb-add \
     --question "In which order does the billing export apply tax and rounding?" \
     --answer "Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified against AC1 and the fix in _line_total()." \
     --source-url "https://example.com/billing/export-spec" \
     --tag billing --tag export
   ```

   Sources: `--source-url` for a fetched page, or `--source-id S1` to bind the entry to a registered research-ledger source (validated against the ledger).

3. **Capture assumptions honestly:**

   ```bash
   $WB kb-add --question "What is the sandbox proxy timeout?" \
     --answer "Assumed 30s based on the default in similar setups; not documented anywhere we found." \
     --assumed --tag infra
   ```

   `--assumed` records LOW confidence and a warning — the entry exports marked **ASSUMPTION (unverified)**. An assumption that later gets evidence should be re-added with a source and the old entry noted.

4. **Export for humans:**

   ```bash
   $WB kb-export --output docs/knowledge-base.md
   ```

   Entries group by first tag; every entry shows its source or its assumption marker and the recording date.

## Guardrails

- **No unsourced, unmarked entries.** The runtime rejects them (`UNSOURCED_ENTRY`): a source URL, a ledger source ID, or an explicit `--assumed`.
- **Answers carry their reasoning**, not just their verdict — 20 characters is the floor, one working sentence is the bar.
- **One question per entry.** Compound questions defeat search; split them.
- **Tags are the retrieval interface**: lowercase, few, stable (`billing`, `export`, `infra`). A tag that appears once is a missed grouping; a tag on everything is no tag.
- **Assumptions decay** — before relying on an ASSUMPTION entry in a deliverable, verify it and re-capture with the source.

## Commands

| Command | Purpose |
|---|---|
| `kb-add` | Record a sourced (or explicitly assumed) Q&A entry |
| `kb-search` | Deterministic offline keyword search, tag-filterable |
| `kb-export` | Render the knowledge base as grouped Markdown |

## Output expectation

A knowledge base where any entry can be traced to a source or is visibly marked as an assumption, and where search finds the entry you captured weeks ago.

## References

- `references/entry-standards.md` — what makes a good question and answer; sourcing rules.
- `references/lifecycle.md` — when to capture, dedup, review cadence, and how entries age.

## Example

- `examples/capture-and-search.md` — capturing two entries (one sourced, one assumed) and finding them again.
