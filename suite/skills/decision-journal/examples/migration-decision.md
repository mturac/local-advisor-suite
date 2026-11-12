# Three entries, one overdue, one overconfident band

A real-shaped run: the CI-migration decision from the devil-advocate example
gets journaled, two more calls from the same quarter join it, and the first
calibration report has teeth — one band is fictional, one entry is overdue.

## 1. Log the decision while it is still a prediction

```bash
$ python3 scripts/workbench.py journal-log \
  --decision "Migrate CI to the managed platform, mobile build included" \
  --prediction "weekly active pipelines on the new platform exceed 60% of the team at the 90-day review" \
  --confidence 75 \
  --review-by 2027-02-10 \
  --mind-changer "adoption stalls below 40% for three consecutive weeks"
```

```json
{
  "status": "OK",
  "entry": {
    "id": "J1",
    "decision": "Migrate CI to the managed platform, mobile build included",
    "prediction": "weekly active pipelines on the new platform exceed 60% of the team at the 90-day review",
    "confidence": 75,
    "review_by": "2027-02-10",
    "mind_changer": "adoption stalls below 40% for three consecutive weeks",
    "status": "OPEN"
  },
  "open_count": 1,
  "next": "When the review date arrives (or reality answers first): journal-resolve --id J1 --outcome HIT|MISS|PARTIAL --lesson \"...\""
}
```

Two more calls the same week: a rewrite-vs-layer decision at 85 ("the
versioned layer ships without breaking any mobile client this quarter") and
a hiring call at 60 ("the contractor is productive on the billing service
within four weeks").

## 2. Reality answers, unevenly

```bash
$ python3 scripts/workbench.py journal-resolve --id J1 \
  --outcome HIT \
  --lesson "the two-week plugin spike de-risked the mobile build before the decision; spike first, decide second"
```

```json
{
  "status": "OK",
  "entry": {"id": "J1", "status": "RESOLVED", "outcome": "HIT",
            "lesson": "the two-week plugin spike de-risked the mobile build before the decision; spike first, decide second"},
  "open_count": 2
}
```

The layer call resolves HIT (no client broke). The contractor call resolves
MISS at eight weeks — productive, but not at four.

## 3. The calibration report

```bash
$ python3 scripts/workbench.py journal-report
```

```json
{
  "status": "OK",
  "entries_total": 3,
  "resolved": 3,
  "open": 0,
  "overdue": [],
  "bands": [
    {"band": "50-69%", "resolved": 1, "avg_confidence": 60, "hit_rate": 0, "gap": 60, "overconfident": true},
    {"band": "70-84%", "resolved": 1, "avg_confidence": 75, "hit_rate": 100, "gap": -25, "overconfident": false},
    {"band": "85-100%", "resolved": 1, "avg_confidence": 85, "hit_rate": 100, "gap": -15, "overconfident": false}
  ],
  "overall": {"resolved": 3, "open": 0, "avg_confidence": 73, "hit_rate": 83, "gap": -10, "overconfident": false},
  "verdict_note": "Calibration is honest within 15 points. Keep resolving on evidence, not on hope."
}
```

With one entry per band the math is illustrative, not significant — the
report says so by being cautious. The pattern it hints at is the classic
one: the 60% contractor call missed (people-timing predictions run hot),
the technical calls landed. After twenty entries, that hint becomes a map:
price people-timing claims 15 points lower than the feeling.

And when the J1 review date had passed unopened, the report would have
listed it in `overdue` until resolved — the debt to reality is not
forgiven, only paid.
