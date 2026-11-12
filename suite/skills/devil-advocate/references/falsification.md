# Falsification: Kill Criteria That Bite

A kill criterion is a signal, agreed in advance, that the plan has failed and
should be stopped or rolled back. Its entire value comes from being written
**before** the plan starts — while the plan is still a hypothesis and stopping
is still emotionally cheap. A kill criterion negotiated at the moment it fires
is not a criterion; it is a debate the plan will win, because by then the plan
has momentum, defenders and sunk costs.

## The test: observable, dated, owned

A kill criterion that cannot bite is theater. Each one must pass three checks:

1. **Observable.** It names a measurement anyone can read off reality, not a
   judgment call. "Adoption is disappointing" cannot bite. "Weekly active
   usage of the new tool is below 40% of the team at the 90-day review" can.
2. **Dated.** It has a deadline or a review moment, or it will be evaluated
   "soon" forever. "At the 90-day review", "after two consecutive sprints",
   "by the end of Q1".
3. **Owned.** Someone specific reads the signal and is empowered to act on
   it. An unowned criterion fires into the void and nothing happens.

## Good and bad, concretely

Bad: "if things get worse we will reconsider" — no observable, no date, no
owner; fires only in hindsight.

Bad: "if the migration has problems" — every migration has problems; this
criterion either never fires or always does.

Good: "if the parallel-run discrepancy exceeds 1% of revenue records at two
consecutive weekly checks, we halt the cutover and rehearse the rollback"
— observable, dated, and names the action.

Good: "if two consecutive retros identify the same part of the new process
as net-negative, that part reverts at the next retro, no reopening the
decision" — the bar, the moment and the action are all pinned.

## Where they come from

The best kill criteria fall out of the work you already did in this session:

- The **premortem causes** are candidate kill signals: each cause, made
  observable, is the early-warning version of the failure it names.
- The **archetype kill signals** from `devil-plan` are calibrated defaults
  per plan type (a migration's rollback rehearsal failing; a hire missing
  agreed 90-day deliverables with no recovery plan).
- The **unanswered SERIOUS challenges** become guards — their defeaters are
  literally "the observation that would prove this attack right", which is
  a kill criterion wearing different clothes.

## The commitment

Writing the criterion is half; honoring it is the other half. When the
signal fires, the pre-committed action happens before any new argument. The
moment to argue that the criterion was wrong was the day it was written,
while it was still cheap. This is the one place where inflexibility is a
feature: the whole point of pre-commitment is to remove the decision from
the moment of maximum bias.
