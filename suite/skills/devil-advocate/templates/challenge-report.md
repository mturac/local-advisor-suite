# Devil's Advocate Verdict — <CLAIM IN ONE LINE>

> Skeleton for the devil-advocate skill. The verdict is mechanical: BLOCK while
> a FATAL challenge stands, PROCEED_WITH_GUARDS while a SERIOUS one does,
> PROCEED only when every attack is answered. Fields match the devil-plan /
> devil-open / devil-premortem / devil-outside / devil-challenge /
> devil-consequence / devil-rebuttal / devil-verdict CLI.

- **Claim under attack**: <the plan/decision/spec, in one sentence>
- **Plan archetype**: <build | launch | migrate | hire | buy | process>
- **Date**: <YYYY-MM-DD>

## The steelman (the plan's best case, stated honestly)

<The plan's best case as its advocates would state it — no strawmen here;
the challenge is only meaningful against this.>

## Premortem (it is 12 months later and the plan failed)

<The failure story, past tense, concrete — then the named causes, each
specific enough that someone could check whether it is already forming.>

- <cause 1>
- <cause 2>

## Outside view (the reference class, before the plan's own story)

- **Reference class**: <who else has tried something like this, named by the
  similarity that matters for the outcome>
- **Base rate**: <X>% of them succeed.
- **Inside-view adjustment**: <why this attempt differs — or "none", which
  auto-opens an optimism-bias challenge that must be rebutted like any other>

## Second-order effects (and then what?)

1. L1 <what the effect directly causes> → L2 <what that causes once people
   and systems react> → L3 <what that world causes; optional>

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
