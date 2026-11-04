# Data Analysis Report — <QUESTION>

> Skeleton for the data-analysis skill. Numbers are computed, not recalled:
> each one is logged as a finding with the exact command or formula that
> produced it. Fields match the data-register / data-finding / data-gap CLI
> (question, path, sha256, statement, method, result, gap reason).

- **Question**: <the analytical question, as registered>
- **Dataset**: `<path>` (<bytes> bytes, SHA-256 `<first 16 hex chars>...`)
- **Date**: <YYYY-MM-DD>

## Answer

<One paragraph answering the registered question. Every number here must
also appear in a finding below — compute it or declare a gap.>

## Findings

| ID | Finding | Method (re-runnable) | Result |
|---|---|---|---|
| F1 | <what was observed> | `<exact command, query or formula>` | <measured value, with unit> |
| F2 | <what was observed> | `<exact command, query or formula>` | <measured value, with unit> |

## Declared gaps

| ID | What could not be computed | Reason |
|---|---|---|
| G1 | <what the file cannot answer> | <NO_DATA / AMBIGUOUS_DEFINITION / OUT_OF_SCOPE / ...> |

## Checks considered

- [ ] Missing values counted; exclusions stated in the methods
- [ ] Units and denominators named in every result
- [ ] Partial periods / date coverage checked for time series
- [ ] Duplicated keys counted if entities, not rows, were asked about
