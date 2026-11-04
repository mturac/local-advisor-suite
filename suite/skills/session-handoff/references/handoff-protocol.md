# Handoff Protocol

## The seven sections and what belongs in each

1. **Objective & Current State** — the task in one paragraph and where it stands. Written for a reader with zero context from the session.
2. **Completed Work** — checkable items ("Export endpoint implemented and verified L3"), not effort reports ("worked on the export").
3. **Pending Next Steps** — concrete, startable actions. "Add pagination for >10k invoices" can be picked up; "improve export" cannot.
4. **Active Blockers & Constraints** — what stops progress and what would unblock it. Name the missing thing precisely (which credential, whose decision, which environment).
5. **Evidence & Verification Snapshot** — auto-generated from the ledgers. Never hand-edit it; if it is wrong, the ledger is wrong and that is the real problem.
6. **Decisions & Open Questions** — decisions with their rationale (or ADR reference), questions with what would answer them.
7. **Resume Instructions** — the protocol: check, read, trust-by-level, resume at first unchecked item.

## Status semantics

- **DONE** — everything verified at the declared level; next steps empty is legitimate.
- **PARTIAL** — progress exists; next steps MUST be non-empty (the check enforces this).
- **BLOCKED** — a blocker is stopping everything; name it and the unblock condition.

## Cross-host resume

The handoff is host-neutral: written by Claude Code, resumed by Codex or ZCode. Practical implications:

- Paths in the handoff are project-relative, never host-specific. `scripts/workbench.py` inside the skill directory, not `/Users/x/.claude/...`.
- The WB runtime path differs per host (`.claude/skills/local-advisor/scripts/workbench.py` vs `.agents/skills/...` vs `.zcode/skills/...` vs `.cursor/skills/...`). The handoff references commands as `$WB <command>` and the resuming host resolves `$WB` from its own rules block (`AGENTS.md`/`CLAUDE.md`/`.cursor/rules`).
- `.local-workbench/` is shared state: it lives in the project, so every host reads the same ledgers. Do not delete it between hosts; do keep it out of version control.

## Staleness and drift

`handoff-check` warns when:

- **Age > 72h** (default, `--max-age-hours`): the world moved. Re-verify the state section before building on the handoff.
- **Git HEAD moved**: someone committed after the handoff was written. Read the diff before assuming the completed section still holds — the fix you were told is done may have been reverted or broken.

A warning is not a failure: it is an instruction to look before leaping.

## Packing etiquette

- Pack before you think you need to — sessions end abruptly. A stale-but-valid handoff beats memory.
- One handoff per state dir; repacking overwrites. If parallel work streams need separate handoffs, give them separate `--state-dir` values from the start.
- After packing, run the check. An unvalidated handoff is a draft, and you will not be there to explain it.
