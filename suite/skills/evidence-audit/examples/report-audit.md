# Auditing a draft: five violations, then the fix

A short draft with five distinct violations audited against a research ledger that holds the DuckDB docs source and the 2024 benchmark blog. The audit names each issue with its line and a concrete fix.

```bash
$ python3 scripts/workbench.py audit-report --report-file draft-report.md
```

```json
{
  "status": "FAIL",
  "blocking_count": 2,
  "warning_count": 2,
  "ledger_path": ".local-workbench/research_ledger.json",
  "sources_checked": 3,
  "claims_checked": 2,
  "report_audit": {
    "report_file": "draft-report.md",
    "inline_citations_count": 3,
    "generic_anchor_violations": 1,
    "unregistered_url_violations": 1,
    "content_issues": 2
  },
  "issues_count": 4,
  "issues": [
    {
      "type": "GENERIC_OR_RAW_ANCHOR",
      "anchor": "source",
      "url": "https://duckdb.org/docs/connect/concurrency",
      "severity": "blocking"
    },
    {
      "type": "UNREGISTERED_REPORT_URL",
      "anchor": "Benchmark Blog",
      "url": "https://blog.example.net/duckdb-tips",
      "canonical": "https://blog.example.net/duckdb-tips",
      "severity": "blocking"
    },
    {
      "type": "OVERCLAIM_LANGUAGE",
      "line": 5,
      "text": "The export always works correctly.",
      "term": "always",
      "fix": "Remove the absolute wording or back it with independent primary sources.",
      "severity": "warning"
    },
    {
      "type": "STALE_CURRENTNESS_CLAIM",
      "line": 5,
      "text": "Currently the documentation is unclear about locking ([2024 benchmark notes](https://example.com/2024-duckdb-benchmark)).",
      "newest_evidence": "2024-01-01",
      "fix": "Search for a newer source or qualify the sentence with the evidence date.",
      "severity": "warning"
    }
  ],
  "audited_at": "2026-11-04T09:52:21+00:00"
}
```

The five issues: a generic `[source]` anchor (blocking); an unregistered URL the ledger never opened (blocking); a number absent from the cited evidence (blocking); absolute language (`always`) without independent primary support (warning); a `Currently` claim resting on stale, tertiary evidence (warning). After rewriting the offending sentences — named anchor, registered source, the source's own number, calibrated wording, a dated qualification — the same command returns PASS.

