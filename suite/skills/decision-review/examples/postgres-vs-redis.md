# A scored decision with sensitivity and an ADR

A full decision: the spec file, the scored result with its sensitivity block, and the ADR generated from it. Scores in this example are illustrative judgments, not researched facts — a real decision researches them first.

```bash
$ python3 scripts/workbench.py decision-score --spec-file decision.json --output .local-workbench/decision_result.json
```

```json
{
  "status": "OK",
  "title": "Queue for background jobs",
  "recommended_option": "Managed cloud queue",
  "ranked_options": [
    {
      "name": "Managed cloud queue",
      "weighted_score": 7.75,
      "disqualified": false,
      "disqualification_reasons": [],
      "unknown_criteria": [],
      "breakdown": {
        "ops": {
          "raw": 8,
          "normalized_weight": 0.375,
          "weighted_contribution": 3.0
        },
        "throughput": {
          "raw": 7,
          "normalized_weight": 0.25,
          "weighted_contribution": 1.75
        },
        "durability": {
          "raw": 8,
          "normalized_weight": 0.375,
          "weighted_contribution": 3.0
        }
      },
      "risks": [
        "vendor lock-in"
      ]
    },
    {
      "name": "Postgres queue",
      "weighted_score": 6.875,
      "disqualified": false,
      "disqualification_reasons": [],
      "unknown_criteria": [],
      "breakdown": {
        "ops": {
          "raw": 7,
          "normalized_weight": 0.375,
          "weighted_contribution": 2.625
        },
        "throughput": {
          "raw": 5,
          "normalized_weight": 0.25,
          "weighted_contribution": 1.25
        },
        "durability": {
          "raw": 8,
          "normalized_weight": 0.375,
          "weighted_contribution": 3.0
        }
      },
      "risks": [
        "poll latency up to 5s"
      ]
    },
    {
      "name": "Redis streams",
      "weighted_score": 5.75,
      "disqualified": false,
      "disqualification_reasons": [],
      "unknown_criteria": [],
      "breakdown": {
        "ops": {
          "raw": 4,
          "normalized_weight": 0.375,
          "weighted_contribution": 1.5
        },
        "throughput": {
          "raw": 8,
          "normalized_weight": 0.25,
          "weighted_contribution": 2.0
        },
        "durability": {
          "raw": 6,
          "normalized_weight": 0.375,
          "weighted_contribution": 2.25
        }
      },
      "risks": [
        "one more stateful system"
      ]
    }
  ],
  "evaluated_at": "2026-11-04T09:52:19+00:00",
  "sensitivity": {
    "winner": "Managed cloud queue",
    "margin": 0.875,
    "robustness": "robust",
    "weight_flips": [],
    "score_flips": [],
    "warnings": []
  }
}
```

Read the sensitivity block before the winner: the margin and the flip points say how much of this decision is assumption. `unknown` scores are listed in `warnings` — research them before committing.

```bash
$ python3 scripts/workbench.py adr-new --title "Use a Postgres queue" --dir docs/adr \
  --owner "@platform" --decision-result .local-workbench/decision_result.json
```

```json
{
  "status": "OK",
  "adr": "docs/adr/0001-use-a-postgres-queue.md",
  "number": "0001",
  "placeholders_left": [
    "CONSTRAINT_1",
    "CONSTRAINT_2",
    "FAILURE_MODE_1",
    "FAILURE_MODE_2",
    "MITIGATION_1",
    "MITIGATION_2",
    "NEGATIVE_CONSEQUENCES",
    "NON_GOAL_1",
    "POINT_OF_NO_RETURN",
    "POSITIVE_CONSEQUENCES",
    "PROBLEM_STATEMENT",
    "R0_R1_R2_R3",
    "RATIONALE",
    "REVERSAL_CONDITION",
    "REVERSAL_COST",
    "SIGNAL_1",
    "SIGNAL_2",
    "STEELMAN_COUNTERARGUMENT",
    "STRENGTH"
  ]
}
```

The ADR is pre-filled from the decision result; `placeholders_left` is the debt list. Fill every placeholder (rationale, steelman, reversibility class R0-R3, pre-mortem), then check it.

```bash
$ python3 scripts/workbench.py adr-check --file docs/adr/0001-use-a-postgres-queue.md
```

```json
{
  "status": "FAIL",
  "file": "docs/adr/0001-use-a-postgres-queue.md",
  "problems": [
    "unfilled placeholders: CONSTRAINT_1, CONSTRAINT_2, FAILURE_MODE_1, FAILURE_MODE_2, MITIGATION_1, MITIGATION_2, NEGATIVE_CONSEQUENCES, NON_GOAL_1, POINT_OF_NO_RETURN, POSITIVE_CONSEQUENCES, PROBLEM_STATEMENT, R0_R1_R2_R3, RATIONALE, REVERSAL_CONDITION, REVERSAL_COST, SIGNAL_1, SIGNAL_2, STEELMAN_COUNTERARGUMENT, STRENGTH"
  ]
}
```

This check ran against the freshly generated ADR, so it correctly reports the unfilled placeholders. After filling them in (and writing an honest steelman and rollback trigger), the same command returns PASS.

