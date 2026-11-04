# Listing templates and instantiating one

`artifact-list` shows every template with its purpose; `artifact-new` instantiates one with TITLE and DATE filled and reports the remaining placeholders.

```bash
$ python3 scripts/workbench.py artifact-list
```

```json
{
  "status": "OK",
  "templates": [
    {
      "type": "data-schema",
      "file": "skills/artifact-studio/templates/data-schema.md",
      "purpose": "Data schema: field-level design for a dataset, API payload or storage format"
    },
    {
      "type": "executive-summary",
      "file": "skills/artifact-studio/templates/executive-summary.md",
      "purpose": "Executive summary: one-page distillation of a report or decision for leadership"
    },
    {
      "type": "incident-postmortem",
      "file": "skills/artifact-studio/templates/incident-postmortem.md",
      "purpose": "Incident postmortem: blameless timeline, mechanism-level cause analysis and owned action items"
    },
    {
      "type": "presentation-outline",
      "file": "skills/artifact-studio/templates/presentation-outline.md",
      "purpose": "Presentation outline: turns a report into a talk with one message per slide"
    },
    {
      "type": "technical-report",
      "file": "skills/artifact-studio/templates/technical-report.md",
      "purpose": "Technical report: structured analysis with context, findings, evidence and recommendations"
    }
  ]
}
```

Every template's first line is an HTML comment stating its purpose — that is what `artifact-list` reads.

```bash
$ python3 scripts/workbench.py artifact-new --type technical-report \
  --title "Batch pipeline postmortem" --output docs/batch-postmortem.md
```

```json
{
  "status": "OK",
  "artifact": "docs/batch-postmortem.md",
  "type": "technical-report",
  "placeholders_left": [
    "AUTHOR",
    "DRAFT_FINAL",
    "FINDING_1_EVIDENCE_AND_REASONING_WITH_CITATIONS",
    "FINDING_1_TITLE",
    "FINDING_2_EVIDENCE_AND_REASONING_WITH_CITATIONS",
    "FINDING_2_TITLE",
    "HOW_THE_ANSWER_WAS_PRODUCED_SEARCHES_COMMANDS_ANALYSES",
    "JUSTIFICATION_LINKED_TO_FINDINGS",
    "L0_L4",
    "LEDGER_OR_DOCUMENT_LIST",
    "RECOMMENDATION_1",
    "RECOMMENDATION_2",
    "RISK_1_WITH_SEVERITY_AND_MITIGATION",
    "RISK_2_WITH_SEVERITY_AND_MITIGATION",
    "THREE_TO_FIVE_SENTENCE_ANSWER_WITH_TOP_EVIDENCE",
    "VERIFICATION_COMMANDS",
    "WHAT_IS_COVERED",
    "WHAT_IS_EXPLICITLY_EXCLUDED",
    "WHAT_QUESTION_THIS_REPORT_ANSWERS",
    "WHAT_REMAINS_UNANSWERED"
  ]
}
```

`placeholders_left` is the contract: the delivered document has none of them left. Fill each with real content (or delete the section deliberately), then confirm the list is empty before delivery.

