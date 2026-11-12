---
name: code-review
description: Structured, severity-graded review of files, diffs or PRs the user names; records every finding with location, category and suggestion in a ledger, and renders a report whose verdict is FAIL while any BLOCKING finding is open; use when asked to review code, a pull request, a diff or specific files before merge.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Code Review

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Review named code with findings that have locations, severities and suggestions — and a verdict that refuses to pass while a BLOCKING finding is open.

## When to use

- The user asks for a review of files, a PR, a diff range or a module.
- A change is about to merge and needs a structured pass.

Do NOT use for opinions about pasted snippets with no files (`local-advisor --mode code-review`), and do not use it to re-lint what CI already lints — findings should be things CI cannot see.

## Workflow

1. **Declare the review's target and focus:**

   ```bash
   $WB review-init --title "Billing export PR #142" \
     --target "PR #142: src/billing/export.py, src/billing/serializers.py, tests/test_export.py" \
     --focus correctness --focus error-handling
   ```

   Read only what the target names. Widening scope is a new review, not a drift.

2. **Inspect the target** (with `scope-read`, inside the project root) and work through `references/review-checklist.md` per focus area.

3. **Record findings as you go:**

   ```bash
   $WB review-finding --file src/billing/export.py --line 42 \
     --severity BLOCKING --category correctness \
     --description "Totals are rounded per line before tax is applied, losing cents on 3+ line invoices" \
     --suggestion "Apply tax before rounding in _line_total(); add a test with 3 x 3.35 lines"
   ```

   Severity definitions are in `references/severity-model.md`; the runtime deduplicates exact repeats. Every finding needs a location and a description a stranger could act on.

4. **Render and deliver:**

   ```bash
   $WB review-report --not-reviewed "Did not inspect the migration or the frontend consumer"
   ```

   The verdict is deterministic: **FAIL** while any BLOCKING finding is open; **PASS_WITH_FINDINGS** with majors/minors; **PASS** when clean. The report includes counts by severity, the findings sorted worst-first, and the severity model for the reader.

5. **After fixes**, re-review the changed lines and record new findings — do not edit old ones into closure. A re-run that renders PASS closes the loop; `delivery-verify` proves the fix commands.

## Guardrails

- **Severity honesty**: BLOCKING means incorrect, insecure or data-losing. Inflating severity to force a fix erodes the verdict's meaning; deflating to be polite is worse.
- **Scope discipline**: findings outside the declared target are out of review — note them in `--not-reviewed` or start another review.
- **Not-reviewed is part of the verdict**: a PASS that silently skipped the migration is a false PASS. Declare the perimeter.
- **Suggestions are cheap, findings are expensive**: a finding says what is wrong and why it matters; the suggestion says the smallest good fix. Do not pad findings with style noise.

## Commands

| Command | Purpose |
|---|---|
| `review-init` | Start the ledger: title, target, focus |
| `review-finding` | Record a located, severity-graded finding |
| `review-report` | Render counts + verdict + findings + perimeter |

## Output expectation

A rendered REVIEW.md with a deterministic verdict, every finding actionable from its location, and an honest perimeter of what was not reviewed.

## References

- `references/severity-model.md` — BLOCKING/MAJOR/MINOR/INFO definitions with examples.
- `references/review-checklist.md` — the per-category checklists (correctness, security, performance, maintainability, tests).

## Example

- `examples/pr-review.md` — a review with one BLOCKING, one MAJOR and one INFO finding, and its FAIL verdict.
