# ADR-{{NUMBER}}: {{TITLE}}

- **Date**: {{DATE}}
- **Status**: {{PROPOSED_ACCEPTED_SUPERSEDED}}
- **Decision Owner**: {{OWNER}}

## Context & Problem Statement
{{PROBLEM_STATEMENT}}

## Hard Constraints & Non-Goals
- **Hard Constraints**:
  - {{CONSTRAINT_1}}
  - {{CONSTRAINT_2}}
- **Non-Goals**:
  - {{NON_GOAL_1}}

## Evaluated Options
| Option | Weighted Score | Disqualified? | Key Strength | Primary Risk |
|---|---:|---|---|---|
| {{OPTION_A}} | {{SCORE_A}} | {{DISQ_A}} | {{STRENGTH_A}} | {{RISK_A}} |
| {{OPTION_B}} | {{SCORE_B}} | {{DISQ_B}} | {{STRENGTH_B}} | {{RISK_B}} |

## Decision
We choose **{{SELECTED_OPTION}}** because {{RATIONALE}}.

## Steelman Counter-Argument (Why This Could Be Wrong)
{{STEELMAN_COUNTERARGUMENT}}

## Reversibility
- **Class**: {{R0_R1_R2_R3}} (R0 trivial undo, R1 cheap undo within a sprint, R2 costly migration, R3 effectively irreversible)
- **Cost to reverse**: {{REVERSAL_COST}}
- **Point of no return**: {{POINT_OF_NO_RETURN}}

## Pre-mortem
Assume it is 12 months later and this decision failed. The most likely causes:
1. {{FAILURE_MODE_1}} - early signal: {{SIGNAL_1}} - mitigation: {{MITIGATION_1}}
2. {{FAILURE_MODE_2}} - early signal: {{SIGNAL_2}} - mitigation: {{MITIGATION_2}}

## Operational Consequences & Rollback Trigger
- **Positive**: {{POSITIVE_CONSEQUENCES}}
- **Negative / Trade-offs**: {{NEGATIVE_CONSEQUENCES}}
- **Reversal Trigger**: Re-evaluate this decision if {{REVERSAL_CONDITION}}.
