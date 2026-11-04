---
name: session-handoff
description: Packs session state into a validated handoff document so the next session, agent or human resumes without loss; includes git HEAD, verification level, decisions, open questions and resume instructions, then validates the file before relying on it; use when ending a session, switching between Claude Code, Codex, ZCode, Cursor or OpenCode, or resuming someone else's work.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.0.0"
---

# Session Handoff

End a session by leaving a complete, validated state behind; resume a session by trusting that state exactly as far as its verification level allows.

## When to use

- **Packing**: the session is ending, switching hosts or tools, or delegating to another agent.
- **Resuming**: you are picking up work described by a HANDOFF.md.
- **Checking**: a handoff exists and you want to know if it is still trustworthy (age, git drift).

## Workflow — packing

1. **Pack with the facts, not a narrative:**

   ```bash
   $WB handoff-pack --title "Billing export v1" --session-status PARTIAL \
     --summary "CSV export implemented for invoices; tax-before-rounding fixed; acceptance criteria AC1-AC2 verified" \
     --completed "Export endpoint implemented" --completed "Rounding fix verified at L3" \
     --next-step "Add pagination for >10k invoices" --next-step "Run the accountant's manual flow (L4)" \
     --blocker "Staging credentials missing" \
     --decision "Tax applied per line before totals" \
     --open-question "Do credit notes need a separate export?"
   ```

   The pack automatically snapshots the research ledger, debug ledger and last verification level — sections 5 of the handoff reflects what the ledgers actually say, not what you remember.

2. **Validate before relying on it:**

   ```bash
   $WB handoff-check
   ```

   The check verifies all seven required sections are present and non-empty, that a PARTIAL/BLOCKED session has next steps, and warns on staleness and git drift.

3. **Deliver the handoff** with the session's final message: status, level, and where HANDOFF.md lives.

## Workflow — resuming

1. **Check first, trust second:**

   ```bash
   $WB handoff-check --file .local-workbench/HANDOFF.md
   ```

   Warnings are instructions: an old handoff means re-verify state; git HEAD moved means read the diff before anything else.

2. **Read HANDOFF.md completely.** Section 5 (Evidence & Verification Snapshot) sets your trust level: completed work is trusted only up to the recorded verification level — an L1 task was written, not run.

3. **Resume at the first unchecked item in section 3.** Do not redo section 2; that is the point of the handoff.

4. **Re-verify what the warnings flagged** before building on top of it.

## Guardrails

- **Status honesty**: PARTIAL means next steps exist; BLOCKED means blockers are named. DONE with empty sections fails the check.
- **Trust is level-bound**: never treat a completed item as more verified than the recorded level.
- **The ledgers are the source of truth**: if your summary and the ledger disagree, the ledger wins — fix the summary.
- **Handoffs rot**: `handoff-check` warns past 72h (configurable); re-verify rather than assume.

## Commands

| Command | Purpose |
|---|---|
| `handoff-pack` | Write HANDOFF.md from arguments + ledger state + git HEAD |
| `handoff-check` | Validate structure, status consistency, staleness, git drift |

## Output expectation

A HANDOFF.md that passes `handoff-check`, whose Evidence section matches the ledgers, and whose next steps are concrete enough to start without questions.

## References

- `references/handoff-protocol.md` — what belongs in each section, and cross-host resume specifics.
- `references/state-inventory.md` — every file in `.local-workbench/` and what it is for.

## Example

- `examples/partial-session.md` — a real PARTIAL pack and its check.
