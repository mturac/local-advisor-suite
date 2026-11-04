<!-- local-advisor-suite:start -->
## Local Advisor Suite: operating rules

These rules apply to every task in this project. Skills live in `.agents/skills/` (Codex), `.zcode/skills/` (ZCode), or are installed as the `local-advisor-suite` plugin. Codex and ZCode pick a skill when its description matches; invoke one explicitly with `$<skill>` or `/skills`. OpenCode loads skills through its native `skill` tool (`skill({ name: "<skill>" })`). The workbench runtime is:

```bash
WB="python3 {{WORKBENCH}}"
```

State is written to `.local-workbench/` (keep it out of version control). After any change to this project, `$WB doctor --project-root .` verifies the installation is still healthy.

### Route the request

| The user wants | Use skill | First command |
|---|---|---|
| Advice, design review, "what should I do", architecture or planning help | `local-advisor` | none (answer from the conversation) |
| Choose between options, an ADR, a trade-off matrix, a pre-mortem | `decision-review` | `$WB decision-score --spec-file decision.json` |
| A bug, failing test or stack trace in a named file | `local-debug` | `$WB debug-hypothesis --symptom ... --target-file ... --repro ...` |
| One factual answer that needs 1-3 sources (version, price, limit, date) | `web-search` | host search tool |
| Research with several sources and a synthesis | `deep-research` | `$WB research-init --topic ... --sub-question ...` |
| Compare many entities across the same fields, as a table | `wide-search` | `$WB research-init --mode wide-matrix --entity ... --field ...` |
| Check a draft's sources, numbers and claims | `evidence-audit` | `$WB audit-report --report-file FILE` |
| Prove that a change works before saying "done" | `delivery-verify` | `$WB verify-delivery --check L2:... --command ...` |
| Write a report, ADR, executive summary, slide outline or data schema | `artifact-studio` | `$WB artifact-new --type ... --title ... --output ...` |
| End, switch tools, delegate or resume work | `session-handoff` | `$WB handoff-pack ...` / `$WB handoff-check` |
| Turn a request into a testable spec with acceptance criteria | `spec-builder` | `$WB spec-new --goal ... --story ... --non-goal ...` |
| A structured, severity-graded review of named files or a diff | `code-review` | `$WB review-init --title ... --target ...` |
| Save, find and reuse reusable project knowledge as sourced Q&A | `knowledge-capture` | `$WB kb-add --question ... --answer ... --source-url ...` |

### Do not scan by default

1. Answer advisory questions from the conversation. Do not list directories, run recursive `find`/`rg`/`grep`, or open files the user did not name.
2. Read a file only when the user names it or explicitly asks you to inspect the project. Use `$WB scope-read` (project root only, line range, no secrets).
3. Never read `.env*`, keys, credential stores, `~/.ssh`, `~/.aws`, or anything outside the project root.
4. If missing context blocks a good answer, ask one precise question instead of searching for it.

### Stop rules

- Debugging: stop after 2 falsified hypotheses; run `$WB debug-report` and ask for the missing information.
- Research: stop at the query budget; record remaining gaps instead of continuing silently.
- Specs: no task enters the plan unless it verifies at least one acceptance criterion (`spec-check` must PASS before implementation starts).
- Reviews: the verdict is FAIL while any BLOCKING finding is open; never merge over it.
- Any loop of the same failing action twice: stop, report what was tried and what is needed.

### Evidence discipline

- Use only the host's own permitted web tools or documents the user supplied. Do not add search providers, API keys or MCP servers the user did not configure.
- A search result is a lead. Cite a page only after opening it; quote it verbatim in the ledger.
- Every researched fact in a deliverable carries an inline link named after the publisher or document. Never "source", "here" or a raw URL.
- Run `$WB audit-report --report-file FILE` before delivering research. Deliver only on PASS.
- Never fill a gap from memory. Write `n.a.` and record the gap.
- Knowledge entries are sourced or explicitly marked `--assumed`; never present an assumption as a fact.

### Verification ladder

| Level | Meaning | Allowed wording |
|---|---|---|
| L0 | Nothing ran | "changed, not verified" |
| L1 | Files exist | "written, not executed" |
| L2 | Compiles, type-checks, lints | "compiles; tests not run" |
| L3 | Tests or program ran, exit 0 | "tests pass" |
| L4 | The user's acceptance criterion checked | "your case now works" |

Run `$WB verify-delivery` and report the achieved level, the commands and what was not run. Never say "done", "fixed" or "tested" above the level you observed.

### Handoff

Before ending a session, switching between hosts (Claude Code, Codex, ZCode, Cursor, OpenCode), or delegating: `$WB handoff-pack ...` then `$WB handoff-check`. When resuming: `$WB handoff-check`, read `.local-workbench/HANDOFF.md`, start with the first unchecked next step.
<!-- local-advisor-suite:end -->
