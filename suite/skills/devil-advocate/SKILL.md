---
name: devil-advocate
description: Adversarial stress-test of a plan, decision or spec before commitment — steelman the plan honestly, attack its load-bearing assumptions with severity-graded challenges that each name their defeater, answer what can be answered with rebuttals, and let the unanswered attacks decide a mechanical verdict (BLOCK / PROCEED_WITH_GUARDS / PROCEED) with guards and pre-committed kill criteria; use for devil's advocate, what could go wrong, poke holes, second opinion, şeytanın avukatı, stres testi.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.3.0"
---

# Devil's Advocate

Argue the other side of the user's plan — systematically, on the record, and fairly. The plan gets an honest steelman, its load-bearing assumptions get attacked with severities, every attack names what would defeat it, and the unanswered attacks decide the verdict mechanically.

## When to use

- The user has a plan, approach, decision or spec they are about to commit to, and asks "what could go wrong", "poke holes in this", "challenge this plan", "şeytanın avukatlığını yap".
- A spec passed `spec-check`, a decision passed `decision-score`, or an ADR is drafted — and the user wants the adversarial pass before committing.
- The user is too excited: "this is perfect", "too good to be true" energy deserves a challenge session before it becomes an implementation.

Do NOT use when:

- The user must choose between named options — that is `decision-review` (score, then come back here to attack the winner).
- The user wants a draft's sources and claims checked — that is `evidence-audit`.
- The user asks for code defects in named files — that is `code-review`. This skill attacks plans, not code.
- There is no plan yet, only a topic — run `local-advisor` or `deep-research` first.

## Workflow

1. **Open the session and steelman first.** State the claim under attack and its best case honestly — an attack on a strawman is worthless:
   `$WB devil-open --claim "the plan in one sentence" --steelman "its best case, stated honestly"`
2. **Attack load-bearing assumptions, not surface details.** For each attack say what specifically breaks and what observation would defeat the attack:
   `$WB devil-challenge --assumption "..." --attack "..." --category unfounded-assumption --severity SERIOUS --defeater "..."`
   Pick the category from `references/attack-categories.md`; `FATAL` means "if this stands, the plan dies" — reserve it.
3. **Answer what can be answered.** A sound rebuttal takes a challenge out of the verdict; record what it rests on (evidence, experience, constraint):
   `$WB devil-rebuttal --id C1 --rebuttal "..." --basis "evidence: ..."`
   Do not rebut to clear the count — a rebuttal that waves at the argument is worse than silence.
4. **Let the gate decide, with kill criteria.** Name the observable signal that would falsify the plan later — pre-committed, before enthusiasm returns:
   `$WB devil-verdict --kill-criterion "..." --kill-criterion "..."`
   `BLOCK` while a FATAL challenge stands (exit 2); `PROCEED_WITH_GUARDS` while a SERIOUS one does; `PROCEED` only when every attack is answered. Writes `CHALLENGE.md`.
5. **Feed the verdict forward.** A BLOCK goes back into the plan, not into softer wording. Guards become things to watch in delivery; kill criteria go into the ADR's rollback trigger or the spec's acceptance criteria.

## Stop rules

- Never proceed over a BLOCK — answer the FATAL challenge or change the plan.
- An attack with no defeater is dogma, not criticism; a rebuttal with no basis is theater, not an answer.
- If every challenge is answered instantly and comfortably, you challenged a strawman — go back to step 2 and find the assumption the plan actually depends on.

## Commands

| Command | Purpose |
|---|---|
| `devil-open` | Open the session: claim under attack + honest steelman |
| `devil-challenge` | Attack a load-bearing assumption (category, severity, defeater) |
| `devil-rebuttal` | Answer an open challenge; a sound rebuttal exits the verdict |
| `devil-verdict` | Mechanical gate: BLOCK / PROCEED_WITH_GUARDS / PROCEED + kill criteria, renders CHALLENGE.md |

## Files

- `references/challenge-discipline.md` — the rules that make an attack fair and a verdict meaningful.
- `references/attack-categories.md` — the eight attack categories, with what evidence answers each.
- `templates/challenge-report.md` — fillable verdict skeleton (same fields the CLI emits).
- `examples/monolith-to-microservices.md` — a real run: open, four challenges, one rebuttal, verdict.
