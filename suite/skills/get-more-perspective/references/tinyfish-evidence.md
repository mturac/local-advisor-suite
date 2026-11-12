# Evidence Gathering for the Panel: the TinyFish pattern

The skeptic and finance seats may not speak without evidence on the table.
This file is how evidence gets there: search to find, fetch to read, then
`panel-evidence` to table the quote. The same ladder works with TinyFish's
agent-grade web tools (when installed) or with the suite's own zero-vendor
`fetch-url` — pick by what your host has, not by habit.

## When to gather evidence

- Before the **skeptic** seat speaks: risks sound different when anchored
  ("competitor undercut us last quarter" vs. a quoted pricing page).
- Before the **finance** seat speaks: every `--number` must stand on a
  quote — a price, a rate, a count, from a page that was actually opened.
- Whenever any seat's opinion turns on a current-world fact (prices, limits,
  release dates, policies) rather than on reasoning from the question.

## Picking the right tool

| Tool | When to use | Cost | Needs |
|------|-------------|------|-------|
| **TinyFish search** | Find URLs and current facts fast: pricing pages, docs, comparisons, "what does X cost today" | Free tier, fast | `tinyfish` CLI + API key |
| **TinyFish fetch** | Read one or more URLs clean — strips nav/ads, returns just the content | Free tier, fast | `tinyfish` CLI + API key |
| **`fetch-url --allow-network`** | The suite's own safe fetcher: same job as fetch, zero external vendors, SSRF-guarded, 1 MB cap | Free, offline-first | Nothing (built into the workbench) |
| **conversation** | The user already said it, or it is in the session's context | Free | Quote it verbatim |
| **local-file** | A file in the scoped project root holds the fact | Free | `--project-root` scoping |

Prefer the suite's `fetch-url` when you already know the URL and want the
zero-dependency path; prefer TinyFish when you need discovery (search) or
clean extraction from heavy JS pages, and the CLI is installed.

## Commands (TinyFish CLI)

### `tinyfish search query`
Web search; returns ranked results with titles, URLs and snippets.
```bash
tinyfish search query "competitor pricing SaaS Pro tier 2026" --location us --pretty
```
- Returns 10 results by default; `--location` / `--language` for geo-targeted
  results; default output is JSON, `--pretty` for human-readable.

### `tinyfish fetch content get`
Clean, extracted content from one or more URLs — strips ads, nav and
boilerplate; returns just the content.
```bash
tinyfish fetch content get --format markdown "https://example.com/pricing"
```
- Accepts **multiple URLs** in a single call — fetched in parallel
  server-side.
- `--format markdown` (default) for readable text; `--format json` for a
  structured document tree; `--links` to include extracted links.
- Response includes `url`, `final_url`, `title`, `published_date`, `text`.

### `fetch-url` (the suite's own, zero-vendor fallback)
```bash
$WB fetch-url --allow-network --url "https://example.com/pricing"
```
- Blocks private IPs (SSRF guard), caps at 1 MB, caches by canonical URL.

## Common pattern: search → fetch → table

```bash
# 1. Find the pages (TinyFish search, or the host's own search tool)
tinyfish search query "Pro tier pricing" --pretty

# 2. Read the best results (TinyFish fetch — multiple URLs in parallel)
tinyfish fetch content get --format markdown "https://retailer-a.com/pricing" "https://retailer-b.com/pricing"

# 3. Table the quote the panel will argue about
$WB panel-evidence --via tinyfish-fetch --source-url "https://retailer-a.com/pricing" \
    --quote "Pro tier: 34 per seat per month, billed yearly, includes SSO" --label EV1

# 4. Cite it from the seat that needs it
$WB panel-voice --role finance --stance support --number "34 vs our 29: a 5-dollar undercut" \
    --evidence EV1 --reasoning "..."
```

The same ladder with the suite's own tools: host search or `fetch-url` for
step 1-2, then `--via fetch-url` (or `conversation` / `local-file`) in step 3.

## General notes

- **Quote verbatim, never paraphrase**: `panel-evidence` enforces a real quote
  (min 20 chars); the panel argues about what was actually seen.
- **One claim per evidence entry**: an entry mixing three facts cannot be
  cited precisely. Split them (EV1, EV2, EV3).
- **Cite the page you opened, not the page that linked to it**: the source URL
  is where the quote lives; a search snippet is not a source.
- **No key, no CLI, no network**: the panel still runs — gather from the
  conversation (`--via conversation`) or scoped local files
  (`--via local-file`), and say so in the quote. An honest offline panel
  beats a fabricated online one.
- **Parallel calls**: when checking several independent sites, make separate
  fetch calls — do not merge them into one goal; independent pages fail
  independently.
