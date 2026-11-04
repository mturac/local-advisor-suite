# Advisory intake for an architecture question

Recorded intake for a service-extraction question. The answer that follows works from this brief alone — no repository scan.

```bash
$ python3 scripts/workbench.py advise-intake \
  --question "Should we move billing into a separate service?" \
  --context "Monolith, 4 engineers, weekly deploys, billing is 12% of the codebase" \
  --constraint "No new infrastructure budget this year" \
  --non-goal "Not rewriting the invoicing domain" \
  --mode architecture
```

```json
{
  "status": "OK",
  "artifact": ".local-workbench/advisory_intake.json",
  "policy": "CONVERSATION_FIRST: Do not scan local files unless requires_repo_inspection=true and the user named a target path or error.",
  "intake": {
    "question": "Should we move billing into a separate service?",
    "context_summary": "Monolith, 4 engineers, weekly deploys, billing is 12% of the codebase",
    "constraints": [
      "No new infrastructure budget this year"
    ],
    "non_goals": [
      "Not rewriting the invoicing domain"
    ],
    "mode": "architecture",
    "requires_repo_inspection": false,
    "created_at": "2026-11-04T09:52:18+00:00"
  }
}
```

The intake pins the question, constraints and non-goals. The advisory answer then follows `references/answer-standards.md`: recommendation first, options with real trade-offs, reversibility, and a confidence label — answered from the conversation, with at most one precise clarifying question if a fact would change the recommendation.

