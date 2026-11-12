# Devil's Advocate Verdict — <CLAIM IN ONE LINE>

> Skeleton for the devil-advocate skill. The verdict is mechanical: BLOCK while
> a FATAL challenge stands, PROCEED_WITH_GUARDS while a SERIOUS one does,
> PROCEED only when every attack is answered. Fields match the devil-open /
> devil-challenge / devil-rebuttal / devil-verdict CLI (claim, steelman,
> assumption, attack, category, severity, defeater, rebuttal, basis, kill
> criteria).

- **Claim under attack**: <the plan/decision/spec, in one sentence>
- **Date**: <YYYY-MM-DD>

## The steelman (the plan's best case, stated honestly)

<The plan's best case as its advocates would state it — no strawmen here;
the challenge is only meaningful against this.>

## Verdict: <BLOCK | PROCEED_WITH_GUARDS | PROCEED>

<One sentence on what the gate saw: how many FATAL / SERIOUS / MINOR stand
open, how many were answered. For PROCEED_WITH_GUARDS, name the first guard
signal that would stop the plan.>

## Challenges

| ID | Assumption attacked | Attack | Category | Severity | Status |
|---|---|---|---|---|---|
| C1 | <the load-bearing belief> | <what specifically breaks, and why> | <category> | <severity> | <OPEN / ANSWERED> |
| C2 | ... | ... | ... | ... | ... |

## Answered challenges

### C1 — answered on the basis of <evidence | experience | constraint>

> Attack: <the attack, quoted>

Rebuttal: <the answer that engages the argument, and the basis it rests on>

## Guards (open SERIOUS challenges)

| Challenge | Guard: assumption to watch | Signal: what defeats the attack |
|---|---|---|
| C2 | <the assumption> | <the defeater, as an observable signal> |

## Kill criteria (pre-committed, observable)

1. <observable signal that would falsify the plan — decided now, checked later>
2. <...>

## Where this verdict goes next

- [ ] BLOCK: the FATAL challenges went back into the plan (not into softer wording)
- [ ] Guards copied into the delivery checklist or spec acceptance criteria
- [ ] Kill criteria copied into the ADR rollback trigger or the spec
