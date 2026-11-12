# Panel Roles: the seats, their lenses, their mandated fields

A seat is not a costume. Each built-in seat exists because its lens catches a
class of failure the others structurally miss, and each one must bring the
field its role mandates — that field is what `panel-voice` enforces and what
makes the opinion the seat's own rather than a paraphrase of the question.

## The five default seats

| Seat | Lens (what only this seat sees) | Mandated fields |
|------|--------------------------------|-----------------|
| `operator` | Execution and delivery — can this ship with the people, time and tooling that exist? | `--path`: the first concrete execution step, with an owner in mind |
| `skeptic` | Risk and failure modes — what breaks first, and which signal says so early? | `--risk`: the named risk, checkable; `--trigger`: the early-warning signal; plus cited `--evidence` |
| `visionary` | Opportunity and upside — what does this make possible that nothing else on the table does? | `--opportunity`: the concrete upside, not a mood |
| `customer-advocate` | User impact — whose life changes, in which direction, by how much? | `--impact`: a segment and its change, not "users" |
| `finance` | The numbers — cost, revenue, payback; arithmetic needs an anchor | `--number`: a digit-bearing anchor; plus cited `--evidence` |

## Why each mandated field exists

- **Operator / path**: opinions without a first step are applause. The path
  forces the operator to have thought about who does the first thing.
- **Skeptic / risk + trigger**: a risk with no early-warning signal cannot be
  monitored, only feared. The trigger is what turns the risk into something
  the plan can watch for and react to. Evidence is mandatory for this seat
  because "I feel this is risky" is the exact failure mode panels exist to
  prevent.
- **Visionary / opportunity**: "strategic value" is not an upside. The seat
  must name what becomes possible — a capability, a market, a position.
- **Customer-advocate / impact**: "users will be happier" names no user. The
  seat must name a segment and the direction and rough size of its change.
- **Finance / number + evidence**: this seat does arithmetic, and arithmetic
  without an anchor is decoration. At least one digit, cited to evidence on
  the table.

## Good and bad examples (skeptic seat)

Bad (refused): `--risk "it might not work out" --reasoning "seems risky to me"`
— no trigger, no evidence, no mechanism; a mood, not a risk.

Good (accepted): `--risk "top-20 accounts sit in the exact price band this
raise hits" --trigger "two canary accounts request data export in week one"
--evidence EV1 --reasoning "the reference class for ten-dollar raises on
small SaaS shows churn spiking in the first renewal cycle; we have no cohort
data to argue ours differs"` — a named risk someone could check, a signal
someone could watch, and evidence on the table.

## Independence discipline

- **One seat, one voice**: a seat speaks once (`--force` to replace its
  opinion; the replacement is the record).
- **No shared speeches**: `panel-voice` computes token overlap between the new
  opinion and every recorded one; overlap above 0.8 is refused as
  `DUPLICATE_VOICE`. Two seats reading the same speech is theater, not
  perspective. Argue from the seat's own lens.
- **Conditional stances name their condition**: "support, if..." must say the
  observable if. A condition that cannot be observed is a hedge.

## Custom seats

`panel-open --roles operator,skeptic,legal,security` convenes a custom board.
Built-in seats keep their enforced fields; custom seats answer to the
convenor: name their lens in one line when convening, keep it consistent for
the whole session, and hold them to the same standards (independent reasoning,
named specifics, evidence for claims that run on numbers). Good custom seats
are disciplines (legal, security, compliance, partner-lead), not outcomes
("growth-seat", "yes-seat") — a seat named after the desired answer is a
stacked jury.

## Confidence

`--confidence` (0-100) is the seat's own calibration, recorded per voice and
shown in the report. It is not averaged into the verdict — the verdict counts
stances — but a high-confidence dissent or a low-confidence support is exactly
the signal a reader should see next to the stance.
