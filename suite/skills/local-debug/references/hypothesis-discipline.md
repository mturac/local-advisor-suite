# Hypothesis Discipline

## What a hypothesis is

A hypothesis is a single, falsifiable statement about the cause of the recorded symptom. It has three mandatory parts:

1. **Statement** — a specific mechanism, not an area. "Totals are rounded per line before tax" is a hypothesis. "Something in the rounding logic" is not.
2. **Prediction** — what you will observe if and only if the statement is true, stated before you look. It must contain an observable: a number, an output string, a row count, a log line.
3. **Test command** — the cheapest command that produces that observation.

## Writing predictions that can fail

A prediction that cannot fail is decoration. Compare:

- Weak: "The rounding function will be involved." (cannot fail — involvement is not observable)
- Weak: "I will look at the code and confirm the bug." (confirmation is not a prediction)
- Strong: "If true, `round(3.35, 2) * 3` returns `10.05`, and the test expects `10.06`." (fails if it returns anything else)
- Strong: "If true, the invoice rows table has 3 rows for invoice 42, not 2." (fails on any other count)

Numeric predictions are the gold standard because they remove judgment from the verdict.

## Recording verdicts

- **CONFIRMED** — the prediction held. The evidence field quotes the actual output. Only now may you design a fix.
- **FALSIFIED** — the prediction did not hold. The evidence field says what you saw instead. A falsification is a result, not a failure: it eliminated a cause for the cost of one test.
- Never edit a recorded verdict to keep the ledger tidy. Record a new hypothesis instead; the history is the value.

## The two-strike rule

After 2 falsified hypotheses, the circuit breaker trips and the ledger refuses new PENDING hypotheses. This exists because the third guess is rarely better than the first two — what is missing is not another guess but information: a log you do not have, a reproduction you cannot see, a scope you were not given. When the breaker trips:

1. Run `debug-report` without `--fix`.
2. Read the brief it renders: both hypotheses, their predictions, their contradicting evidence.
3. Ask the user for exactly one thing: the telemetry, the access, or the decision that would discriminate between the remaining possibilities.

## Fix discipline

- Fix only after a CONFIRMED hypothesis, and only what the confirmed mechanism implies.
- After the fix, re-run the original repro command. The root-cause report's `--fix` claim is verified only up to the level `delivery-verify` observed.
- Record what you did NOT check (`--open-risk`). "I did not verify credit notes" in the report is honesty; discovering it in production is not.
