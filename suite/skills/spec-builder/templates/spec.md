# Spec — <TITLE>

> Skeleton for the spec-builder skill. Work that starts without fences never
> ends: goal, stories, criteria, non-goals — before any code. Fields match
> the spec-* CLI (goal, story, non-goal, criterion, task).

- **Title**: <short name>
- **Goal**: <one sentence, observable from outside>
- **Non-goals**: <explicitly NOT doing — as important as the goal>
- **Opened**: <YYYY-MM-DD>

## User stories

| ID | Story |
|----|-------|
| US1 | As a <role> I want <capability> so that <benefit> |

## Acceptance criteria

| ID | Story | Criterion (observable) |
|----|-------|------------------------|
| AC1 | US1 | <what must be true to accept> |

## Tasks

| ID | Covers criterion | Task | Status |
|----|------------------|------|--------|
| T1 | AC1 | <implementation unit> | TODO / DONE |

## Coverage self-check

- Every criterion covered by ≥1 task? <yes/no>
- Dependency cycles among tasks? <no/list>
- Any task without a criterion? <no/list — that is scope creep>
