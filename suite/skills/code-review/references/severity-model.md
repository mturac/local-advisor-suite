# Review Severity Model

The verdict is only as honest as the severity grades. These definitions are calibrated so that two reviewers looking at the same finding agree.

## BLOCKING — the verdict is FAIL while any is open

The change is incorrect, insecure, or loses data as written. It must be fixed before merge; there is no "follow-up ticket" version of a BLOCKING.

- Wrong behavior on a realistic input (money, boundaries, empty sets, unicode, timezones).
- Security: injection, auth bypass, secret exposure, unsafe deserialization, SSRF.
- Data loss or corruption in any path the change touches.
- A test that asserts the wrong thing with enough confidence to mask the bug.
- Breaking a public contract without a version bump or migration.

Test: "Would I be embarrassed to explain to the user why this shipped?" If yes, BLOCKING.

## MAJOR — correct today, bites soon

The code works but carries a real, near-term cost or risk that the author should address in this change.

- Changed behavior with no updated test (the next refactor will silently break it).
- An unclear API contract others will build on wrongly (ambiguous units, unclear nullability).
- An N+1 or unbounded query on a path that will grow.
- Missing error handling on a failure mode the environment actually produces.
- A TODO/FIXME marking unfinished work inside the change's scope.

Test: "Will someone have to touch this again within weeks, expensively?" If yes, MAJOR.

## MINOR — worth fixing in passing

Real but small; the reviewer would fix it if editing the same lines anyway.

- Misleading naming, small duplication, stale comment.
- A test that could be table-driven; a fixture that could be shared.
- Inconsistent formatting the linter does not cover.

Test: "Would I block a merge over it?" No. "Would I fix it while in the file?" Yes.

## INFO — observation, no change requested

The finding carries information the author or future reader wants, without requesting action.

- "This mirrors the pattern in X; if you change one, change both."
- "This limitation is documented in the spec's non-goals — confirming it is deliberate."
- A pointer to prior art or a relevant ADR.

INFO never affects the verdict.

## Calibration practice

- **Severity is about the finding, not the confidence.** If you suspect a bug but cannot prove it from the target, record it at the severity it would have if true, say what evidence would settle it in the description, and let the author respond. Do not pre-shrink to MINOR out of politeness.
- **One finding, one defect.** A finding with three defects is three findings — they get fixed at different times.
- **The suggestion is not the severity.** An easy fix does not downgrade a BLOCKING; a hard fix does not upgrade a MINOR.
- **Categories are lenses, not verdicts**: correctness, security, performance, maintainability, tests, style. A security finding can be MAJOR when the exposure is internal-only; the category names where to look, the severity names how much it matters.
