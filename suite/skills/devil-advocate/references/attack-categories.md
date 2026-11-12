# Attack Categories — Where Plans Hide Their Weakness

Eight categories, ordered roughly by how often they kill plans in practice. For
each: what the attack sounds like, and what evidence answers it.

## 1. unfounded-assumption

The plan rests on a belief nobody verified.

- Attack: "Nobody on the team has shipped this stack; the schedule assumes a
  learning curve we don't have."
- Defeater: two team members show shipped projects on that stack.
- Answered by: `experience` (a directly comparable past run) or revising the
  plan's estimates. Hand-waving ("we'll learn it") does not answer it.

## 2. missing-evidence

A load-bearing claim has no source or measurement behind it.

- Attack: "The 40% conversion lift is quoted from a blog post; no experiment in
  our own traffic supports it."
- Defeater: an A/B run, even small, showing the lift on this product's audience.
- Answered by: `evidence` — run `web-search`/`deep-research` for external
  evidence or `data-analysis` for internal measurement. If neither can produce
  it, the claim must shrink or the challenge stands.

## 3. second-order-effect

The immediate effect is fine; the follow-on is not.

- Attack: "Free tier cuts support load today, but attracts automated signups
  that raise it 3x by month three."
- Defeater: cohort data from a comparable product showing free-tier support
  load stays flat after week 6.
- Answered by: `evidence` or a guard with an explicit signal (support tickets
  per free signup above N).

## 4. alternative-explanation

The same observations support a different conclusion.

- Attack: "Sales rose after the redesign — and after the price cut, and after
  the competitor's outage. The redesign takes credit for all three."
- Defeater: a segment where only the redesign changed and the lift still shows.
- Answered by: `evidence` (a separated measurement) or honest downgrading of
  the claim's strength in the plan.

## 5. cost-complexity

The plan is possible but costs more than claimed — in money, focus or
maintenance surface.

- Attack: "Running three regional clusters is feasible; the claim that ops
  overhead stays 'roughly the same' is not."
- Defeater: a runbook comparison from a team already doing it showing overhead
  within 20% of single-cluster.
- Answered by: revised numbers in the plan (then it stops being an attack) or
  `evidence` from comparable setups.

## 6. reversibility

Once done, undoing it is slow, expensive or impossible.

- Attack: "Migrating customer data into the vendor's proprietary format makes
  the exit cost scale with adoption — the exact wrong direction."
- Defeater: a documented, tested export path that restores the current format.
- Answered by: `evidence` (an actual export test) or an R-class downgrade in the
  decision record (see `decision-review`'s reversibility classes).

## 7. timing

Right plan, wrong moment.

- Attack: "The framework's threading model is still behind a flag; building on
  it now means tracking breaking changes weekly."
- Defeater: a stable release announcement with a committed date inside the
  project's window.
- Answered by: `evidence` (release notes, roadmap commits) or an explicit wait
  decision.

## 8. external-risk

Success depends on a party or event outside your control.

- Attack: "The whole integration depends on the partner's undocumented
  endpoint, which changed twice last quarter."
- Defeater: a signed support commitment or a contract with an SLA.
- Answered by: `evidence` (the contract exists) or a fallback path in the plan
  that removes the dependency.

---

**When you run out of attacks**: the fastest way to find more is to reread the
steelman and ask, sentence by sentence, "says who?" — every answer that is not
already on the record is either an assumption to attack or evidence to gather.
