# Knowledge Entry Standards

## The question

- **Written as the person would ask it later**, not as it was discussed: "In which order does the billing export apply tax and rounding?" — not "The tax thing from Tuesday".
- **Atomic.** One question, one answer. "How does export handle taxes and pagination?" is two entries; search cannot rank a compound.
- **Specific enough to discriminate**: "What port does the sandbox proxy use?" beats "Sandbox networking?".

## The answer

- **Verdict first, then reasoning**: "Tax is applied per line before totals are rounded; rounding mode is HALF_UP." Then the constraint that makes it true ("per AC1 and the fix in `_line_total()`").
- **Includes its boundaries**: where the answer holds (versions, environments, scales) and where it stops. "This holds for v1.4 configs; the 2.x default changes it."
- **20 characters is the floor; one working sentence is the bar.** If the answer needs three paragraphs, either the question is compound or the knowledge is not yet distilled — distill it, then capture.
- **No new claims the source does not support.** The entry compresses verified knowledge; it does not extend it.

## Sourcing rules

The runtime enforces the first rule mechanically; the rest is discipline:

1. Every entry has `--source-url`, `--source-id` (a registered research-ledger source), or `--assumed`. No exceptions.
2. The source should be the **most primary available**: the spec, the fix commit's test, the official doc — in that order.
3. `--source-id` binds the entry into the research trail: the audit can later re-verify the underlying page.
4. For answers that emerged from a verified fix, cite the criterion or the verification record ("AC1, verified L3") in the answer text.
5. `--assumed` is not a failure state — it is an explicit marker. The entry exports as **ASSUMPTION (unverified)** with LOW confidence so nobody quotes it as fact.

## Tags

- Lowercase, single words where possible, 2-4 per entry.
- Tags name the **domain of the question** (`billing`, `infra`, `export`, `auth`), not the project phase or the person.
- Before inventing a tag, search what exists: `kb-export` output shows the current grouping; reuse before minting.

## What does not belong

- Session state ("we decided to postpone X") — that is a handoff decision line.
- Opinions without verification — assumptions must be marked, and opinions are not even assumptions.
- Anything the repository already documents canonically: link it in an answer if useful, but do not duplicate docs into the KB.
- Raw quotes without a question — the question is the retrieval key; a quote without one is unfindable.
