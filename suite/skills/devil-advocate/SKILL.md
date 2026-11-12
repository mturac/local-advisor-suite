---
name: devil-advocate
description: Adversarial stress-test of a plan, decision or spec before commitment — steelman the plan honestly, run the premortem (write the failure story before it happens), take the outside view (reference class + base rate, with an automatic optimism-bias challenge), attack load-bearing assumptions in archetype order with severity-graded challenges that each name their defeater, map second-order effects three levels deep, answer what can be answered, and let the unanswered attacks decide a mechanical verdict (BLOCK / PROCEED_WITH_GUARDS / PROCEED) with guards and pre-committed kill criteria; use for devil's advocate, what could go wrong, poke holes, second opinion, premortem, şeytanın avukatı, stres testi.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.5.0"
---

# Devil's Advocate

Argue the other side of the user's plan — systematically, on the record, and fairly. The plan gets an honest steelman, its own failure story written in advance, the base rate of everyone who tried the same thing, and severity-graded attacks on its load-bearing assumptions. The unanswered attacks decide the verdict mechanically. This is not "be negative": it is the cheapest point in time to discover the plan is wrong, and every protocol here exists because it catches a failure mode that generic skepticism misses.

## When to use

- The user has a plan, approach, decision or spec they are about to commit to, and asks "what could go wrong", "poke holes in this", "challenge this plan", "run a premortem", "şeytanın avukatlığını yap".
- A spec passed `spec-check`, a decision passed `decision-score`, or an ADR is drafted — and the user wants the adversarial pass before committing.
- The user is too excited: "this is perfect", "too good to be true" energy deserves a challenge session before it becomes an implementation.

Do NOT use when:

- The user must choose between named options — that is `decision-review` (score, then come back here to attack the winner).
- The user wants a draft's sources and claims checked — that is `evidence-audit`.
- The user asks for code defects in named files — that is `code-review`. This skill attacks plans, not code.
- There is no plan yet, only a topic — run `local-advisor` or `deep-research` first.

## Workflow

1. **Get the attack plan for this kind of plan.** Building, launching, migrating, hiring, buying and process changes fail differently; attack in the order that plan type actually breaks:
   `$WB devil-plan --archetype build|launch|migrate|hire|buy|process`
   Returns the attack order (e.g. a migration dies on rollback-path first, not on features), the premortem prompts, the reference class to look up and archetype kill signals. Works before the session opens.

2. **Open the session and steelman first.** State the claim under attack and its best case honestly — an attack on a strawman is worthless:
   `$WB devil-open --claim "the plan in one sentence" --steelman "its best case, stated honestly"`

3. **Run the premortem before the challenges.** It is 12 months later and the plan has failed — write the story. This is not a mood exercise: assuming failure already happened is the only reliably proven way to get people to surface doubts they are politely withholding:
   `$WB devil-premortem --failure-story "..." --cause "..." --cause "..."`
   Concrete, past tense, named causes specific enough that someone could go check whether they are already forming. Turn each cause into a challenge (or an answer).

4. **Take the outside view.** Find the reference class — everyone who has tried something like this — and its base rate, before trusting the plan's own story:
   `$WB devil-outside --reference-class "..." --base-rate 30 --adjustment "none"`
   A base rate of 50% or worse with no argued adjustment auto-opens a SERIOUS optimism-bias challenge: "this case beats the reference class" is now an assumption under attack, not a free premise.

5. **Attack load-bearing assumptions, in archetype order, not surface details.** For each attack say what specifically breaks and what observation would defeat the attack:
   `$WB devil-challenge --assumption "..." --attack "..." --category unfounded-assumption --severity SERIOUS --defeater "..."`
   Pick the category from `references/attack-categories.md`; `FATAL` means "if this stands, the plan dies" — reserve it.

6. **Map second-order effects for the top risks.** First-order thinking stops at the intended effect; the interesting failures live one and two levels later:
   `$WB devil-consequence --l1 "what the effect causes" --l2 "what that causes" --l3 "what that causes in turn"`
   Any level with no owner becomes a challenge (`--category second-order-effect`).

7. **Answer what can be answered.** A sound rebuttal takes a challenge out of the verdict; record what it rests on (evidence, experience, constraint):
   `$WB devil-rebuttal --id C1 --rebuttal "..." --basis "evidence: ..."`
   Do not rebut to clear the count — a rebuttal that waves at the argument is worse than silence.

8. **Let the gate decide, with kill criteria.** Name the observable signal that would falsify the plan later — pre-committed, before enthusiasm returns:
   `$WB devil-verdict --kill-criterion "..." --kill-criterion "..."`
   `BLOCK` while a FATAL challenge stands (exit 2); `PROCEED_WITH_GUARDS` while a SERIOUS one does; `PROCEED` only when every attack is answered. Renders `CHALLENGE.md` with the premortem, the outside view, the consequence chains, guards and kill criteria.

9. **Feed the verdict forward.** A BLOCK goes back into the plan, not into softer wording. Guards become things to watch in delivery; kill criteria go into the ADR's rollback trigger or the spec's acceptance criteria.

## Stop rules

- Never proceed over a BLOCK — answer the FATAL challenge or change the plan.
- No verdict without a premortem on record: the session can still close (the v3.3 contract stands), but the report will carry `premortem_missing` and the next session should fix the habit.
- An attack with no defeater is dogma, not criticism; a rebuttal with no basis is theater, not an answer.
- If every challenge is answered instantly and comfortably, you challenged a strawman — go back to step 5 and find the assumption the plan actually depends on.

## Commands

| Command | Purpose |
|---|---|
| `devil-plan` | Archetype attack plan: what to attack first, premortem prompts, reference class, kill signals |
| `devil-open` | Open the session: claim under attack + honest steelman |
| `devil-premortem` | The failure story, written before the challenges |
| `devil-outside` | Reference class + base rate; auto-flags optimism bias |
| `devil-challenge` | Attack a load-bearing assumption (category, severity, defeater) |
| `devil-consequence` | L1 → L2 → L3 "and then what?" chain for a top risk |
| `devil-rebuttal` | Answer an open challenge; a sound rebuttal exits the verdict |
| `devil-verdict` | Mechanical gate: BLOCK / PROCEED_WITH_GUARDS / PROCEED + kill criteria, renders CHALLENGE.md |

## Files

- `references/challenge-discipline.md` — the rules that make an attack fair and a verdict meaningful.
- `references/attack-categories.md` — the eight attack categories, with what evidence answers each.
- `references/premortem-protocol.md` — how to write a failure story that actually surfaces doubts.
- `references/outside-view.md` — how to pick the reference class and argue (or refuse) an adjustment.
- `references/second-order-effects.md` — the "and then what?" discipline, with worked chains.
- `references/falsification.md` — kill criteria that are observable, and the ones that are theater.
- `templates/challenge-report.md` — fillable verdict skeleton (same fields the CLI emits).
- `examples/monolith-to-microservices.md` — a real run: open, four challenges, one rebuttal, verdict.
- `examples/premortem-tool-adoption.md` — a full protocol run: plan, premortem, outside view, consequences, verdict.
