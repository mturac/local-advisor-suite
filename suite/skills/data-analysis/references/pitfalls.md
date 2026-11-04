# Analysis Pitfalls — The Recurring Traps

Check this list before writing the answer. Each trap is a way to produce a technically-logged number that still misleads.

## 1. Missing data silently shifts the denominator

- Rows with empty cells are usually dropped by naive aggregations, so "average order value" is really "average of orders that had a value". Count the exclusions as a finding, or declare a gap.
- `0` is a value; empty is not. Confirm which one the file uses before summing.

## 2. Unit and currency confusion

- A column named `amount` may mix currencies, or `price` may be in cents. Verify with a value you can sanity-check, and name the unit in every result.
- Durations may be seconds, milliseconds or days; bytes may be binary (1024) or decimal (1000) multiples. State the convention in the method.

## 3. Aggregation traps

- **Simpson's pattern**: a trend visible in every subgroup can reverse in the total (or the reverse) when group sizes differ. Before claiming a total trend, check whether a dominant group drives it.
- **Averaging averages**: the mean of per-group means is not the overall mean unless groups have equal size. Compute from the underlying rows.
- **Percentages of small bases**: "up 50%" from 4 to 6 orders is noise. Report the base alongside the rate.

## 4. Time-series traps

- Partial periods: a "monthly" series whose last month is half over will look like a crash. Check the last row's date coverage before calling a downturn.
- Gaps in months: a file that skips March is not "flat through spring". Enumerate the periods you actually have.
- Seasonality vs trend: 12 points spanning one year cannot separate them; say so instead of projecting.

## 5. Identity and duplication

- Repeated IDs mean you may be counting events, not entities. Count distinct keys when the question is about things, not rows.

## 6. Correlation theater

- Two columns moving together is not causation, and with few rows almost anything correlates. If the question asks "why", the honest answer is usually about what the data cannot establish — declare it as a gap.

## 7. Overreach in the answer

- The answer's scope is the file, as hashed. Generalizing to "the business", "all users", or "next quarter" is an assumption, not a finding. Either keep the wording file-bound or mark the extrapolation explicitly.
