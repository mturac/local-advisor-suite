# Changelog

## 4.1.2 (2026-11-12)

v4.1.1 command set and JSON contract preserved. This release makes the suite
installable as a Claude Code **plugin** — and keeps every skill self-describing
in that form — plus the decide-playbook demonstration that closed the Azure
example's split.

### Added: Claude Code plugin form (repo-root marketplace)

- `.claude-plugin/marketplace.json` now exists at the **repository root**,
  pointing at `./suite` as the plugin source. `/plugin marketplace add
  <this-repo>` followed by `/plugin install
  local-advisor-suite@local-advisor-suite` now resolves: the plugin manifest
  (`suite/.claude-plugin/plugin.json`) and all 18 skills are found through it.
  Previously the marketplace manifest only existed inside `suite/`, where
  Claude Code never looks when the repository itself is added.
- Every one of the 18 `SKILL.md` files now documents its runtime in one line:
  `$WB` is `python3 scripts/workbench.py` relative to the skill's own
  directory. A plugin install writes no host rules file (no CLAUDE.md), so
  the skill body itself has to resolve the workbench path — now it does, in
  every install form (project, global, plugin).
- New tests: `test_repo_root_marketplace_resolves_plugin_chain` (root
  manifest → plugin manifest → 18 skills) and
  `test_every_skill_md_documents_the_runtime` (no skill may ship without the
  runtime note). 169 tests total.

### Added: the decide playbook run on the panel's split

- The Azure example's `SPLIT_PANEL` was carried through the full chain, all
  commands real: `decision-score` scored the two panel positions (accept-and-
  measure 6.46 vs scale-out-now 5.77, margin 0.69, robustness moderate — and
  the sensitivity block shows the verdict flips exactly when visitor-risk is
  weighted 5+, which is the split the panel could not resolve); `devil-open`/
  `devil-challenge`×2/`devil-premortem`/`devil-verdict` on the winning option
  returned PROCEED_WITH_GUARDS with the finance seat's open challenge X2 as
  guard C1; `journal-log` recorded J1 with a falsifiable prediction and
  review date 2027-02-12; `adr-new` + placeholder fill + `adr-check` → PASS
  (ADR-0001, reversibility R1, the kill criterion as reversal trigger). The
  panel example doc now closes with this outcome so the chain is documented
  end to end.

### Changed

- Root README refreshed: stale counts (125 tests, v3.0.0/v4.0.0 references,
  15-skill console line) now match reality (169 tests, v4.1.2, 18 skills).
- All 18 SKILL.md metadata versions bumped to 4.1.2 (the runtime note touched
  every skill layer; per-skill version = suite version of its last change).
- Suite README plugin section rewritten: root-marketplace install path, and
  an explicit statement that the chain is domain-agnostic (Azure, AWS,
  Shopware, pricing — the question changes, the discipline does not).

## 4.1.1 (2026-11-12)

v4.1.0 command set and JSON contract preserved; a repair release for the
panel's first real-world run, which surfaced two latent defects and one
documentation gap.

### Fixed: panel evidence attribution in PANEL.md

- Local-file evidence rendered as "(from conversation)" in the report's
  evidence table — the attribution now follows the `via` field: local-file
  entries print "(from a local file — see note)" (or "(from a local file)"
  when no note), conversation entries keep their label, URL-backed entries
  keep their URL.

### Fixed: get-more-perspective was missing from the generator registry

- `SKILL_INTERFACES` in `tools/generate_shared.py` still had 17 entries
  after v4.1.0 added the 18th skill, so `generate_shared.py` never
  refreshed `skills/get-more-perspective/scripts/workbench.py` (its copy
  was created manually in v4.1.0 and would have drifted from the root
  workbench on every future edit). The registry now carries all 18 skills;
  `test_versions_align_everywhere` derives the expected skill count from
  the `skills/` directory and fails on any skill missing from the
  registry, so this class of drift cannot ship silently again. The
  marketplace manifest description follows the real count (18).

### Added: second worked example for get-more-perspective

- `examples/azure-cms-single-instance.md` — an architecture question
  (single-instance production Umbraco vs scale-out) run through the panel
  with local-file evidence quoted verbatim from an attached plan document,
  including quotes in the document's own language. Complements
  `pricing-decision.md` by demonstrating the paths it does not: document
  evidence instead of web evidence, a `SPLIT_PANEL` verdict with the
  finance dissent flagged, and an unanswered cross-examination that stays
  OPEN and forces the WARN status.

## 4.1.0 (2026-11-12)

v4.0.0 command set and JSON contract preserved; everything below is additive.
The 18th skill arrives: `get-more-perspective` — the virtual advisory panel,
built so it cannot collapse into five echoes of the question.

### Added: get-more-perspective (the advisory panel)

- `panel-open` — convene the board: a question, its context and a seat
  roster. Default: the five-seat board (operator, skeptic, visionary,
  customer-advocate, finance); `--roles` reshapes it with custom seats.
  Below two seats the panel is refused as a monologue.
- `panel-evidence` — table a quoted observation (verbatim, min 20 chars,
  with source) before the seats that cannot run on vibes speak.
  `--via tinyfish-search | tinyfish-fetch | fetch-url | conversation |
  local-file` records how it was gathered; the TinyFish ladder
  (search → fetch → table) is documented in
  `references/tinyfish-evidence.md` with the suite's zero-vendor
  `fetch-url` as the offline fallback.
- `panel-voice` — one seat's independent opinion. Role-mandated fields are
  enforced mechanically: the operator must bring an execution path, the
  skeptic a named risk AND an early-warning trigger, the visionary a
  concrete opportunity, the customer advocate a segment-specific impact,
  the finance seat a digit-bearing anchor. The skeptic and finance seats
  are additionally refused without cited evidence. Token-overlap check
  refuses two seats reading the same speech (`DUPLICATE_VOICE`); a
  conditional stance must name its observable condition; one seat speaks
  once (`--force` revises on the record).
- `panel-cross` — seat-to-seat cross-examination; unanswered challenges
  stay OPEN in the report and force a WARN synthesis.
- `panel-synth` — mechanical verdict: UNANIMOUS_SUPPORT /
  SUPPORT_WITH_CONDITIONS / MAJORITY_SUPPORT_WITH_DISSENT / SPLIT_PANEL.
  Manufactured agreement is refused by design: a split renders the map of
  the split (no joint recommendation) and hands off to decision-review;
  dissents print in full; a finance dissent is flagged and never buried
  under a majority. Renders PANEL.md. Synthesis refuses an incomplete
  board (PANEL_INCOMPLETE, exit 2).

### Added: integration

- SKILL_ROUTES card with TR/EN triggers ("uzmanlar ne düşünür",
  "danışma paneli", "what would experts think", "advisory panel", ...).
- The decide playbook routes through the panel between option scoring and
  the red team: splits go back to decision-review, dissents go to
  devil-advocate.
- Skill layer: SKILL.md, `references/panel-roles.md`,
  `references/tinyfish-evidence.md`, `references/synthesis-rules.md`,
  `templates/panel-report.md`, `examples/pricing-decision.md`,
  `agents/openai.yaml`.
- 15 new workbench tests (TestGetMorePerspective); console: new scenario
  group (6 scenarios, 64 total) and seeded panel ledgers in the demo
  workspace.
- `doctor` now version-checks every skill's workbench copy against the
  runtime (runs on the shared generator's output).


## 4.0.0 (2026-11-12)

v3.8.0 command set and JSON contract preserved; everything below is additive.
The suite grows from a skill collection into an advisory system: depth-aware
routing, a red-team protocol stack, a pre-flight question contract, a scored
decision journal, and playbooks that compose it all.

### Added: v4 console scenarios

- Eleven new demo scenarios in the web console (58 total): the full
  devil-advocate protocol run (devil-plan / devil-premortem / devil-outside
  with its optimism-bias flag / devil-consequence), the question-contract
  group (qc-pin with the vague-term scan firing, qc-check gate, qc-assume),
  the decision-journal group (log → resolve HIT → calibration report), and
  load-skills --core.
- test_scenarios.py duplicate check refined: same command with different
  flags is an intentional scenario, not a duplicate; only identical
  command+argv pairs are rejected.

### Changed: documentation for the system, not the list

- suite/README.md rewritten for v4: the "why" leads with the depth system,
  the question contract, the red-team protocols and the calibration loop;
  the growth-path section traces 14 skills → 17 skills + playbooks.
- Root console README updated (59 commands, 17 skills, 5 playbooks).


## 3.8.0 (2026-11-12)

v3.7.0 command set and JSON contract preserved; everything below is additive.

### Added: playbooks — orchestration without a state machine

Seventeen skills only help if the agent knows which chain to walk. Five
pre-composed playbooks — **decide, investigate, build, launch, debug** —
each render as an ordered step list where every step names its skill, what
it contributes, and the **gate** that must pass before the next step starts
(qc-check READY, spec-check PASS, no open BLOCKING finding, verdict not
BLOCK, ...). Handoff rules are part of the render: the contract is every
step's intake, devil-advocate guards land in the ADR's rollback triggers,
and the journal closes the loop.

- **`playbook-list`** — the five chains, one line each.
- **`playbook-show --name NAME`** — the full render: steps, gates, handoffs.
- Deterministic and stateless: no new ledger, no hidden ordering — the same
  playbook always renders the same chain, and the gates live in the skills
  that own them.


## 3.7.0 (2026-11-12)

v3.6.0 command set and JSON contract preserved; everything below is additive.

### Added: decision-journal skill (17th skill) — the feedback loop

The advisory stack was missing its other half: advice that is never scored
cannot improve. Every significant decision now gets logged with a falsifiable
prediction and a confidence, reality later grades it, and the calibration
report measures whether "90% confident" actually means 90% right.

- New commands **`journal-log` / `journal-resolve` / `journal-report`** and
  a new `journal_ledger.json` state file:
  - `journal-log --decision ... --prediction ... --confidence N
    --review-by YYYY-MM-DD [--mind-changer ...]` records the commitment, the
    gradeable prediction ("adoption above 60% at the 90-day review", not "it
    will go well"), the confidence as a bet you would take, and the review
    date. The mind-changer is the early-warning field: the observation that
    would flip you before the review date.
  - `journal-resolve --id Jn --outcome HIT|MISS|PARTIAL --lesson ...` grades
    the entry against the prediction as written — no goalpost moves; PARTIAL
    is for substance-held-specifics-slipped, not for dodging a MISS.
  - `journal-report` computes hit rate vs claimed confidence per band
    (50-69 / 70-84 / 85-100), flags overconfidence when the gap exceeds 15
    points, and lists overdue OPEN entries as debts to reality.
- The router now proposes the journal from `decision-review` and
  `devil-advocate`: a verdict without a journaled prediction is a lesson
  nobody will learn from.
- New references: `journal-discipline.md` (what makes an entry gradeable,
  resolution honesty) and `calibration.md` (reading the bands, why 15
  points); fillable entry template and a three-entry example report with
  teeth included.


## 3.6.0 (2026-11-12)

v3.5.0 command set and JSON contract preserved; everything below is additive.

### Added: question-contract skill (16th skill)

The pre-flight layer: the most expensive AI failure is a brilliant answer to
the wrong question, and it is the most preventable. "Before you start",
"clarify what I need" and "tam olarak ne istiyorsun" now route somewhere
real — and the router's also_consider now proposes the contract from
local-advisor and deep-research before big work starts.

- New commands **`qc-pin` / `qc-check` / `qc-assume`** and a new
  `qc_ledger.json` state file:
  - `qc-pin --question ... --decision ... [--consumer ...] [--budget ...]
    [--decided ...] [--open ...]` pins the contract. The decision (what the
    answer will inform) is mandatory: an answer that informs no decision is
    trivia. `decided` kills re-litigated ground; `open` bounds what the
    answer may leave unresolved.
  - `qc-check` is the gate: READY, or NEEDS_INPUT (JSON FAIL, exit 2) naming
    exactly which fields are missing — the decision and the consumer cannot
    stay unpinned.
  - `qc-assume --assumption ...` records full-statement assumptions where
    ambiguity survived; every one is stated in the answer's caveat.
- **Deterministic vague-term scan**: better, optimal, scalable, verimli,
  daha iyi, and friends each return the clarifying question they demand
  ("better by which measure?"). The discipline is one question — the one
  whose answer most changes the work — and assumptions for the rest.
- New references: `contract-fields.md` (each field's purpose, good/bad
  examples) and `vague-terms.md` (the scan list and the one-question craft);
  fillable template and a full example run included.

## 3.5.0 (2026-11-12)

v3.4.0 command set and JSON contract preserved; everything below is additive.

### Added: devil-advocate v2 — the red-team engine

The adversarial pass grows from a challenge ledger into a full red-team
protocol stack. Generic skepticism ("what could go wrong?") catches obvious
risks and misses the failure modes each protocol below exists for.

- **`devil-plan --archetype build|launch|migrate|hire|buy|process`** —
  attack plans per plan archetype. A migration dies on rollback-path, a tool
  adoption on adoption-risk, a hire on key-person-risk; the archetype says
  what to attack first, with premortem prompts, the reference class to look
  up and archetype-calibrated kill signals. Stateless (usable before the
  session opens); records the archetype on an open session.
- **`devil-premortem --failure-story ... --cause ...`** — the premortem,
  run before the challenges: it is 12 months later and the plan failed;
  write the story. Assuming failure already happened is the one reliably
  proven way to surface politely-withheld doubts. Story min 40 chars, causes
  specific enough to check, one premortem per session, and each cause comes
  back as a ready-to-run devil-challenge command.
- **`devil-outside --reference-class ... --base-rate N [--adjustment ...]`**
  — the outside view: what happens to most who try this. A base rate of 50%
  or worse with no argued adjustment auto-opens a SERIOUS optimism-bias
  challenge — "this case beats the reference class" becomes an assumption
  under attack instead of a free premise.
- **`devil-consequence --l1 ... --l2 ... [--l3 ...]`** — second-order
  effects, three levels deep with a mechanism in each. The failures that
  surprise people are rarely first-order; the discipline forces the chain
  onto the record before the verdict.
- **Verdict report upgrade**: CHALLENGE.md now renders the archetype, the
  premortem, the outside view and the consequence chains, and every verdict
  returns `protocols_used`; a session closed without a premortem carries
  `premortem_missing` on the record (the v3.3 gate semantics are unchanged).
- New references: `premortem-protocol.md`, `outside-view.md`,
  `second-order-effects.md`, `falsification.md`; new example
  `premortem-tool-adoption.md` (a full protocol run); SKILL.md workflow
  rewritten around the protocol order (plan → open → premortem → outside →
  challenges → consequences → rebuttals → verdict).

## 3.4.0 (2026-11-12)

v3.3.0 command set and JSON contract preserved; everything below is additive.

### Added: response-depth system for load-skills (the efficiency pass)

- **`--core` depth**: `load-skills --core --prompt ...` (or `--core --skill X`)
  renders a run-from-this-card brief — skill, its 3-step core loop, first
  command, stop rule. Zero file reading. The core loop is the skill distilled:
  for a quick ask it replaces reading SKILL.md plus 1-3 references, which is
  most of the context a simple question used to cost.
- Every one of the 15 routes now carries a **`core` loop** (distilled 3-step
  protocol), exposed in every brief at every depth — including full — so the
  agent always knows the fast path exists and what escalating means.
- **`suggested_depth`**: every prompt routing now returns a deterministic
  recommendation — `core` (single HIGH-confidence route, short prompt),
  `compact` (multiple routed skills, coordination pass first), `full`
  (fallback, low confidence, or a long complex ask). The response also carries
  a `depth` field reflecting the flag actually used.
- New tests: core brief structure and length, direct core load, suggested
  depth for core/compact/full cases, and a contract test that every route has
  a 3-step core loop.

## 3.3.0 (2026-11-12)

v3.2.0 command set and JSON contract preserved; everything below is additive.

### Added: devil-advocate skill (15th skill)

- New skill **`devil-advocate`** — the adversarial second opinion. "Play devil's
  advocate", "what could go wrong" and "şeytanın avukatlığını yap" previously
  fell through the routing table; now they open a structured challenge session
  where the plan gets a fair hearing and its assumptions get attacked on the
  record.
- New commands **`devil-open` / `devil-challenge` / `devil-rebuttal` /
  `devil-verdict`** and a new `devil_ledger.json` state file:
  - `devil-open --claim ... --steelman ...` opens the session; the steelman
    (the plan's best case, stated honestly) is mandatory and min 30 characters
    — an attack on a strawman is refused by design.
  - `devil-challenge --assumption ... --attack ... --category ...
    --severity ... --defeater ...` attacks a load-bearing assumption. Eight
    categories (unfounded-assumption, missing-evidence, second-order-effect,
    alternative-explanation, cost-complexity, reversibility, timing,
    external-risk), three severities. Every attack must name its defeater —
    the observation that would prove it wrong; an attack with no defeater is
    dogma, not criticism.
  - `devil-rebuttal --id Cn --rebuttal ... --basis ...` answers an OPEN
    challenge; a sound rebuttal removes it from the verdict, and the basis
    (evidence / experience / constraint) is recorded for later readers.
  - `devil-verdict --kill-criterion ...` is a mechanical gate: BLOCK while any
    FATAL challenge stands (JSON status FAIL, exit 2), PROCEED_WITH_GUARDS
    while any SERIOUS one does (WARN, guards rendered), PROCEED when every
    attack is answered (PASS). Refuses to run without at least one observable,
    pre-committed kill criterion, and renders `CHALLENGE.md` with the steelman,
    the full challenge table, rebuttals with their defeaters, guards and kill
    criteria.
- Skill assets: `SKILL.md`, `references/challenge-discipline.md` (steelman
  first, attack assumptions not adjectives, severity is a claim, rebuttals
  must engage), `references/attack-categories.md` (the eight categories with
  what evidence answers each), `templates/challenge-report.md`,
  `examples/monolith-to-microservices.md` captured from a real run; shared
  layer regenerated for 15 skills.
- Routing: `load-skills` gains the devil-advocate route with EN/TR triggers
  (devil's advocate, poke holes, stress test, second opinion, şeytanın avukat,
  delik bul, ikinci görüş, neden yanlış, ...); `local-advisor`,
  `decision-review` and `spec-builder` now list it in `also_consider`, so the
  adversarial pass is offered exactly where overconfidence lives.
  `architecture-and-boundaries.md` gains section 8 (Adversarial Challenge
  Discipline) and `evidence-ledger-schema.md` documents `devil_ledger.json`.

### Added: load-skills --compact

- `--compact` emits a one-line-per-skill brief (skill, confidence, compressed
  read order, first command, stop rule) instead of the full brief — a
  token-efficient routing pass for hosts where context is expensive. The full
  brief remains the default for when the work itself begins.

### Counts

- 15 skills, 47 commands, 125 tests (11 new: the challenge ledger lifecycle,
  its error paths, TR/EN routing, and the compact brief).
- Console: new "Devil's advocate" scenario group (4 scenarios) covering all
  four commands; the seeded demo workspace now pre-opens a challenge session
  with one answered FATAL so every scenario also works standalone.

## 3.2.0 (2026-11-04)

v3.1.0 command set and JSON contract preserved; everything below is additive.

### Added: data-analysis skill (14th skill)

- New skill **`data-analysis`** — grounded analysis of a data file the user
  names (CSV, TSV, JSON, logs). Prompts like "analyze this CSV" or "bu veri
  dosyasını analiz et" previously fell through the `load-skills` routing
  table to the advisory fallback; this closes the gap with the same ledger
  discipline the other skills enforce, applied to numbers instead of quotes.
- New commands **`data-register` / `data-finding` / `data-gap` /
  `data-report`** and a new `data_ledger.json` state file:
  - `data-register --path FILE --question "..."` pins the dataset (path, byte
    size, SHA-256), binding every later number to an exact dataset version;
    one dataset per ledger, switching requires `--force` and resets findings.
  - `data-finding --statement ... --method ... --result ...` logs a number
    with the re-runnable command, query or formula that produced it; a method
    under 10 characters is rejected, and a drifted file (hash mismatch) is
    refused with `DATASET_DRIFT` until re-registered.
  - `data-gap --description ... --reason ...` declares what the file cannot
    answer (NO_DATA, AMBIGUOUS_DEFINITION, ...) instead of guessing it.
  - `data-report --answer "..."` renders `ANALYSIS.md`; numbers in the answer
    that no finding supports are rejected (`UNLEDGERED_NUMBERS`) unless
    `--allow-unverified-numbers` publishes them visibly marked UNVERIFIED.
- Skill assets: `SKILL.md`, `references/dataset-intake.md` (profile before
  interpreting), `references/computation-ledger.md` (no number without a
  method), `references/pitfalls.md` (missing data, units, aggregation traps),
  `templates/analysis-report.md`, and `examples/sales-trend.md` from a real
  run.
- `load-skills` routes EN/TR triggers (analyze, dataset, csv, spreadsheet,
  how many rows, analiz, veri seti, kaç satır, excel, ...); all three host
  rule templates (AGENTS / CLAUDE / CURSOR_RULE) gained the routing row.

## 3.1.0 (2026-11-04)

v3.0.0 command set and JSON contract preserved; everything below is additive.

### Added: dynamic skill loading

- New command **`load-skills`** — deterministic prompt → skill routing with a
  context brief. Given the user's request (Turkish or English), it matches
  trigger keywords per skill, ranks the matches (HIGH = 2+ hits, MEDIUM = 1)
  and emits a `brief_text` the agent loads into context: the skills to use,
  the exact read order (`SKILL.md` → `references/…`), the template to fill,
  the first command to run and the stop rule. `--skill NAME` loads one
  skill's brief directly; `--list` dumps the full route table; prompts that
  match nothing fall back to the `local-advisor` advisory route (LOW
  confidence, with the reason on record). Skills were static instruction
  packs before — nothing told the agent *when* to load which one or *what*
  to read first; this closes that gap without an LLM in the loop.
- The AGENTS / CLAUDE / CURSOR_RULE templates now open with **Step 0 —
  dynamic routing**: run `$WB load-skills --prompt "<request verbatim>"` and
  follow the returned brief; the static routing table remains as fallback.
- Every skill's `templates/` folder is now populated (10 fillable skeletons
  added in 3.0.x hotfixes consolidated here): research-notebook,
  findings-report, delivery-evidence, audit-verdict, kb-entry,
  root-cause-report, handoff-pack, spec, search-log,
  wide-comparison-matrix — all using the same field names as the workbench
  CLI flags, so hand-filled and CLI-generated documents stay
  interchangeable.

## 3.0.0 (2026-11-04)

The v2.1 command set and JSON contract are preserved exactly: every v2.1 command and flag still works with the same output shape. Everything below is additive.

### Added: hosts

- **ZCode** support: skills install to `.zcode/skills/` (project) and `~/.zcode/skills/` (user); rules via the project `AGENTS.md`. The generator now enforces the ZCode frontmatter contract — `name` + `description` required, description <= 1024 characters, body <= 100KB — because ZCode silently drops skills that violate it.
- **Cursor** support: the installer generates `.cursor/rules/local-advisor-suite.mdc` (always-on operating rules), `.cursor/commands/<skill>.md` (one invokable command per skill that points the agent at `.cursor/skills/<skill>/SKILL.md`), and the skill folders themselves. Cursor also receives the standard `AGENTS.md` block it reads natively.
- **generic** host: `install.py --hosts generic` writes the `AGENTS.md` rules block only, for any AGENTS.md-compatible agent (Gemini CLI, Amp, ...). Refused without `--no-rules` when no skill host is selected, since the block must reference an installed workbench copy.
- New command **`doctor`**: verifies an installation across every detected host — Python version, state-dir writability, vendor-neutrality scan, host skill directories (claude/codex/zcode/opencode/cursor), rules blocks, per-skill frontmatter limits, workbench copy versions against the runtime, and the install manifest. `doctor` exits 0 for OK and WARN (informational), 2 only for FAIL conditions; the CLI now maps status `WARN` to exit 0 generally (no v2.1 command ever returned WARN).

### Added: skills

- **`spec-builder`** — turns requests into testable specifications. Commands: `spec-new` (goal >= 20 chars, stories, non-goals), `spec-criterion` (Given/When/Then, each clause >= 5 chars), `spec-task` (must `--verifies` at least one criterion; dependencies must exist), `spec-check` (PASS gate: complete clauses, coverage report, dependency-cycle detection; warnings for uncovered criteria and missing non-goals).
- **`code-review`** — severity-graded review ledger. Commands: `review-init` (declared target and focus), `review-finding` (location, severity BLOCKING/MAJOR/MINOR/INFO, category, suggestion; exact duplicates rejected), `review-report` (REVIEW.md with counts; the verdict is mechanically FAIL while any BLOCKING finding is open).
- **`knowledge-capture`** — sourced Q&A knowledge base. Commands: `kb-add` (requires `--source-url`, a ledger-validated `--source-id`, or an explicit `--assumed` marker forcing LOW confidence; duplicate questions rejected), `kb-search` (deterministic offline token scoring: tags x3, question x2, answer x1), `kb-export` (grouped Markdown with visible ASSUMPTION markers).

### Added: depth

- All 13 skills now carry full `references/` and `templates/` layers (35 reference documents, 9 per-skill templates) and `examples/` transcripts captured from real command runs; the test suite re-validates that every example's JSON blocks parse and that every command referenced in a SKILL.md exists in the runtime.
- The shared layer gained the v3.0 ledger schemas (`spec_ledger.json`, `review_ledger.json`, `kb_ledger.json`) in `references/evidence-ledger-schema.md`, a six-host `references/host-compatibility.md`, and testability/verdict rules in `references/architecture-and-boundaries.md`.
- Rule templates (AGENTS, CLAUDE, Cursor rule) extended to route all 13 skills and to encode the new stop rules (spec gate, review verdict, assumption marking).

### Added: installer

- Six hosts (`claude,codex,zcode,cursor,opencode,generic`) with a per-host directory table; Cursor install/uninstall manages rules, commands and skill folders as manifest-tracked whole files; the `.mdc` uninstall deletes the file when only frontmatter remains.
- The manifest gained a `files` list (Cursor artifacts) while remaining loadable for v2.1 manifests.

### Added: tests

- 66 tests (was 38): full coverage of the new commands and their error paths, v2.1 contract compatibility (all 27 v2.1 subcommands must exist), six-host install/uninstall/dry-run behavior, manifest v2.1 compatibility, and package consistency (frontmatter limits, workbench copy drift, plugin manifests, docs coverage).

### Changed

- README rewritten in English for the six-host, 13-skill surface.
- `selfcheck`'s vendor scan factored into `scan_vendor_references()`, shared with `doctor`.

### Fixed

- `kb-add` no longer errors on first use: the knowledge ledger is created empty when missing (previously the NO_KB guard fired before the first entry could exist).

## 2.1.0 (2026-11-02)

Built on the user's own `workbench.py` (v2.0) and `tools/generate_shared.py`. The original command set and JSON contract are kept; every original command still works with the same flags.

### Fixed in the original workbench

- `research-add-claim` accepted a quote that does not appear in the stored excerpt and still recorded it as HIGH/VERIFIED. It now fails with `QUOTE_NOT_IN_SOURCE`; `--allow-unverified-quote` forces LOW/PROVISIONAL.
- `audit-report` skipped the unregistered-URL check when the ledger had no sources (`if registered_canonicals and ...`), so a report with only unopened links passed. It now flags them.
- `verify-delivery` crashed with an uncaught `TimeoutExpired` when a command hung. It now records exit 124 and `timed_out: true`. With nothing declared it now errors (`NOTHING_TO_VERIFY`) instead of reporting a verification.
- `scope-scan` broke only the inner loop at the file cap and kept walking directories. It now stops and reports `cap_reached`; `--max-files` lowers the cap.
- `research-status` compared values verbatim, so "1,000 USD" and "1000 usd" were reported as a contradiction, and superseded claims kept conflicts open. Values are normalised and resolved claims are excluded; `ready_to_synthesize` now also requires no open contradictions.
- The module docstring and CLI description named a hosted research vendor. Removed; `selfcheck` now guards the whole package.

### Fixed in generate_shared.py

- `ROOT` was an absolute path from the author's machine; it is now relative to the script.
- "8 skills" wording corrected to the 10 skills in the spec.
- The OpenCode row claimed `@skill` mentions. OpenCode loads skills through its native `skill` tool; corrected, and permission and web-tool rows added.
- It now also writes `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and per-skill `agents/openai.yaml` and `scripts/workbench.py` copies, so `tests/test_package.py` can detect drift.

### Added

- Commands: `research-score`, `research-gaps`, `research-resolve`, `research-pack`, `wide-table`, `adr-new`, `adr-check`, `debug-report`, `handoff-check`, `artifact-list`, `artifact-new`, `selfcheck`, `--version`.
- `decision-score` sensitivity block (margin, robustness, weight and score flips).
- `audit-report` content checks: uncited numbers, numbers absent from the cited source, years ahead of evidence, overclaim language, stale currentness, undated evidence, single-source reliance; severities, `--strict`, `--max-age-days`.
- `verify-delivery` L0-L4 ladder: `--check Lx:cmd`, `--require`, `--cwd`, `achieved_level`, `levels_not_checked`, git snapshot.
- `debug-hypothesis` case recording without a hypothesis, `--target-file`, `--repro`, `STATEMENT_REQUIRED`; `scope-read --debug-scope`.
- `handoff-pack` git HEAD, decisions, open questions and resume instructions.
- 10 skills with references, templates, examples and `agents/openai.yaml`; `AGENTS.template.md`, `CLAUDE.template.md`; `install.py`; 38 unittest tests.
