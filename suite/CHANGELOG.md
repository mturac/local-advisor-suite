# Changelog

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
