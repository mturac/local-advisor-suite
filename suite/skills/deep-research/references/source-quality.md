# Source Quality Scoring (0-5)

The deterministic rules `research-score` applies to every registered source. The score is advisory input to coverage decisions, not a verdict on truth.

## Base score by declared tier

| Tier | Base | What qualifies |
|---|---|---|
| PRIMARY | 4.0 | The origin of the fact: official docs, specs, standards, changelogs, filings, papers, the vendor's own pages. |
| SECONDARY | 3.0 | Reputable reporting or analysis of primary material: established press, technical books, serious reviews with methodology. |
| TERTIARY | 2.0 | Aggregators, wikis, forums, community answers. Starting points for finding primaries, rarely citable alone. |

## Adjustments

| Condition | Effect | Rationale |
|---|---|---|
| Government / academic / standards domain (`.gov`, `.edu`, `.int`, `.mil`, europa.eu, ietf.org, w3.org, iso.org, ...) | +1.0 | Institutional accountability. |
| `docs.` / `developer.` host and PRIMARY tier | +0.5 | Official documentation subdomain. |
| Forum / social / self-publishing host (reddit, stackoverflow, medium, substack, personal blogs, ...) | -1.5 | No editorial accountability; fine for discovery, weak for citation. |
| Excerpt shorter than 80 characters | -0.5 | Too thin to verify quotes against. |
| Time-sensitive topic, no date | -0.5 | Undated evidence cannot support current claims. |
| Time-sensitive topic, 365-730 days old | -0.5 | Aging evidence on volatile ground. |
| Time-sensitive topic, older than 730 days | -1.0 | Probably superseded. |

Final score is clamped to [0, 5] and rounded to 2 decimals, with every adjustment's reason recorded in `quality_reasons`.

## Reading the score

- **4.0-5.0** — citable as primary support on its own.
- **2.5-3.9** — citable with corroboration; pair with an independent domain.
- **0-2.4** — a lead, not a source. Use it to find the primary (`research-gaps` will keep asking).

## Coverage rules that use the score

A sub-question is STRONG only when:

1. 2+ independent registrable domains support it (or 1 primary + corroboration), AND
2. at least one PRIMARY-tier source is present or the best quality score is >= 4, AND
3. at least one claim has a verbatim quote verified in the stored excerpt.

These are the exact conditions `research-gaps` checks; a WEAK verdict comes with the specific unmet condition and the action to fix it.

## Honesty about the limits

- Domain-based trust is a heuristic: a vendor's own docs are primary for "what the vendor says", but self-interested for "what is best". Comparison claims need the *user's* criteria, not vendor rankings.
- The score never inspects content truth: a perfectly-formatted page can be wrong. That is what cross-domain corroboration and the audit are for.
- If a source's score surprises you, read the reasons before overriding your judgment — and if you override, say why in the report.
