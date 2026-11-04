# Writing Acceptance Criteria

## The Given/When/Then contract

Every criterion has three clauses, each at least 5 characters, each doing one job:

- **Given** — the precondition: the world state before the act. Real data, real quantities.
- **When** — the act: one action by one actor. Not a sequence.
- **Then** — the observable outcome: what a test (or the user's eyes) can check. Numbers, counts, contents, states.

## What makes a Then-clause testable

Run this checklist on every `then`:

1. **Could a script verify it?** "The response contains a `total` field equal to 10.06" — yes. "The response is correct" — no.
2. **Is there a number?** Counts, sums, sizes, codes, durations. Criteria without numbers are usually under-thought. Where a number genuinely does not apply, name the exact content ("the header row is `invoice_id,due_date,total`").
3. **Is the boundary stated?** "Up to 10k rows" and "more than 10k rows" are different criteria; both may be needed.
4. **Would it fail if the feature were broken?** If you cannot describe the failure this criterion catches, it is decoration.

## Examples, fixed

Vague: "Export works correctly for large accounts."
- Given an account with 12,000 unpaid invoices
- When the accountant runs the CSV export
- Then the export completes in under 30 seconds and the CSV contains 12,000 data rows

Vague: "Invalid date ranges are handled."
- Given the fiscal year 2024 filter is applied
- When the accountant exports with range 2024-01-01 to 2023-12-31 (end before start)
- Then the API returns status 422 with error code `INVALID_RANGE` and no file is written

Vague: "The export is secure."
- Given an authenticated accountant with the viewer role
- When they request the export for another company's account
- Then the API returns 403 and the audit log records the denial

## Anti-patterns

- **Implementation details**: "using the streaming serializer, the export..." — the criterion must survive a rewrite.
- **Conjunction creep**: "Then the CSV is correct and fast and secure" — three criteria wearing one coat.
- **Unowned pronouns**: "it works" — name the actor, the artifact and the observation.
- **Testing the mock**: criteria that verify the test fixture instead of the behavior.
- **The disappearing user**: every story has a user; criteria should echo their observable world, not the system's internals.

## Coverage discipline

- Each story needs enough criteria to detect its main failure modes: the happy path, the boundary, the error path. That is usually 2-4 criteria — not 15.
- Cross-cutting concerns (auth, rate limits, idempotency) get their own story when they matter to the user, or they do not belong in this spec.
- Anything you cannot make testable today becomes either a non-goal (explicit) or an open question recorded in the handoff — never a silent hope.
