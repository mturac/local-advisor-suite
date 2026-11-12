# Local Advisor Suite — Console

**v4.1.2** · cross-host agent skill suite + a web console to drive every command from your browser.

> **Türkçe:** Bu depo iki şey içerir: **Local Advisor Suite** (çevrimdışı çalışan, 59 komutluk, 6 araca kurulabilen bir beceri paketi) ve onu **tarayıcıdan denemeni sağlayan web konsolu**. Kurulum yok, hesap yok: bir hikâye seç, *Çalıştır*'a bas, gerçek komutların gerçek çıktılarını gör. Arayüz **Türkçe ve İngilizce** — sağ üstteki TR/EN düğmesiyle değiştir.

This repository contains two things:

| Path | What it is |
| --- | --- |
| `suite/` | **Local Advisor Suite v4.1.2** — the offline, vendor-neutral workbench: 64 commands, 18 skills, 5 playbooks, 169 tests, installer for 6 hosts (Claude Code, Codex, ZCode, Cursor, OpenCode, generic AGENTS.md) |
| root | **Web Console** — a bilingual (🇹🇷 TR / 🇬🇧 EN) Next.js 16 app that runs every workbench command against a seeded demo workspace, no setup required |

![Console](public/console.png)

## Why a console?

The suite is a CLI (`suite/workbench.py`) designed to be driven by coding agents. The console gives humans the same seat: pick a story, press Run, and watch the real command execute — with a plain-language explanation, the exact command line, a "you'll see" preview of the expected result, and the structured JSON it actually emitted. / Konsol, aynı koltuğu insanlara verir: hikâyeyi seç, Çalıştır'a bas — sade dilde açıklamayı, tam komut satırını, "şu görünecek" önizlemesini ve gerçek çıktıyı gör.

Everything the console runs is **the real Python CLI**, spawned server-side with:

- an **allowlist** derived from the CLI's own argparse tree (unknown commands are rejected with HTTP 400),
- a **pinned `--state-dir`** (user-supplied overrides are stripped) so runs stay inside the demo workspace,
- a hard **45 s timeout** and captured stdout/stderr,
- a **seeded workspace** (`.workspace/`, gitignored) with a 6-host install, research/spec/review/knowledge/debug ledgers, an ADR, an artifact and a handoff pack — resettable with one click.

## Quick start (console) / Hızlı başlangıç

```bash
bun install                 # or: npm install
cp .env.example .env        # SQLite via Prisma
bun run db:push             # create the run-history database
bun run dev                 # http://localhost:3000
```

Requirements: Node.js / Bun, Python 3.9+ on PATH. The first page load introspects the CLI and caches the command catalog. The UI opens in Turkish by default (or your browser language) — switch any time with the **TR/EN** toggle in the header.

On first run the workspace is empty — open the **Files / Dosyalar** tab and hit **Reset workspace** (seeds demo state, ~10 s), or run any command; read-only ones work against whatever state exists.

## Quick start (suite)

```bash
cd suite
./run_tests.sh                          # 169 tests, zero dependencies
python3 install.py --project ~/myapp    # installs skills for 6 hosts
python3 workbench.py doctor             # installation health check
```

See `suite/README.md` for the full suite documentation, and `suite/CHANGELOG.md` for what changed.

## Console tour

| Tab | Ne yapar (TR) | What you can do (EN) |
| --- | --- | --- |
| **Hikâyeler / Stories** | Baştan sona anlatılan senaryolar: soldan hikâyeyi seç, *Tümünü çalıştır*'a bas; her adımın ne yaptığını, komutunu ve "şu görünecek" kutusunu gör, sonunda gerçek bir dosyayla bitir | Guided end-to-end stories — each step explained in plain language with its exact command, a "you'll see" preview, and its real result; ends with a real artifact (evidence pack, handoff, root-cause report, ADR) |
| **Komut Dene / Try Commands** | 64 senaryonun tamamı hazır argümanlarla, tek tıkla; istersen kendi argümanlarınla çalıştır | Sandbox for single commands: one-click examples for all 64 scenarios, auto-generated argument forms, raw JSON output |
| **Beceriler / Skills** | 18 beceriyi gez, SKILL.md'leri oku | Browse the 18 bundled skills, read each `SKILL.md` and its bundled examples |
| **Sağlık / Health** | Tek tıkla `doctor` ve `selfcheck` | One-click `doctor` (per-check health table) and `selfcheck` (vendor-neutrality scan) |
| **Dosyalar / Files** | Canlı defterleri ve üretilen dosyaları incele, tek tıkla sıfırla | Inspect live ledgers and generated artifacts, reset everything |
| **Geçmiş / History** | Her çalıştırma SQLite'ta saklanır | Every run persisted in SQLite, expandable |

Four walkthrough stories ship today (all bilingual, all validated end to end):

| Hikâye / Story | Steps | Ends with |
| --- | --- | --- |
| **Bir soruyu kanıtlarla cevapla / Answer a question with evidence** | 13 | cited `evidence pack` + passing integrity audit |
| **Bir değişikliği güvenle teslim et / Ship a change safely** | 10 | L2-verified delivery, reviewed verdict, session handoff |
| **Bir hatayı kök nedenine kadar kovala / Chase a bug to its root cause** | 7 | root-cause report for a real bug in the bundled demo project |
| **Pişman olmayacağın bir karar ver / Make a call you won't regret** | 3 | numbered, table-filled ADR |

Every step sequence is validated end to end by `scripts/test_walkthroughs.py` (fresh seeded workspace, expected exit codes and statuses, deliverable files checked on disk — 36/36 passing), and the UI data (including the Turkish/English text for every step) is generated from the same `scripts/walkthroughs.json` via `scripts/gen_walkthroughs_ts.py`.

For single commands, the **one-click examples** cover all 64 scenarios with pre-filled working arguments; amber chips (e.g. `research-init`, `spec-new`, `review-init`, `devil-open`) wipe their ledger first, and the demo data can be restored anytime with *Reset workspace*.

## Repository layout

```
├── suite/                    # Local Advisor Suite v4.1.2 (self-contained)
│   ├── workbench.py          # 47-command CLI (JSON in, JSON out)
│   ├── install.py            # 6-host installer / uninstaller
│   ├── skills/               # 18 skills with references/templates/examples
│   ├── tests/                # 169 tests (run_tests.sh)
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
│   ├── scenarios.json         # one-command examples for all 64 scenarios
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
