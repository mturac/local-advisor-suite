---
name: local-debug
description: Scoped root-cause debugging for a bug in a file the user names; records the case, reads only the declared target files inside the project root, tests at most 2 hypotheses with predictions before editing, and writes a root-cause report or an escalation brief; use for failing tests, stack traces and reproducible errors.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Local Debug

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Debug a concrete, reproducible problem in a file the user named — with a ledger, a prediction-first discipline, and a hard stop after 2 falsified hypotheses.

## When to use

- A test fails, a stack trace exists, or a reproducible error occurs in code the user points at.
- The user asks "why does X break?" about a named file or module.

Do NOT use when:

- The problem is strategic ("our architecture is slow") — that is `local-advisor`.
- No file is named and no repro exists — ask for one before starting; do not go hunting.

## Workflow

1. **Record the case before touching anything.**

   ```bash
   $WB debug-hypothesis --symptom "test_total: 10.05 != 10.06 (2 failures)" \
     --target-file billing/invoice.py \
     --repro "pytest -q tests/test_invoice.py"
   ```

   `--target-file` is repeatable and files must be inside the project root. This is a scoping decision: `scope-read --debug-scope` refuses anything not on this list.

2. **Reproduce.** Run the repro command exactly as recorded. If it does not reproduce, the case record is wrong — fix the symptom or the repro first. A bug you cannot reproduce is a telemetry problem, not a code problem.

3. **Read the target — scoped.**

   ```bash
   $WB scope-read --project-root . --file billing/invoice.py --start-line 1 --end-line 120 --debug-scope
   ```

   Secrets, binary files, paths outside the root and symlink escapes are blocked by the runtime itself.

4. **Log exactly one hypothesis with a prediction.**

   ```bash
   $WB debug-hypothesis --id H1 --status PENDING \
     --statement "Totals are rounded per line before tax" \
     --prediction "If true, invoice with 3 x 3.35 lines totals 10.05 not 10.06" \
     --test-command "python3 -c 'print(round(3.35,2)*3)'"
   ```

   The prediction must say what you will observe **if the hypothesis is true** — a number, an output, a state. "The code is wrong somewhere" is not a hypothesis.

5. **Run the test, record the verdict with evidence.**

   ```bash
   $WB debug-hypothesis --id H1 --status FALSIFIED --evidence "round(3.35,2)*3 = 10.05; totals match the test expectation"
   ```

   Repeat from step 4 with the next hypothesis. **After 2 falsified hypotheses the circuit breaker trips** and the runtime refuses new PENDING hypotheses.

6. **Report.**

   ```bash
   $WB debug-report --fix "Apply tax before rounding in _line_total()" \
     --open-risk "Did not check credit notes path" \
     --needed ""
   ```

   With a confirmed hypothesis this renders a root-cause report; with the breaker tripped it renders an escalation brief for the user (see `references/escalation.md` for what belongs in it).

7. **Verify the fix** with `delivery-verify` (`--check L3:"<the repro command>"`). The debug report's claim of a fix is only as good as its verification level.

## Guardrails

- **Target scoping**: read only the recorded target files. Widening scope requires asking the user and adding the file with another `--target-file`.
- **Two strikes**: the circuit breaker is the point of this skill. When it trips, stop, summarize evidence, ask for the missing telemetry or decision. Escalation is a success, not a failure.
- **One hypothesis at a time**: no parallel guessing, no shotgun edits.
- **No fix without a confirmed hypothesis.** If you cannot state the root cause, you cannot claim the fix addresses it — say what you changed and at what verification level, nothing more.

## Commands

| Command | Purpose |
|---|---|
| `debug-hypothesis` | Record the case; add/update hypotheses; trip the breaker on the 2nd falsification |
| `scope-read --debug-scope` | Read a file inside the project root, restricted to declared debug targets |
| `scope-scan` | Bounded search inside the project root (pattern, glob, file cap) |
| `debug-report` | Render the root-cause report or the escalation brief |

## Output expectation

Either a root-cause report (confirmed hypothesis, evidence, fix, verification level) or an escalation brief (both falsified hypotheses with their evidence, what was tried, what is needed to unblock). Never a bare "fixed it".

## References

- `references/hypothesis-discipline.md` — what makes a hypothesis testable, and how to write predictions that can fail.
- `references/escalation.md` — the anatomy of a good escalation brief.

## Example

- `examples/invoice-rounding.md` — a real case from symptom to root-cause report, including a falsified first hypothesis.
