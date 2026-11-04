# A five-month sales trend, computed and traceable

A real run over `sales.csv` (month, sales — 2026-01 to 2026-05). The dataset is
pinned by hash first; every number in the final answer comes from a logged
finding whose method the user can re-run; what the file cannot answer becomes
an explicit gap.

```bash
$ python3 scripts/workbench.py data-register --path sales.csv \
  --question "What is the monthly sales trend in this file?"
```

```json
{
  "status": "OK",
  "dataset": {
    "path": "sales.csv",
    "bytes": 72,
    "sha256": "a5289da978c9db43d66ceff99ace993fa6c61cd74ade4674f64d655d2f4b302b",
    "registered_at": "2026-11-04T14:34:35+00:00"
  },
  "question": "What is the monthly sales trend in this file?",
  "findings_reset": false,
  "content_drift": false,
  "findings_count": 0,
  "warning": ""
}
```

Profiling first: how many data rows actually exist.

```bash
$ python3 scripts/workbench.py data-finding \
  --statement "The file has 5 data rows, one per month from 2026-01 to 2026-05" \
  --method 'tail -n +2 sales.csv | wc -l' --result "5 rows"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F1",
    "statement": "The file has 5 data rows, one per month from 2026-01 to 2026-05",
    "method": "tail -n +2 sales.csv | wc -l",
    "result": "5 rows",
    "created_at": "2026-11-04T14:34:35+00:00"
  },
  "findings_count": 1
}
```

The endpoints of the series, with the command that printed them:

```bash
$ python3 scripts/workbench.py data-finding \
  --statement "Monthly sales start at 120 and end at 170" \
  --method "cut -d, -f2 sales.csv | tail -n +2 | sed -n '1p;$p'" --result "120 and 170"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F2",
    "statement": "Monthly sales start at 120 and end at 170",
    "method": "cut -d, -f2 sales.csv | tail -n +2 | sed -n '1p;$p'",
    "result": "120 and 170",
    "created_at": "2026-11-04T14:34:35+00:00"
  },
  "findings_count": 2
}
```

A derived number needs its formula in the method, not just the outcome:

```bash
$ python3 scripts/workbench.py data-finding \
  --statement "Sales increased by 41.6 percent from first to last month" \
  --method '(170-120)/120*100 = 41.66, rounded to one decimal' --result "41.6 percent"
```

```json
{
  "status": "OK",
  "finding": {
    "id": "F3",
    "statement": "Sales increased by 41.6 percent from first to last month",
    "method": "(170-120)/120*100 = 41.66, rounded to one decimal",
    "result": "41.6 percent",
    "created_at": "2026-11-04T14:34:35+00:00"
  },
  "findings_count": 3
}
```

The user also asked about regions; the file cannot answer that, so it goes on
the record as a gap instead of being guessed:

```bash
$ python3 scripts/workbench.py data-gap \
  --description "Per-region breakdown is not computable from this file" \
  --reason "NO_DATA: the file has no region column"
```

```json
{
  "status": "OK",
  "gap": {
    "id": "G1",
    "description": "Per-region breakdown is not computable from this file",
    "reason": "NO_DATA: the file has no region column",
    "created_at": "2026-11-04T14:34:36+00:00"
  },
  "gaps_count": 1
}
```

Finally the report. The answer names only ledgered numbers — trying to sneak in
an unlogged figure would fail with `UNLEDGERED_NUMBERS` before the file renders.

```bash
$ python3 scripts/workbench.py data-report \
  --answer "Sales rose from 120 to 170 across 5 months, a 41.6 percent increase; the region split cannot be computed from this file."
```

```json
{
  "status": "OK",
  "report": ".local-workbench/ANALYSIS.md",
  "findings_count": 3,
  "gaps_count": 1,
  "dataset_drift": false,
  "contains_unverified_numbers": false,
  "unverified_numbers": []
}
```

Rendered `ANALYSIS.md`:

```markdown
# Data Analysis Report

**Question**: What is the monthly sales trend in this file?
**Dataset**: `sales.csv` (72 bytes, SHA-256 `a5289da978c9db43...`)
**Findings**: 3 | **Gaps**: 1

## Answer

Sales rose from 120 to 170 across 5 months, a 41.6 percent increase; the
region split cannot be computed from this file.

## Findings

| ID | Finding | Method (re-runnable) | Result |
|---|---|---|---|
| F1 | The file has 5 data rows, one per month from 2026-01 to 2026-05 | `tail -n +2 sales.csv \| wc -l` | 5 rows |
| F2 | Monthly sales start at 120 and end at 170 | `cut -d, -f2 sales.csv \| tail -n +2 \| sed -n '1p;$p'` | 120 and 170 |
| F3 | Sales increased by 41.6 percent from first to last month | `(170-120)/120*100 = 41.66, rounded to one decimal` | 41.6 percent |

## Declared gaps

| ID | What could not be computed | Reason |
|---|---|---|
| G1 | Per-region breakdown is not computable from this file | NO_DATA: the file has no region column |
```
