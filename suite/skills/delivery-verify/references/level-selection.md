# Choosing Checks per Level

How to pick `--check` commands so the recorded level means what it says. The rule: a level's checks must fail if the deliverable is broken at that level.

## Code

| Level | Good checks | Why |
|---|---|---|
| L1 | `--artifact src/app.py` (and every file you claim to have written) | Existence and non-emptiness. |
| L2 | `py_compile` / `tsc --noEmit` / `gofmt -l` / `ruff check` / build command | Catches syntax, type and build breakage without execution. Pick the project's own toolchain. |
| L3 | The project's test command, the smallest command that exercises the changed path, the repro command from `local-debug` | Real execution, exit 0. Prefer the narrow test over the full suite when the full suite is slow — and say which ran. |
| L4 | The user's own scenario: the exact input they reported, the script they run, the curl they care about | Acceptance is the user's criterion, not yours. |

## Documents and reports

| Level | Checks |
|---|---|
| L1 | `--artifact report.md` |
| L2 | A structural check: `grep -c "^##" report.md` behind a level that fails on wrong counts, or the audit command `L2:python3 scripts/workbench.py audit-report --report-file report.md` (exit 0 on PASS) |
| L3 | For generated artifacts, the generation command re-run idempotently; for analyses, the computation command re-run |
| L4 | The user's acceptance: the number they asked to know, present and cited |

## Configuration and infrastructure

| Level | Checks |
|---|---|
| L1 | `--artifact deploy.yaml` |
| L2 | `L2:<the validator>` — `kubeconform`, `terraform validate`, the schema check |
| L3 | A dry-run that executes the toolchain (`terraform plan`, `helm template \| kubeconform -`) |
| L4 | Deployment to the real target, or the health check against it |

## Data processing

| Level | Checks |
|---|---|
| L1 | `--artifact output.csv` |
| L2 | Schema check: header row, column count (`L2:python3 -c "import csv;..."`) |
| L3 | Row counts / spot values matching the expectation, computed by a command not by your eyes |
| L4 | The consumer's check: the downstream report opens, the total matches the known control figure |

## Rules of thumb

- **Two or three checks, not twenty.** Each check should discriminate: if it cannot fail for a plausible mistake, it is decoration.
- **Fast at L2, real at L3.** L2 catches cheaply what L3 catches expensively; do not skip L2 on non-trivial code.
- **The repro is sacred.** If this delivery closes a debug case, the L3 check IS the recorded repro command — the one that used to fail.
- **Name the gap.** What you cannot check belongs in `--not-run` and in your report: "L4 not run: requires staging credentials".

## Reading a record later

The record's value is that a future reader (or `session-handoff`) can answer: which commands, on which code (git HEAD), with what outcomes, and which levels were never checked. If any of those four is ambiguous, the record was written wrong — declare more, assume less.
