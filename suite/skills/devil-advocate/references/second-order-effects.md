# Second-Order Effects

First-order thinking stops at the plan's intended effect. Second-order thinking asks
"and then what?" — once the effect exists, what does it cause, and what does *that*
cause? The failures that surprise people are rarely first-order: the first-order
effect usually works, that is why the plan got approved. The damage arrives later,
down the chain, in a place nobody was watching.

## The discipline

Three levels, each a full sentence with a mechanism, not a category:

- **L1** — what the plan's intended effect directly causes. Not the effect itself
  (that is first-order); the effect's own consequence.
- **L2** — what the L1 situation causes, once people and systems react to it.
  This is where incentives enter: every L1 change makes some behavior cheaper
  and some more expensive, and behavior moves.
- **L3** — what the L2 world causes. Optional when the chain has clearly
  attenuated; mandatory when L2 involves people adapting or incentives shifting.

```
$WB devil-consequence \
  --l1 "free tier removes the signup barrier, so trial volume roughly triples" \
  --l2 "support load triples with it because trials are unqualified, and the
   support team has no hiring budget" \
  --l3 "support response time degrades for paying customers, and the loudest
   ones start evaluating competitors"
```

## Why three levels and not more

Chains longer than three usually collapse into speculation — each level
multiplies the uncertainty. Three is enough to force you past the plan's
frame (L1), past the obvious reaction (L2), and into the adaptation regime
(L3) where the expensive surprises live. If the chain is still mechanically
strong at L3, say so; do not pad it to L4 to look thorough.

## The patterns worth knowing

- **Incentive shift**: the plan changes what is rewarded, and behavior follows
  the reward, not the intention. Metrics are gamed in the direction they
  measure.
- **Load coupling**: success increases load on a system that was sized for
  the old world — support, ops, review capacity, the founder's calendar.
- **Trust dynamics**: what the plan signals (to the team, the market, the
  partner) can matter more than what it does.
- **Option destruction**: the plan forecloses a future choice cheaply
  available today — the cost is invisible until that future arrives.
- **Second pandemic of success**: the plan's success triggers imitation or
  dependency elsewhere, and you inherit coordination costs you did not sign
  up for.

## What to do with a chain

A consequence is not automatically a challenge. For each chain ask: does the
plan already own this level (a named owner, a budgeted response), or does it
stop at L1 and hope? Unowned levels at L2 or beyond become challenges with
`--category second-order-effect`, the assumption being the specific L2/L3
step the plan leaves unguarded. A chain where every level has an owner is a
plan that has done its thinking — that is the outcome worth aiming at.
