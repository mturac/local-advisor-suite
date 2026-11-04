# A review with a BLOCKING finding and a FAIL verdict

Three findings at three severities, rendered into a report whose verdict is FAIL while the BLOCKING finding is open.

```bash
$ python3 scripts/workbench.py review-init --title "Billing export PR #142" \
  --target "PR #142: src/billing/export.py, tests/test_export.py" \
  --focus correctness --focus tests
```

```json
{
  "status": "OK",
  "review_path": ".local-workbench/review_ledger.json",
  "target": "PR #142: src/billing/export.py, tests/test_export.py",
  "next_action": "Inspect only the declared target. Record findings with review-finding --file ... --description ..."
}
```

```bash
$ python3 scripts/workbench.py review-finding --file src/billing/export.py --line 42 \
  --severity BLOCKING --category correctness \
  --description "Totals are rounded per line before tax is applied, losing cents on multi-line invoices" \
  --suggestion "Apply tax before rounding in _line_total(); add a test with 3 x 3.35 lines"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F1",
    "file": "src/billing/export.py",
    "line": 42,
    "severity": "BLOCKING",
    "category": "correctness",
    "description": "Totals are rounded per line before tax is applied, losing cents on multi-line invoices",
    "suggestion": "Apply tax before rounding in _line_total(); add a test with 3 x 3.35 lines",
    "created_at": "2026-11-04T09:52:23+00:00"
  },
  "open_blocking": 1,
  "next_action": "Fix BLOCKING findings before any delivery claim."
}
```

```bash
$ python3 scripts/workbench.py review-finding --file tests/test_export.py \
  --severity MAJOR --category tests \
  --description "No test covers the changed rounding order; the existing test asserts the buggy value" \
  --suggestion "Update test_total to expect 10.06 and add a multi-line case"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F2",
    "file": "tests/test_export.py",
    "line": null,
    "severity": "MAJOR",
    "category": "tests",
    "description": "No test covers the changed rounding order; the existing test asserts the buggy value",
    "suggestion": "Update test_total to expect 10.06 and add a multi-line case",
    "created_at": "2026-11-04T09:52:23+00:00"
  },
  "open_blocking": 1,
  "next_action": "Fix BLOCKING findings before any delivery claim."
}
```

```bash
$ python3 scripts/workbench.py review-finding --file src/billing/export.py --line 87 \
  --severity INFO --category maintainability \
  --description "The CSV escaping helper mirrors utils/csv_escape.py; consider importing it instead"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F3",
    "file": "src/billing/export.py",
    "line": 87,
    "severity": "INFO",
    "category": "maintainability",
    "description": "The CSV escaping helper mirrors utils/csv_escape.py; consider importing it instead",
    "suggestion": "",
    "created_at": "2026-11-04T09:52:23+00:00"
  },
  "open_blocking": 1,
  "next_action": "Fix BLOCKING findings before any delivery claim."
}
```

```bash
$ python3 scripts/workbench.py review-report \
  --not-reviewed "Did not inspect the migration or the frontend consumer"
```

```json
{
  "status": "FAIL",
  "verdict": "FAIL",
  "counts": {
    "BLOCKING": 1,
    "MAJOR": 1,
    "MINOR": 0,
    "INFO": 1
  },
  "findings_count": 3,
  "report": ".local-workbench/REVIEW.md"
}
```

The verdict is FAIL, mechanically, because a BLOCKING finding is open. After the fix lands, re-review the changed lines and record a fresh report; the new PASS closes the loop, with `delivery-verify` proving the fix commands.

