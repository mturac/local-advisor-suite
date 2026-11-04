#!/usr/bin/env bash
# Generate the real-run example JSON for skills/data-analysis/examples/sales-trend.md
set -euo pipefail
rm -rf /tmp/dataex && mkdir -p /tmp/dataex && cd /tmp/dataex
printf 'month,sales\n2026-01,120\n2026-02,135\n2026-03,150\n2026-04,145\n2026-05,170\n' > sales.csv
WB=/home/z/my-project/suite/workbench.py

python3 "$WB" data-register --path sales.csv --question "What is the monthly sales trend in this file?"
python3 "$WB" data-finding \
  --statement "The file has 5 data rows, one per month from 2026-01 to 2026-05" \
  --method 'tail -n +2 sales.csv | wc -l' \
  --result "5 rows"
python3 "$WB" data-finding \
  --statement "Monthly sales start at 120 and end at 170" \
  --method "cut -d, -f2 sales.csv | tail -n +2 | sed -n '1p;\$p'" \
  --result "120 and 170"
python3 "$WB" data-finding \
  --statement "Sales increased by 41.6 percent from first to last month" \
  --method '(170-120)/120*100 = 41.66, rounded to one decimal' \
  --result "41.6 percent"
python3 "$WB" data-gap \
  --description "Per-region breakdown is not computable from this file" \
  --reason "NO_DATA: the file has no region column"
python3 "$WB" data-report \
  --answer "Sales rose from 120 to 170 across 5 months, a 41.6 percent increase; the region split cannot be computed from this file."
echo "=== ANALYSIS.md ==="
cat .local-workbench/ANALYSIS.md
