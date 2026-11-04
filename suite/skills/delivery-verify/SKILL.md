---
name: delivery-verify
description: Proves delivery with observable evidence on an L0-L4 ladder before any "done" claim; runs the real commands, records exit codes and durations, snapshots git HEAD, and reports the achieved level with allowed wording per level; use before claiming work is finished, fixed or tested.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.0.0"
---

# Delivery Verify

Replace "done" with evidence. `verify-delivery` runs the commands you declare, records what passed, and computes the honest verification level — L0 (claimed) through L4 (acceptance-verified).

## When to use

- Before claiming any task, fix or feature is complete.
- At the end of a spec task (`spec-builder` tasks reference criteria — verify at L3+).
- After a fix from `local-debug`, to prove the repro now passes.
- Whenever the user asks "does it actually work?"

## The ladder

| Level | Meaning | Allowed wording |
|---|---|---|
| L0 | Nothing observable was checked | "changed, not verified" |
| L1 | Artifact exists and is non-empty | "written, not executed" |
| L2 | Static checks pass (compile, lint, type-check, build) | "compiles; tests not run" |
| L3 | Real execution passed (tests, program exit 0) | "tests pass" |
| L4 | The user's acceptance criterion checked | "your case now works" |

Never use wording above the level you observed. "Fixed" is an L3+ word; "your case now works" is an L4 sentence, earned only by running the user's own scenario.

## Workflow

1. **Declare artifacts and checks:**

   ```bash
   $WB verify-delivery \
     --artifact src/app.py --artifact tests/test_app.py \
     --check "L2:python3 -m py_compile src/app.py" \
     --check "L3:python3 -m pytest -q tests/test_app.py" \
     --check "L4:python3 -c \"from app import total; assert total([1.01,2.02])==3.03\"" \
     --require L3
   ```

   - `--artifact` = L1 evidence: files that must exist and be non-empty.
   - `--check "L2:cmd"` / `--check "L3:cmd"` / `--check "L4:cmd"` = levelled commands; `--command` still works and counts as L3 (v2.1 compatibility).
   - `--require L3` fails the verification unless L3 is achieved.

2. **Read the record.** The JSON carries: each command with exit code, duration, timed-out flag and output previews; the achieved level; `levels_not_checked`; git HEAD and dirty state — the snapshot of exactly what was verified.

3. **Report the level, not a feeling.** "L3: the test suite passes (12 passed, 3.4s). L4 not checked — your manual flow is the missing step." Declare what you did not run with `--not-run`.

4. **Timeouts are findings.** A hung command records exit 124 and `timed_out: true` and fails the level — that is a result, not an inconvenience.

## Guardrails

- **Declare what you run, run what you declare.** The record is the evidence; a check that was not declared did not happen.
- **No level skipping claims**: L2 passing says nothing about L3. Say both.
- **Nothing to verify is L0.** Calling `verify-delivery` with no artifacts and no commands errors with `NOTHING_TO_VERIFY` — a delivery with no observable check is a claim, and the tool refuses to bless it.
- **Verification is point-in-time.** The git snapshot says which code was verified; after further edits, re-verify.

## Commands

| Command | Purpose |
|---|---|
| `verify-delivery` | Run declared checks, compute the L0-L4 level, snapshot git, write the record |

## Output expectation

A verification record with the achieved level, per-command evidence, what was not checked, and delivery wording that matches the level exactly.

## References

- `references/level-selection.md` — how to choose checks per level for different deliverable types (code, documents, configs, data).

## Example

- `examples/verify-fix.md` — a bugfix verified L1 through L3, with an explicit L4 gap.
