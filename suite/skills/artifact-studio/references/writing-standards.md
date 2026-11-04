# Writing Standards for Suite Artifacts

Every document produced from these templates follows the same rules. They exist so a reader can trust the shape of what they are reading.

## Structure

- **Sections in template order.** The order is the argument: context before options, findings before recommendations, gaps before conclusions.
- **One idea per section.** If a section needs "and also", it is two sections.
- **The executive summary stands alone**: a reader who stops after it leaves with the correct conclusion and its evidence level.

## Placeholders

- Named `{{UPPER_SNAKE}}` placeholders are debts. `artifact-new` lists them; a delivered document has none.
- Fill a placeholder with the real content or delete the section — an empty section is worse than a missing one.

## Claims and numbers

- Every number carries its source (inline citation, or a named file/command for internal data).
- State the unit and the measurement context next to the number, not in a footnote three pages away.
- Ranges where ranges are true ("3-5 ms at p99 under 1k rps"), point values only where point values are real.

## Language

- Plain declarative sentences. If a sentence needs a second reading, it is badly written, not subtle.
- Calibrated wording everywhere: "in the cited benchmark", "according to the vendor", "as of 2026-11". Absolute terms are earned by evidence or removed.
- The reader is technical but not telepathic: expand acronyms on first use, name versions, link documents.

## Markdown mechanics

- GitHub-Flavored Markdown; tables for comparisons, lists only for enumerable items, prose for reasoning.
- No HTML, no inline styling: these documents are diffed, grepped and piped.
- Code and commands in fenced blocks with a language tag; file paths as inline code.

## Postmortem-specific rules

- Timeline in UTC with absolute timestamps; cause analysis separated from timeline.
- Blameless about people, precise about mechanisms: "the retry loop doubled the write because the lock was released early", not "the developer made an error".
- Action items carry an owner and a due state, or they are wishes.

## Schema-specific rules

- Every field: name, type, nullability, unit/semantics, and an example.
- State what validates the schema and where the validation runs.

## Before delivering any artifact

1. Zero placeholders left.
2. Every fact cited or attributable to a named command.
3. `evidence-audit` PASS if the document cites research.
4. The executive summary still matches the body after your last edit (summaries drift).
