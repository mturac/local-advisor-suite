# Dataset Intake — Profile Before Interpreting

Run these checks before answering any question about a registered dataset, and log each as a finding. The goal is to know the shape of the data before making claims about its meaning.

## 1. Existence and identity

- The file must exist and be named by the user. `data-register` records its path, byte size and SHA-256; all later numbers are bound to that hash.
- If the file is a sample of something larger, say so in the report; conclusions about the sample are not automatically conclusions about the population.

## 2. Shape

- Row count (excluding the header for CSV/TSV) — `tail -n +2 FILE | wc -l` or the equivalent.
- Column count and names — `head -1 FILE` for CSV/TSV, key inventory for JSON.
- Delimiter and encoding: verify the delimiter actually splits the columns you think exist (`head -2 FILE | cut -d, -f1-3`). A comma inside a quoted field changes everything; prefer a real parser (`python3 -c` with the `csv` module) when in doubt.

## 3. Types and ranges

- For each column you will aggregate: what does it contain — numbers, dates, free text, IDs? Confirm with the first and last values, not assumptions from the header name.
- Date ranges: earliest and latest value of every time column (a "monthly" file may start mid-month).
- Numeric ranges: min and max, to catch sentinel values (`-1`, `9999`, `NULL` rendered as `0`).

## 4. Missing and duplicated data

- Count empty cells in the columns you will use. Decide explicitly: exclude rows, treat as zero, or declare a gap. Record which in the finding.
- Duplicate rows or repeated IDs: count them; know whether you are counting records or entities.

## 5. Scope confirmation

- Re-read the registered question. If the file cannot answer it (no such column, wrong granularity, wrong time span), record a `data-gap` with reason `NO_DATA` or `AMBIGUOUS_DEFINITION` and ask the user before improvising a substitute question.

Every check above that produces a number used later in the answer must be logged with `data-finding` — including the profiling numbers.
