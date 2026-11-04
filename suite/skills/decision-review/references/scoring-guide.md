# Scoring Guide: Criteria, Weights, Hard Constraints, Sensitivity

## Choosing criteria

1. **Extract them from the user's words.** "We cannot afford another system to babysit" → criterion `ops-burden`, not a generic "maintainability". Name criteria in the user's language.
2. **3 to 6 criteria.** Fewer means you have not decomposed "good"; more means the matrix becomes noise. If you need more, group related criteria into one and note the sub-factors in the ADR.
3. **Criteria must differentiate.** A criterion on which every option scores the same is dead weight; drop it.
4. **One criterion, one meaning.** "Performance" is not a criterion; "p99 latency at 5k req/s" is.

## Weights

- 1 = nice to have, 5 = decisive. Weights are relative within the matrix only.
- Before scoring, ask: "if this criterion is terrible but others are great, do we still say yes?" If no, you have a hard constraint, not a weight — use `min_score`.

## Hard constraints (`min_score`)

`min_score` (0-10) disqualifies any option scoring below it on that criterion. Use it for:

- Compliance and licensing floors ("must be OSS-compatible").
- Operational floors ("team must be able to operate it without a new hire").
- Data-integrity floors ("must support ACID").

A disqualified option appears in `ranked_options` with `disqualified: true` and its reasons — keep them visible so the reader sees what was excluded and why.

## Unknown scores

An unknown or missing score is recorded as `unknown` and treated as neutral 5.0. This is deliberately conservative: it does not silently reward ignorance, and the sensitivity `warnings` list names every unknown criterion. Resolve unknowns with research (`deep-research`, `wide-search`) before treating the recommendation as final.

## Reading the sensitivity block

| Field | Meaning | Action |
|---|---|---|
| `margin` | Score gap between winner and runner-up (0-10 scale) | Under 0.5: treat as a tie; decide on reversibility or cost, not the score |
| `robustness` | `robust` / `moderate` / `fragile` | `fragile` decisions need the flip points confirmed by the user |
| `weight_flips` | How far a single criterion weight must move to change the winner | Ask: "is that weight actually knowable, or did we guess it?" |
| `score_flips` | Single ±1 score changes that flip the winner | Re-examine those specific scores; they are carrying the decision |

A decision that flips on a ±1 score you guessed is not a decision. Either verify that score or record the decision as "tied, resolved by {cost/reversibility/preference}" in the ADR — that is an honest, reviewable outcome.

## Anti-patterns

- **Retrofitting weights**: choosing weights after seeing scores to produce a preferred winner. The sensitivity output makes this visible; do not do it.
- **Criterion stuffing**: adding variants of one criterion to double its effective weight. If two criteria always correlate in every realistic option, merge them.
- **False precision**: reporting a 6.74-vs-6.71 margin as meaningful. Margins under 0.5 are ties.
- **Scoring from memory**: scoring vendor capabilities, benchmarks or prices without a verified source. Research first, score second.
