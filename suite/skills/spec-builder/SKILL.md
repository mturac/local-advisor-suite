---
name: spec-builder
description: Turns a request into a testable specification; records the goal and user stories, adds Given/When/Then acceptance criteria, breaks work into tasks that must each verify at least one criterion, and validates coverage before implementation starts; use when the user describes something to build, wants requirements made testable, or asks for acceptance criteria or a task breakdown.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.0.0"
---

# Spec Builder

Convert "we need X" into a specification where every story has testable acceptance criteria and every task in the plan verifies at least one of them. If it cannot be tested, it does not ship.

## When to use

- The user describes a feature, change or integration to build.
- Requirements exist but are vague ("make export fast", "support big files") and need to become testable.
- A plan needs a task breakdown where done is definable.

Do NOT use for decisions between options (`decision-review` first, then spec the chosen option), or for pure research questions (`deep-research`).

## Workflow

1. **Start the spec from the goal, stories and non-goals:**

   ```bash
   $WB spec-new \
     --goal "Ship a verified CSV export of invoices for enterprise accountants" \
     --story "As an accountant I export all unpaid invoices to CSV so I can reconcile in my ledger tool" \
     --story "As an auditor I export a date-ranged invoice history for a fiscal year" \
     --non-goal "No PDF export in v1" \
     --non-goal "No scheduled/recurring exports"
   ```

   The goal states the outcome, not the activity. Non-goals are half the spec: they are what you will say "no" to mid-project.

2. **Write acceptance criteria in Given/When/Then:**

   ```bash
   $WB spec-criterion --story-id US1 \
     --given "an account with 3 unpaid invoices totaling 10.06" \
     --when "the accountant runs the CSV export" \
     --then "the CSV contains exactly 3 rows, one header row, and the total column sums to 10.06"
   ```

   Rules for good criteria are in `references/acceptance-criteria.md`: observable outcomes, real numbers, no implementation details, no "works correctly".

3. **Break into tasks that verify criteria:**

   ```bash
   $WB spec-task --task "Implement the CSV serialization with per-line escaping" --verifies AC1
   $WB spec-task --task "Add pagination to the invoice query for large accounts" --verifies AC1 --depends-on T1
   $WB spec-task --task "Add the date-range filter to the export endpoint" --verifies AC2 --depends-on T1
   ```

   A task without `--verifies` is rejected (`TASK_NOT_VERIFIABLE`): work that verifies nothing does not belong in the plan. Dependencies must reference existing tasks; cycles are caught by the check.

4. **Gate before implementation:**

   ```bash
   $WB spec-check
   ```

   PASS requires: goal >= 20 chars, every story has criteria, every criterion has complete GWT clauses, no dependency cycles. Warnings name criteria with no implementing task and missing non-goals. Fix until PASS — implementation before a PASS-ing spec is building against a moving target.

5. **Deliver per task, verify per criterion.** While implementing, each completed task gets proven with `delivery-verify` (L3 or better for code). The spec's criterion IDs are the shared language: task T1 claims done by pointing at AC1's observable outcome.

6. **Change control.** Mid-project discoveries change the spec openly: add criteria (`spec-criterion`), add tasks, or restart with `spec-new --force` when the goal itself moved. Silent scope drift is how specs die.

## Guardrails

- **Testability over completeness.** Three sharp criteria beat ten vague ones.
- **No implementation in criteria.** "The CSV contains 3 rows" is a criterion; "using a streaming serializer" is a design decision.
- **Numbers are owed.** "Large accounts" is not a criterion; ">10k invoices" is.
- **The check is the gate.** `spec-check` PASS is the entry condition for implementation and the exit condition for claiming the spec done.

## Commands

| Command | Purpose |
|---|---|
| `spec-new` | Start the ledger: goal, stories, non-goals |
| `spec-criterion` | Add a Given/When/Then criterion to a story |
| `spec-task` | Add a task bound to the criteria it verifies |
| `spec-check` | Validate completeness and coverage; the gate |

## Output expectation

A PASS-ing spec ledger (goal, stories with GWT criteria, verifying tasks) that `delivery-verify` and `session-handoff` can reference criterion-by-criterion.

## References

- `references/acceptance-criteria.md` — GWT writing rules, testability checklist, anti-patterns.
- `references/task-breakdown.md` — task sizing, dependency hygiene, verification binding.

## Example

- `examples/billing-export.md` — a spec from goal to PASS-ing check with two stories and three criteria.
