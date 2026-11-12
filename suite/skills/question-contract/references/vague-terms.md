# Vague Terms and the One Question

Some words make an answer unjudgeable: you cannot be wrong about "better"
because "better" does not mean anything until a measure is named. The scan is
deterministic — every hit below comes back with the clarifying question it
demands — but the craft is in which question you actually ask.

## The scan list

English: better, best, optimal, improve, faster, cheaper, modernize,
efficient, scalable, robust, user-friendly, clean, simple, production-ready.
Turkish: daha iyi, en iyi, verimli, hızlı, temiz, basit, kullanışlı,
ölçeklenebilir.

Each maps to its question: "better by which measure (speed, cost,
maintainability)?", "faster by how much, measured where?", "cheaper on which
cost line — license, ops, or engineering time?", "simple for whom — the
writer or the next reader?", "verimli — hangi kaynakta: zaman, para, emek?".

## Why one question, not all of them

A prompt with three vague terms could generate three clarifying questions,
and the user will answer the easiest one, not the most important one. The
discipline:

1. Ask the question whose **answer would most change the work you are about
   to do**. "Better by which measure?" changes the entire comparison matrix;
   "by when do you need this?" changes the schedule. The first wins.
2. Everything else becomes an assumption: `qc-assume --assumption "cheaper
   means lower license cost; ops cost was not raised"`. The user can correct
   an assumption in one sentence — often cheaper than answering a question.
3. If the user is gone (batch mode), all of it becomes assumptions, stated
   in the caveat.

## The vague-term false negative

The scan catches words; it cannot catch a missing constraint. "Which CI
platform should we migrate to?" scans clean but hides the real question:
mobile build support, which no platform comparison would surface unless
someone asked. That is what `--open` on qc-pin is for: the open list is
where you write the constraint the question forgot to mention. A clean scan
means the words are precise, not that the question is complete.

## When a vague word is fine

"Better" in the user's mouth is fine — it is honest; they have not decided
the measure. "Better" in *your answer* is a defect: an answer must commit to
measures. The scan runs on the pinned question to force the commitment
conversation early, so the answer itself never has to say "it depends".
