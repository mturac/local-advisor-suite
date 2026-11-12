# "Should we rewrite the API" — a contract that saved a rewrite

A real-shaped run: the ask arrives as one vague sentence — "our API is
getting old, should we modernize it?" — and the naive move is a comparison of
rewrite strategies. The contract takes four commands and about a minute, and
changes the work entirely.

## 1. Pin the contract

```bash
$ python3 scripts/workbench.py qc-pin \
  --question "Should we modernize the public API?" \
  --decision "Decide this sprint between a full rewrite and a versioned compatibility layer, and commit the next quarter's engineering time to it" \
  --consumer "The two backend engineers who will do the work; a one-page recommendation" \
  --decided "The mobile clients cannot ship a breaking upgrade this year" \
  --open "Whether the web clients can absorb a versioned layer"
```

```json
{
  "status": "OK",
  "vague_terms": [
    {"term": "modernize", "ask": "modernize which property — the stack, the interface, the ops?"}
  ],
  "note": "Vague terms found in the question. Each one makes the answer unjudgeable; ask the single most answer-changing question before proceeding, or record assumptions with qc-assume."
}
```

## 2. The gate

```bash
$ python3 scripts/workbench.py qc-check
```

```json
{
  "status": "OK",
  "gate": "READY",
  "missing": [],
  "vague_terms": [
    {"term": "modernize", "ask": "modernize which property — the stack, the interface, the ops?"}
  ],
  "clarify_opportunities": ["modernize which property — the stack, the interface, the ops?"],
  "next": "Answer against the contract. If a vague term survives, qc-assume the interpretation you chose and state it in the answer's caveat."
}
```

The contract is complete (question, decision, consumer all pinned), so the
gate passes — but the vague-term scan surfaced the question that actually
matters. One message to the user, not five:

> "When you say modernize — do you mean the stack it runs on, the interface
> clients see, or how it's operated? The answer is a different document for
> each."

The reply: "the interface, mostly — clients keep complaining about the
pagination and auth". The comparison matrix now has its real criteria, and
the stack-vs-interface question that would have eaten half the answer is
settled in one sentence.

## 3. Assumptions where ambiguity survived

```bash
$ python3 scripts/workbench.py qc-assume \
  --assumption "modernize means the client-facing interface; stack and ops changes are out of scope this quarter" \
  --assumption "mobile clients stay on the current shapes, so any new interface ships as a versioned layer beside them"
```

```json
{
  "status": "OK",
  "assumptions": [
    "modernize means the client-facing interface; stack and ops changes are out of scope this quarter",
    "mobile clients stay on the current shapes, so any new interface ships as a versioned layer beside them"
  ],
  "assumption_count": 2,
  "next": "State every assumption in the answer's caveat — an unstated assumption is a landmine the next reader steps on."
}
```

## 4. What the contract did to the answer

Without the contract: a forty-page rewrite-strategy comparison, scope
including the stack (out of scope), optimized for the wrong reader, with the
mobile constraint — the fact that decides everything — discovered in review.

With it: a one-page recommendation of a versioned compatibility layer,
written for the two engineers, opening with the decision it informs, closing
with two assumptions the client can correct in one sentence if wrong. The
research pass that follows (deep-research, or decision-review for the
layer-vs-rewrite trade) starts from the contract, not from the vague
sentence — which is the entire point: the expensive ambiguity was resolved
at the cheapest possible moment.
