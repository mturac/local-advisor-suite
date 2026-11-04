# State Inventory: `.local-workbench/`

Every file the runtime writes, what it is for, and who reads it. The directory stays out of version control; it is session state, not project state.

| File | Written by | Read by | Contents |
|---|---|---|---|
| `advisory_intake.json` | `advise-intake` | advisory answers | Question, context, constraints, non-goals, mode |
| `research_ledger.json` | `research-*`, `wide-table` | status/gaps/pack, audit, handoff | Topic, sub-questions, query log, sources (with SHA-256), claims (with quotes), gaps, resolutions |
| `debug_ledger.json` | `debug-hypothesis` | `scope-read --debug-scope`, `debug-report`, handoff | Symptom, target files, repro, hypotheses, circuit breaker state |
| `delivery_verification.json` | `verify-delivery` | handoff | Last verification: level, commands, outcomes, git snapshot |
| `spec_ledger.json` | `spec-*` | `spec-check`, handoff | Goal, stories, acceptance criteria (Given/When/Then), tasks with `verifies` links |
| `review_ledger.json` | `review-*` | `review-report`, handoff | Review target, focus, severity-graded findings |
| `kb_ledger.json` | `kb-*` | `kb-search`, `kb-export` | Sourced or assumed Q&A entries with tags |
| `evidence_pack.md` | `research-pack` | synthesis | Claims + quotes + citations grouped by sub-question |
| `HANDOFF.md` | `handoff-pack` | `handoff-check`, the next session | The seven-section handoff |
| `DEBUG_REPORT.md` | `debug-report` | the user / escalation | Root-cause report or escalation brief |
| `REVIEW.md` | `review-report` | the user | Review findings + verdict |
| `KNOWLEDGE_BASE.md` | `kb-export` | anyone | Rendered knowledge base |
| `fetch_cache/*.json` | `fetch-url` | `fetch-url` | Cached fetched pages (cleaned text, hash, date) |

## Lifecycle rules

- **Ledgers accumulate within a work item.** `research-init` starts a fresh research ledger; `spec-new --force` restarts a spec. Do not hand-delete ledger files to "clean up" — the IDs and history are the audit trail.
- **Parallel work streams get separate `--state-dir` values** (e.g. `.local-workbench-research/`, `.local-workbench-debug/`). One directory = one coherent state.
- **Reports (`evidence_pack.md`, `HANDOFF.md`, ...) are regenerable** from their ledgers. Delete freely; regenerate with the command that wrote them.
- **Cache is disposable** but useful: repeat reads of the same URL come from disk, saving fetches. `fetch-url --no-cache` bypasses it.

## What never lives here

- Secrets of any kind (the runtime refuses to read them from your project; it certainly does not store them).
- Anything meant for version control: deliverables go to `docs/`, reports to the repo, state stays here.
- Other tools' state. If a host writes its own session files, they live in the host's directories, not here.
