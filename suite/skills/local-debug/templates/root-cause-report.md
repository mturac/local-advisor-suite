# Root-Cause Report — <SYMPTOM>

> Skeleton for the local-debug skill. Hypotheses are recorded, not muttered:
> each one carries a prediction and is confirmed or falsified with evidence.
> Fields match the debug-hypothesis CLI (symptom, statement, prediction,
  test-command, status, evidence).

- **Symptom**: <what is observably wrong, one sentence>
- **Target file**: <path>
- **Repro**: <exact command that shows the symptom>
- **Date**: <YYYY-MM-DD>

## Hypotheses

| ID | Statement | Prediction | Test command | Status | Evidence |
|----|-----------|------------|--------------|--------|----------|
| H1 | <suspected cause> | <what must be true if H1 holds> | `<command>` | OPEN / PENDING / CONFIRMED / FALSIFIED | <what the test showed> |

Status meanings: **OPEN** recorded, not yet sharpened · **PENDING** has a
prediction, test not run · **CONFIRMED** evidence supports it ·
**FALSIFIED** evidence refutes it (still valuable — a closed path).

## Root cause

<the confirmed hypothesis, stated as a sentence with its evidence chain:
input → X → Y → observed symptom>

## Fix applied

<what was changed, in one or two sentences>

## Open risks

- <inputs/cases the fix was not exercised with>
