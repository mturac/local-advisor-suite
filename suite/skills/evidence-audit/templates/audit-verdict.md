# Audit Verdict — <DOCUMENT>

> Skeleton for the evidence-audit skill. An audit does not re-do the work;
> it checks the work against explicit rules and reports each rule's result.

- **Audited document**: <path>
- **Audited at**: <YYYY-MM-DD>
- **Auditor**: <agent/session>

## Rules checked

| # | Rule | Result | Detail |
|---|------|--------|--------|
| 1 | Every claim carries a source | PASS / FAIL | <n>/<n> claims sourced |
| 2 | Quotes are non-empty | PASS / FAIL | |
| 3 | No unresolved contradiction | PASS / FAIL | <list or "none"> |
| 4 | Gaps declared, not hidden | PASS / FAIL | |
| 5 | Query budget respected | PASS / FAIL | <used>/<max> |

## Blocking findings

| Finding | Why it blocks | Fix |
|---------|---------------|-----|
| <finding> | <reason> | <minimal fix> |

## Verdict

**PASS / FAIL** — blocking_count: <n>

A FAIL is a result, not an error: it says exactly what must be fixed before
the document can be trusted.
