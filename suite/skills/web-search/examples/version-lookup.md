# A quick verified lookup

A one-fact lookup with the optional ledger. The source is registered from the fetched page text; the claim's quote must appear verbatim in the stored excerpt or it is rejected.

```bash
$ python3 scripts/workbench.py research-init --topic "DuckDB external process concurrency model" \
  --mode quick-verify --max-queries 3
```

```json
{
  "status": "OK",
  "ledger_path": ".local-workbench/research_ledger.json",
  "topic": "DuckDB external process concurrency model",
  "max_queries": 3,
  "sub_questions": [],
  "entities": []
}
```

```bash
$ python3 scripts/workbench.py research-log-query --query "DuckDB concurrency multiprocess file locking documentation" --sub-question-id Q1
```

```json
{
  "status": "OK",
  "query_entry": {
    "id": "QRY-1",
    "query": "DuckDB concurrency multiprocess file locking documentation",
    "sub_question_id": "Q1",
    "tool_used": "host-native-search",
    "executed_at": "2026-11-04T09:52:19+00:00"
  },
  "queries_executed": 1,
  "queries_remaining": 2
}
```

```bash
$ python3 scripts/workbench.py research-add-source \
  --url https://duckdb.org/docs/connect/concurrency \
  --title "Concurrency - DuckDB Documentation" --publisher "DuckDB Foundation" \
  --tier PRIMARY --published-date 2026 --content-file page.txt
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

The source is the *opened page's* cleaned text, saved with `--content-file` (or `--excerpt`). A search snippet never qualifies.

```bash
$ python3 scripts/workbench.py research-add-claim \
  --sub-question-id Q1 --entity DuckDB --field process_concurrency \
  --statement "DuckDB allows either a single read-write process or multiple read-only processes" \
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
    "sub_question_id": "Q1",
    "entity": "DuckDB",
    "field": "process_concurrency",
    "statement": "DuckDB allows either a single read-write process or multiple read-only processes",
    "value": "1 RW or N RO",
    "source_ids": [
      "S1"
    ],
    "quote": "one process with read-write access, or multiple processes with read-only access",
    "quote_verified_in_excerpt": true,
    "confidence": "HIGH",
    "status": "VERIFIED",
    "created_at": "2026-11-04T09:52:20+00:00"
  }
}
```

`quote_verified_in_excerpt: true` is the whole point of the ledger — the answer can now be given with an inline citation to the opened page.

