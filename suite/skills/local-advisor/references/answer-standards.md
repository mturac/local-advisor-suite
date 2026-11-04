# Answer Standards for Advisory Output

An advisory answer is a deliverable. It must survive being read a week later, out of context, by someone who was not in the conversation.

## Required structure

1. **Recommendation first.** One paragraph, unambiguous: "Do X, because Y, unless Z." If you cannot write this paragraph, you do not have an answer yet.
2. **Options considered.** Each option gets: what it is, its strongest genuine advantage, and its real cost. Two options maximum for simple questions; three for architecture. More options than that signals you have not pruned.
3. **Trade-offs that drove the recommendation.** Name the forces (latency vs. consistency, speed vs. debt, buy vs. build). The reader must be able to disagree with your weighting, not your facts.
4. **Risks and mitigations.** Top 2-3 risks only. Every risk carries a mitigation or an explicit "accepted".
5. **Reversibility.** State how expensive it is to undo the recommendation (align with the R0-R3 classes used by `decision-review`), and the point of no return.
6. **What to verify next.** The assumptions that, if false, collapse the recommendation, and how to test each one cheaply.

## Confidence labels

End the answer with a confidence label and its justification:

- **High** — grounded in verified sources or the user's own stated facts, and you have seen this pattern work at this scale.
- **Medium** — grounded in general experience; scale, stack or team specifics unverified.
- **Low** — materially depends on unverified assumptions; the answer is a hypothesis, not advice.

State plainly what evidence would move the confidence up. Never use "High" to mean "I feel good about this".

## Language rules

- Concrete nouns and numbers over abstractions: "p99 under 200 ms", not "fast enough".
- No filler best-practice paragraphs (version control, tests, monitoring) unless the user asked about exactly that.
- Calibrated wording. Avoid "always", "never", "guaranteed", "the best". The evidence-audit skill flags these patterns in research deliverables; advisory answers hold themselves to the same bar.
- Name the trade-off you are rejecting. "We are choosing velocity over consistency here, and that is wrong if X" is a sentence worth writing.

## Sourcing inside advice

- Facts that could differ across versions, vendors or scale points (benchmarks, limits, prices, support policies) must be verified (`web-search`, `deep-research`) or labeled `assumption — verify`.
- The user's own statements are primary evidence. Quote their constraints back when the recommendation depends on them.
- Never cite a URL you have not opened this session.
