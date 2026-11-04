# Advisory Modes and Intake Questions

`advise-intake --mode` selects how to interrogate the request. Match the mode to what the user is actually asking; the mode changes the intake questions and the shape of the answer, never the guardrails.

## architecture

The user asks how a system should be structured, or whether a proposed structure is sound.

Intake questions that matter (ask only what the conversation does not already answer):

1. What are the load and growth expectations (users, requests/sec, data volume)?
2. What are the operational constraints (team size, deploy cadence, budget, compliance)?
3. What must not change (existing contracts, data formats, SLAs)?

Answer shape: 2-3 candidate structures, the forces that distinguish them (consistency vs. latency, coupling vs. velocity, cost vs. elasticity), a recommendation, and the first architectural decision that would need reversing if the recommendation is wrong.

## tradeoff

The user weighs two or more concrete options ("Postgres queue vs. Redis streams").

1. What are the hard constraints that could disqualify an option outright (latency budget, license, ops expertise)?
2. What does "good" mean, in the user's words? Turn that into 3-6 criteria before any scoring.
3. How reversible is each option if it turns out wrong?

Answer shape: the trade-off table in prose, then a recommendation. If the user wants rigor, hand off to `decision-review` for a scored matrix with sensitivity analysis.

## code-review

The user asks whether a described approach or a snippet pasted into the conversation is sound.

1. What invariants must the code preserve (correctness, security, performance)?
2. What is the blast radius if it is wrong?

Answer shape: findings ordered by severity, each with the concrete failure mode, then a verdict. Do not run `code-review` commands for this — that skill is for reviewing files or diffs the user points at. If the user names files, switch skills.

## planning

The user asks how to sequence work or what to build first.

1. What is the deadline and what is genuinely fixed versus negotiable?
2. What is the riskiest assumption, and what cheapest experiment retires it?

Answer shape: an ordered plan where every step either delivers value or retires risk, with explicit cut lines ("if step 2 fails, stop and re-plan"). Offer `spec-builder` to turn the plan into acceptance criteria.

## general

Everything else. Still: identify the real question behind the question, state assumptions, and answer concretely.

## The one-question rule

Missing context blocks a good answer only when the answer would materially change based on it. Ask **one** precise question per round, never a questionnaire. If the missing context does not change the recommendation, state the assumption you are making and proceed.
