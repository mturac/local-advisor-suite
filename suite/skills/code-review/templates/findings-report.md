# Findings Report — <TARGET>

> Skeleton for the code-review skill. Mirrors the review-* ledger fields
> (severity, file, lines, evidence) so hand-written and CLI-written reviews
> stay interchangeable.

- **Target**: <path / glob reviewed>
- **Reviewed at**: <YYYY-MM-DD>
- **Scope**: <what was in and out of scope>

## Findings

| ID | Severity | File | Lines | Finding | Evidence (quote the code) | Suggested fix |
|----|----------|------|-------|---------|---------------------------|---------------|
| F1 | MAJOR / MINOR / INFO | <path> | <start-end> | <what is wrong> | `<exact code line>` | <one-line fix> |

Severity: **MAJOR** = correctness/security/data loss · **MINOR** = style,
duplication, naming · **INFO** = observation, no change requested.

## Verdict

- **Blockers**: <n MAJOR findings> — merge blocked until fixed
- **Summary**: <two sentences: overall state, biggest risk>

## Evidence discipline

Every finding quotes the exact line(s) it refers to — no "somewhere in the
file". A finding without quoted evidence is an opinion, not a finding.
