# Delivery Evidence — <TITLE>

> Skeleton for the delivery-verify skill. "It works" is not evidence; a
> runnable check is. Fill every level you can actually prove and mark the
> rest honestly.

- **Delivered**: <what was delivered, one sentence>
- **Date**: <YYYY-MM-DD>

## What was asked

- **Goal**: <the acceptance criterion, verbatim from the spec>
- **Non-goals**: <explicitly not delivered>

## Evidence ladder

| Level | Meaning | Check run (exact command) | Expected sentence in output | Result |
|-------|---------|---------------------------|-----------------------------|--------|
| L0 | claimed only | — | — | <n/a> |
| L1 | artifact exists | `test -s <path>` | (exit 0) | PASS / FAIL |
| L2 | command runs | `<the command>` | "<sentence>" | PASS / FAIL |

## Verification record

- **Artifact**: <path> (<size>)
- **Strongest level achieved**: <L0/L1/L2>
- **Unverified claims**: <list, or "none">

## Open risks

- <what was not exercised and could still break>
