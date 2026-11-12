# A microservices split that deserved its BLOCK

A real run: a plan to split a monolith "this quarter to speed up deploys" gets
its adversarial pass. The steelman is stated honestly first; four load-bearing
assumptions are attacked; one challenge is answered with evidence; the open
FATAL (no ops staffing for a dozen services) decides the verdict. Exit code 2
is the point — the gate is mechanical, so scripts and hosts can rely on it.

## 1. Open the session — steelman first

```bash
$ python3 scripts/workbench.py devil-open \
  --claim "Split the monolith into microservices this quarter to speed up deploys" \
  --steelman "Independent deploys end the release train: each team ships daily, failures stay inside one service, and the org already runs containers in production"
```

```json
{
  "status": "OK",
  "claim": "Split the monolith into microservices this quarter to speed up deploys",
  "steelman": "Independent deploys end the release train: each team ships daily, failures stay inside one service, and the org already runs containers in production",
  "next": "devil-challenge --assumption ... --attack ... --defeater ..."
}
```

## 2. Attack load-bearing assumptions

The second-order challenge — the plan's stated goal may be undermined by the
plan itself:

```bash
$ python3 scripts/workbench.py devil-challenge \
  --assumption "each team ships daily once split" \
  --attack "Deploy frequency is currently limited by review capacity, not by the release train; splitting adds coordination overhead that makes daily deploys less likely, not more" \
  --category second-order-effect --severity SERIOUS \
  --defeater "deploy frequency per team rises within 6 weeks of each split"
```

```json
{
  "status": "OK",
  "challenge": {
    "id": "C1",
    "assumption": "each team ships daily once split",
    "attack": "Deploy frequency is currently limited by review capacity, not by the release train; splitting adds coordination overhead that makes daily deploys less likely, not more",
    "category": "second-order-effect",
    "severity": "SERIOUS",
    "defeater": "deploy frequency per team rises within 6 weeks of each split",
    "status": "OPEN",
    "rebuttal": null,
    "rebuttal_basis": null,
    "created_at": "2026-11-12T01:48:56+00:00"
  },
  "open_counts": {"FATAL": 0, "SERIOUS": 1, "MINOR": 0},
  "answered_count": 0
}
```

The FATAL — the plan quietly assumes an ops reality that does not exist:

```bash
$ python3 scripts/workbench.py devil-challenge \
  --assumption "the org can operate 12+ services" \
  --attack "There is one on-call rotation for the monolith; the plan creates a dozen failure surfaces with no budget for the ops staffing the diagram quietly assumes" \
  --category cost-complexity --severity FATAL \
  --defeater "an approved headcount plan naming the second on-call rotation"
```

```json
{
  "status": "OK",
  "challenge": {
    "id": "C2",
    "assumption": "the org can operate 12+ services",
    "attack": "There is one on-call rotation for the monolith; the plan creates a dozen failure surfaces with no budget for the ops staffing the diagram quietly assumes",
    "category": "cost-complexity",
    "severity": "FATAL",
    "defeater": "an approved headcount plan naming the second on-call rotation",
    "status": "OPEN",
    "rebuttal": null,
    "rebuttal_basis": null,
    "created_at": "2026-11-12T01:48:56+00:00"
  },
  "open_counts": {"FATAL": 1, "SERIOUS": 1, "MINOR": 0},
  "answered_count": 0
}
```

Two more (C3: nine shared Order/Inventory tables force dual writes — the bug
class the last incident review banned, `reversibility`, SERIOUS; C4: the
timeline assumes the reporting layer needs no migration, `unfounded-assumption`,
MINOR) bring the session to four challenges.

## 3. Answer what can be answered

C4 is checkable right now, and the check kills the attack:

```bash
$ python3 scripts/workbench.py devil-rebuttal --id C4 \
  --rebuttal "The reporting layer already goes through a nightly export view; checked the code before answering — no direct table reads exist" \
  --basis "evidence: grep of the reporting repo, zero direct table references"
```

```json
{
  "status": "OK",
  "challenge": {
    "id": "C4",
    "assumption": "the quarter timeline holds",
    "attack": "The estimate assumes zero migration of the reporting layer, which reads all 9 shared tables directly",
    "category": "unfounded-assumption",
    "severity": "MINOR",
    "defeater": "reporting reads confirmed via a single view during migration",
    "status": "ANSWERED",
    "rebuttal": "The reporting layer already goes through a nightly export view; checked the code before answering — no direct table reads exist",
    "rebuttal_basis": "evidence: grep of the reporting repo, zero direct table references",
    "answered_at": "2026-11-12T01:48:56+00:00",
    "created_at": "2026-11-12T01:48:56+00:00"
  },
  "open_counts": {"FATAL": 1, "SERIOUS": 2, "MINOR": 0},
  "answered_count": 1
}
```

Note what the rebuttal did **not** do: answer C2. The ops-staffing attack has no
evidence behind a rebuttal, so it stays open — and that honesty is what the
verdict reads.

## 4. The gate decides

```bash
$ python3 scripts/workbench.py devil-verdict \
  --kill-criterion "per-team deploy frequency not above baseline 6 weeks after each split" \
  --kill-criterion "any dual-write window opened during the data split"
```

```json
{
  "status": "FAIL",
  "verdict": "BLOCK",
  "report": "CHALLENGE.md",
  "open_counts": {"FATAL": 1, "SERIOUS": 2, "MINOR": 0},
  "answered_count": 1,
  "guards": [
    {
      "challenge": "C1",
      "guard": "each team ships daily once split",
      "watch": "deploy frequency per team rises within 6 weeks of each split"
    },
    {
      "challenge": "C3",
      "guard": "data can be split cleanly along service lines",
      "watch": "an approved data split design with no dual-write window"
    }
  ],
  "kill_criteria": [
    "per-team deploy frequency not above baseline 6 weeks after each split",
    "any dual-write window opened during the data split"
  ]
}
```

Exit code 2. `CHALLENGE.md` carries the steelman, all four challenges, the C4
rebuttal, the guards and the kill criteria.

## What the verdict changes

The BLOCK does not say "never split" — it says the plan, as written, assumes an
ops reality that does not exist. The honest next moves: staff the second
on-call rotation (C2's defeater) or descope to a two-service split that one
rotation can absorb, then re-run the session. The kill criteria stay armed
either way: they are the pre-committed signals that falsify the plan later,
when enthusiasm is back.
