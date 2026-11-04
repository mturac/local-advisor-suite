# Local Advisor Suite — Console

**v3.0.0** · cross-host agent skill suite + a web console to drive every command from your browser.

This repository contains two things:

| Path | What it is |
| --- | --- |
| `suite/` | **Local Advisor Suite v3.0.0** — the offline, vendor-neutral workbench: 38 commands, 13 skills, 95 tests, installer for 6 hosts (Claude Code, Codex, ZCode, Cursor, OpenCode, generic AGENTS.md) |
| root | **Web Console** — a Next.js 16 app that runs every workbench command against a seeded demo workspace, no setup required |

![Console](public/console.png)

## Why a console?

The suite is a CLI (`suite/workbench.py`) designed to be driven by coding agents. The console gives humans the same seat: pick a command, fill its real arguments, run it, and inspect the structured JSON it emits — plus a doctor dashboard, a skills browser, live workspace ledgers and a persisted run history.

Everything the console runs is **the real Python CLI**, spawned server-side with:

- an **allowlist** derived from the CLI's own argparse tree (unknown commands are rejected with HTTP 400),
- a **pinned `--state-dir`** (user-supplied overrides are stripped) so runs stay inside the demo workspace,
- a hard **45 s timeout** and captured stdout/stderr,
- a **seeded workspace** (`.workspace/`, gitignored) with a 6-host install, research/spec/review/knowledge/debug ledgers, an ADR, an artifact and a handoff pack — resettable with one click.

## Quick start (console)

```bash
bun install                 # or: npm install
cp .env.example .env        # SQLite via Prisma
bun run db:push             # create the run-history database
bun run dev                 # http://localhost:3000
```

Requirements: Node.js / Bun, Python 3.9+ on PATH. The first page load introspects the CLI and caches the command catalog.

On first run the workspace is empty — open the **Workspace** tab and hit **Reset workspace** (seeds demo state, ~10 s), or run any command; read-only ones work against whatever state exists.

## Quick start (suite)

```bash
cd suite
./run_tests.sh                          # 95 tests, zero dependencies
python3 install.py --project ~/myapp    # installs skills for 6 hosts
python3 workbench.py doctor             # installation health check
```

See `suite/README.md` for the full suite documentation, and `suite/CHANGELOG.md` for what changed in v3.0.0.

## Console tour

| Tab | What you can do |
| --- | --- |
| **Walkthroughs** | Guided end-to-end stories — pick a flow (research, ship, debug, decide), hit *Run all steps* and watch the whole task complete against the real CLI, with each step explained, its command shown and its result summarized. Ends with a real artifact (evidence pack, handoff, root-cause report, ADR) |
| **Runner** | Sandbox for single commands: search all 38 commands by category, fill auto-generated argument forms (repeatable flags, switches, choice dropdowns), add raw extra args, run and inspect JSON output — plus one-click examples with pre-filled arguments for every command |
| **Skills** | Browse the 13 bundled skills, read each `SKILL.md` rendered as markdown, and open the bundled `examples/*.md` walkthroughs in per-skill tabs |
| **Doctor** | One-click `doctor` (host detection, per-check health table) and `selfcheck` (vendor-neutrality scan over the whole suite) |
| **Workspace** | Inspect the seeded ledgers (research, spec, review, kb, debug, advisory), generated artifacts, and reset everything |
| **History** | Every run persisted in SQLite — expand any row to replay its JSON output |

Four walkthrough flows ship today, each a complete story on the seeded demo workspace:

| Flow | Steps | Ends with |
| --- | --- | --- |
| **Answer a question with evidence** | 13 | cited `evidence pack` + passing integrity audit |
| **Ship a change safely** | 10 | L2-verified delivery, reviewed verdict, session handoff |
| **Chase a bug to its root cause** | 7 | root-cause report for a real bug in the bundled demo project |
| **Make a call you won't regret** | 3 | numbered, table-filled ADR |

Every step sequence is validated end to end by `scripts/test_walkthroughs.py` (fresh seeded workspace, expected exit codes and statuses, deliverable files checked on disk — 33/33 passing), and the UI data is generated from the same `scripts/walkthroughs.json` via `scripts/gen_walkthroughs_ts.py`.

For single commands, the Runner's **one-command examples** cover all 38 commands with pre-filled working arguments; amber chips (e.g. `research-init`, `spec-new`, `review-init`) wipe their ledger first, and the demo data can be restored anytime with *Reset workspace*.

## Repository layout

```
├── suite/                    # Local Advisor Suite v3.0.0 (self-contained)
│   ├── workbench.py          # 38-command CLI (JSON in, JSON out)
│   ├── install.py            # 6-host installer / uninstaller
│   ├── skills/               # 13 skills with references/templates/examples
│   ├── tests/                # 95 tests (run_tests.sh)
│   └── references/ templates/ tools/
├── src/
│   ├── app/                  # Next.js app router (single page + API routes)
│   │   └── api/              # /catalog /run /skills /workspace /history
│   ├── components/console/   # Runner, SkillsBrowser, DoctorPanel, WorkspacePanel, HistoryPanel
│   └── lib/suite.ts          # spawn/isolation layer between web and CLI
├── scripts/
│   ├── introspect_catalog.py  # argparse → JSON command catalog
│   ├── seed_workspace.py      # demo workspace seeder (also used by "Reset")
│   ├── walkthroughs.json      # guided end-to-end flows (single source of truth)
│   ├── test_walkthroughs.py   # validates every flow against a fresh seed
│   ├── gen_walkthroughs_ts.py # walkthroughs.json → src/lib/walkthroughs.ts
│   ├── scenarios.json         # one-command examples for all 38 commands
│   ├── test_scenarios.py      # validates every scenario against a fresh seed
│   └── gen_scenarios_ts.py    # scenarios.json → src/lib/scenarios.ts
├── prisma/schema.prisma      # RunLog model (run history)
└── .env.example
```

## Notes

- The console never modifies `suite/` — the suite stays a pristine, agent-consumable package; all runtime state lives in `.workspace/` (gitignored).
- Run history is best-effort: if the database is unavailable the console still executes commands.
- To point the console at a different suite checkout: `SUITE_DIR=/path/to/suite bun run dev`.

## License

MIT — see `suite/LICENSE`.
