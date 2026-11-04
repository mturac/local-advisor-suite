# From failing test to root-cause report

A real case: an invoice total mismatch. The first hypothesis is falsified by a one-line prediction test; the second is confirmed. Both are in the ledger — the falsification is part of the record.

```bash
$ python3 scripts/workbench.py debug-hypothesis \
  --symptom "test_total: 10.05 != 10.06 (1 failure)" \
  --target-file billing/invoice.py \
  --repro "pytest -q tests/test_invoice.py::test_total"
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/debug_ledger.json",
  "case_recorded": true,
  "symptom": "test_total: 10.05 != 10.06 (1 failure)",
  "target_files": [
    "billing/invoice.py"
  ],
  "repro_command": "pytest -q tests/test_invoice.py::test_total",
  "next_action": "Run the repro, read the target with scope-read --debug-scope, then log H1 with --status PENDING.",
  "failed_attempts": 0,
  "circuit_breaker_tripped": false
}
```

The case is recorded before anything is read or changed. `--target-file` scopes every later `scope-read --debug-scope` to this file.

```bash
$ python3 scripts/workbench.py debug-hypothesis --id H1 --status PENDING \
  --statement "Totals are rounded per line before summing" \
  --prediction "If true, round(3.35, 2) * 3 returns 10.05 while the test expects 10.06" \
  --test-command "python3 -c 'print(round(3.35, 2) * 3)'"
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/debug_ledger.json",
  "target_files": [
    "billing/invoice.py"
  ],
  "next_action": "Run the test command, then record CONFIRMED or FALSIFIED with --evidence.",
  "failed_attempts": 0,
  "circuit_breaker_tripped": false,
  "active_hypothesis": {
    "id": "H1",
    "statement": "Totals are rounded per line before summing",
    "prediction": "If true, round(3.35, 2) * 3 returns 10.05 while the test expects 10.06",
    "test_command": "python3 -c 'print(round(3.35, 2) * 3)'",
    "status": "PENDING",
    "evidence": "",
    "updated_at": "2026-11-04T09:52:19+00:00"
  }
}
```

The prediction is numeric on purpose: it can fail. A prediction that cannot fail is not a prediction.

```bash
$ python3 scripts/workbench.py debug-hypothesis --id H1 --status FALSIFIED \
  --evidence "round(3.35, 2) * 3 = 10.05 matches the observed value, but the failing fixture has a single line, so per-line rounding cannot produce the observed 10.05 on one line"
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/debug_ledger.json",
  "target_files": [
    "billing/invoice.py"
  ],
  "next_action": "Run the test command, then record CONFIRMED or FALSIFIED with --evidence.",
  "failed_attempts": 1,
  "circuit_breaker_tripped": false,
  "active_hypothesis": {
    "id": "H1",
    "statement": "Totals are rounded per line before summing",
    "prediction": "If true, round(3.35, 2) * 3 returns 10.05 while the test expects 10.06",
    "test_command": "python3 -c 'print(round(3.35, 2) * 3)'",
    "status": "FALSIFIED",
    "evidence": "round(3.35, 2) * 3 = 10.05 matches the observed value, but the failing fixture has a single line, so per-line rounding cannot produce the observed 10.05 on one line",
    "updated_at": "2026-11-04T09:52:19+00:00"
  }
}
```

One strike. The evidence explains *why* the hypothesis is dead — the next reader does not re-run it.

```bash
$ python3 scripts/workbench.py debug-hypothesis --id H2 --status PENDING \
  --statement "Tax is applied after the total is rounded to 2 decimals" \
  --prediction "If true, applying tax after rounding a 10.05 subtotal yields 10.05, not the expected 10.06" \
  --test-command "python3 -c 'print(round(10.05 + 10.05 * 0.006, 2))'"
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/debug_ledger.json",
  "target_files": [
    "billing/invoice.py"
  ],
  "next_action": "Run the test command, then record CONFIRMED or FALSIFIED with --evidence.",
  "failed_attempts": 1,
  "circuit_breaker_tripped": false,
  "active_hypothesis": {
    "id": "H2",
    "statement": "Tax is applied after the total is rounded to 2 decimals",
    "prediction": "If true, applying tax after rounding a 10.05 subtotal yields 10.05, not the expected 10.06",
    "test_command": "python3 -c 'print(round(10.05 + 10.05 * 0.006, 2))'",
    "status": "PENDING",
    "evidence": "",
    "updated_at": "2026-11-04T09:52:19+00:00"
  }
}
```

Second hypothesis, informed by the first one's failure — not a blind second guess.

```bash
$ python3 scripts/workbench.py debug-hypothesis --id H2 --status CONFIRMED \
  --evidence "Order of operations in _line_total(): round(subtotal, 2) happens before tax is added, losing the tax fraction"
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/debug_ledger.json",
  "target_files": [
    "billing/invoice.py"
  ],
  "next_action": "Run the test command, then record CONFIRMED or FALSIFIED with --evidence.",
  "failed_attempts": 1,
  "circuit_breaker_tripped": false,
  "active_hypothesis": {
    "id": "H2",
    "statement": "Tax is applied after the total is rounded to 2 decimals",
    "prediction": "If true, applying tax after rounding a 10.05 subtotal yields 10.05, not the expected 10.06",
    "test_command": "python3 -c 'print(round(10.05 + 10.05 * 0.006, 2))'",
    "status": "CONFIRMED",
    "evidence": "Order of operations in _line_total(): round(subtotal, 2) happens before tax is added, losing the tax fraction",
    "updated_at": "2026-11-04T09:52:19+00:00"
  }
}
```

Confirmed — the root cause is a mechanism, not a vibe. Only now is a fix designed.

```bash
$ python3 scripts/workbench.py debug-report \
  --fix "Apply tax before rounding in _line_total()" \
  --open-risk "Did not check credit notes, which use a different total path"
```

```json
{
  "status": "OK",
  "report": ".local-workbench/DEBUG_REPORT.md",
  "root_cause_confirmed": true,
  "circuit_breaker_tripped": false
}
```

The report distinguishes what was fixed from what was not checked. The fix claim is then proven separately with `delivery-verify --check "L3:pytest -q tests/test_invoice.py::test_total"`.

