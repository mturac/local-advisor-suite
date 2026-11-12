# Example: a pricing decision through the five-seat panel

Question: *Should we raise the Pro plan price from $29 to $39?* — 42 paying
customers, three competitors between $25 and $35, churn at 3% monthly, no
price change in two years.

## 1. Convene

```bash
$WB panel-open \
  --question "Should we raise the Pro plan price from 29 to 39 dollars" \
  --context "42 paying customers, 3 competitors at 25-35, churn currently 3% monthly, no price change in 2 years"
```

```json
{
  "status": "OK",
  "seat_count": 5,
  "panel": [
    {"seat": "operator", "lens": "execution and delivery — can this ship with the people, time and tooling that exist"},
    {"seat": "skeptic", "lens": "risk and failure modes — what breaks first, and which signal says so early"},
    {"seat": "visionary", "lens": "opportunity and upside — what this makes possible that nothing else on the table does"},
    {"seat": "customer-advocate", "lens": "user impact — whose life changes, in which direction, by how much"},
    {"seat": "finance", "lens": "the numbers — cost, revenue, payback; arithmetic needs an anchor"}
  ],
  "next": "Gather evidence before the skeptic and finance seats speak (panel-evidence), then panel-voice --role ... for every seat."
}
```

## 2. Evidence first (TinyFish search → fetch → table)

```bash
tinyfish search query "SaaS Pro tier pricing comparison" --pretty
tinyfish fetch content get --format markdown "https://competitor.example.com/pricing"
$WB panel-evidence --via tinyfish-fetch \
  --source-url "https://competitor.example.com/pricing" \
  --quote "Competitor X Pro tier: 34 per seat per month, billed yearly, includes SSO" \
  --label EV1
```

```json
{
  "status": "OK",
  "evidence": {
    "label": "EV1",
    "quote": "Competitor X Pro tier: 34 per seat per month, billed yearly, includes SSO",
    "source_url": "https://competitor.example.com/pricing",
    "via": "tinyfish-fetch"
  },
  "evidence_count": 1,
  "next": "panel-voice --role ... --evidence EV1"
}
```

## 3. Every seat speaks (skeptic shown; one command per seat)

```bash
$WB panel-voice --role skeptic --stance oppose \
  --risk "Price-sensitive segment churns at renewal; the 3% baseline hides a top-20-accounts concentration" \
  --trigger "Two canary accounts request export of their data within the first week of the announcement" \
  --evidence EV1 --confidence 65 \
  --reasoning "The biggest accounts sit in the exact band this raise hits; the reference class for ten-dollar raises on small SaaS shows a churn spike concentrated in the first renewal cycle, and we have no cohort data to argue ours differs"
```

```json
{
  "status": "OK",
  "voice": {
    "id": "V2",
    "role": "skeptic",
    "stance": "oppose",
    "confidence": 65,
    "role_fields": {
      "risk": "Price-sensitive segment churns at renewal; the 3% baseline hides a top-20-accounts concentration",
      "trigger": "Two canary accounts request export of their data within the first week of the announcement"
    },
    "evidence": ["EV1"]
  },
  "coverage": "2/5 seats have spoken",
  "awaiting": ["visionary", "customer-advocate", "finance"]
}
```

The customer-advocate spoke **conditional** — "existing customers keep their
price for 12 months; only new signups pay 39" — which `panel-voice` required
it to name as an observable condition. Finance supported with a digit-bearing
anchor: at $29, MRR is $1,218; at $39 with 15% churn it is $1,390 — breakeven
at 12% churn, citing EV1.

## 4. Cross-examination

```bash
$WB panel-cross --from-role operator --to-role skeptic \
  --challenge "The canary rollout catches the churn signal before it spreads; your trigger is observable in week one, so why oppose rather than condition" \
  --response "The canary measures announcement shock, not renewal-cycle churn; renewals land 30 days later, after the flag is already at 100 percent"
```

```json
{
  "status": "OK",
  "cross": {"id": "X1", "from": "operator", "to": "skeptic", "resolved": true},
  "open_challenges": []
}
```

## 5. Synthesis

```bash
$WB panel-synth
```

```json
{
  "verdict": "MAJORITY_SUPPORT_WITH_DISSENT",
  "support": 3,
  "oppose": 1,
  "conditional": 1,
  "finance_dissent": false,
  "unsourced": [],
  "status": "WARN",
  "open_challenges": [],
  "next": "Carry the dissent to devil-advocate, or the split to decision-review; log the final call in decision-journal."
}
```

Three seats support, one conditions, the skeptic dissents — so the verdict is
**majority support with the dissent printed in full**, not a consensus that
quietly drops it. `PANEL.md` renders every opinion with its mandated fields,
the evidence table, the exchange, and the handoffs: the skeptic's risk and
trigger become a `devil-advocate` challenge; the customer-advocate's
grandfathering condition becomes a guard; the final call goes to
`decision-journal` with a falsifiable prediction.

Had finance opposed instead, `finance_dissent` would be true and the report
would refuse to bury the arithmetic under the 3-seat majority. Had two seats
opposed, the verdict would be `SPLIT_PANEL` — no joint recommendation, just
the map of the split for `decision-review`.
