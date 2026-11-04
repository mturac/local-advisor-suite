<!-- BEGIN LOCAL-ADVISOR-SUITE RULES -->
## Local Advisor & Research Operating Rules

1. **Conversation-First Advisory (`local-advisor`, `decision-review`)**:
   - Answer architecture, design, planning, and trade-off questions directly from the conversation context first.
   - NEVER scan local directories, run broad `find`/`rg`/`grep` sweeps, or inspect unrelated files unless the user explicitly names a file path or asks to inspect this repository.

2. **Strict Repository Scope (`local-debug`, `code-review`)**:
   - Restrict all file reads and code searches strictly to the current project root.
   - Never traverse `..`, follow external symlinks, or read `.env`, SSH keys, or credential files.
   - Stop after **2 falsified debugging hypotheses** and report the evidence instead of guessing or widening search scope.

3. **Zero External Vendor Lock-In (`web-search`, `deep-research`, `wide-search`)**:
   - Never call third-party research APIs or MCP servers the user did not configure, and never switch search providers silently.
   - Use only the host environment's native search/fetch tools or user-supplied documents, and record every source, verbatim quote, and knowledge gap in `.local-workbench/research_ledger.json`.
   - Separate "file created" (`L1`) from "tests/commands verified" (`L3`).

4. **Testability and Verdicts (`spec-builder`, `code-review`, `delivery-verify`)**:
   - No task enters a plan without a verifying acceptance criterion; `spec-check` PASS gates implementation.
   - A review verdict is FAIL while any BLOCKING finding is open; declare what was not reviewed.
   - Report the achieved verification level and never claim wording above it.
<!-- END LOCAL-ADVISOR-SUITE RULES -->
