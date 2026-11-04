# Architecture & Operational Boundaries

## 1. Zero Hidden Vendor Dependencies
- This suite never connects to any proprietary research API, remote MCP endpoint, or paid background agent service.
- All reasoning, synthesis, and planning are executed by the model already active in your host (Claude Code, Codex, ZCode, Cursor, OpenCode, or any AGENTS.md-compatible agent).
- All state tracking, URL canonicalization, quote verification, and scope checks run locally via `scripts/workbench.py` using only the Python 3 standard library.

## 2. Conversation-First Advisory Rule
- When the user asks an architecture, design, strategy, or trade-off question (`local-advisor`, `decision-review`), the agent **must not** run `find`, `rg`, `grep`, `ls -R`, or glob searches across the machine.
- The agent answers from the conversation context first.
- Repository files are read **only** when the user explicitly names a file/directory or asks to inspect the current repository.

## 3. Strict Project-Root Containment
- When local file access is needed (`local-debug`, `code-review`, or repo-grounded `local-advisor`), file reads and searches must stay strictly inside the explicit `--project-root`.
- Parent traversal (`..`), symlinks pointing outside the repo, home directory sweeps (`~`), `.git/`, `node_modules/`, virtual environments, binary files, and secret files (`.env`, `.pem`, `.key`, `id_rsa`, `.aws`, `.ssh`) are blocked by `workbench.py scope-read` and `scope-scan`.

## 4. Two-Strike Debugging Circuit Breaker
- During debugging (`local-debug`), every hypothesis must be logged with a testable prediction before editing code.
- If **2 hypotheses** are falsified (`status=FALSIFIED`), the circuit breaker trips (`circuit_breaker_tripped=true`).
- Once tripped, the agent must stop guessing, refrain from widening its search scope, and report the falsified hypotheses and missing telemetry to the user.

## 5. Local Deep Research Discipline
- Search results and snippets are discovery leads, never final evidence.
- Every material claim requires:
  1. A registered source (`research-add-source`) from a fetched page or local document with a SHA-256 content hash.
  2. An atomic claim entry (`research-add-claim`) with a verbatim quote (`>= 10` characters) verified against the stored source excerpt.
- Unverified attributes in wide comparisons are recorded as explicit knowledge gaps (`research-add-gap`) and rendered as `n.a.` in tables — never guessed from model memory.

## 6. Testability and Verifiability Boundaries (v3.0)
- Work enters a plan only bound to an acceptance criterion (`spec-task --verifies`); `spec-check` PASS is the gate before implementation.
- Review verdicts are mechanical: `review-report` is FAIL while any BLOCKING finding is open, and every review declares what was **not** inspected.
- Delivery claims are level-bound: `verify-delivery` records the L0-L4 level actually observed, and wording never exceeds that level.
- Knowledge entries are sourced or explicitly marked `--assumed`; assumptions export visibly as unverified and are never quoted as fact.

## 7. Number-Grounded Data Analysis (v3.2)
- Analysis work starts by registering the exact file (`data-register`): path, byte size and SHA-256 are pinned in `data_ledger.json`, binding every later number to a dataset version.
- Every number presented to the user is logged as a finding (`data-finding`) that carries the re-runnable command, query or formula which produced it; a number without a method is rejected.
- What the file cannot answer is declared as a gap (`data-gap` with a reason), never guessed or interpolated.
- `data-report` lints the answer against the findings (`UNLEDGERED_NUMBERS`) and refuses to render numbers no finding supports; the `--allow-unverified-numbers` escape hatch publishes them visibly marked UNVERIFIED.
- Findings computed on content that no longer matches the registered hash are refused (`DATASET_DRIFT`) until the dataset is re-registered and the affected findings redone.
