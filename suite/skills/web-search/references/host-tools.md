# Host Web Tools Reference

What each supported environment provides for search and fetch, and what that means for this skill.

| Host | Search tool | Fetch tool | Notes |
|---|---|---|---|
| Claude Code | `WebSearch` | `WebFetch` | Subject to the project's `permissions` rules; ask the user to allow them if denied. |
| Codex | `web_search` (default `cached`; `live` for current facts) | `web_search` follow-ups / shell fetch | Cached results may be stale — request live mode for volatile facts. |
| ZCode | built-in web search in the agent loop | built-in fetch | Availability depends on the ZCode plan and settings; if absent, say so. |
| Cursor | agent web search | agent fetch / terminal | In Agent mode with web enabled; otherwise ask the user to enable it. |
| OpenCode | `websearch` (only with the OpenCode provider or `OPENCODE_ENABLE_EXA=1`) | `webfetch` (always) | `webfetch` alone is workable: search can be replaced by asking the user for candidate URLs, or by the host's configured search. |
| Any AGENTS.md host | whatever the host permits | whatever the host permits | The rules block instructs the agent to use only permitted tools and to declare when none are available. |

## Rules that hold on every host

1. **Only host-native tools.** This suite never calls third-party research APIs, MCP servers or paid services on its own. `fetch-url` is the single fallback and requires the explicit `--allow-network` flag.
2. **Declare the unavailable.** If no web tool is enabled, the correct behavior is to say which setting would enable one — never to answer from model memory and present it as verified.
3. **Respect the query budget.** Log every query with `research-log-query` when a ledger is active; the budget is what separates research from drifting.

## When to use `fetch-url` instead of the host fetch tool

- The host fetch tool is unavailable or refuses a page, and the user has approved direct network access.
- You need the cleaned-text cache (`--state-dir` fetch cache) for repeat reads.

`fetch-url` enforces: HTTPS only, public IPs only (SSRF guard), 1 MB cap, local cache. It never follows the host's authentication; pages behind login are out of scope for this suite.
