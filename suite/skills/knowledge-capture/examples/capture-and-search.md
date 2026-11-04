# Two entries and finding them again

One sourced entry bound to the research ledger, one explicit assumption, and a search that ranks deterministically.

```bash
$ python3 scripts/workbench.py kb-add \
  --question "In which order does the billing export apply tax and rounding?" \
  --answer "Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified by criterion AC1 and the fix in _line_total()." \
  --source-id S1 \
  --tag billing --tag export
```

```json
{
  "status": "OK",
  "entry": {
    "id": "K1",
    "question": "In which order does the billing export apply tax and rounding?",
    "answer": "Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified by criterion AC1 and the fix in _line_total().",
    "source_url": "",
    "source_id": "S1",
    "tags": [
      "billing",
      "export"
    ],
    "assumed": false,
    "confidence": "MEDIUM",
    "created_at": "2026-11-04T09:52:23+00:00"
  },
  "entries_count": 1,
  "warning": ""
}
```

`--source-id S1` is validated against the research ledger — the entry inherits the evidence trail of the registered source.

```bash
$ python3 scripts/workbench.py kb-add \
  --question "What is the staging proxy timeout?" \
  --answer "Assumed 30s based on defaults in similar setups; not documented anywhere we found." \
  --assumed --tag infra
```

```json
{
  "status": "OK",
  "entry": {
    "id": "K2",
    "question": "What is the staging proxy timeout?",
    "answer": "Assumed 30s based on defaults in similar setups; not documented anywhere we found.",
    "source_url": "",
    "source_id": "",
    "tags": [
      "infra"
    ],
    "assumed": true,
    "confidence": "LOW",
    "created_at": "2026-11-04T09:52:23+00:00"
  },
  "entries_count": 2,
  "warning": "Recorded as an explicit assumption (LOW confidence). Revisit with evidence before relying on it."
}
```

`--assumed` is the honest marker: LOW confidence, and the export renders it as **ASSUMPTION (unverified)** so nobody quotes it as fact.

```bash
$ python3 scripts/workbench.py kb-search --query "csv export tax rounding order"
```

```json
{
  "status": "OK",
  "query": "csv export tax rounding order",
  "matched": 1,
  "results": [
    {
      "id": "K1",
      "score": 13,
      "question": "In which order does the billing export apply tax and rounding?",
      "answer": "Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified by criterion AC1 and the fix in _line_total().",
      "tags": [
        "billing",
        "export"
      ],
      "source_url": "",
      "source_id": "S1",
      "assumed": false
    }
  ],
  "note": "Deterministic offline keyword match. Open the cited source before quoting an entry in a deliverable."
}
```

Deterministic offline scoring: tags x3, question tokens x2, answer tokens x1. The billing entry ranks first; the timeout entry does not match this query at all — as it should.

```bash
$ python3 scripts/workbench.py kb-export
```

```json
{
  "status": "OK",
  "knowledge_base": ".local-workbench/KNOWLEDGE_BASE.md",
  "entries": 2
}
```

The exported knowledge base groups entries by first tag, shows each entry's source or assumption marker, and dates every entry — the project's memory, browsable.

