# Contract Fields

A question contract has six fields. Two are mandatory (the question and the
decision); the rest are cheap insurance against the standard rework loops.
Each field below says what it is for, and what its absence typically costs.

## question (mandatory)

The ask, restated as a question that can be answered. Not the user's original
words — their words are data; the contract is the interpretation. Restating
is where you discover the ask was three questions wearing one sentence.

- Bad: "the API" (a topic). Bad: "should we improve the API?" (improve = vague).
- Good: "is rewriting the public API worth the client-migration cost, or is
  a versioned compatibility layer enough?"

Rule of thumb: if two competent people could give different answers to your
restated question and both be right, the restatement is not done.

## decision (mandatory)

What the answer will inform. The single discipline that separates advisory
work from trivia generation. If no decision follows from the answer, either
the question is curiosity (fine — say so, and stop billing it as advice) or
the real question is hiding one level deeper.

- Bad: "want to know" (informs nothing). Bad: "architecture" (not a decision).
- Good: "choose between a rewrite and a compatibility layer this sprint, and
  commit engineering time to it."

The decision also bounds the answer's depth: an answer that informs a sprint
decision does not need a five-year TCO study.

## consumer

Who reads the answer, in what form. The consumer determines the artifact: the
two engineers doing the migration want migration-order specifics; a CFO wants
one page with the number that moves. Answering for the wrong reader produces
work that is technically correct and operationally useless.

## budget

What the answer may cost: time, tokens, queries, money. The budget field
makes over-delivery a choice instead of an accident. A quick question with a
one-hour budget should not trigger a twelve-source research ledger; the
contract is where that trade-off is made explicit, before the work starts.

## decided (list)

What is already settled and not open for debate. The most under-used field:
teams routinely re-litigate settled ground because nobody wrote it down, and
advisors routinely waste half their answer arguing a decision the asker
already made. "We are leaving the in-house CI" in `decided` kills a third of
the comparison work before it starts.

## open (list)

The genuinely open sub-questions. The complement of `decided`: what the
answer is allowed — sometimes required — to leave unresolved. An answer that
resolves the named open questions and honestly parks the rest is a finished
answer, not a partial one.

## assumptions (the ledger)

Where ambiguity survived and work proceeded anyway, each assumption is a full
statement recorded by `qc-assume`, and every one of them appears in the
answer's caveat. The test of a good assumption: if the user later says
"that's not what I meant", the caveat shows exactly which sentence to
correct — and nothing else needs to change.
