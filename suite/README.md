# local-advisor-suite 3.3.0

A provider-neutral advisory, research, debugging, specification, review, verification, knowledge, data-analysis and adversarial-challenge suite — **15 skills** that run identically in **Claude Code, Codex, ZCode, Cursor, OpenCode, and any AGENTS.md-compatible agent**.

The suite depends on no search vendor, no API key, and no MCP server. When web access is needed, it uses only the search and fetch tools your host already provides. All ledger, scoring, audit and verification work is done by a single standard-library Python file (`workbench.py`) that runs offline and deterministically.

Built on the user's own `workbench.py` and `tools/generate_shared.py`. The v2.1 command set and JSON contract are preserved exactly; every v2.1 command and flag still works. Additions and fixes are listed in [CHANGELOG.md](CHANGELOG.md).

## Why this suite

- **Does not scan files by default.** `local-advisor` works from the conversation. A file is read only when you name it, via `scope-read`, inside the project root. `.env`, key files and out-of-root paths are blocked.
- **Does not retry forever.** `local-debug` stops after 2 falsified hypotheses and writes a root-cause or escalation report.
- **Accepts no fabricated sources.** A claim is rejected unless its quote appears verbatim in the stored text of an opened page. Reports are audited for unopened links, unsupported numbers and overclaim language.
- **Proves before saying "done".** `delivery-verify` runs the real commands and reports the achieved level on the L0-L4 ladder.
- **Makes specs testable.** `spec-builder` turns requests into Given/When/Then acceptance criteria and tasks that must each verify a criterion.
- **Makes reviews mechanical.** `code-review` grades findings by severity; the verdict is FAIL while any BLOCKING finding is open.
- **Argues back before commitment.** `devil-advocate` steelmans the plan, attacks its load-bearing assumptions with severity-graded challenges, and BLOCKs while a FATAL one stands unanswered.
- **Remembers honestly.** `knowledge-capture` stores sourced Q&A entries; assumptions are marked, never quoted as fact.
- **No extra cost.** No paid services. The only command that can open a socket is `fetch-url`, and only with `--allow-network`.
- **Works everywhere.** One installer, six hosts; `doctor` verifies any installation's health.

## Skills

| Skill | When | Core commands |
|---|---|---|
| `local-advisor` | Architecture, design, plan and trade-off advice (no file scanning) | `advise-intake` (optional) |
| `decision-review` | Option comparison, ADRs, reversibility (R0-R3), pre-mortem | `decision-score`, `adr-new`, `adr-check` |
| `local-debug` | A bug in a file you name; at most 2 hypotheses | `debug-hypothesis`, `scope-read --debug-scope`, `debug-report` |
| `data-analysis` | A data file you name; every number traceable to a logged command | `data-register`, `data-finding`, `data-gap`, `data-report` |
| `devil-advocate` | Stress-test a plan before committing: steelman, challenges, rebuttals, verdict | `devil-open`, `devil-challenge`, `devil-rebuttal`, `devil-verdict` |
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

The 14th skill arrived in v3.2.0: prompts like "analyze this CSV" or "bu veri dosyasını analiz et" previously fell through the routing table to the advisory fallback; `data-analysis` closes that gap with the same discipline the other ledgers enforce — a number is only speakable when the command that produced it is on the record.

The 15th skill arrived in v3.3.0: `devil-advocate` is the adversarial second opinion the suite lacked. "Şeytanın avukatlığını yap" now routes somewhere real: the plan gets an honest steelman first, then its load-bearing assumptions are attacked with severities and defeaters, answered challenges leave the verdict, and the unanswered ones decide it mechanically — BLOCK while a FATAL stands, PROCEED_WITH_GUARDS over an open SERIOUS, with pre-committed kill criteria either way.

## Installation

Requirement: Python 3.9+ (standard library only; tested with Python 3.12/3.14). No `pip install`.

```bash
unzip local-advisor-suite.zip
cd local-advisor-suite
./run_tests.sh                                     # 125 tests

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

- Claude Code: `/plugin marketplace add ./local-advisor-suite`, then `/plugin install local-advisor-suite@local-advisor-suite`. Plugin skills are invoked as `/local-advisor-suite:<skill>`.
- Codex: `codex plugin marketplace add ./local-advisor-suite`. The manifest is `.codex-plugin/plugin.json`, the marketplace file `.agents/plugins/marketplace.json`.
- ZCode: the repository root's flat `skills/<name>/SKILL.md` layout is a valid plugin source for a ZCode marketplace that accepts local directories.

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

# Decision: weighted score, hard constraint, sensitivity
$WB decision-score --spec-file decision.json --output .local-workbench/decision_result.json
$WB adr-new --title "Use a Postgres queue" --dir docs/adr --decision-result .local-workbench/decision_result.json
$WB adr-check --file docs/adr/0001-use-a-postgres-queue.md

# Debugging: case first, then hypotheses
$WB debug-hypothesis --symptom "test_total: 10.05 != 10.06" --target-file billing/invoice.py --repro "pytest -q tests/test_invoice.py"
$WB debug-hypothesis --id H1 --status PENDING --statement "..." --prediction "..." --test-command "..."
$WB debug-report

# Data analysis: register the file, log findings with methods, then report
$WB data-register --path sales.csv --question "What is the monthly sales trend in this file?"
$WB data-finding --statement "The file has 5 data rows" --method 'tail -n +2 sales.csv | wc -l' --result "5 rows"
$WB data-gap --description "Per-region breakdown is not computable" --reason "NO_DATA: no region column"
$WB data-report --answer "Sales rose from 120 to 170 across 5 months; the region split cannot be computed."

# Devil's advocate: steelman, attack, answer, gate
$WB devil-open --claim "Split the monolith into microservices this quarter" --steelman "Independent deploys end the release train"
$WB devil-challenge --assumption "each team ships daily once split" --attack "Review capacity, not the release train, limits deploys today" --severity SERIOUS --defeater "per-team deploy frequency rises within 6 weeks"
$WB devil-rebuttal --id C1 --rebuttal "Review data from last quarter shows reviews complete in hours" --basis "evidence: review metrics"
$WB devil-verdict --kill-criterion "per-team deploys stay at baseline 6 weeks after a split"

# Research and audit
$WB research-init --topic "..." --sub-question "..." --max-queries 12 --time-sensitive
$WB research-add-source --url URL --title "..." --tier PRIMARY --published-date 2026-10-01 --content-file page.txt
$WB research-add-claim --sub-question-id Q1 --statement "..." --source-id S1 --quote "verbatim sentence from the page"
$WB research-gaps && $WB research-pack && $WB audit-report --report-file report.md

# Specification
$WB spec-new --goal "..." --story "..." --non-goal "..."
$WB spec-criterion --story-id US1 --given "..." --when "..." --then "..."
$WB spec-task --task "..." --verifies AC1 --depends-on T1
$WB spec-check

# Review
$WB review-init --title "PR #142" --target "src/billing/export.py"
$WB review-finding --file src/billing/export.py --line 42 --severity BLOCKING --description "..."
$WB review-report --not-reviewed "the migration"

# Knowledge
$WB kb-add --question "..." --answer "..." --source-url URL --tag billing
$WB kb-search --query "csv export tax"

# Delivery verification
$WB verify-delivery --artifact src/app.py --check "L2:python3 -m py_compile src/app.py" --command "pytest -q" --require L3

# Handoff
$WB handoff-pack --title "..." --session-status PARTIAL --summary "..." --next-step "..."
$WB handoff-check
```

Every command returns JSON. Exit codes: `0` = OK/PASS (doctor's WARN is also `0`), `2` = FAIL, `1` = error.

## Package structure

```
local-advisor-suite/
├── workbench.py               # the single runtime (47 subcommands, v3.3)
├── install.py                 # project/global install for 6 hosts, manifest, uninstall
├── AGENTS.template.md         # rules block for Codex/ZCode/OpenCode/generic ({{WORKBENCH}})
├── CLAUDE.template.md         # rules block for Claude Code
├── CURSOR_RULE.template.mdc   # always-on Cursor rule
├── CURSOR_COMMAND.template.md # per-skill Cursor command generator input
├── skills/<15 skills>/        # SKILL.md, references/, templates/, examples/, agents/, scripts/
├── references/ templates/     # shared layer (generate_shared.py writes it)
├── .claude-plugin/ .codex-plugin/ .agents/plugins/   # plugin and marketplace manifests
├── tools/generate_shared.py   # generates shared files, skill copies; enforces frontmatter limits
└── tests/                     # test_workbench, test_install, test_package (125 tests)
```

After editing `workbench.py` or shared files, run `python3 tools/generate_shared.py`. `tests/test_package.py` fails if the skill copies drift.

## Limits

- The audit checks that numbers and links trace to registered pages and quotes. It cannot prove a number is used in the right context or that reasoning is valid; those steps are manual and documented in `evidence-audit/references/audit-rules.md`.
- Number checking works at the digit level: any number appearing anywhere in the quoted evidence passes.
- Web search depends on the host's tools. With no web tool enabled, skills do not guess; they tell you which setting to enable or ask for the page text.
- Cursor loads skills on demand via generated commands (no native skills auto-discovery); everything else behaves the same.
- ZCode project-level skill discovery follows `.zcode/skills/`; if your ZCode build differs, use the Settings -> Skills -> Import path, which scans Claude Code and Codex directories.
