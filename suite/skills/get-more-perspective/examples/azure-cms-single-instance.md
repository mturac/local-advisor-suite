# Example: an architecture question through the panel — with a split

Question: *Should the production Umbraco CMS stay single-instance, accepting
minutes of CMS unavailability during deploys and Azure maintenance, or scale
out to a second instance?* — the context is an attached architecture plan
(Azure Front Door + Next.js ISR frontend + self-hosted Umbraco), so the
evidence is **local-file**: quoted verbatim from the document, in the
document's own language (Turkish — a quote is a quote; the panel argues in
yours, the evidence stays in its own words).

This example is the complement of `pricing-decision.md`: document evidence
instead of web evidence, and a panel that does **not** agree — the verdict is
`SPLIT_PANEL` with a finance dissent and an unanswered challenge, which is
what the synthesis is built to protect rather than launder.

## 1. Convene

```bash
$WB panel-open \
  --question "Should the production Umbraco CMS stay single-instance, accepting minutes of CMS unavailability during deploys and Azure maintenance, or scale out to a second instance?" \
  --context "Next.js frontend runs 2+ instances with blue-green slots and a Redis-backed ISR cache in front; Umbraco runs on its own App Service plan, deployed in place at low-traffic hours under content freeze; the plan itself lists the single-instance limitation as a known constraint and defers final sizing to load tests (Azure Architecture and Deployment Plan v4)"
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

## 2. Evidence first (from the attached plan, via local-file)

The plan is already on the machine — no search needed. Read it, quote it
verbatim, table each quote with `--via local-file` and a `--note` naming the
file and section, one claim per entry:

```bash
$WB panel-evidence --via local-file \
  --quote "Bilinen kısıt: Tek instance olduğu için Azure bakımı veya yeniden başlatma sırasında backoffice ve Delivery API kısa süre erişilemez. Cache'te bulunan sayfalar servis edilmeye devam eder; cache'te olmayan sayfalar bu sürede üretilemeyebilir." \
  --label EV1 --note "Azure Altyapı ve Deployment Planı 4.pdf, CMS ortam gereksinimleri"

$WB panel-evidence --via local-file \
  --quote "Production için ayrı bir App Service Plan'da tek instance. Kapasite plan büyütülerek (dikey) artırılır." \
  --label EV2 --note "Azure Altyapı ve Deployment Planı 4.pdf, CMS ortam gereksinimleri"

$WB panel-evidence --via local-file \
  --quote "Production'da deploy yerinde, düşük trafikli bir saatte yapılır. Deploy sırasında backoffice ve Delivery API birkaç dakika erişilemez." \
  --label EV3 --note "Azure Altyapı ve Deployment Planı 4.pdf, CMS deployment stratejisi"
```

Two more went on the table the same way: EV4, the **frontend** sizing
("en az 2 instance, instance başına 2 vCPU ve 4 GB RAM") — noted as the
asymmetry: the frontend tier gets redundancy, the CMS tier does not — and
EV5, the Redis degradation posture ("Site yavaşlar ama ayakta kalır"). Five
entries, five single claims, one document.

## 3. Every seat speaks (skeptic and finance shown; one command per seat)

```bash
$WB panel-voice --role skeptic --stance oppose --confidence 60 \
  --risk "Unplanned Azure platform maintenance does not check the low-traffic calendar: a mid-campaign restart turns every cache-miss page into a visitor-facing error, and the plan quantifies neither the cache-miss share of traffic nor the maintenance frequency" \
  --trigger "One availability-test failure or 5xx-rate alert on the public site that coincides with a CMS restart outside a content-freeze window" \
  --evidence EV1,EV3 \
  --reasoning "The plan sizes the exposure by the deploy case it controls — low-traffic hour, a few minutes, freeze in force — and stays silent on the case it does not control: platform maintenance at Azure's discretion; until the cache-miss share of requests is actually measured, 'kısa süre erişilemez' is an editor-inconvenience story that can silently be a visitor-incident story"
```

```json
{
  "status": "OK",
  "voice": {
    "role": "skeptic",
    "stance": "oppose",
    "confidence": 60,
    "role_fields": {
      "risk": "Unplanned Azure platform maintenance does not check the low-traffic calendar: a mid-campaign restart turns every cache-miss page into a visitor-facing error, and the plan quantifies neither the cache-miss share of traffic nor the maintenance frequency",
      "trigger": "One availability-test failure or 5xx-rate alert on the public site that coincides with a CMS restart outside a content-freeze window"
    },
    "evidence": ["EV1", "EV3"]
  },
  "coverage": "2/5 seats have spoken"
}
```

The operator **supported** — its path: instrument first (an App Insights
counter for cache-miss requests reaching the CMS during backoffice/Delivery
API downtime, one month of telemetry before any scale-out decision). The
visionary and customer-advocate spoke **conditional**: the visionary on
cache-coverage completion before the first high-traffic season, the
customer-advocate on measured (not assumed) editor downtime and cold-tail
error share. The finance seat opposed — and its anchor is arithmetic built
from the table, not a price lookup:

```bash
$WB panel-voice --role finance --stance oppose --confidence 55 \
  --number "The stack already pays for redundancy everywhere else — 'en az 2 instance' on the frontend (EV4), HA-capable Redis (EV5) — while the CMS, the one component every revenue page and the whole editing workflow depends on, runs 'tek instance' (EV2); closing that gap is roughly one more App Service instance, about a third more compute, against a 'birkaç dakika' exposure on every deploy (EV3) plus unplanned maintenance" \
  --evidence EV2,EV3,EV4,EV5 \
  --reasoning "This is an insurance-asymmetry problem, not a capacity problem: we insure the frontend tier and the cache tier against the same class of outage, then leave the content-originating tier uninsured because its failure is 'brief'; a maintenance window landing inside a campaign prices frozen editors plus erroring landing pages well above one instance-month"
```

## 4. Cross-examination — one answered, one left open

```bash
$WB panel-cross --from-role operator --to-role skeptic \
  --challenge "Your trigger is observable in week one, so why oppose rather than condition — instrument the restart windows first and let the data escalate the stance" \
  --response "Because the thing to be measured does not exist yet: nobody counts the cache-miss share of requests today, so my trigger can only fire on an incident instead of on telemetry; the stance flips to conditional the day that counter ships"
```

```json
{
  "status": "OK",
  "cross": {"id": "X1", "from": "operator", "to": "skeptic", "resolved": true},
  "open_challenges": []
}
```

Finance then challenged the operator and the operator **did not answer** —
deliberately left open, because it had no defensible threshold yet:

```bash
$WB panel-cross --from-role finance --to-role operator \
  --challenge "Your first step measures visitor impact but never prices it: if the counter shows a cold-tail error share during maintenance windows, what threshold turns measure-first into buy-the-second-instance?"
```

```json
{
  "status": "OK",
  "cross": {"id": "X2", "from": "finance", "to": "operator", "resolved": false},
  "open_challenges": ["X2"]
}
```

An unanswered challenge is not resolved by silence: X2 stays OPEN, appears in
the report, and forces the WARN status — that is the mechanism working, not
the session failing.

## 5. Synthesis — the panel splits

```bash
$WB panel-synth
```

```json
{
  "verdict": "SPLIT_PANEL",
  "support": 1,
  "oppose": 2,
  "conditional": 2,
  "finance_dissent": true,
  "unsourced": [],
  "status": "WARN",
  "open_challenges": ["X2"],
  "next": "Carry the dissent to devil-advocate, or the split to decision-review; log the final call in decision-journal."
}
```

One support does not outvote two oppositions, so the verdict is
**SPLIT_PANEL**: `PANEL.md` refuses to emit a joint recommendation and renders
the map of the split instead — the operator's measure-first position against
the skeptic's unquantified-risk objection and the finance seat's
insurance-asymmetry dissent, with both dissents printed in full (the finance
dissent additionally flagged, never buried) and the two conditional seats'
conditions listed as gates. X2's open challenge is printed in its own
section, so whoever reads the report knows exactly what is unanswered.

The handoffs do the resolving, not the vote: the split goes to
`decision-review` to score the positions (accept-and-measure vs
scale-out-now); the finance dissent's strongest point — nobody priced the
cold-tail risk — becomes a `devil-advocate` challenge with a named defeater;
and whichever way the call lands, it goes into `decision-journal` with a
falsifiable prediction ("the cache-miss counter stays under X% of requests
across N restart windows") and a review date.

Had the customer-advocate's condition been met on record — the cold-tail
measured near zero — the count would have been 2 support / 2 oppose / 1
conditional: still `SPLIT_PANEL`. Had the skeptic accepted the counter as
sufficient and moved to conditional, it would have been 1 support / 1
oppose / 3 conditional: `SPLIT_PANEL` again, because in both cases support
does not exceed oppose — and that is the point. The verdict table counts
stances mechanically precisely so nobody has to negotiate what "mostly
agreed" means; changing this panel's verdict requires changing a seat's
stance on the record, not the reader's impression of the mood.

## 6. What happened next: the split went to decision-review

The handoffs were taken, in order, with real commands — this is the
`decide` playbook's tail operating on the panel's output:

1. **`decision-score`** — the two panel positions became the two options
   (A: keep single-instance, instrument first; B: scale out now), scored on
   five criteria taken from the seats' own concerns. A won, 6.462 vs 5.769,
   margin 0.692, robustness moderate. The sensitivity block is the split
   speaking mechanically: **the verdict flips to B the moment visitor-risk
   is weighted 5.1 instead of 3** — exactly the weight the skeptic would
   assign if the cold-tail turns out large, and exactly the number nobody
   has because the counter does not exist yet. The recommendation is honest
   about what it hangs on.
2. **`devil-advocate`** on the winning option — the finance seat's open
   challenge X2 became SERIOUS challenge C1 (*measurement without a
   pre-committed threshold measures nothing*), joined by C2 (*the plan's own
   words limit the cache guarantee to warmed pages*). Premortem: the
   counter exists, nobody actioned it, a maintenance window hits during a
   campaign. Verdict: **PROCEED_WITH_GUARDS** — C1 and C2 become guards,
   plus a pre-committed kill criterion (any visitor-facing 5xx burst of 2+
   minutes coinciding with a restart outside a freeze window falsifies
   keep-and-measure).
3. **`journal-log`** — J1: the decision, a falsifiable prediction
   (cache-miss requests under 1% across restart windows, no restart-
   attributable 5xx burst over 2 minutes), confidence 70, review date
   2027-02-12, and the mind-changer named.
4. **`adr-new` + `adr-check`** — ADR-0001, reversibility R1 (scaling out
   later is a config change), the finance dissent written in full as the
   steelman counter-argument, the kill criterion as the reversal trigger.
   `adr-check`: PASS.

The panel refused to average its disagreement; the decision process scored
it, the red team attacked the winner, the journal made the call falsifiable,
and the ADR made it reversible. Five skills, one question, no step trusted
to memory — and nothing in the chain is Azure-specific: the same seats,
commands and gates run on an AWS migration, a Shopware upgrade or a pricing
change.
