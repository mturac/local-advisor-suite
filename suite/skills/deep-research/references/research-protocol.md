# Research Protocol

The operating loop of a deep-research session. Follow it in order; every stage has a stop rule.

## Stage 1 — Decompose

Turn the topic into 3-6 sub-questions. Quality bar:

- **Answerable independently.** If answering Q1 always answers Q3, merge them.
- **Decisive, not encyclopedic.** Each sub-question should change what the reader does. Background that changes nothing gets cut.
- **Scoped to verifiable facts.** "What is the licensing model?" is verifiable. "Is it good?" belongs to the decision layer.

Set `--max-queries` to roughly 2 per sub-question (12 for 6 sub-questions). Use `--time-sensitive` when any answer rots (prices, versions, policies, benchmarks).

**Stop rule**: if you cannot write the sub-questions, you do not understand the request — ask the user one clarifying question instead of searching your way to one.

## Stage 2 — Search and open

- One query at a time, logged (`research-log-query`), attached to a sub-question.
- Prefer primary sources: official docs, specs, changelogs, filings, papers, standards bodies.
- Open every page you might cite, with the host's fetch tool. Skim for the sub-question's answer; if absent, move on.
- Register the source **immediately after opening** (`research-add-source` with `--content-file`), not in a batch later — excerpts get lost that way.

**Stop rule**: the budget. When `research-log-query` reports 0 remaining, stop searching. Record gaps for what is missing and go to synthesis. If coverage is unacceptable, ask the user to raise the budget explicitly.

## Stage 3 — Claim extraction

- One claim per fact, with `--entity` and `--field` when the fact could populate a comparison cell.
- The quote is copied verbatim from the page text — punctuation, casing, spacing. If the ledger rejects the quote (`QUOTE_NOT_IN_SOURCE`), the fix is to re-copy the sentence or re-register the source with a longer excerpt. The escape hatch `--allow-unverified-quote` exists for genuinely unquotable-but-true facts and forces LOW/PROVISIONAL — use it rarely, and say so in the report.
- Values are normalized short forms for table cells ("1 RW or N RO", "$29/mo", "MPL-1.1"). Statements are full sentences.

**Stop rule**: a sub-question reaches STRONG coverage (2+ independent domains, or 1 primary + 1 corroboration) — then stop adding sources to it and move to the next.

## Stage 4 — Confront the evidence

Run `research-status`. Handle what it reports:

| Signal | Response |
|---|---|
| Contradiction (same entity+field, different values) | Register both claims, then `research-resolve` with a reason that names the scope/date/edition difference. If you cannot resolve it, the contradiction goes in the report as-is. |
| WEAK sub-question | `research-gaps` names the exact next action: independent domain, primary source, or longer excerpt. Do that action or record a gap. |
| Low-quality sources | `research-score` lists reasons (forum host, undated, thin excerpt). Upgrade the source, or accept and say so. |
| Budget exhausted with OPEN sub-questions | `research-add-gap --reason BUDGET_REACHED` for each, then synthesize. |

## Stage 5 — Synthesize

- `research-pack` renders the claims, quotes and citations grouped by sub-question. Synthesize **from the pack only** (see `synthesis-standard.md`).
- The report's structure follows the sub-questions, not the chronology of the search.
- Gaps get their own section with the queries tried and reasons — they are results.
- Volatile facts are dated in the text ("as of 2026-11").

## Stage 6 — Audit and deliver

`audit-report --report-file report.md` must return PASS before delivery. Fix what it flags (it names the line and the fix). Then optionally `delivery-verify --artifact report.md` to record the artifact, and `handoff-pack` if the session ends here.

## Cadence rules

- Never search without a ledger sub-question to attach the result to.
- Never register a source you did not open this session.
- Never resolve a contradiction without writing why the winner wins.
- Never let a gap silently become a sentence in the report.
