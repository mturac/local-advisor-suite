---
name: web-search
description: Fast, source-verified answers to single factual questions using the host's own search and fetch tools; opens every cited page, quotes it verbatim in a small ledger, and answers with 1-3 inline citations; use for versions, prices, limits, dates, API behavior and other lookups that need a current, checkable source.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.0.0"
---

# Web Search

Answer one factual question with 1-3 verified sources. Fast path: search, open the pages, quote them, answer with inline citations. A search snippet is never evidence.

## When to use

- The user asks a single factual question: "What is the latest LTS of X?", "Does Y support Z?", "What is the rate limit?".
- You need one or two facts to unblock another skill (`local-advisor`, `decision-review`).

Do NOT use when:

- The question decomposes into several sub-questions or compares entities across fields — that is `deep-research` or `wide-search`.
- The answer is knowable from the conversation or the user's own files — do not search.

## Workflow

1. **Use the host's search tool** (see `references/host-tools.md` for the exact tool per environment). If no web tool is available in this environment, say so and stop — do not answer from memory.

2. **Open the pages.** Fetch every page you intend to cite, with the host's fetch tool (or `fetch-url --allow-network` as a fallback). Read the actual text. If a promising result is paywalled or unfetchable, it is a lead, not a source — find another or record the failure.

3. **Register what you verified** (optional for one-off lookups, required if the answer will be cited in a deliverable):

   ```bash
   $WB research-init --topic "DuckDB latest stable version" --mode quick-verify --max-queries 3
   $WB research-add-source --url https://duckdb.org/ --title "DuckDB" --tier PRIMARY --published-date 2026 \
     --excerpt "..."          # or --content-file page.txt
   $WB research-add-claim --statement "DuckDB 1.4.0 is the current stable release" \
     --source-id S1 --quote "<exact sentence from the page>"
   ```

   The claim is rejected unless the quote appears verbatim in the stored excerpt — that rejection is the value of the ledger.

4. **Answer with inline citations** named after the publisher or document: "DuckDB 1.4.0 is the current stable release ([DuckDB docs](https://duckdb.org/))." Never `[source]`, `[here]`, or a raw URL.

5. **Date-stamp anything volatile.** For prices, versions and policies, write "as of <today>" or cite the page's own date. If the fact is older than it should be, say so and offer `deep-research`.

## Guardrails

- **Open before citing.** No URL appears in your answer that was not fetched this session.
- **No memory answers.** If web tools are unavailable, the honest answer is "I cannot verify this here" plus what to enable.
- **Snippet discipline.** A search-result snippet is a pointer to a page, never the page itself.
- **No silent provider switches.** Use the tools this environment already permits; do not add APIs, keys or MCP servers the user did not configure.

## Commands (optional ledger use)

| Command | Purpose |
|---|---|
| `research-init --mode quick-verify` | Start a 3-query budget for the lookup |
| `research-add-source` / `research-add-claim` | Register opened pages and verbatim-quoted facts |
| `fetch-url --allow-network` | Fallback HTTPS fetch with SSRF protection and caching |

## Output expectation

A one-paragraph answer, inline citations after every fact, an "as of" date for volatile facts, and a note when verification was not possible.

## References

- `references/host-tools.md` — which search/fetch tool each host exposes and its limits.
- `references/quick-verification-protocol.md` — the search-open-quote loop in detail, including failure handling.

## Example

- `examples/version-lookup.md` — a version lookup with a registered source and a quoted claim.
