# The Computation Ledger — No Number Without a Method

The data ledger (`.local-workbench/data_ledger.json`) is the contract between what you computed and what you claim. The report renderer only trusts it.

## Finding anatomy

A finding is `{id, statement, method, result, created_at}`:

- **statement** — what was observed, in plain language, tied to the question ("The file has 5 data rows").
- **method** — the exact, re-runnable command, query or formula (`tail -n +2 sales.csv | wc -l`, `SELECT SUM(amount) FROM t WHERE status='paid'`, `mean(col) = sum/count with n=250`). The user must be able to paste it and get the same number.
- **result** — the measured value(s), exactly as observed, with their units.

## Rules

1. **Compute, then log, then report.** Never write a number into `--answer` that does not appear in some finding's statement or result. `data-report` enforces this mechanically (`UNLEDGERED_NUMBERS`) — the escape hatch `--allow-unverified-numbers` exists, but using it means the report ships with a visible UNVERIFIED warning; prefer logging the finding instead.
2. **One finding, one number family.** A finding whose result is "120 and 170" should come from a method that really printed both (e.g. first and last value). Do not bundle numbers from different commands.
3. **Show the units and the denominator.** "45%" is not a result; "45% (9 of 20 paid invoices)" is. The percentage-of-what must be reconstructible from the method.
4. **Rounding is a method step.** State it inside the method ("rounded to 2 decimals with ROUND(x,2)") and stay consistent between findings and answer.
5. **Derived numbers need their formula.** Growth rates, deltas, per-month averages: the method is the formula plus its inputs (`(170-120)/120 = 41.6% increase from first to last month`).
6. **Counts that exclude rows must say so.** If you filtered (missing values, a status, a date window), the filter belongs in the method, and the excluded-row count is itself a finding.
7. **Drift is fatal until re-registered.** If the file changed after registration, `data-finding` refuses (`DATASET_DRIFT`); re-run `data-register` on the same path to refresh the hash, then redo the affected findings. Numbers computed on the old content must not survive silently into a report on the new content.

## What the report guarantees

`data-report` renders `ANALYSIS.md` containing only: the registered question, the pinned dataset identity (path, bytes, SHA-256 prefix), the answer, the findings table (every method re-runnable), and the declared gaps. A reader who distrusts a number can re-run its method; a number with no method row does not exist.
