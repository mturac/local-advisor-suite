# Quick Verification Protocol

The loop behind every verified one-shot answer. Target: 1-3 sources, under the query budget, every citation opened.

## The loop

1. **Formulate one query** that would surface a primary source (official docs, changelog, spec, vendor page). Prefer `site:` scoping and exact product terms over natural-language questions.
2. **Search** with the host tool. Log it if a ledger is active: `research-log-query --query "..."`.
3. **Pick by promise of primary evidence**, not by rank: the vendor's own documentation outranks any article about it.
4. **Open the page.** Read the text. If the fact is not on the page you opened, it is not verified — go back to step 1 with a narrower query, or accept failure honestly.
5. **Quote verbatim.** Copy the exact sentence containing the fact. Punctuation included. This quote is what the ledger checks.
6. **Answer** with the inline citation. Done.

## Budget

A quick-verify ledger starts with `--max-queries 3`. If three queries have not produced an openable primary source:

- Record the failure: `research-add-gap --description "..." --reason NO_PUBLIC_SOURCE --query-tried "..."`.
- Tell the user what you tried and what is missing (paywall, no public source, wrong terms).
- Do not silently widen into an unplanned deep-research session. Offer it explicitly instead.

## Common failure modes

| Failure | Correct response |
|---|---|
| Search results are all SEO rewrites of an older announcement | Query the vendor's docs or changelog directly; try `site:vendor.com` |
| The page is behind a paywall | Treat as a lead; look for the primary source it cites, or record a gap `--reason PAYWALL` |
| The page opens but the fact is absent | Not verified. Narrow the query or try the next result; do not paraphrase from memory |
| Two sources disagree | Register both; if the disagreement matters, escalate to `deep-research` (contradiction handling) instead of picking silently |
| The fact is volatile and the page is undated | Answer with "as of <access date>"; flag that a dated source is needed for a durable claim |

## Volatile facts

Versions, prices, rate limits, policies and "currently" statements all rot. For each:

- Prefer a dated page (changelog entry, release notes, dated announcement).
- Write the answer as "X, as of <date> ([Publisher](url))".
- If the answer will live in a deliverable that gets audited, register the source and claim in the ledger — `evidence-audit` will check the staleness rules for you.
