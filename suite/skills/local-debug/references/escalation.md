# The Anatomy of a Good Escalation Brief

When the circuit breaker trips (2 falsified hypotheses), `debug-report` renders an escalation brief. Its job is to let a human — or a future session with better access — continue without redoing your work.

## What the brief must contain

1. **The symptom, verbatim.** The exact assertion, error string or observed behavior. Not a paraphrase.
2. **The reproduction command, exactly as run.** If the repro is environment-dependent, say which environment it reproduced in.
3. **Both falsified hypotheses with their predictions and evidence.** The reader must see what was eliminated, and why the evidence was convincing. "H1: per-line rounding before tax — falsified: `round(3.35,2)*3 = 10.05` matches the expected total; the bug is not in line rounding."
4. **What was NOT tried, and why.** Scope you did not have, access you lacked, areas you deliberately excluded. This prevents the next session from assuming the ground was covered.
5. **One precise ask.** The single piece of telemetry, access or information that best discriminates between the remaining candidate causes. Not "please advise".

## Writing the ask

Rank the remaining candidate causes, then ask for the observation that splits them:

- If the cause is either "the data" or "the code", ask for the exact input record — one command that dumps it.
- If the cause is either "this environment" or "all environments", ask for one run in a second environment.
- If the cause is either "recent change" or "longstanding", ask for the last-known-good commit and whether the repro exists there.

## What the brief must NOT contain

- Guesses presented as candidates without predictions. If you list a remaining possibility, state what observation would confirm it.
- Blame. "The billing team's code" adds nothing; `billing/invoice.py:42` does.
- A fix proposal. The breaker tripped because you do not know the cause; proposing a fix now is the guessing the breaker exists to stop.

## Handing off

`session-handoff` should carry the escalation forward: the HANDOFF.md summary references the brief path, and the next session starts by reading it — not by re-running the falsified hypotheses.
