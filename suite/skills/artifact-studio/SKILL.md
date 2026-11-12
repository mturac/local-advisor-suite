---
name: artifact-studio
description: Instantiates deliverable templates — technical reports, executive summaries, ADRs, presentation outlines, data schemas and postmortems — with enforced structure and placeholder tracking; use when the user asks for a structured document skeleton they will fill in, or to see which artifact types exist.
license: MIT
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.2"
---

# Artifact Studio

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Start a deliverable from a template that already has the right skeleton: sections in the right order, placeholders named, and a first-line comment stating the template's purpose.

## When to use

- The user asks for "a report / summary / outline / schema / postmortem" and will fill in or review the content.
- A workflow needs its output to follow a known structure (a postmortem after `local-debug` escalation, an exec summary after `deep-research`).

Do NOT use to bypass evidence: a research report's facts still come from the ledger (`deep-research`), and ADRs come from `decision-review`. This skill provides structure, not content.

## Workflow

1. **See what exists:**

   ```bash
   $WB artifact-list
   ```

   Each template lists its type, file and purpose.

2. **Instantiate:**

   ```bash
   $WB artifact-new --type technical-report --title "Batch pipeline postmortem" --output docs/batch-postmortem.md
   ```

   `{{TITLE}}` and `{{DATE}}` are filled; everything else stays as a named placeholder.

3. **Fill deliberately.** The result reports `placeholders_left` — the list of what you still owe. Fill them in the document; do not leave `{{...}}` markers in anything you deliver.

4. **Match the template to the workflow:**

   | Template | Use it after / with |
   |---|---|
   | `technical-report` | any substantial written analysis |
   | `executive-summary` | distilling research or a decision for leadership |
   | `presentation-outline` | turning a report into a talk |
   | `data-schema` | designing a data model or API payload |
   | `incident-postmortem` | after an incident or an escalated debug case |

## Guardrails

- **No placeholder survives delivery.** `placeholders_left` is a contract: anything still listed means the document is a draft.
- **Structure is not substance.** A perfectly-shaped report with uncited facts still fails `evidence-audit`.
- **Overwrite protection**: writing to an existing path requires `--force` — a deliberate act, not an accident.

## Commands

| Command | Purpose |
|---|---|
| `artifact-list` | List available templates with purposes |
| `artifact-new --type T --title X --output F` | Instantiate template T (fills TITLE/DATE, reports placeholders) |

## Output expectation

A skeleton document with the right sections, named placeholders for what is owed, and zero `{{...}}` markers by the time it is delivered.

## References

- `references/writing-standards.md` — the writing rules that apply inside every template.

## Example

- `examples/new-technical-report.md` — listing templates and instantiating one.
