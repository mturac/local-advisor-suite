---
name: decision-review
description: Structured decision making with a weighted criteria matrix, hard-constraint disqualification, sensitivity analysis, reversibility classes R0-R3, pre-mortem and numbered ADRs; use when the user must choose between named options, wants a trade-off matrix, asks for an ADR, or wants to check a recorded decision.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Decision Review

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Turn a choice between options into a reproducible decision: criteria with weights, hard constraints that disqualify, a sensitivity check that says how fragile the winner is, and an ADR that survives review.

## When to use

- The user must choose between 2+ named options (technologies, architectures, vendors, build-vs-buy).
- The user asks for a trade-off matrix, a decision record, or a pre-mortem.
- A recorded decision needs checking (`adr-check`) before it is accepted.

Do NOT use when the choice hinges on verifiable external facts you have not gathered — run `web-search`/`deep-research` for those facts first, then come back and score.

## Workflow

1. **Elicit criteria and options.** From the conversation, list 3-6 criteria (what "good" means for this user) and the options. Weights start at 1-5. Mark any criterion with a `min_score` if falling below it disqualifies an option outright.

2. **Write the spec file** (see `templates/decision-spec.json`):

   ```json
   {
     "title": "Queue for background jobs",
     "criteria": [
       {"id": "ops", "weight": 3, "min_score": 4},
       {"id": "throughput", "weight": 2},
       {"id": "license", "weight": 1, "min_score": 5}
     ],
     "options": [
       {"name": "Postgres queue", "scores": {"ops": 7, "throughput": 5, "license": 8}, "risks": ["poll latency"]},
       {"name": "Redis streams", "scores": {"ops": 5, "throughput": 8, "license": 7}, "risks": ["one more system to run"]}
     ]
   }
   ```

3. **Score it.**

   ```bash
   $WB decision-score --spec-file decision.json --output .local-workbench/decision_result.json
   ```

   Read the output: `recommended_option`, `ranked_options` (with disqualifications), and the `sensitivity` block (margin, robustness, weight flips, score flips). Unknown scores are treated as neutral 5.0 and listed in `warnings` — research them before committing.

4. **Interrogate the sensitivity.** If `robustness` is `fragile` or the margin is under 0.5, the recommendation is an assumption, not a conclusion. Verify the flip-point criteria with the user or with research, then re-score.

5. **Record the ADR.**

   ```bash
   $WB adr-new --title "Use a Postgres queue" --dir docs/adr --owner "@platform" \
     --decision-result .local-workbench/decision_result.json
   $WB adr-check --file docs/adr/0001-use-a-postgres-queue.md
   ```

   Fill every placeholder the ADR reports (`placeholders_left`), write the steelman counter-argument honestly, state the reversibility class (R0-R3, see `references/reversibility-classes.md`), and complete the pre-mortem. Re-run `adr-check` until PASS.

6. **Close the loop.** The rollback trigger in the ADR should name an observable signal. When that signal fires in a later session, re-open the ADR instead of silently drifting.

## Guardrails

- Scores are judgments; make them explainable. If you cannot justify a score in one sentence, it is not a score, it is noise.
- Never adjust weights to make a preferred option win. The sensitivity block exists to expose exactly that.
- A disqualified option stays disqualified: hard constraints are not preferences.
- An ADR without a steelman counter-argument and a rollback trigger fails `adr-check` for a reason — do not pad those sections with boilerplate.

## Commands

| Command | Purpose |
|---|---|
| `decision-score` | Weighted scoring, hard-constraint disqualification, sensitivity analysis |
| `adr-new` | Create the next numbered ADR from the template, pre-filled from a decision result |
| `adr-check` | Validate sections, R0-R3 class, option rows and unfilled placeholders |

## Output expectation

A ranked matrix with the winner, its fragility, and a PASS-ing ADR. The reader should be able to reconstruct the decision, and to know under what conditions to revisit it.

## References

- `references/scoring-guide.md` — how to pick criteria, weights and min_scores; how to read flips.
- `references/reversibility-classes.md` — R0-R3 definitions with examples and reversal costs.
- `templates/decision-spec.json` — annotated spec skeleton.
- `templates/adr.md` — the ADR template `adr-new` instantiates.

## Example

- `examples/postgres-vs-redis.md` — a full scored decision with sensitivity and the generated ADR.
