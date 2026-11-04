# Packing and checking a PARTIAL session

A PARTIAL pack whose evidence section is auto-filled from the ledgers (research, debug, verification), followed by the check that validates it.

```bash
$ python3 scripts/workbench.py handoff-pack --title "Billing export v1" --session-status PARTIAL \
  --summary "CSV export implemented; tax-before-rounding fixed and verified at L3; pagination pending" \
  --completed "Export endpoint implemented" \
  --next-step "Add pagination for >10k invoices" \
  --next-step "Run the accountant's manual flow (L4)" \
  --decision "Tax applied per line before totals are rounded" \
  --open-question "Do credit notes need a separate export?"
```

```json
{
  "status": "OK",
  "handoff_file": ".local-workbench/HANDOFF.md",
  "session_status": "PARTIAL"
}
```

Section 5 (Evidence & Verification Snapshot) is generated from the actual ledgers — the numbers of sources, claims, falsified hypotheses and the last verification level are read, not remembered.

```bash
$ python3 scripts/workbench.py handoff-check
```

```json
{
  "status": "PASS",
  "file": ".local-workbench/HANDOFF.md",
  "problems": [],
  "warnings": []
}
```

PASS: all seven sections present, PARTIAL status carries next steps. Warnings would appear for a handoff older than 72h or a git HEAD that moved since packing — both are instructions to re-verify before trusting the state.

