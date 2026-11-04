# Reversibility Classes R0-R3

Every ADR states its reversibility class. The class determines how much evidence you need before committing, and how eagerly you should look for cheap exit points.

## R0 — trivially reversible

Undoing the decision is a one-line change or a settings toggle, with no data or contract impact.

- Examples: a linter rule, a logging level, a feature flag default, a dependency patch upgrade.
- Evidence bar: low. Try it; revert on the first bad signal.
- ADR duty: name the revert command.

## R1 — cheap to reverse within a sprint

Undoing requires code changes across a bounded area, but no data migration and no external contract break.

- Examples: swapping an internal library with a thin wrapper, restructuring a module, changing an internal queue implementation behind an interface.
- Evidence bar: moderate. A spike or a prototype in one service is enough.
- ADR duty: name the wrapper/seam that contains the blast radius.

## R2 — costly migration

Undoing requires data migration, coordinated multi-service changes, or renegotiating an external contract.

- Examples: changing a database engine, a public API contract, an identity provider, a message schema consumed by other teams.
- Evidence bar: high. Verify the decisive criteria with primary sources; run a pre-mortem; pilot on one slice before committing.
- ADR duty: name the point of no return (the first data or contract change that cannot be unwound) and the rollback trigger signal with a numeric threshold.

## R3 — effectively irreversible

Undoing is indistinguishable from starting over.

- Examples: burning a bridge in a migration, publishing a hardcoded number to customers, deleting data without backup, choosing a company name.
- Evidence bar: maximum. This is the only class where "we are not sure" legitimately means "do not ship yet". Require independent primary evidence for every decisive criterion, and an explicit sign-off from the decision owner.
- ADR duty: state what makes it irreversible and what the last cheap exit was.

## Using the class in reviews

- A fragile decision (small sensitivity margin) at R2/R3 deserves more scrutiny than a robust one at R0. Read the sensitivity block and the class together.
- When a decision is a tie on scores, prefer the more reversible option and say so in the ADR rationale.
- The rollback trigger must be observable: "error budget burn exceeds 2x for a week", not "things get bad".
