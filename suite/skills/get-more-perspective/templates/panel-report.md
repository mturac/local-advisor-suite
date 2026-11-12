<!-- Purpose: manual panel report for hosts running the skill without the
     workbench runtime. When the runtime is present, panel-synth renders
     PANEL.md automatically; use this template only for by-hand panels,
     keeping the same section order so reports stay comparable. -->

# Panel Report: {the question before the panel}

**Context**: {options on the table, constraints, what is already decided}

## The panel

| Seat | Lens | Spoke |
|------|------|-------|
| operator | execution and delivery | yes |
| skeptic | risk and failure modes | yes |
| visionary | opportunity and upside | yes |
| customer-advocate | user impact | yes |
| finance | the numbers | yes |

<!-- One row per convened seat, custom seats included. A NO in the Spoke
     column means the panel is incomplete — do not synthesize. -->

## Evidence on the table

- **EV1** [via] "{verbatim quote}" — {source URL or "(from conversation)"}

<!-- Every entry: a real quote, not a paraphrase, with where it was seen.
     The skeptic and finance voices below cite these labels. -->

## Independent opinions

### {seat} — {SUPPORT / OPPOSE / CONDITIONAL} (confidence {0-100})

- **{role-mandated field}**: {path / risk+trigger / opportunity / impact / number}
- **evidence**: {EV labels, if cited}

{the seat's own reasoning, argued from its lens — not a paraphrase of the
 question, not a restatement of another seat's opinion}

<!-- Repeat per seat. Conditional stances add: **condition**: {the observable
     state support depends on}. -->

## Cross-examination

- **X1** {from-seat} → {to-seat}: {the challenge}
  - {to-seat} answers: {the response}
  - or: **OPEN** — {to-seat} has not answered this challenge.

## Where the panel stands

{support count} support · {conditional count} conditional · {oppose count} oppose

## Panel verdict: {UNANIMOUS_SUPPORT / SUPPORT_WITH_CONDITIONS / MAJORITY_SUPPORT_WITH_DISSENT / SPLIT_PANEL}

<!-- Apply the synthesis rules verbatim:
     - oppose=0, conditional=0 → UNANIMOUS_SUPPORT
     - oppose=0, conditional≥1 → SUPPORT_WITH_CONDITIONS (conditions are gates)
     - support>oppose → MAJORITY_SUPPORT_WITH_DISSENT (dissent in full below)
     - otherwise → SPLIT_PANEL (no joint recommendation — render the split map)
     Finance opposing sets finance_dissent=true in any verdict. -->

### Dissent on the record

- **{seat}** opposes: {full reasoning}

### Conditions named

- **{seat}**: {the named condition}

### Unanswered challenges

- {X id}: {from} → {to} — {challenge}

## Handoffs

- Dissent to answer before acting → `devil-advocate`
- Split to resolve → `decision-review`
- Final call to log → `decision-journal`
