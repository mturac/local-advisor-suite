# Review Checklist

Work the categories that match the review's `--focus`. Every item is phrased as a question about the diff, not the codebase at large — out-of-scope observations go to `--not-reviewed` or a new review.

## Correctness

- [ ] Do the boundary values work: empty collections, zero, one, max, off-by-one edges?
- [ ] Money and quantities: rounding mode and order, currency, integer cents vs. floats?
- [ ] Time: timezones, DST, "today" computed once vs. per-row, ISO vs. local formats?
- [ ] Unicode and escaping on every crossing (shell, CSV, SQL, JSON, URL)?
- [ ] Failure paths: what happens when the dependency errors, times out, returns partial data?
- [ ] Idempotency: does a retry double-apply the effect?
- [ ] Concurrency: what is the interleaving that breaks this? Is a lock/marker actually held across the critical section?
- [ ] Does each test assert the behavior in the criterion (if a spec exists), or just the implementation's echo?

## Security

- [ ] Inputs: validated at the boundary, or trusted because "the frontend checks"?
- [ ] Authorization: does the actor's identity flow to the data access, or just to the route?
- [ ] Secrets: any in code, logs, error messages, test fixtures? (The runtime blocks reading them; the diff should not add them either.)
- [ ] Injection: every query/command/parse built from user-influenced strings?
- [ ] Outbound calls: URL built from user input (SSRF), redirect followed blindly?
- [ ] Errors: do messages leak internals (paths, stack, other users' data)?
- [ ] New dependencies: license, maintenance, and why they are needed at all?

## Performance

- [ ] Any query in a loop, or a loop that became a query per row?
- [ ] Unbounded result sets: pagination, limits, streaming — or a future outage?
- [ ] N+1 across a network boundary (API, DB, cache)?
- [ ] Work done per-request that could be cached or precomputed — and is the cache correct under invalidation?
- [ ] Locks held across I/O?

## Maintainability

- [ ] Can a new team member trace a request through this change without tribal knowledge?
- [ ] Do names say what things do, or what they are implemented with?
- [ ] Is there duplication that will drift (same validation in two layers)?
- [ ] Are the failure modes visible (log/metric/trace) or silent?
- [ ] Do comments explain why, where the code cannot?

## Tests

- [ ] Does changed behavior have a changed-or-added test?
- [ ] Do tests fail for the right reason (assert the outcome, not the implementation)?
- [ ] Is the interesting case tested (boundary), not just the happy path?
- [ ] Are fixtures honest (realistic shapes) or oversimplified into tautologies?
- [ ] Would this test catch the bug it was written for if reverted?

## Style

Only where the project has no linter: consistency with the surrounding file beats global preference.

## Recording findings

Each finding: `--file`, `--line`, `--severity`, `--category`, a description that names the failure mode ("loses cents on 3+ line invoices" not "rounding issue"), and a suggestion that is the smallest good fix. If you cannot name the failure mode, it is not a finding yet — investigate or record INFO.
