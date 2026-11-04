# Diagnostic Escalation Brief: {{SYMPTOM_TITLE}}

- **Project Root**: `{{PROJECT_ROOT}}`
- **Circuit Breaker Status**: `TRIPPED (2 Falsified Hypotheses)`

## Observed Symptom & Reproduction
- **Command / Action**: `{{REPRO_COMMAND}}`
- **Exact Error / Traceback**:
```text
{{ERROR_OUTPUT}}
```

## Falsified Hypotheses Ledger
| ID | Hypothesis Statement | Testable Prediction | Command Run | Observed Evidence (Why Falsified) |
|---|---|---|---|---|
| `H1` | {{H1_STATEMENT}} | {{H1_PREDICTION}} | `{{H1_CMD}}` | {{H1_EVIDENCE}} |
| `H2` | {{H2_STATEMENT}} | {{H2_PREDICTION}} | `{{H2_CMD}}` | {{H2_EVIDENCE}} |

## Scoped Files Inspected
- `{{FILE_1}}` (lines {{LINES_1}})
- `{{FILE_2}}` (lines {{LINES_2}})

## What Is Needed to Unblock
- {{MISSING_TELEMETRY_OR_USER_DECISION}}
