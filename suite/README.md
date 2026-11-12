# local-advisor-suite 4.1.0

A provider-neutral advisory system — **18 skills + 5 playbooks** that run identically in **Claude Code, Codex, ZCode, Cursor, OpenCode, and any AGENTS.md-compatible agent**.

The suite depends on no search vendor, no API key, and no MCP server. When web access is needed, it uses only the search and fetch tools your host already provides. All ledger, scoring, audit and verification work is done by a single standard-library Python file (`workbench.py`) that runs offline and deterministically.

Built on the user's own `workbench.py` and `tools/generate_shared.py`. The v2.1 command set and JSON contract are preserved exactly; every v2.1 command and flag still works. Additions and fixes are listed in [CHANGELOG.md](CHANGELOG.md).

## Why this suite

- **Spends context only when the ask is worth it.** `load-skills` routes any prompt (TR/EN) to its skills at three depths — `--core` is a run-from-this-card brief with zero file reading, and every routing returns a deterministic `suggested_depth`.
- **Pins the question before answering it.** `question-contract` refuses to let work start until the question, the decision it informs and the consumer are pinned; vague words ("better", "verimli", "scalable") come back with the clarifying question they demand.
- **Does not scan files by default.** `local-advisor` works from the conversation. A file is read only when you name it, via `scope-read`, inside the project root. `.env`, key files and out-of-root paths are blocked.
- **Does not retry forever.** `local-debug` stops after 2 falsified hypotheses and writes a root-cause or escalation report.
- **Accepts no fabricated sources.** A claim is rejected unless its quote appears verbatim in the stored text of an opened page. Reports are audited for unopened links, unsupported numbers and overclaim language.
- **Proves before saying "done".** `delivery-verify` runs the real commands and reports the achieved level on the L0-L4 ladder.
- **Argues back like a red team, not a grump.** `devil-advocate` runs the premortem (the failure story, written before the challenges), takes the outside view (reference class + base rate — a bad base rate with no argued adjustment auto-opens an optimism-bias challenge), attacks load-bearing assumptions in archetype order, maps second-order effects three levels deep, and lets the unanswered attacks decide the verdict mechanically.
- **Scores its own advice.** `decision-journal` logs decisions with falsifiable predictions and confidences, grades them HIT/MISS/PARTIAL against reality, and reports calibration per confidence band — overconfidence is a flag, not a feeling.
- **Convenes a real panel, not five echoes.** `get-more-perspective` seats Operator, Skeptic, Visionary, Customer Advocate and Finance at one board: each speaks independently through role-mandated fields (a skeptic without a named risk and trigger signal is refused at the door; finance without a digit-bearing anchor likewise; two seats may not read the same speech), the skeptic and finance seats must cite evidence on the table first — gathered with the TinyFish search/fetch pattern or the suite's own `fetch-url` — and the mechanical synthesis refuses to manufacture agreement: splits stay splits, dissents stay on the record, a finance dissent is never buried.
- **Remembers honestly.** `knowledge-capture` stores sourced Q&A entries; assumptions are marked, never quoted as fact.
- **No extra cost.** No paid services. The only command that can open a socket is `fetch-url`, and only with `--allow-network`.
- **Works everywhere.** One installer, six hosts; `doctor` verifies any installation's health.

## Skills

| Skill | When | Core commands |
|---|---|---|
| `local-advisor` | Architecture, design, plan and trade-off advice (no file scanning) | `advise-intake` (optional) |
| `question-contract` | Pin the question, the decision it informs and the consumer before work starts; vague-term scan | `qc-pin`, `qc-check`, `qc-assume` |
| `decision-review` | Option comparison, ADRs, reversibility (R0-R3), pre-mortem | `decision-score`, `adr-new`, `adr-check` |
| `decision-journal` | Log decisions with falsifiable predictions; grade them against reality; calibration report | `journal-log`, `journal-resolve`, `journal-report` |
| `devil-advocate` | Stress-test a plan: premortem, outside view, archetype attack plan, challenges, second-order chains, mechanical verdict | `devil-plan`, `devil-premortem`, `devil-outside`, `devil-challenge`, `devil-consequence`, `devil-rebuttal`, `devil-verdict` |
| `get-more-perspective` | A virtual advisory panel on any decision or dilemma: five independent seats, evidence-mandated skeptic/finance voices, cross-examination, mechanical verdict that never manufactures agreement | `panel-open`, `panel-evidence`, `panel-voice`, `panel-cross`, `panel-synth` |
| `local-debug` | A bug in a file you name; at most 2 hypotheses | `debug-hypothesis`, `scope-read --debug-scope`, `debug-report` |
| `data-analysis` | A data file you name; every number traceable to a logged command | `data-register`, `data-finding`, `data-gap`, `data-report` |
| `web-search` | Quick verified answers with 1-3 sources | host search/fetch tools + optional ledger |
| `deep-research` | Multi-step research: decomposition, ledger, scoring, contradictions, gaps, synthesis | `research-*`, `audit-report` |
| `wide-search` | Entity x field tables; every cell bound to a verified URL | `research-init --mode wide-matrix`, `wide-table --strict` |
| `evidence-audit` | Audit a draft against the research ledger | `audit-report --report-file` |
| `delivery-verify` | Prove code/output with the L0-L4 ladder | `verify-delivery --check Lx:cmd --require` |
| `artifact-studio` | Technical reports, ADRs, exec summaries, deck outlines, data schemas | `artifact-list`, `artifact-new` |
| `session-handoff` | Context handoff across sessions, tools and agents | `handoff-pack`, `handoff-check` |
| `spec-builder` | Requests into testable specs: GWT criteria and verifying tasks | `spec-new`, `spec-criterion`, `spec-task`, `spec-check` |
| `code-review` | Severity-graded review of named files or a PR | `review-init`, `review-finding`, `review-report` |
| `knowledge-capture` | Sourced or explicitly-assumed Q&A knowledge base | `kb-add`, `kb-search`, `kb-export` |

Every skill carries `SKILL.md`, `references/`, `templates/`, `examples/`, `agents/openai.yaml` and `scripts/workbench.py`. All files are English and written in the imperative mood. Example command outputs were taken from real runs and are re-validated by the test suite.

## Playbooks: the chains

Skills compose, and the composition is written down. `playbook-list` shows the
five pre-composed chains; `playbook-show --name decide` renders the full
sequence — every step names the skill, what it contributes, and the **gate**
that must pass before the next step starts:

- **decide** — options on the table: contract → score → attack the winner → journal → ADR
- **investigate** — evidence, not opinion: contract → research → audit → report → capture
- **build** — request to verified delivery: contract → spec → (debug) → review → verify → capture
- **launch** — in front of real users: verify → premortem → journal the prediction → announce
- **debug** — symptom to lesson: repro → fix review → prove → capture → (journal)

A gate that fails stops the chain — fix the gate or explicitly record why the step is skipped. A skipped gate, silently, is the difference between a pipeline and a vibe.

## The growth path

The 14th skill arrived in v3.2.0: `data-analysis` — a number is only speakable when the command that produced it is on the record.

The 15th skill arrived in v3.3.0: `devil-advocate` — "şeytanın avukatlığını yap" routes somewhere real, with a mechanical BLOCK/PROCEED gate.

v3.4.0 added depth-aware routing: every route carries a distilled 3-step core loop, `--core` renders it with zero file reading, and every routing suggests its depth.

v3.5.0 turned devil-advocate into a red-team engine: archetype attack plans, the premortem, the outside view with its automatic optimism-bias challenge, and second-order chains.

The 16th skill (v3.6.0) is `question-contract` — the pre-flight layer that kills the most expensive failure in advisory work: a brilliant answer to the wrong question.

The 17th skill (v3.7.0) is `decision-journal` — the feedback loop that scores the advice, so the suite can tell you it was overconfident before you find out the hard way.

The 18th skill (v4.1.0) is `get-more-perspective` — the advisory panel. Five seats argue independently from role-mandated fields, the skeptic and finance seats must cite evidence tabled first (TinyFish search → fetch pattern, or the suite's zero-vendor `fetch-url`), seats cross-examine each other, and the synthesis is mechanical: UNANIMOUS_SUPPORT / SUPPORT_WITH_CONDITIONS / MAJORITY_SUPPORT_WITH_DISSENT / SPLIT_PANEL — a split is a valid answer, and manufacturing agreement is refused by design.

v4.0.0 composes it all: five playbooks chain the skills end-to-end with gates (the decide playbook now routes through the panel between scoring and the red team).

## Installation

Requirement: Python 3.9+ (standard library only; tested with Python 3.12/3.14). No `pip install`.

```bash
unzip local-advisor-suite.zip
cd local-advisor-suite
./run_tests.sh                                     # 152+ tests

# Install into a project (Claude Code + Codex + ZCode + Cursor + OpenCode)
python3 install.py --project ~/code/my-app --gitignore

# One host only, symlinked (edits in this repo apply immediately)
python3 install.py --project ~/code/my-app --hosts claude --link

# User-wide install
python3 install.py --global --hosts codex,opencode

# Any AGENTS.md-reading agent (Gemini CLI, Amp, ...) — rules block only
python3 install.py --project ~/code/my-app --hosts generic --no-rules

# See what would change first / remove everything
python3 install.py --project ~/code/my-app --dry-run
python3 install.py --project ~/code/my-app --uninstall
```

### What the installer does

| Host | Project skills | User skills | Rules file |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | `CLAUDE.md` / `~/.claude/CLAUDE.md` |
| Codex | `.agents/skills/` | `~/.agents/skills/` | `AGENTS.md` / `~/.codex/AGENTS.md` |
| ZCode | `.zcode/skills/` | `~/.zcode/skills/` | `AGENTS.md` |
| Cursor | `.cursor/skills/` + `.cursor/commands/<skill>.md` | project-level only | `.cursor/rules/local-advisor-suite.mdc` + `AGENTS.md` |
| OpenCode | `.agents/skills/` (shared with Codex; own dir only when alone) | `~/.config/opencode/skills/` | `AGENTS.md` / `~/.config/opencode/AGENTS.md` |
| generic | none (rules only) | none | `AGENTS.md` |

- Rule blocks are written between `<!-- local-advisor-suite:start -->` and `<!-- local-advisor-suite:end -->` markers. Your own text is preserved, and re-running does not duplicate the block.
- Every change is recorded in the `.local-advisor-suite.json` manifest. `--uninstall` removes exactly what the manifest lists; a same-named skill belonging to someone else is never touched without `--force`.
- Add `.local-workbench/` to `.gitignore`; `--gitignore` does it for you.
- OpenCode reads both `.claude/skills` and `.agents/skills`; when Claude and Codex are installed together OpenCode sees each skill twice (identical content), so the installer only notes this.
- ZCode can additionally import skills from Claude Code / Codex directories via Settings -> Skills -> Import.

### Optional plugin installs

- Claude Code: `/plugin marketplace add <this-repo>` (the repo root carries `.claude-plugin/marketplace.json`; it points at `./suite`, where the plugin manifest and all 18 skills live), then `/plugin install local-advisor-suite@local-advisor-suite`. Plugin skills are invoked as `/local-advisor-suite:<skill>`. A plugin install writes no rules file — every `SKILL.md` documents its own `$WB` runtime path, so the skills stay self-contained.
- Codex: `codex plugin marketplace add ./local-advisor-suite`. The manifest is `.codex-plugin/plugin.json`, the marketplace file `.agents/plugins/marketplace.json`.
- ZCode: the repository root's flat `skills/<name>/SKILL.md` layout is a valid plugin source for a ZCode marketplace that accepts local directories.

The skills are domain-agnostic by design: the same panel → decision → red-team → journal chain runs on an Azure architecture question, an AWS cost question, a Shopware migration or a pricing decision — the question changes, the discipline does not.

## Using the suite per host

- **Claude Code:** a skill whose description matches is loaded automatically; invoke explicitly with `/<skill>`. Web via `WebSearch`/`WebFetch`, granted through `permissions`.
- **Codex:** skills are found in `.agents/skills` and `~/.agents/skills`. Invoke with `$<skill>` or `/skills`. `agents/openai.yaml` sets the display name and implicit invocation. `web_search` defaults to `cached`; use `live` for current facts.
- **ZCode:** skills live in `.zcode/skills` and `~/.zcode/skills`; invoke with `$<skill>` in the input box (also listed in the `/` menu). Frontmatter `name` + `description` are required; descriptions over 1024 characters make ZCode drop the skill — this suite's generator enforces that limit.
- **Cursor:** invoke `/<skill>` from the generated `.cursor/commands/<skill>.md`; the command directs the agent to read the skill in `.cursor/skills/`. Operating rules are always-on via `.cursor/rules/local-advisor-suite.mdc`, and Cursor additionally reads the project `AGENTS.md`.
- **OpenCode:** skills are loaded by the native `skill` tool (no `@` invocation). Permissions via `permission.skill` in `opencode.json`. `webfetch` always exists; `websearch` requires the OpenCode provider or `OPENCODE_ENABLE_EXA=1`. The suite never changes these settings for you.
- **Any AGENTS.md host:** the rules block routes requests to skills and names the workbench path; hosts without a skills loader can still run every command directly.

After installing (or after any change to the project setup), verify the installation:

```bash
python3 .claude/skills/local-advisor/scripts/workbench.py doctor --project-root .
```

`doctor` checks Python, the state directory, every detected host's skill directories, SKILL.md frontmatter limits, workbench copy versions, rules blocks and the manifest.

## Quick examples

```bash
WB="python3 .claude/skills/local-advisor/scripts/workbench.py"

# Route a prompt at the right depth (the suggested depth is in the response)
$WB load-skills --core --prompt "what is the latest python version and its release date"

# Playbooks: the composed chains, with gates
$WB playbook-list
$WB playbook-show --name decide

# Question contract: pin before work starts
$WB qc-pin --question "Which CI platform should we migrate to?" \
           --decision "choose one and start the migration next sprint" \
           --consumer "the two engineers doing the migration"
$WB qc-check
$WB qc-assume --assumption "better means faster pipeline, since budget was not raised"

# Devil's advocate: the full red-team pass
$WB devil-plan --archetype migrate
$WB devil-open --claim "Split the monolith into microservices this quarter" --steelman "Independent deploys end the release train"
$WB devil-premortem --failure-story "Cutover week broke on the billing adapter nobody rewrote" --cause "the billing adapter was never scoped"
$WB devil-outside --reference-class "monolith splits at teams under 15 engineers" --base-rate 35
$WB devil-challenge --assumption "each team ships daily once split" --attack "Review capacity, not the release train, limits deploys today" --severity SERIOUS --defeater "per-team deploy frequency rises within 6 weeks"
$WB devil-consequence --l1 "the old CI stops receiving changes" --l2 "edge cases break quietly while it is still a release path" --l3 "release week finds both pipelines drifted"
$WB devil-rebuttal --id C1 --rebuttal "Review data from last quarter shows reviews complete in hours" --basis "evidence: review metrics"
$WB devil-verdict --kill-criterion "per-team deploys stay at baseline 6 weeks after a split"

# Decision journal: score the advice
$WB journal-log --decision "Migrate CI to the managed platform" \
                --prediction "adoption exceeds 60% of the team at the 90-day review" \
                --confidence 75 --review-by 2027-02-10
$WB journal-resolve --id J1 --outcome HIT --lesson "the plugin spike de-risked the build before the decision"
$WB journal-report

# Decision: weighted score, hard constraint, sensitivity
$WB decision-score --spec-file decision.json --output .local-workbench/decision_result.json
$WB adr-new --title "Use a Postgres queue" --dir docs/adr --decision-result .local-workbench/decision_result.json
$WB adr-check --file docs/adr/0001-use-a-postgres-queue.md

# Debugging: case first, then hypotheses
$WB debug-hypothesis --symptom "test_total: 10.05 != 10.06" --target-file billing/invoice.py --repro "pytest -q tests/test_invoice.py"
$WB debug-report

# Data analysis: register the file, log findings with methods, then report
$WB data-register --path sales.csv --question "What is the monthly sales trend in this file?"
$WB data-finding --statement "The file has 5 data rows" --method 'tail -n +2 sales.csv | wc -l' --result "5 rows"
$WB data-report --answer "Sales rose from 120 to 170 across 5 months; the region split cannot be computed."

# Research and audit
$WB research-init --topic "..." --sub-question "..." --max-queries 12 --time-sensitive
$WB research-add-source --url URL --title "..." --tier PRIMARY --published-date 2026-10-01 --content-file page.txt
$WB research-add-claim --sub-question-id Q1 --statement "..." --source-id S1 --quote "verbatim sentence from the page"
$WB research-gaps && $WB research-pack && $WB audit-report --report-file report.md

# Specification, review, knowledge, verification, handoff
$WB spec-new --goal "..." --story "..." --non-goal "..." && $WB spec-check
$WB review-init --title "PR #142" --target "src/billing/export.py" && $WB review-report --not-reviewed "the migration"
$WB kb-add --question "..." --answer "..." --source-url URL --tag billing && $WB kb-search --query "csv export tax"
$WB verify-delivery --artifact src/app.py --check "L2:python3 -m py_compile src/app.py" --command "pytest -q" --require L3
$WB handoff-pack --title "..." --session-status PARTIAL --summary "..." --next-step "..." && $WB handoff-check
```

Every command returns JSON. Exit codes: `0` = OK/PASS (doctor's WARN is also `0`), `2` = FAIL, `1` = error.

## Package structure

```
local-advisor-suite/
├── workbench.py               # the single runtime (59 subcommands, v4.0)
├── install.py                 # project/global install for 6 hosts, manifest, uninstall
├── AGENTS.template.md         # rules block for Codex/ZCode/OpenCode/generic ({{WORKBENCH}})
├── CLAUDE.template.md         # rules block for Claude Code
├── CURSOR_RULE.template.mdc   # always-on Cursor rule
├── CURSOR_COMMAND.template.md # per-skill Cursor command generator input
├── skills/<18 skills>/        # SKILL.md, references/, templates/, examples/, agents/, scripts/
├── references/ templates/     # shared layer (generate_shared.py writes it)
├── .claude-plugin/ .codex-plugin/ .agents/plugins/   # plugin and marketplace manifests
├── tools/generate_shared.py   # generates shared files, skill copies; enforces frontmatter limits
└── tests/                     # test_workbench, test_install, test_package
```

After editing `workbench.py` or shared files, run `python3 tools/generate_shared.py`. `tests/test_package.py` fails if the skill copies drift.

## Limits

- The audit checks that numbers and links trace to registered pages and quotes. It cannot prove a number is used in the right context or that reasoning is valid; those steps are manual and documented in `evidence-audit/references/audit-rules.md`.
- Number checking works at the digit level: any number appearing anywhere in the quoted evidence passes.
- Web search depends on the host's tools. With no web tool enabled, skills do not guess; they tell you which setting to enable or ask for the page text.
- The vague-term scan is a word list, not a mind reader: it catches "better"; it cannot catch a missing constraint. The contract's `open` list is where you write the constraint the question forgot to mention.
- Calibration math needs volume: below ten resolved entries the bands are illustrative. The report is honest about this; keep resolving.
- Cursor loads skills on demand via generated commands (no native skills auto-discovery); everything else behaves the same.
- ZCode project-level skill discovery follows `.zcode/skills/`; if your ZCode build differs, use the Settings -> Skills -> Import path, which scans Claude Code and Codex directories.
