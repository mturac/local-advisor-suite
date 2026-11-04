# Search Log — <QUESTION>

> Skeleton for the web-search skill. A search without a trail cannot be
> audited: record what was asked, what was kept, and what was discarded —
> including the queries that found nothing.

- **Question**: <the question the searches serve>
- **Started**: <YYYY-MM-DD>
- **Budget**: <max queries>

## Queries

| # | Query | Tool | Kept | Note |
|---|-------|------|------|------|
| 1 | <query string> | <firecrawl-search / …> | <n> | <what looked promising> |
| 2 | <query that found nothing> | | 0 | dead end — do not retry unchanged |

## Kept results

| ID | Title | URL | Why kept |
|----|-------|-----|----------|
| R1 | | <https://…> | <relevant to sub-question …> |

## Quick verification

For each kept result, before citing it:

- [ ] URL opens and is the page it claims to be
- [ ] The quoted sentence exists on the page, word for word
- [ ] Publisher identified; primary vs secondary noted

## Not found (record it)

<what the searches could not find — this is a finding, not a failure>
