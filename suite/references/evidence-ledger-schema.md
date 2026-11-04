# Evidence & State Ledger Schemas

All deterministic state files live inside `.local-workbench/` (configurable via `--state-dir`). Every command returns JSON; exit codes are `0` OK/PASS, `2` FAIL, `1` error.

## 1. Research Ledger (`research_ledger.json`)

```json
{
  "topic": "Compare embedded analytical databases for local Python workloads",
  "mode": "deep-research",
  "max_queries": 12,
  "queries_executed": 2,
  "sub_questions": [
    {"id": "Q1", "question": "What are the licensing and concurrency models?", "status": "ANSWERED"},
    {"id": "Q2", "question": "What are the memory limits and benchmarks?", "status": "GAP_RECORDED"}
  ],
  "entities": ["DuckDB", "SQLite"],
  "query_log": [
    {
      "id": "QRY-1",
      "query": "DuckDB concurrency multiprocess file locking documentation",
      "sub_question_id": "Q1",
      "tool_used": "host-web-search",
      "executed_at": "2026-11-02T12:00:00+00:00"
    }
  ],
  "sources": {
    "S1": {
      "id": "S1",
      "url": "https://duckdb.org/docs/connect/concurrency",
      "canonical_url": "https://duckdb.org/docs/connect/concurrency",
      "title": "Concurrency - DuckDB Documentation",
      "publisher": "DuckDB Foundation",
      "published_date": "2026",
      "source_tier": "PRIMARY",
      "content_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "excerpt": "DuckDB supports two concurrency models: one process with read-write access, or multiple processes with read-only access.",
      "fetched_at": "2026-11-02T12:01:00+00:00"
    }
  },
  "claims": [
    {
      "id": "C1",
      "sub_question_id": "Q1",
      "entity": "DuckDB",
      "field": "process_concurrency",
      "statement": "DuckDB allows either a single read-write process or multiple read-only processes.",
      "value": "1 RW or N RO processes",
      "source_ids": ["S1"],
      "quote": "one process with read-write access, or multiple processes with read-only access",
      "quote_verified_in_excerpt": true,
      "confidence": "HIGH",
      "status": "VERIFIED",
      "created_at": "2026-11-02T12:02:00+00:00"
    }
  ],
  "gaps": [
    {
      "id": "G1",
      "sub_question_id": "Q2",
      "entity": "DuckDB",
      "field": "encrypted_swap_overhead",
      "description": "Official docs do not publish a fixed percentage overhead for encrypted spill-to-disk.",
      "queries_tried": ["DuckDB encrypted spill to disk benchmark overhead"],
      "reason": "NO_PUBLIC_SOURCE",
      "created_at": "2026-11-02T12:03:00+00:00"
    }
  ]
}
```

Additional keys: `fields` (wide-matrix columns), `time_sensitive` (enables recency penalties), `resolutions` (`"<entity>::<field>" -> {winner_claim, value, losing_claims, reason}`), and per-source `quality_score` / `quality_reasons` written by `research-score`. Claims whose quote is not found in the stored excerpt are rejected unless `--allow-unverified-quote` is passed, which forces `LOW` / `PROVISIONAL`.

## 2. Debug Ledger (`debug_ledger.json`)

Tracks root-cause hypotheses and enforces the 2-strike circuit breaker:
- `failed_attempts`: integer count of `FALSIFIED` hypotheses.
- `circuit_breaker_tripped`: boolean (`true` when `failed_attempts >= 2`).
- `hypotheses`: ordered array of `{id, statement, prediction, test_command, status, evidence, updated_at}`.
- `target_files`: files the user named; `scope-read --debug-scope` refuses anything else.
- `repro_command`: the command that reproduces the symptom.

## 3. Delivery Verification Record (`delivery_verification.json`)

Tracks observable verification levels:
- `achieved_level` follows the L0-L4 ladder: `L0` claimed only, `L1` artifact exists (`--artifact`), `L2` static checks (`--check L2:<cmd>`), `L3` execution (`--command` or `--check L3:<cmd>`), `L4` acceptance (`--check L4:<cmd>`).
- A level counts only if every declared check at that level passed and no lower declared level failed. Levels with no checks are listed in `levels_not_checked`.
- `verification_level` keeps the legacy labels: `L1_ARTIFACT_EXISTENCE_ONLY`, `L2_STATIC_VERIFIED`, `L3_EXECUTION_VERIFIED`, `L4_ACCEPTANCE_VERIFIED`, `L0_UNVERIFIED`, or `VERIFICATION_FAILED`.
- `git.head` / `git.dirty` record exactly which code was verified. Timeouts are recorded as exit `124` with `timed_out: true`.

## 4. Spec Ledger (`spec_ledger.json`, v3.0)

```json
{
  "title": "Verified CSV export for accountants",
  "goal": "Ship a verified CSV export of invoices for enterprise accountants",
  "non_goals": ["No PDF export in v1"],
  "stories": [
    {
      "id": "US1",
      "text": "As an accountant I export all unpaid invoices to CSV",
      "status": "SPECIFIED",
      "criteria": [
        {
          "id": "AC1",
          "story_id": "US1",
          "given": "an account with 3 unpaid invoices totaling 10.06",
          "when": "the accountant runs the CSV export",
          "then": "the CSV contains exactly 3 rows and the total column sums to 10.06"
        }
      ]
    }
  ],
  "tasks": [
    {"id": "T1", "task": "Implement the CSV serialization", "verifies": ["AC1"], "depends_on": [], "created_at": "..."}
  ]
}
```

Lifecycle: `spec-new` (goal >= 20 chars, `--force` restarts) -> `spec-criterion` (Given/When/Then, each >= 5 chars) -> `spec-task` (must `--verifies` existing criteria; `--depends-on` existing tasks) -> `spec-check` (PASS gate: complete GWT clauses, no cycles; warnings for uncovered criteria and missing non-goals).

## 5. Review Ledger (`review_ledger.json`, v3.0)

```json
{
  "title": "Billing export PR #142",
  "target": "PR #142: src/billing/export.py",
  "focus": ["correctness", "error-handling"],
  "findings": [
    {
      "id": "F1",
      "file": "src/billing/export.py",
      "line": 42,
      "severity": "BLOCKING",
      "category": "correctness",
      "description": "Totals are rounded per line before tax is applied",
      "suggestion": "Apply tax before rounding in _line_total()",
      "created_at": "..."
    }
  ]
}
```

Severities: `BLOCKING` / `MAJOR` / `MINOR` / `INFO`. Categories: `correctness`, `security`, `performance`, `maintainability`, `tests`, `style`. `review-report` renders REVIEW.md; its verdict is `FAIL` while any BLOCKING finding is open, `PASS_WITH_FINDINGS` with majors/minors, else `PASS`.

## 6. Knowledge Base Ledger (`kb_ledger.json`, v3.0)

```json
{
  "entries": [
    {
      "id": "K1",
      "question": "In which order does the billing export apply tax and rounding?",
      "answer": "Tax is applied per line before totals are rounded; mode HALF_UP.",
      "source_url": "https://example.com/billing/export-spec",
      "source_id": "",
      "tags": ["billing", "export"],
      "assumed": false,
      "confidence": "MEDIUM",
      "created_at": "..."
    }
  ]
}
```

Every entry is sourced (`source_url` or `source_id` validated against the research ledger) or explicitly `assumed` (LOW confidence). `kb-search` scores deterministic token overlap (tags x3, question x2, answer x1); `kb-export` renders grouped Markdown with visible ASSUMPTION markers.
