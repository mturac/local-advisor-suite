---
name: question-contract
description: Pin what the question actually is before spending tokens on it — the question restated, the decision it informs, who consumes the answer, what is already decided and what is genuinely open; a deterministic vague-term scan names the word that makes the answer unjudgeable and the one clarifying question that would change it most; a READY/NEEDS_INPUT gate blocks answering without a decision and consumer; ambiguities proceed as recorded assumptions stated in the answer's caveat; use for clarify the request, before you start, what do you actually need, scope it, soruyu netleştir, tam olarak ne istiyorsun.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Question Contract

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

The most expensive failure in advisory work is not a wrong answer — it is a brilliant answer to the wrong question. Rework, wasted research, and decisions made on answers nobody asked for all trace back to the same root: nobody pinned what the question actually was. This skill makes that pin explicit and cheap: the question, the decision it informs, who consumes the answer, and the assumptions made where the question stayed vague.

## When to use

- Any non-trivial request before research, analysis, comparison or building starts — especially when the ask contains "better", "improve", "efficient", "modernize", "verimli", "daha iyi".
- The user explicitly asks to clarify: "clarify what I need", "before you start", "tam olarak ne istiyorsun anlatayım".
- A routing pass (load-skills) returns multiple skills for one vague prompt — the contract decides which skill actually applies.
- The user is not available for questions (batch mode): the contract's assumption ledger is the honest way to proceed.

Do NOT use when:

- The ask is a single precise fact ("Python 3.13 release date?") — answer it; a contract would cost more than the answer.
- The user is mid-flow in a debugging session with concrete errors in named files — the question is already pinned by reality.
- The contract for this work is already pinned and qc-check returned READY — proceed with the actual skill.

## Workflow

1. **Pin the contract.** The question restated as a question, the decision it informs, and — ideally — who consumes the answer and what is already decided:
   `$WB qc-pin --question "which CI platform should we migrate to?" --decision "choose one platform and start the migration next sprint" --consumer "the two engineers doing the migration" --decided "leaving the in-house CI is settled" --open "mobile build support"`
   The decision field is the discipline: an answer that informs no decision is trivia. If you cannot name the decision, ask.

2. **Run the gate.** READY means answer; NEEDS_INPUT names exactly what is missing:
   `$WB qc-check`
   Missing decision or consumer → NEEDS_INPUT: ask the user in one message, re-pin with `--force`, or — in batch mode — proceed and record the guesses.

3. **Read the vague-term scan.** Every vague word in the pinned question comes back with the clarifying question it demands ("better by which measure?"). Ask the ONE question whose answer would most change your work. Do not interrogate: one precise question beats five forms.

4. **Record assumptions where ambiguity survives.** When nobody can answer and you must proceed:
   `$WB qc-assume --assumption "better means faster pipeline, not cheaper, since budget was not raised"`
   Every assumption must appear in the answer's caveat — an unstated assumption is a landmine for the next reader.

5. **Answer against the contract.** The consuming skill (deep-research, decision-review, data-analysis, ...) runs with the contract as its intake; the answer opens by addressing the decision, and closes by listing the assumptions it rests on.

## Stop rules

- Never answer a question whose decision and consumer are unpinned — qc-check exists to make this mechanical.
- One clarifying question maximum per round; if you need to ask five, the contract is wrong, not the user.
- An assumption is a full statement, not a hedge: "better means faster" is an assumption, "the user probably wants something good" is noise.
- If the pinned question turns out wrong mid-work, re-pin (qc-pin --force) — do not silently drift to a different question.

## Commands

| Command | Purpose |
|---|---|
| `qc-pin` | Pin the contract: question, decision, consumer, budget, decided/open lists |
| `qc-check` | The gate: READY, or NEEDS_INPUT with exactly what to ask |
| `qc-assume` | Record a stated assumption; every one lands in the answer's caveat |

## Files

- `references/contract-fields.md` — each field's purpose, with good and bad examples.
- `references/vague-terms.md` — the vague-term scan, and how to ask the one question that matters.
- `templates/question-contract.md` — fillable contract skeleton (same fields the CLI emits).
- `examples/api-rewrite-decision.md` — a real run: pin, gate, vague terms, assumptions, and the answer that respected them.
