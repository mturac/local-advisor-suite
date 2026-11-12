---
name: decision-journal
description: The feedback loop the advisory stack was missing — log decisions with falsifiable predictions, confidences and review dates; resolve them HIT/MISS/PARTIAL against reality with the lesson attached; read the calibration report (hit rate vs claimed confidence per band) that flags overconfidence mechanically; an unresolved entry past its review date is listed as a debt to reality; use for track this decision, log the prediction, how good were our calls, were we right, calibration, karar defteri, tahminler ne kadar tuttu.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "3.7.0"
---

# Decision Journal

Advice that is never scored cannot improve — and neither can the advisor. This skill closes the loop the rest of the suite opens: every significant decision gets logged with a falsifiable prediction and a confidence, reality later grades it HIT / MISS / PARTIAL, and the calibration report shows whether "90% confident" actually means 90% right. Overconfidence is the default human state; this is the instrument that measures it.

## When to use

- A decision was just made — `decision-review` scored the options, or `devil-advocate` issued a verdict — and there is a claim about the future worth grading.
- The user asks to track a call: "log this decision", "let's see if I was right", "karar defteri tutalım".
- A review date arrives: an entry is OPEN and reality has answered; resolve it.
- Periodically: "how good have our calls been?" → the calibration report.

Do NOT use when:

- Nothing was decided yet — the journal records commitments, not musings.
- The prediction cannot be graded by reality ("the team will feel better") — sharpen it first or do not log it.
- The decision is trivial and reversible in an hour — journaling it costs more than it teaches.

## Workflow

1. **Log the decision with its falsifiable prediction.** What was chosen, what you predict will happen, how confident (0-100), and when to grade it:
   `$WB journal-log --decision "migrated CI to the managed platform" --prediction "weekly active pipelines on the new platform exceed 60% by the 90-day review" --confidence 75 --review-by 2027-02-10 --mind-changer "adoption stalls below 40% for three consecutive weeks"`
   The prediction is the discipline: if reality cannot grade it later, it is an aspiration, not a prediction.

2. **Resolve against reality when the date arrives — or reality answers early.** The grade is HIT, MISS or PARTIAL, and the lesson is what you would do differently:
   `$WB journal-resolve --id J1 --outcome HIT --lesson "the plugin spike de-risked the mobile build early; do the spike before the migration decision next time"`
   Resolve on evidence (the number, the event), never on hope ("it feels like it is working").

3. **Read the calibration report.** Hit rate versus claimed confidence, per band:
   `$WB journal-report`
   The mechanical verdict: average confidence minus hit rate over 15 points = overconfident. The bands tell you where the distortion lives — most people are honest at 60% and fictional at 90%.

4. **Feed it back.** An overconfidence flag changes the next round: spread your confidences wider, sharpen predictions to things reality can grade, and price the next decision off measured rates instead of feelings.

## Stop rules

- An OPEN entry past its review date is a debt to reality — the report lists it as overdue until resolved.
- Confidence without a review date is a mood; both fields are mandatory.
- Never resolve an entry "PARTIAL" to avoid the discomfort of MISS — the lesson attached to a MISS is the most valuable row in the journal.
- The journal grades predictions, not people; if it starts being used to grade people, it will start lying.

## Commands

| Command | Purpose |
|---|---|
| `journal-log` | Record the decision, its falsifiable prediction, confidence and review date |
| `journal-resolve` | Grade it HIT / MISS / PARTIAL against reality, with the lesson |
| `journal-report` | Calibration: hit rate vs confidence per band, overconfidence verdict, overdue entries |

## Files

- `references/journal-discipline.md` — what makes a journal entry worth grading, and the resolution honesty rules.
- `references/calibration.md` — how to read the bands, and why the 15-point gap threshold.
- `templates/decision-entry.md` — fillable journal entry skeleton (same fields the CLI emits).
- `examples/migration-decision.md` — three entries, one overdue, one overconfident band: a report with teeth.
