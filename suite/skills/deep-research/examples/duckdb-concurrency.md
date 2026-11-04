# A research ledger with a contradiction and its resolution

A condensed real run continuing the same ledger: a third source creates a contradiction on the same (entity, field), which is then resolved on the record, scored, and packed. In a live session the pages are fetched with the host's tools and saved with `--content-file`.

```bash
$ python3 scripts/workbench.py research-log-query --query "2024 DuckDB benchmark single process limitation" --sub-question-id Q1
```

```json
{
  "status": "OK",
  "query_entry": {
    "id": "QRY-2",
    "query": "2024 DuckDB benchmark single process limitation",
    "sub_question_id": "Q1",
    "tool_used": "host-native-search",
    "executed_at": "2026-11-04T09:52:20+00:00"
  },
  "queries_executed": 2,
  "queries_remaining": 1
}
```

```bash
$ python3 scripts/workbench.py research-add-source --url https://example.com/2024-duckdb-benchmark \
  --title "2024 benchmark notes" --tier TERTIARY --published-date 2024 --content-file oldblog.txt
```

```json
{
  "status": "OK",
  "source_id": "S2",
  "deduplicated": false,
  "canonical_url": "https://example.com/2024-duckdb-benchmark",
  "content_sha256": "81467cac123b062f9ed23934daf12cf006eb51dc61e7ff0ddbbbada31e6baea2"
}
```

The tertiary blog is registered because it is about to create a contradiction — contradictions are resolved on the record, not ignored.

```bash
$ python3 scripts/workbench.py research-add-claim --sub-question-id Q1 --entity DuckDB --field process_concurrency \
  --statement "Only a single external process can open the database file" \
  --value "single process only" --source-id S2 \
  --quote "only a single external process opening the database file" --confidence LOW
```

```json
{
  "status": "OK",
  "claim_id": "C2",
  "quote_verified_in_excerpt": true,
  "claim": {
    "id": "C2",
    "sub_question_id": "Q1",
    "entity": "DuckDB",
    "field": "process_concurrency",
    "statement": "Only a single external process can open the database file",
    "value": "single process only",
    "source_ids": [
      "S2"
    ],
    "quote": "only a single external process opening the database file",
    "quote_verified_in_excerpt": true,
    "confidence": "LOW",
    "status": "VERIFIED",
    "created_at": "2026-11-04T09:52:20+00:00"
  }
}
```

```bash
$ python3 scripts/workbench.py research-status
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/research_ledger.json",
  "topic": "DuckDB external process concurrency model",
  "queries_executed": 2,
  "max_queries": 3,
  "sources_count": 2,
  "claims_count": 2,
  "gaps_count": 0,
  "unresolved_sub_questions": [],
  "contradictions": [
    {
      "entity": "DuckDB",
      "field": "process_concurrency",
      "values": [
        "1 RW or N RO",
        "single process only"
      ],
      "claim_ids": [
        "C1",
        "C2"
      ]
    }
  ],
  "resolved_contradictions": [],
  "weak_sub_questions": [],
  "ready_to_synthesize": false
}
```

The contradiction is visible: same (entity, field), two different normalized values. It blocks `ready_to_synthesize` until resolved.

```bash
$ python3 scripts/workbench.py research-resolve --entity DuckDB --field process_concurrency \
  --winner-claim C1 \
  --reason "C1 cites the current official documentation; C2's source describes the older 2024 behavior and is TERTIARY"
```

```json
{
  "status": "OK",
  "entity": "DuckDB",
  "field": "process_concurrency",
  "winner_claim": "C1",
  "value": "1 RW or N RO",
  "superseded_claims": [
    "C2"
  ]
}
```

The reason is part of the record: scope, date, tier — why the winner wins.

```bash
$ python3 scripts/workbench.py research-score
```

```json
{
  "status": "OK",
  "time_sensitive": false,
  "sources": [
    {
      "source_id": "S1",
      "domain": "duckdb.org",
      "tier": "PRIMARY",
      "published_date": "2026",
      "quality_score": 4.0,
      "reasons": [
        "tier PRIMARY base 4"
      ]
    },
    {
      "source_id": "S2",
      "domain": "example.com",
      "tier": "TERTIARY",
      "published_date": "2024",
      "quality_score": 2.0,
      "reasons": [
        "tier TERTIARY base 2"
      ]
    }
  ],
  "low_quality": [
    "S2"
  ]
}
```

Each source carries its 0-5 score and the reasons for every adjustment (tier base, domain trust, excerpt length, recency).

```bash
$ python3 scripts/workbench.py research-pack
```

```json
{
  "status": "OK",
  "evidence_pack": ".local-workbench/evidence_pack.md",
  "claims": 2,
  "gaps": 0
}
```

The pack is the synthesis boundary: claims, quotes and citations grouped by sub-question, with superseded claims marked. The report is written from this file only, then audited with `audit-report`.

