# Task Breakdown and Verification Binding

## The verifies rule

Every task carries at least one `--verifies AC<n>`. This binding is the spec's spine: it answers, for any moment in the project, "which criteria are covered by planned work?" — and, after delivery, "which work claims which proof?".

Consequences:

- **A task that verifies nothing is rejected.** If you cannot name the criterion, either the criterion is missing (write it) or the work is out of scope (cut it).
- **A criterion with no task is a warning** surfaced by `spec-check` — either plan it, or move it to a later spec deliberately.
- **One task may verify several criteria** when they genuinely ship together; avoid using this to smuggle scope.

## Sizing

- A task is sized to be **verifiable in one sitting**: you can implement it, run its verification, and record the result without a context switch. If your task reads "build the export feature", it is three tasks wearing a coat.
- Two to eight `verifies`-bound tasks per story is the healthy range. More suggests the story is an epic; split the story.
- Include the unglamorous verifiable work: the migration script (verifies the schema criterion), the seed data (verifies the boundary criterion), the rollback path (verifies the safety criterion).

## Dependency hygiene

- `--depends-on` references tasks that already exist (the runtime enforces this) and the check catches cycles.
- Depict only **hard** dependencies (T2 cannot even be attempted without T1). "Would be nice to do after" is sequencing, not dependency — leave it out; planners lie with soft dependencies.
- The verification chain is a dependency graph in disguise: if AC2's test needs the pagination from T1, then the task that verifies AC2 depends on T1. Say it.

## During implementation

1. Pick the first task whose dependencies are done.
2. Implement it.
3. Prove it: `delivery-verify` at L3+ for code, referencing the criterion in the summary ("T1 done: AC1 verified — 3 rows, total 10.06").
4. Record honestly: L2-only verification leaves the criterion covered-but-not-proven; the handoff's evidence section will show exactly that.

## When the spec is wrong

Mid-implementation discoveries are normal; hiding them is not:

- **A criterion turned out untestable as written** — rewrite it (`spec-criterion` adds a corrected one; note the supersession in the task or handoff).
- **A task cannot verify its criterion** — the binding was wrong; re-bind or split.
- **The goal moved** — `spec-new --force` and an honest restart beats a ledger that describes a dead spec. Say what changed and why in the handoff.

The spec ledger is a living document with one rule: every change is a recorded change, never a silent one.
