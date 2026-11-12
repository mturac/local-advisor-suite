# A tool adoption that survived its own optimism

A full protocol run: the team wants to replace their in-house CI with a managed
platform. The attack plan comes first (archetype: buy), then the steelman, then
the premortem surfaces two causes nobody had said out loud, the outside view
flags optimism bias mechanically, one consequence chain finds an unowned L2, and
the verdict lands on PROCEED_WITH_GUARDS with kill criteria that can actually
fire. Every command is real output shape — copy the flow, change the substance.

## 1. Get the attack plan for this kind of plan

```bash
$ python3 scripts/workbench.py devil-plan --archetype buy
```

```json
{
  "status": "OK",
  "archetype": "buy",
  "label": "Buy or adopt a tool, service or vendor",
  "attack_order": [
    "problem-existence — the workflow this tool fixes: does it actually cost what you think",
    "lock-in-surface — data, formats, integrations: the cost of leaving in 18 months",
    "tco-honesty — licenses are the small number; setup, training, ops, drift are the big one",
    "vendor-mortality — what happens to you if they are acquired, pivot or die",
    "integration-reality — the promised connector vs your actual edge cases",
    "adoption-risk — the tool works and nobody uses it: the default failure mode"
  ],
  "kill_signal_candidates": [
    "adoption below the agreed usage threshold at the 90-day review",
    "migration-out cost estimate exceeds the value the tool has delivered"
  ]
}
```

The order is the plan: a *buy* fails on adoption and lock-in long before it
fails on features, so those get attacked first.

## 2. Open the session — steelman first

```bash
$ python3 scripts/workbench.py devil-open \
  --claim "Replace the in-house CI with a managed platform this quarter" \
  --steelman "Two engineers stop maintaining glue scripts, pipelines get caching and parallelism we cannot afford to build, and releases stop depending on one person's laptop"
```

```json
{
  "status": "OK",
  "claim": "Replace the in-house CI with a managed platform this quarter",
  "steelman": "Two engineers stop maintaining glue scripts, pipelines get caching and parallelism we cannot afford to build, and releases stop depending on one person's laptop",
  "next": "devil-challenge --assumption ... --attack ... --defeater ..."
}
```

## 3. The premortem, before the challenges

```bash
$ python3 scripts/workbench.py devil-premortem \
  --failure-story "Twelve months on, the managed platform is the demo pipeline and the in-house CI is still the real one: the mobile build needs a native plugin nobody ported, the old scripts were never deleted, and we are paying for both" \
  --cause "the mobile build was assumed to be 'just another pipeline' but needs a native plugin we would have to write and maintain ourselves" \
  --cause "no owner was named for deleting the old pipelines, so both systems stayed alive"
```

```json
{
  "status": "OK",
  "premortem": {
    "failure_story": "Twelve months on, the managed platform is the demo pipeline and the in-house CI is still the real one: the mobile build needs a native plugin nobody ported, the old scripts were never deleted, and we are paying for both",
    "causes": [
      "the mobile build was assumed to be 'just another pipeline' but needs a native plugin we would have to write and maintain ourselves",
      "no owner was named for deleting the old pipelines, so both systems stayed alive"
    ]
  },
  "cause_count": 2,
  "suggested_challenges": [
    "devil-challenge --assumption \"the mobile build was assumed to be 'just another pipeline'...\" ..."
  ]
}
```

Note what the premortem did: the plugin issue was *known* to the mobile lead and
polite about being raised. Assuming failure made it sayable.

## 4. The outside view — optimism bias, flagged mechanically

```bash
$ python3 scripts/workbench.py devil-outside \
  --reference-class "small teams migrating CI to a managed platform" \
  --base-rate 40 --adjustment "none"
```

```json
{
  "status": "OK",
  "outside_view": {
    "reference_class": "small teams migrating CI to a managed platform",
    "base_rate": 40,
    "adjustment": "none"
  },
  "open_counts": {"FATAL": 0, "SERIOUS": 1, "MINOR": 0},
  "optimism_bias_flagged": true,
  "note": "Bad base rate + no adjustment → an auto SERIOUS challenge is now open. Rebut it with the concrete reason this case differs, or change the plan."
}
```

The team estimated "most migrations like this end up fully switched" — the
honest base rate says most do not. With no argued adjustment, the burden is now
on the plan, on the record.

## 5. Attacks in archetype order

```bash
$ python3 scripts/workbench.py devil-challenge \
  --assumption "the mobile build is just another pipeline" \
  --attack "The managed platform has no first-class support for our native build step; we would write and maintain a plugin, which is exactly the glue-maintenance burden the plan claims to eliminate" \
  --category integration-reality --severity SERIOUS \
  --defeater "a working mobile build on the platform within the 2-week spike, plugin included"
```

```bash
$ python3 scripts/workbench.py devil-challenge \
  --assumption "the old CI can be retired in month two" \
  --attack "No owner is named for deleting the old pipelines, and the premortem's failure story is literally both systems alive at month twelve; migration without a decommission owner is paying twice indefinitely" \
  --category cost-complexity --severity SERIOUS \
  --defeater "a named owner and a dated decommission list in the plan document"
```

## 6. A consequence chain, because the first-order story was fine

```bash
$ python3 scripts/workbench.py devil-consequence \
  --l1 "the new platform builds everything, so the old CI stops receiving changes" \
  --l2 "edge cases quietly break in the old pipeline while it is still the release path for two products" \
  --l3 "release week discovers both systems drifted, and nobody knows which pipeline produced the last good artifact"
```

```json
{
  "status": "OK",
  "consequence": {
    "l1": "the new platform builds everything, so the old CI stops receiving changes",
    "l2": "edge cases quietly break in the old pipeline while it is still the release path for two products",
    "l3": "release week discovers both systems drifted, and nobody knows which pipeline produced the last good artifact"
  },
  "consequence_count": 1
}
```

L2 has no owner in the plan — that becomes a guard at the verdict.

## 7. Answer what can be answered

The optimism-bias challenge gets a real rebuttal, not a wave:

```bash
$ python3 scripts/workbench.py devil-rebuttal --id C1 \
  --rebuttal "We differ from the class in one checkable way: both prior migrations here (test runner, artifact storage) fully retired the old system within a quarter, with the same two engineers driving this one" \
  --basis "experience: two completed migrations, both fully switched"
```

```json
{
  "status": "OK",
  "open_counts": {"FATAL": 0, "SERIOUS": 2, "MINOR": 0},
  "answered_count": 1
}
```

## 8. The gate decides

```bash
$ python3 scripts/workbench.py devil-verdict \
  --kill-criterion "mobile build running on the platform (plugin included) by day 14 of the spike, or the plan stops" \
  --kill-criterion "weekly active pipelines on the new platform below 60% at the 90-day review, or we halt the migration and reassess"
```

```json
{
  "status": "WARN",
  "verdict": "PROCEED_WITH_GUARDS",
  "open_counts": {"FATAL": 0, "SERIOUS": 2, "MINOR": 0},
  "guards": [
    {"challenge": "C2", "guard": "the mobile build is just another pipeline", "watch": "a working mobile build on the platform within the 2-week spike"},
    {"challenge": "C3", "guard": "the old CI can be retired in month two", "watch": "a named owner and a dated decommission list"}
  ],
  "kill_criteria": [
    "mobile build running on the platform (plugin included) by day 14 of the spike, or the plan stops",
    "weekly active pipelines on the new platform below 60% at the 90-day review, or we halt the migration and reassess"
  ],
  "protocols_used": {"premortem": true, "outside_view": true, "second_order": true}
}
```

`PROCEED_WITH_GUARDS` is a real answer: the plan is allowed to start its
2-week spike, and two observable signals — day-14 mobile build, the 90-day
adoption threshold — were pre-committed while stopping was still cheap. The
CHALLENGE.md report carries the premortem, the outside view and the
consequence chain, so the next reader sees why.
