# Synthesis Rules: how the panel verdict is counted

`panel-synth` does not negotiate. It counts stances, applies the rules below,
and renders `PANEL.md`. Every rule exists to prevent a specific way panels
launder disagreement — read them as the panel's constitution.

## The verdict table

| Condition | Verdict | Status |
|-----------|---------|--------|
| oppose = 0 and conditional = 0 | `UNANIMOUS_SUPPORT` | PASS |
| oppose = 0, conditional ≥ 1 | `SUPPORT_WITH_CONDITIONS` | WARN |
| oppose ≥ 1 and support > oppose | `MAJORITY_SUPPORT_WITH_DISSENT` | WARN |
| everything else (support ≤ oppose) | `SPLIT_PANEL` | WARN |

PASS requires more than a unanimous count: no unbacked mandated seats and no
unanswered cross-examinations. Anything the reader should act on before
trusting the report downgrades the status to WARN.

## The rules, and the failure each prevents

1. **A split stays a split.** Averaging opposing opinions into "consensus" is
   how panels manufacture agreement nobody signed. A `SPLIT_PANEL` report
   refuses to emit a joint recommendation; it renders the map of the split
   (who wants what, on which grounds) and hands it to `decision-review`,
   because resolving a real disagreement needs a decision process, not a
   vote.
2. **Dissent stays on the record.** In `MAJORITY_SUPPORT_WITH_DISSENT` the
   minority opinion is printed in full in a "Dissent on the record" section —
   not summarized into "some concerns were raised".
3. **The finance dissent is never buried.** If the finance seat opposes, the
   verdict — whatever it is — carries `finance_dissent: true` and the report
   carries a dedicated section: the arithmetic must be answered before the
   recommendation is acted on, even when every other seat supports.
4. **Conditions are gates, not footnotes.** In `SUPPORT_WITH_CONDITIONS` the
   named conditions ARE the recommendation; the report lists each with its
   seat. A condition that cannot be observed was already refused at
   `panel-voice`.
5. **Unbacked claims are named.** A skeptic or finance voice without cited
   evidence cannot happen through the command gate — but if a ledger was
   hand-edited into that state, synthesis flags it as an unbacked claim.
6. **Unanswered challenges stay OPEN.** A cross-examination without a
   response is not resolved by silence; it appears in the report as an open
   challenge and forces the WARN status.

## Coverage gate

Synthesis refuses to run until every convened seat has spoken
(`PANEL_INCOMPLETE`, exit 2). A five-seat panel with four opinions is not a
panel verdict; it is four opinions wearing one. If a seat has nothing to say,
that itself is a stance — have it speak its abstention reasoning or remove
the seat at convening time.

## What synthesis does NOT do

- It does not weight seats (no seat outranks another in the count; the
  finance veto is visibility, not extra votes).
- It does not average confidences. Confidence is recorded per voice and shown
  as calibration context next to each stance.
- It does not pick between options. Picking is `decision-review`'s job; this
  skill's job is to make sure the picker sees every disciplined angle first.

## Handoffs (rendered into every report)

- A dissent that must be answered before acting → `devil-advocate`: turn the
  dissent's strongest point into a challenge with a named defeater.
- A split panel → `decision-review`: score the positions on weighted
  criteria and decide.
- The final call → `decision-journal`: log it with a falsifiable prediction,
  confidence and a review date.
