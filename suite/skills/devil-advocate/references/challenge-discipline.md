# Challenge Discipline — What Makes an Attack Fair and a Verdict Meaningful

The point of this skill is not to perform skepticism; it is to find the ways a plan
dies **before** resources are spent on it. These rules keep the exercise honest in
both directions — no strawmen to knock down, no drive-by cynicism.

## 1. Steelman before you attack

- `devil-open` refuses a steelman under 30 characters for a reason: the attack is
  only meaningful against the plan's **best case**, stated as its own advocates
  would state it.
- If you cannot write the steelman convincingly, you do not understand the plan
  well enough to attack it. Say so and ask before challenging.

## 2. Attack assumptions, not adjectives

- Every challenge names the **load-bearing assumption** it attacks: the belief
  that, if false, makes the plan collapse. "The migration assumes zero downtime
  is achievable with dual writes" — not "the migration seems risky".
- Surface complaints (naming, folder structure, tone) are MINOR at best. A
  challenge that survives is about something the plan *depends on*.

## 3. Every attack names its defeater

- The `--defeater` field is the observation or argument that would prove the
  attack wrong. This keeps attacks falsifiable and gives the verdict's guards
  something concrete to watch later.
- An attack with no possible defeater is not analysis — it is dogma, and the
  command rejects it.

## 4. Severity is a claim, spend it honestly

- **FATAL**: if this stands unanswered, the plan in its current shape should not
  proceed. Reserve it for attacks on foundations (feasibility, legality, the
  premise itself). A session that finds five FATALs usually means the plan was
  never examined, or the challenger is inflating.
- **SERIOUS**: the plan can proceed only with a guard — a watched assumption
  with a defined signal.
- **MINOR**: real but cheap to fix or unlikely to matter; recorded, not gated.

## 5. Rebuttals must engage

- A rebuttal answers the *argument* ("here is the profile that shows cold-start
  is the bottleneck"), not the tone ("we considered that").
- Name the basis: `evidence` (a measurement, a source), `experience` (a directly
  comparable past run), `constraint` (the plan was already revised to remove it).
  The basis is what lets a reader later judge whether the answer has aged.
- Answering your own challenge to clear the count is worse than leaving it open:
  an open challenge is at least visible in the verdict.

## 6. The verdict is mechanical, kill criteria are not optional

- The gate does no arithmetic on eloquence: one open FATAL → BLOCK, any open
  SERIOUS → PROCEED_WITH_GUARDS, everything answered → PROCEED. Exit code 2 on
  BLOCK — scripts and hosts can rely on it.
- A verdict without `--kill-criterion` is refused. A kill criterion is an
  **observable** signal, pre-committed while the challenge session is still
  fresh, that would falsify the plan later ("p95 cold-start above 300ms after
  week 2", not "if things go badly").
- Guards and kill criteria are the part of this session that survives into
  delivery: put them in the ADR's rollback trigger or the spec's acceptance
  criteria. A challenge session whose verdict nobody can check later was
  entertainment.
