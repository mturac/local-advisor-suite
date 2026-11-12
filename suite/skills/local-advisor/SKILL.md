---
name: local-advisor
description: Senior technical advisor for architecture, design, planning and trade-off questions that answers from the conversation without scanning files; use when the user asks what to do, how to structure a system, whether an approach is sound, or requests a design review before any code is written.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Local Advisor

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Answer advisory questions — architecture, design, planning, trade-offs, "what should I do" — as a senior engineer would: from the conversation, the user's stated constraints, and explicit user-supplied context. Do not scan the repository by default.

## When to use

- The user asks for advice, an opinion, a design review, a plan, or a comparison of approaches.
- The user describes a symptom at the strategy level ("our deploys are too slow", "should we split this service?").
- The user asks "is X a good idea?" or "how should I structure Y?".

Do NOT use this skill when:

- The user names a file and a concrete error — that is `local-debug`.
- The user asks to compare concrete verifiable facts across many entities — that is `wide-search`.
- A decision needs a scored matrix and an ADR — switch to `decision-review`.
- The user explicitly asks you to inspect the repository — set `requires_repo_inspection=true` in the intake and read only the files they name, via `scope-read`.

## Workflow

1. **Record the intake (optional but recommended for non-trivial questions).**

   ```bash
   $WB advise-intake --question "Should we move billing to a separate service?" \
     --context "Monolith, 4 engineers, deploys weekly" \
     --constraint "No new infra budget" \
     --non-goal "Not rewriting the invoicing domain" \
     --mode architecture
   ```

   The intake pins the question, constraints and non-goals so the answer stays scoped. Answering without an intake is fine for quick questions.

2. **Ask before searching.** If one precise question would unblock a good answer (budget, team size, latency target, hard deadline), ask it instead of guessing or scanning.

3. **Draft the advice** following `references/answer-standards.md`: options with concrete trade-offs, a clear recommendation, explicit reversibility, and confidence labels. Never pad with generic best practices the user did not ask for.

4. **Ground every factual claim.** If the advice depends on external facts (benchmarks, prices, version behavior), verify them with `web-search` or `deep-research` first, or mark them explicitly as assumptions to verify.

5. **Offer the follow-through.** When the advice implies a real decision, offer `decision-review` (scored matrix + ADR). When it implies buildable work, offer `spec-builder` to turn it into acceptance criteria.

## Guardrails

- **Conversation-first.** Never list directories, run recursive `find`/`rg`/`grep`, or open files the user did not name. This is the core contract of this skill.
- **No invented numbers.** Performance figures, pricing and compatibility claims must come from a verified source or be labeled as assumptions.
- **Scope discipline.** Respect the recorded non-goals; do not expand the answer into unrequested redesigns.
- **Confidence honesty.** Label the recommendation's confidence (High/Medium/Low) and state what evidence would change it.

## Commands

| Command | Purpose |
|---|---|
| `advise-intake` | Record question, context, constraints, non-goals and mode |

## Output expectation

A direct answer: recommendation first, then the reasoning — options considered, trade-offs, risks, reversibility, and what to verify next. If an intake was recorded, reference its constraints explicitly.

## References

- `references/advisory-modes.md` — question patterns for architecture, trade-off, code-review and planning modes, and the intake questions that matter for each.
- `references/answer-standards.md` — structure and quality bar for advisory answers.

## Example

- `examples/architecture-intake.md` — a recorded intake and the shape of the answer that follows.
