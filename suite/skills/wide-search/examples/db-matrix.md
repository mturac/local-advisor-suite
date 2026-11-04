# A 2-entity matrix with a resolved conflict and a gap

Wide-matrix mode on a fresh ledger: claims carry (entity, field) and land in cells; a conflict on one cell is resolved; another cell is declared `n.a.` with its attempted queries.

```bash
$ python3 scripts/workbench.py research-init --mode wide-matrix \
  --topic "Embedded analytical DBs compared" \
  --entity DuckDB --entity SQLite \
  --field process_concurrency --field writer_model \
  --max-queries 6
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/research_ledger.json",
  "topic": "Embedded analytical DBs compared",
  "max_queries": 6,
  "sub_questions": [],
  "entities": [
    "DuckDB",
    "SQLite"
  ]
}
```

```bash
$ python3 scripts/workbench.py research-add-source \
  --url https://duckdb.org/docs/connect/concurrency \
  --title "Concurrency - DuckDB Documentation" --tier PRIMARY --published-date 2026 \
  --content-file page.txt
```

```json
{
  "status": "OK",
  "source_id": "S1",
  "deduplicated": false,
  "canonical_url": "https://duckdb.org/docs/connect/concurrency",
  "content_sha256": "61819c70bc7591eca2f068c1f754aed878c2f521fc0e56b24fffa78cf780a14e"
}
```

S1 registered from the opened DuckDB docs page. S2 (SQLite docs) and S3 (the 2024 benchmark blog) are registered the same way before their cells are claimed.

{
  "status": "OK",
  "source_id": "S2",
  "deduplicated": false,
  "canonical_url": "https://sqlite.org/whentouse.html",
  "content_sha256": "5ecdfa3bd59f65c183481c0a381f36a8b4bdba371ebecaf5f5090703553d2110"
}

{
  "status": "OK",
  "source_id": "S3",
  "deduplicated": false,
  "canonical_url": "https://example.com/2024-duckdb-benchmark",
  "content_sha256": "81467cac123b062f9ed23934daf12cf006eb51dc61e7ff0ddbbbada31e6baea2"
}

```bash
$ python3 scripts/workbench.py research-add-claim --entity DuckDB --field process_concurrency \
  --statement "DuckDB allows one read-write process or multiple read-only processes" \
  --value "1 RW or N RO" --source-id S1 \
  --quote "one process with read-write access, or multiple processes with read-only access"
```

```json
{
  "status": "OK",
  "claim_id": "C1",
  "quote_verified_in_excerpt": true,
  "claim": {
    "id": "C1",
    "sub_question_id": "",
    "entity": "DuckDB",
    "field": "process_concurrency",
    "statement": "DuckDB allows one read-write process or multiple read-only processes",
    "value": "1 RW or N RO",
    "source_ids": [
      "S1"
    ],
    "quote": "one process with read-write access, or multiple processes with read-only access",
    "quote_verified_in_excerpt": true,
    "confidence": "HIGH",
    "status": "VERIFIED",
    "created_at": "2026-11-04T09:52:21+00:00"
  }
}
```

```bash
$ python3 scripts/workbench.py research-add-claim --entity DuckDB --field process_concurrency \
  --statement "Only a single external process can open the database file" \
  --value "single process only" --source-id S3 \
  --quote "only a single external process opening the database file"
```

```json
{
  "status": "OK",
  "claim_id": "C2",
  "quote_verified_in_excerpt": true,
  "claim": {
    "id": "C2",
    "sub_question_id": "",
    "entity": "DuckDB",
    "field": "process_concurrency",
    "statement": "Only a single external process can open the database file",
    "value": "single process only",
    "source_ids": [
      "S3"
    ],
    "quote": "only a single external process opening the database file",
    "quote_verified_in_excerpt": true,
    "confidence": "HIGH",
    "status": "VERIFIED",
    "created_at": "2026-11-04T09:52:21+00:00"
  }
}
```

```bash
$ python3 scripts/workbench.py research-resolve --entity DuckDB --field process_concurrency --winner-claim C1 \
  --reason "C1 cites current official docs; C3's 2024 tertiary source describes superseded behavior"
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

```bash
$ python3 scripts/workbench.py research-add-gap --entity DuckDB --field writer_model \
  --description "No documented coordination guarantee for concurrent external writers; left to the application" \
  --query-tried "DuckDB external writer coordination" --reason NO_PUBLIC_SOURCE
```

```json
{
  "status": "OK",
  "gap_id": "G1",
  "gap": {
    "id": "G1",
    "sub_question_id": "",
    "entity": "DuckDB",
    "field": "writer_model",
    "description": "No documented coordination guarantee for concurrent external writers; left to the application",
    "queries_tried": [
      "DuckDB external writer coordination"
    ],
    "reason": "NO_PUBLIC_SOURCE",
    "created_at": "2026-11-04T09:52:21+00:00"
  }
}
```

```bash
$ python3 scripts/workbench.py wide-table --strict
```

```json
{
  "status": "FAIL",
  "counts": {
    "verified": 1,
    "unverified": 0,
    "conflict": 0,
    "na": 1,
    "missing": 2
  },
  "verified_ratio": 0.25,
  "problems": [
    "SQLite / process_concurrency: no claim and no recorded gap",
    "SQLite / writer_model: no claim and no recorded gap"
  ],
  "output": "",
  "markdown": "| Entity | process_concurrency | writer_model |\n|---|---|---|\n| **DuckDB** | 1 RW or N RO ([Concurrency - DuckDB Documentation](https://duckdb.org/docs/connect/concurrency)) | n.a. |\n| **SQLite** | ? | ? |\n\n**Gap register (`n.a.`)**\n\n- DuckDB / writer_model: No documented coordination guarantee for concurrent external writers; left to the application (tried: DuckDB external writer coordination; NO_PUBLIC_SOURCE)\n\nCells: 4 | verified 1 | unverified 0 | conflict 0 | n.a. 1 | missing 2\n"
}
```

Strict fails while any cell is unverified, conflicting or missing — it is the quality gate, not an error. This run names exactly what remains: the SQLite cells have no claims yet. After filling them (or declaring them), a strict run with all cells verified or `n.a.` returns OK.

