# From goal to a PASS-ing spec

A spec with two stories and three criteria, tasks bound to the criteria they verify, and the check that gates implementation.

```bash
$ python3 scripts/workbench.py spec-new \
  --goal "Ship a verified CSV export of invoices for enterprise accountants" \
  --story "As an accountant I export all unpaid invoices to CSV to reconcile in my ledger tool" \
  --story "As an auditor I export a date-ranged invoice history for a fiscal year" \
  --non-goal "No PDF export in v1"
```

```json
{
  "status": "OK",
  "spec_path": ".local-workbench/spec_ledger.json",
  "title": "Ship a verified CSV export of invoices for enterprise accountants",
  "stories": [
    "US1",
    "US2"
  ],
  "next_action": "Add testable acceptance criteria: spec-criterion --story-id US1 --given ... --when ... --then ..."
}
```

```bash
$ python3 scripts/workbench.py spec-criterion --story-id US1 \
  --given "an account with 3 unpaid invoices totaling 10.06" \
  --when "the accountant runs the CSV export" \
  --then "the CSV contains exactly 3 data rows and the total column sums to 10.06"
```

```json
{
  "status": "OK",
  "criterion": {
    "id": "AC1",
    "story_id": "US1",
    "given": "an account with 3 unpaid invoices totaling 10.06",
    "when": "the accountant runs the CSV export",
    "then": "the CSV contains exactly 3 data rows and the total column sums to 10.06"
  },
  "story": "US1",
  "criteria_in_story": 1,
  "next_action": "Keep adding criteria, then break the work down with spec-task --task ... --verifies AC1."
}
```

```bash
$ python3 scripts/workbench.py spec-criterion --story-id US1 \
  --given "an account with more than 10,000 unpaid invoices" \
  --when "the accountant runs the CSV export" \
  --then "the export completes without error and streams all rows without loading them into memory"
```

```json
{
  "status": "OK",
  "criterion": {
    "id": "AC2",
    "story_id": "US1",
    "given": "an account with more than 10,000 unpaid invoices",
    "when": "the accountant runs the CSV export",
    "then": "the export completes without error and streams all rows without loading them into memory"
  },
  "story": "US1",
  "criteria_in_story": 2,
  "next_action": "Keep adding criteria, then break the work down with spec-task --task ... --verifies AC1."
}
```

```bash
$ python3 scripts/workbench.py spec-criterion --story-id US2 \
  --given "the range 2024-01-01 to 2023-12-31 (end before start)" \
  --when "the auditor exports" \
  --then "the API returns status 422 with error code INVALID_RANGE and writes no file"
```

```json
{
  "status": "OK",
  "criterion": {
    "id": "AC3",
    "story_id": "US2",
    "given": "the range 2024-01-01 to 2023-12-31 (end before start)",
    "when": "the auditor exports",
    "then": "the API returns status 422 with error code INVALID_RANGE and writes no file"
  },
  "story": "US2",
  "criteria_in_story": 1,
  "next_action": "Keep adding criteria, then break the work down with spec-task --task ... --verifies AC1."
}
```

```bash
$ python3 scripts/workbench.py spec-task --task "Implement the CSV serialization with per-line escaping" --verifies AC1
```

```json
{
  "status": "OK",
  "task": {
    "id": "T1",
    "task": "Implement the CSV serialization with per-line escaping",
    "verifies": [
      "AC1"
    ],
    "depends_on": [],
    "created_at": "2026-11-04T09:52:22+00:00"
  },
  "next_action": "After implementing each task, prove it with verify-delivery and reference the criterion ID in the summary."
}
```

A task without `--verifies` is rejected with TASK_NOT_VERIFIABLE — work that verifies nothing does not belong in the plan.

```bash
$ python3 scripts/workbench.py spec-task --task "Add streaming pagination to the invoice query for large accounts" \
  --verifies AC2 --depends-on T1
```

```json
{
  "status": "OK",
  "task": {
    "id": "T2",
    "task": "Add streaming pagination to the invoice query for large accounts",
    "verifies": [
      "AC2"
    ],
    "depends_on": [
      "T1"
    ],
    "created_at": "2026-11-04T09:52:22+00:00"
  },
  "next_action": "After implementing each task, prove it with verify-delivery and reference the criterion ID in the summary."
}
```

Dependencies must reference existing tasks; the check catches cycles.

```bash
$ python3 scripts/workbench.py spec-check
```

```json
{
  "status": "PASS",
  "spec_path": ".local-workbench/spec_ledger.json",
  "problems": [],
  "warnings": [
    "criteria with no implementing task: AC3"
  ],
  "coverage": {
    "stories": 2,
    "criteria": 3,
    "tasks": 2,
    "covered_criteria": [
      "AC1",
      "AC2"
    ],
    "criteria_without_tasks": [
      "AC3"
    ]
  },
  "checked_at": "2026-11-04T09:52:22+00:00"
}
```

PASS is the implementation gate. The warning is honest: AC3 (the invalid-range criterion) has no implementing task yet — plan it or move it to a later spec deliberately.

