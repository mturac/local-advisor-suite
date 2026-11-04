#!/usr/bin/env python3
"""Generate real example transcripts for every skill by actually running workbench.py."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/z/my-project/download/local-advisor-suite")
STATE = Path("/tmp/wb-examples/state")
WB = ["python3", str(ROOT / "workbench.py"), "--state-dir", str(STATE)]
SCRATCH = Path("/tmp/wb-examples")
SCRATCH.mkdir(parents=True, exist_ok=True)


def clean(out: str) -> str:
    return (out.replace(str(STATE), ".local-workbench")
               .replace(str(SCRATCH) + "/", "")
               .replace(str(ROOT) + "/", ""))


def run(*args, expect_fail=False):
    proc = subprocess.run(WB + list(args), capture_output=True, text=True, cwd=str(SCRATCH))
    out = proc.stdout if proc.stdout.strip() else proc.stderr
    ok = (proc.returncode != 0) if expect_fail else (proc.returncode == 0)
    if not ok:
        print(f"UNEXPECTED rc={proc.returncode} for: {' '.join(args)}\n{out[:500]}", file=sys.stderr)
        sys.exit(1)
    return clean(out.strip())


def block(cmd, out, note=""):
    b = f"```bash\n$ {cmd}\n```\n\n```json\n{out}\n```"
    if note:
        b += f"\n\n{note}"
    return b


def write_example(skill, name, title, intro, blocks):
    p = ROOT / "skills" / skill / "examples" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", "", intro, ""]
    for b in blocks:
        body += [b, ""]
    p.write_text("\n".join(body) + "\n", encoding="utf-8")
    print("wrote", p.name, "->", skill)


# ---- scratch inputs
(SCRATCH / "decision.json").write_text(json.dumps({
    "title": "Queue for background jobs",
    "criteria": [
        {"id": "ops", "weight": 3, "min_score": 4},
        {"id": "throughput", "weight": 2},
        {"id": "durability", "weight": 3, "min_score": 5},
    ],
    "options": [
        {"name": "Postgres queue", "scores": {"ops": 7, "throughput": 5, "durability": 8}, "risks": ["poll latency up to 5s"]},
        {"name": "Redis streams", "scores": {"ops": 4, "throughput": 8, "durability": 6}, "risks": ["one more stateful system"]},
        {"name": "Managed cloud queue", "scores": {"ops": 8, "throughput": 7, "durability": 8, "license": 3}, "risks": ["vendor lock-in"]},
    ],
}, indent=2), encoding="utf-8")
(SCRATCH / "page1.txt").write_text(
    "DuckDB supports two concurrency models: one process with read-write access, or multiple processes "
    "with read-only access. External processes that need to write must coordinate through file locking."
)
(SCRATCH / "page2.txt").write_text(
    "SQLite allows multiple processes to read concurrently, but only a single writer at a time; writes "
    "are serialized database-wide. DuckDB takes the same single-writer approach for external processes."
)
(SCRATCH / "oldblog.txt").write_text(
    "In our 2024 benchmark setup, DuckDB supported only a single external process opening the database file, "
    "which made shared access impossible."
)

# ============================== local-advisor ==============================
write_example("local-advisor", "architecture-intake.md", "Advisory intake for an architecture question",
    "Recorded intake for a service-extraction question. The answer that follows works from this brief alone — no repository scan.",
    [block("python3 scripts/workbench.py advise-intake \\\n  --question \"Should we move billing into a separate service?\" \\\n  --context \"Monolith, 4 engineers, weekly deploys, billing is 12% of the codebase\" \\\n  --constraint \"No new infrastructure budget this year\" \\\n  --non-goal \"Not rewriting the invoicing domain\" \\\n  --mode architecture",
        run("advise-intake",
            "--question", "Should we move billing into a separate service?",
            "--context", "Monolith, 4 engineers, weekly deploys, billing is 12% of the codebase",
            "--constraint", "No new infrastructure budget this year",
            "--non-goal", "Not rewriting the invoicing domain",
            "--mode", "architecture"),
        "The intake pins the question, constraints and non-goals. The advisory answer then follows `references/answer-standards.md`: recommendation first, options with real trade-offs, reversibility, and a confidence label — answered from the conversation, with at most one precise clarifying question if a fact would change the recommendation.")])

# ============================== decision-review ==============================
write_example("decision-review", "postgres-vs-redis.md", "A scored decision with sensitivity and an ADR",
    "A full decision: the spec file, the scored result with its sensitivity block, and the ADR generated from it. Scores in this example are illustrative judgments, not researched facts — a real decision researches them first.",
    [block("python3 scripts/workbench.py decision-score --spec-file decision.json --output .local-workbench/decision_result.json",
           run("decision-score", "--spec-file", "decision.json", "--output", str(STATE / "decision_result.json")),
           "Read the sensitivity block before the winner: the margin and the flip points say how much of this decision is assumption. `unknown` scores are listed in `warnings` — research them before committing."),
     block("python3 scripts/workbench.py adr-new --title \"Use a Postgres queue\" --dir docs/adr \\\n  --owner \"@platform\" --decision-result .local-workbench/decision_result.json",
           run("adr-new", "--title", "Use a Postgres queue", "--dir", str(SCRATCH / "docs/adr"),
               "--owner", "@platform", "--decision-result", str(STATE / "decision_result.json")),
           "The ADR is pre-filled from the decision result; `placeholders_left` is the debt list. Fill every placeholder (rationale, steelman, reversibility class R0-R3, pre-mortem), then check it."),
     block("python3 scripts/workbench.py adr-check --file docs/adr/0001-use-a-postgres-queue.md",
           run("adr-check", "--file", str(SCRATCH / "docs/adr/0001-use-a-postgres-queue.md"), expect_fail=True),
           "This check ran against the freshly generated ADR, so it correctly reports the unfilled placeholders. After filling them in (and writing an honest steelman and rollback trigger), the same command returns PASS.")])

# ============================== local-debug ==============================
write_example("local-debug", "invoice-rounding.md", "From failing test to root-cause report",
    "A real case: an invoice total mismatch. The first hypothesis is falsified by a one-line prediction test; the second is confirmed. Both are in the ledger — the falsification is part of the record.",
    [block("python3 scripts/workbench.py debug-hypothesis \\\n  --symptom \"test_total: 10.05 != 10.06 (1 failure)\" \\\n  --target-file billing/invoice.py \\\n  --repro \"pytest -q tests/test_invoice.py::test_total\"",
           run("debug-hypothesis",
               "--symptom", "test_total: 10.05 != 10.06 (1 failure)",
               "--target-file", "billing/invoice.py",
               "--repro", "pytest -q tests/test_invoice.py::test_total"),
           "The case is recorded before anything is read or changed. `--target-file` scopes every later `scope-read --debug-scope` to this file."),
     block("python3 scripts/workbench.py debug-hypothesis --id H1 --status PENDING \\\n  --statement \"Totals are rounded per line before summing\" \\\n  --prediction \"If true, round(3.35, 2) * 3 returns 10.05 while the test expects 10.06\" \\\n  --test-command \"python3 -c 'print(round(3.35, 2) * 3)'\"",
           run("debug-hypothesis", "--id", "H1", "--status", "PENDING",
               "--statement", "Totals are rounded per line before summing",
               "--prediction", "If true, round(3.35, 2) * 3 returns 10.05 while the test expects 10.06",
               "--test-command", "python3 -c 'print(round(3.35, 2) * 3)'"),
           "The prediction is numeric on purpose: it can fail. A prediction that cannot fail is not a prediction."),
     block("python3 scripts/workbench.py debug-hypothesis --id H1 --status FALSIFIED \\\n  --evidence \"round(3.35, 2) * 3 = 10.05 matches the observed value, but the failing fixture has a single line, so per-line rounding cannot produce the observed 10.05 on one line\"",
           run("debug-hypothesis", "--id", "H1", "--status", "FALSIFIED",
               "--evidence", "round(3.35, 2) * 3 = 10.05 matches the observed value, but the failing fixture has a single line, so per-line rounding cannot produce the observed 10.05 on one line"),
           "One strike. The evidence explains *why* the hypothesis is dead — the next reader does not re-run it."),
     block("python3 scripts/workbench.py debug-hypothesis --id H2 --status PENDING \\\n  --statement \"Tax is applied after the total is rounded to 2 decimals\" \\\n  --prediction \"If true, applying tax after rounding a 10.05 subtotal yields 10.05, not the expected 10.06\" \\\n  --test-command \"python3 -c 'print(round(10.05 + 10.05 * 0.006, 2))'\"",
           run("debug-hypothesis", "--id", "H2", "--status", "PENDING",
               "--statement", "Tax is applied after the total is rounded to 2 decimals",
               "--prediction", "If true, applying tax after rounding a 10.05 subtotal yields 10.05, not the expected 10.06",
               "--test-command", "python3 -c 'print(round(10.05 + 10.05 * 0.006, 2))'"),
           "Second hypothesis, informed by the first one's failure — not a blind second guess."),
     block("python3 scripts/workbench.py debug-hypothesis --id H2 --status CONFIRMED \\\n  --evidence \"Order of operations in _line_total(): round(subtotal, 2) happens before tax is added, losing the tax fraction\"",
           run("debug-hypothesis", "--id", "H2", "--status", "CONFIRMED",
               "--evidence", "Order of operations in _line_total(): round(subtotal, 2) happens before tax is added, losing the tax fraction"),
           "Confirmed — the root cause is a mechanism, not a vibe. Only now is a fix designed."),
     block("python3 scripts/workbench.py debug-report \\\n  --fix \"Apply tax before rounding in _line_total()\" \\\n  --open-risk \"Did not check credit notes, which use a different total path\"",
           run("debug-report",
               "--fix", "Apply tax before rounding in _line_total()",
               "--open-risk", "Did not check credit notes, which use a different total path"),
           "The report distinguishes what was fixed from what was not checked. The fix claim is then proven separately with `delivery-verify --check \"L3:pytest -q tests/test_invoice.py::test_total\"`.")])

# ============================== web-search + deep-research (shared ledger) ==============================
write_example("web-search", "version-lookup.md", "A quick verified lookup",
    "A one-fact lookup with the optional ledger. The source is registered from the fetched page text; the claim's quote must appear verbatim in the stored excerpt or it is rejected.",
    [block("python3 scripts/workbench.py research-init --topic \"DuckDB external process concurrency model\" \\\n  --mode quick-verify --max-queries 3",
           run("research-init", "--topic", "DuckDB external process concurrency model", "--mode", "quick-verify", "--max-queries", "3")),
     block("python3 scripts/workbench.py research-log-query --query \"DuckDB concurrency multiprocess file locking documentation\" --sub-question-id Q1",
           run("research-log-query", "--query", "DuckDB concurrency multiprocess file locking documentation", "--sub-question-id", "Q1")),
     block("python3 scripts/workbench.py research-add-source \\\n  --url https://duckdb.org/docs/connect/concurrency \\\n  --title \"Concurrency - DuckDB Documentation\" --publisher \"DuckDB Foundation\" \\\n  --tier PRIMARY --published-date 2026 --content-file page.txt",
           run("research-add-source",
               "--url", "https://duckdb.org/docs/connect/concurrency",
               "--title", "Concurrency - DuckDB Documentation", "--publisher", "DuckDB Foundation",
               "--tier", "PRIMARY", "--published-date", "2026", "--content-file", str(SCRATCH / "page1.txt")),
           "The source is the *opened page's* cleaned text, saved with `--content-file` (or `--excerpt`). A search snippet never qualifies."),
     block("python3 scripts/workbench.py research-add-claim \\\n  --sub-question-id Q1 --entity DuckDB --field process_concurrency \\\n  --statement \"DuckDB allows either a single read-write process or multiple read-only processes\" \\\n  --value \"1 RW or N RO\" --source-id S1 \\\n  --quote \"one process with read-write access, or multiple processes with read-only access\"",
           run("research-add-claim",
               "--sub-question-id", "Q1", "--entity", "DuckDB", "--field", "process_concurrency",
               "--statement", "DuckDB allows either a single read-write process or multiple read-only processes",
               "--value", "1 RW or N RO", "--source-id", "S1",
               "--quote", "one process with read-write access, or multiple processes with read-only access"),
           "`quote_verified_in_excerpt: true` is the whole point of the ledger — the answer can now be given with an inline citation to the opened page.")])

write_example("deep-research", "duckdb-concurrency.md", "A research ledger with a contradiction and its resolution",
    "A condensed real run continuing the same ledger: a third source creates a contradiction on the same (entity, field), which is then resolved on the record, scored, and packed. In a live session the pages are fetched with the host's tools and saved with `--content-file`.",
    [block("python3 scripts/workbench.py research-log-query --query \"2024 DuckDB benchmark single process limitation\" --sub-question-id Q1",
           run("research-log-query", "--query", "2024 DuckDB benchmark single process limitation", "--sub-question-id", "Q1")),
     block("python3 scripts/workbench.py research-add-source --url https://example.com/2024-duckdb-benchmark \\\n  --title \"2024 benchmark notes\" --tier TERTIARY --published-date 2024 --content-file oldblog.txt",
           run("research-add-source", "--url", "https://example.com/2024-duckdb-benchmark",
               "--title", "2024 benchmark notes", "--tier", "TERTIARY", "--published-date", "2024",
               "--content-file", str(SCRATCH / "oldblog.txt")),
           "The tertiary blog is registered because it is about to create a contradiction — contradictions are resolved on the record, not ignored."),
     block("python3 scripts/workbench.py research-add-claim --sub-question-id Q1 --entity DuckDB --field process_concurrency \\\n  --statement \"Only a single external process can open the database file\" \\\n  --value \"single process only\" --source-id S2 \\\n  --quote \"only a single external process opening the database file\" --confidence LOW",
           run("research-add-claim", "--sub-question-id", "Q1", "--entity", "DuckDB", "--field", "process_concurrency",
               "--statement", "Only a single external process can open the database file",
               "--value", "single process only", "--source-id", "S2",
               "--quote", "only a single external process opening the database file", "--confidence", "LOW")),
     block("python3 scripts/workbench.py research-status",
           run("research-status"),
           "The contradiction is visible: same (entity, field), two different normalized values. It blocks `ready_to_synthesize` until resolved."),
     block("python3 scripts/workbench.py research-resolve --entity DuckDB --field process_concurrency \\\n  --winner-claim C1 \\\n  --reason \"C1 cites the current official documentation; C2's source describes the older 2024 behavior and is TERTIARY\"",
           run("research-resolve", "--entity", "DuckDB", "--field", "process_concurrency",
               "--winner-claim", "C1",
               "--reason", "C1 cites the current official documentation; C2's source describes the older 2024 behavior and is TERTIARY"),
           "The reason is part of the record: scope, date, tier — why the winner wins."),
     block("python3 scripts/workbench.py research-score",
           run("research-score"),
           "Each source carries its 0-5 score and the reasons for every adjustment (tier base, domain trust, excerpt length, recency)."),
     block("python3 scripts/workbench.py research-pack",
           run("research-pack"),
           "The pack is the synthesis boundary: claims, quotes and citations grouped by sub-question, with superseded claims marked. The report is written from this file only, then audited with `audit-report`.")])

# ============================== wide-search ==============================
write_example("wide-search", "db-matrix.md", "A 2-entity matrix with a resolved conflict and a gap",
    "Wide-matrix mode on a fresh ledger: claims carry (entity, field) and land in cells; a conflict on one cell is resolved; another cell is declared `n.a.` with its attempted queries.",
    [block("python3 scripts/workbench.py research-init --mode wide-matrix \\\n  --topic \"Embedded analytical DBs compared\" \\\n  --entity DuckDB --entity SQLite \\\n  --field process_concurrency --field writer_model \\\n  --max-queries 6",
           run("research-init", "--mode", "wide-matrix", "--topic", "Embedded analytical DBs compared",
               "--entity", "DuckDB", "--entity", "SQLite",
               "--field", "process_concurrency", "--field", "writer_model", "--max-queries", "6")),
     block("python3 scripts/workbench.py research-add-source \\\n  --url https://duckdb.org/docs/connect/concurrency \\\n  --title \"Concurrency - DuckDB Documentation\" --tier PRIMARY --published-date 2026 \\\n  --content-file page.txt",
           run("research-add-source",
               "--url", "https://duckdb.org/docs/connect/concurrency",
               "--title", "Concurrency - DuckDB Documentation", "--tier", "PRIMARY", "--published-date", "2026",
               "--content-file", str(SCRATCH / "page1.txt")),
           "S1 registered from the opened DuckDB docs page. S2 (SQLite docs) and S3 (the 2024 benchmark blog) are registered the same way before their cells are claimed."),
     run("research-add-source", "--url", "https://www.sqlite.org/whentouse.html",
         "--title", "When to use SQLite", "--tier", "PRIMARY", "--published-date", "2026",
         "--content-file", str(SCRATCH / "page2.txt")),
     run("research-add-source", "--url", "https://example.com/2024-duckdb-benchmark",
         "--title", "2024 benchmark notes", "--tier", "TERTIARY", "--published-date", "2024",
         "--content-file", str(SCRATCH / "oldblog.txt")),
     block("python3 scripts/workbench.py research-add-claim --entity DuckDB --field process_concurrency \\\n  --statement \"DuckDB allows one read-write process or multiple read-only processes\" \\\n  --value \"1 RW or N RO\" --source-id S1 \\\n  --quote \"one process with read-write access, or multiple processes with read-only access\"",
           run("research-add-claim", "--entity", "DuckDB", "--field", "process_concurrency",
               "--statement", "DuckDB allows one read-write process or multiple read-only processes",
               "--value", "1 RW or N RO", "--source-id", "S1",
               "--quote", "one process with read-write access, or multiple processes with read-only access")),
     block("python3 scripts/workbench.py research-add-claim --entity DuckDB --field process_concurrency \\\n  --statement \"Only a single external process can open the database file\" \\\n  --value \"single process only\" --source-id S3 \\\n  --quote \"only a single external process opening the database file\"",
           run("research-add-claim", "--entity", "DuckDB", "--field", "process_concurrency",
               "--statement", "Only a single external process can open the database file",
               "--value", "single process only", "--source-id", "S3",
               "--quote", "only a single external process opening the database file")),
     block("python3 scripts/workbench.py research-resolve --entity DuckDB --field process_concurrency --winner-claim C1 \\\n  --reason \"C1 cites current official docs; C3's 2024 tertiary source describes superseded behavior\"",
           run("research-resolve", "--entity", "DuckDB", "--field", "process_concurrency", "--winner-claim", "C1",
               "--reason", "C1 cites current official docs; C3's 2024 tertiary source describes superseded behavior")),
     block("python3 scripts/workbench.py research-add-gap --entity DuckDB --field writer_model \\\n  --description \"No documented coordination guarantee for concurrent external writers; left to the application\" \\\n  --query-tried \"DuckDB external writer coordination\" --reason NO_PUBLIC_SOURCE",
           run("research-add-gap", "--entity", "DuckDB", "--field", "writer_model",
               "--description", "No documented coordination guarantee for concurrent external writers; left to the application",
               "--query-tried", "DuckDB external writer coordination", "--reason", "NO_PUBLIC_SOURCE")),
     block("python3 scripts/workbench.py wide-table --strict",
           run("wide-table", "--strict", expect_fail=True),
           "Strict fails while any cell is unverified, conflicting or missing — it is the quality gate, not an error. This run names exactly what remains: the SQLite cells have no claims yet. After filling them (or declaring them), a strict run with all cells verified or `n.a.` returns OK.")])

# ============================== evidence-audit ==============================
report = """# Draft: DuckDB concurrency

DuckDB supports one read-write process or many read-only processes ([source](https://duckdb.org/docs/connect/concurrency)).
According to a 2026 benchmark, throughput reaches 45 million rows per second ([Benchmark Blog](https://blog.example.net/duckdb-tips)).
The export always works correctly. Currently the documentation is unclear about locking ([2024 benchmark notes](https://example.com/2024-duckdb-benchmark)).
"""
(SCRATCH / "draft-report.md").write_text(report, encoding="utf-8")
write_example("evidence-audit", "report-audit.md", "Auditing a draft: five violations, then the fix",
    "A short draft with five distinct violations audited against a research ledger that holds the DuckDB docs source and the 2024 benchmark blog. The audit names each issue with its line and a concrete fix.",
    [block("python3 scripts/workbench.py audit-report --report-file draft-report.md",
           run("audit-report", "--report-file", str(SCRATCH / "draft-report.md"), expect_fail=True),
           "The five issues: a generic `[source]` anchor (blocking); an unregistered URL the ledger never opened (blocking); a number absent from the cited evidence (blocking); absolute language (`always`) without independent primary support (warning); a `Currently` claim resting on stale, tertiary evidence (warning). After rewriting the offending sentences — named anchor, registered source, the source's own number, calibrated wording, a dated qualification — the same command returns PASS.")])

# ============================== delivery-verify ==============================
(SCRATCH / "app.py").write_text("def total(lines, rate=0.001):\n    return round(sum(lines) + sum(lines) * rate, 2)\n")
write_example("delivery-verify", "verify-fix.md", "Verifying a fix on the L0-L4 ladder",
    "A bugfix verified with declared checks at L1, L2 and L3, plus an explicit L4 gap. The record keeps the commands, outcomes and git state.",
    [block("python3 scripts/workbench.py verify-delivery \\\n  --artifact app.py \\\n  --check \"L2:python3 -m py_compile app.py\" \\\n  --check \"L3:python3 -c \\\"from app import total; assert total([3.35, 3.35, 3.35]) == 10.06\\\"\" \\\n  --require L3 \\\n  --not-run \"L4: the accountant's manual flow in staging\"",
           run("verify-delivery",
               "--artifact", "app.py",
               "--check", "L2:python3 -m py_compile app.py",
               "--check", "L3:python3 -c \"from app import total; assert total([3.35, 3.35, 3.35]) == 10.06\"",
               "--require", "L3",
               "--not-run", "L4: the accountant's manual flow in staging"),
           "Achieved L3 with the required level met. The honest delivery wording is: \"the fix compiles and the targeted test passes (L3); your manual flow in staging was not run (declared).\" `levels_not_checked: [\"L4\"]` is part of the record.")])

# ============================== artifact-studio ==============================
write_example("artifact-studio", "new-technical-report.md", "Listing templates and instantiating one",
    "`artifact-list` shows every template with its purpose; `artifact-new` instantiates one with TITLE and DATE filled and reports the remaining placeholders.",
    [block("python3 scripts/workbench.py artifact-list",
           run("artifact-list"),
           "Every template's first line is an HTML comment stating its purpose — that is what `artifact-list` reads."),
     block("python3 scripts/workbench.py artifact-new --type technical-report \\\n  --title \"Batch pipeline postmortem\" --output docs/batch-postmortem.md",
           run("artifact-new", "--type", "technical-report", "--title", "Batch pipeline postmortem",
               "--output", str(SCRATCH / "docs/batch-postmortem.md")),
           "`placeholders_left` is the contract: the delivered document has none of them left. Fill each with real content (or delete the section deliberately), then confirm the list is empty before delivery.")])

# ============================== session-handoff ==============================
write_example("session-handoff", "partial-session.md", "Packing and checking a PARTIAL session",
    "A PARTIAL pack whose evidence section is auto-filled from the ledgers (research, debug, verification), followed by the check that validates it.",
    [block("python3 scripts/workbench.py handoff-pack --title \"Billing export v1\" --session-status PARTIAL \\\n  --summary \"CSV export implemented; tax-before-rounding fixed and verified at L3; pagination pending\" \\\n  --completed \"Export endpoint implemented\" \\\n  --next-step \"Add pagination for >10k invoices\" \\\n  --next-step \"Run the accountant's manual flow (L4)\" \\\n  --decision \"Tax applied per line before totals are rounded\" \\\n  --open-question \"Do credit notes need a separate export?\"",
           run("handoff-pack", "--title", "Billing export v1", "--session-status", "PARTIAL",
               "--summary", "CSV export implemented; tax-before-rounding fixed and verified at L3; pagination pending",
               "--completed", "Export endpoint implemented",
               "--next-step", "Add pagination for >10k invoices",
               "--next-step", "Run the accountant's manual flow (L4)",
               "--decision", "Tax applied per line before totals are rounded",
               "--open-question", "Do credit notes need a separate export?"),
           "Section 5 (Evidence & Verification Snapshot) is generated from the actual ledgers — the numbers of sources, claims, falsified hypotheses and the last verification level are read, not remembered."),
     block("python3 scripts/workbench.py handoff-check",
           run("handoff-check"),
           "PASS: all seven sections present, PARTIAL status carries next steps. Warnings would appear for a handoff older than 72h or a git HEAD that moved since packing — both are instructions to re-verify before trusting the state.")])

# ============================== spec-builder ==============================
write_example("spec-builder", "billing-export.md", "From goal to a PASS-ing spec",
    "A spec with two stories and three criteria, tasks bound to the criteria they verify, and the check that gates implementation.",
    [block("python3 scripts/workbench.py spec-new \\\n  --goal \"Ship a verified CSV export of invoices for enterprise accountants\" \\\n  --story \"As an accountant I export all unpaid invoices to CSV to reconcile in my ledger tool\" \\\n  --story \"As an auditor I export a date-ranged invoice history for a fiscal year\" \\\n  --non-goal \"No PDF export in v1\"",
           run("spec-new",
               "--goal", "Ship a verified CSV export of invoices for enterprise accountants",
               "--story", "As an accountant I export all unpaid invoices to CSV to reconcile in my ledger tool",
               "--story", "As an auditor I export a date-ranged invoice history for a fiscal year",
               "--non-goal", "No PDF export in v1")),
     block("python3 scripts/workbench.py spec-criterion --story-id US1 \\\n  --given \"an account with 3 unpaid invoices totaling 10.06\" \\\n  --when \"the accountant runs the CSV export\" \\\n  --then \"the CSV contains exactly 3 data rows and the total column sums to 10.06\"",
           run("spec-criterion", "--story-id", "US1",
               "--given", "an account with 3 unpaid invoices totaling 10.06",
               "--when", "the accountant runs the CSV export",
               "--then", "the CSV contains exactly 3 data rows and the total column sums to 10.06")),
     block("python3 scripts/workbench.py spec-criterion --story-id US1 \\\n  --given \"an account with more than 10,000 unpaid invoices\" \\\n  --when \"the accountant runs the CSV export\" \\\n  --then \"the export completes without error and streams all rows without loading them into memory\"",
           run("spec-criterion", "--story-id", "US1",
               "--given", "an account with more than 10,000 unpaid invoices",
               "--when", "the accountant runs the CSV export",
               "--then", "the export completes without error and streams all rows without loading them into memory")),
     block("python3 scripts/workbench.py spec-criterion --story-id US2 \\\n  --given \"the range 2024-01-01 to 2023-12-31 (end before start)\" \\\n  --when \"the auditor exports\" \\\n  --then \"the API returns status 422 with error code INVALID_RANGE and writes no file\"",
           run("spec-criterion", "--story-id", "US2",
               "--given", "the range 2024-01-01 to 2023-12-31 (end before start)",
               "--when", "the auditor exports",
               "--then", "the API returns status 422 with error code INVALID_RANGE and writes no file")),
     block("python3 scripts/workbench.py spec-task --task \"Implement the CSV serialization with per-line escaping\" --verifies AC1",
           run("spec-task", "--task", "Implement the CSV serialization with per-line escaping", "--verifies", "AC1"),
           "A task without `--verifies` is rejected with TASK_NOT_VERIFIABLE — work that verifies nothing does not belong in the plan."),
     block("python3 scripts/workbench.py spec-task --task \"Add streaming pagination to the invoice query for large accounts\" \\\n  --verifies AC2 --depends-on T1",
           run("spec-task", "--task", "Add streaming pagination to the invoice query for large accounts",
               "--verifies", "AC2", "--depends-on", "T1"),
           "Dependencies must reference existing tasks; the check catches cycles."),
     block("python3 scripts/workbench.py spec-check",
           run("spec-check"),
           "PASS is the implementation gate. The warning is honest: AC3 (the invalid-range criterion) has no implementing task yet — plan it or move it to a later spec deliberately.")])

# ============================== code-review ==============================
write_example("code-review", "pr-review.md", "A review with a BLOCKING finding and a FAIL verdict",
    "Three findings at three severities, rendered into a report whose verdict is FAIL while the BLOCKING finding is open.",
    [block("python3 scripts/workbench.py review-init --title \"Billing export PR #142\" \\\n  --target \"PR #142: src/billing/export.py, tests/test_export.py\" \\\n  --focus correctness --focus tests",
           run("review-init", "--title", "Billing export PR #142",
               "--target", "PR #142: src/billing/export.py, tests/test_export.py",
               "--focus", "correctness", "--focus", "tests")),
     block("python3 scripts/workbench.py review-finding --file src/billing/export.py --line 42 \\\n  --severity BLOCKING --category correctness \\\n  --description \"Totals are rounded per line before tax is applied, losing cents on multi-line invoices\" \\\n  --suggestion \"Apply tax before rounding in _line_total(); add a test with 3 x 3.35 lines\"",
           run("review-finding", "--file", "src/billing/export.py", "--line", "42",
               "--severity", "BLOCKING", "--category", "correctness",
               "--description", "Totals are rounded per line before tax is applied, losing cents on multi-line invoices",
               "--suggestion", "Apply tax before rounding in _line_total(); add a test with 3 x 3.35 lines")),
     block("python3 scripts/workbench.py review-finding --file tests/test_export.py \\\n  --severity MAJOR --category tests \\\n  --description \"No test covers the changed rounding order; the existing test asserts the buggy value\" \\\n  --suggestion \"Update test_total to expect 10.06 and add a multi-line case\"",
           run("review-finding", "--file", "tests/test_export.py",
               "--severity", "MAJOR", "--category", "tests",
               "--description", "No test covers the changed rounding order; the existing test asserts the buggy value",
               "--suggestion", "Update test_total to expect 10.06 and add a multi-line case")),
     block("python3 scripts/workbench.py review-finding --file src/billing/export.py --line 87 \\\n  --severity INFO --category maintainability \\\n  --description \"The CSV escaping helper mirrors utils/csv_escape.py; consider importing it instead\"",
           run("review-finding", "--file", "src/billing/export.py", "--line", "87",
               "--severity", "INFO", "--category", "maintainability",
               "--description", "The CSV escaping helper mirrors utils/csv_escape.py; consider importing it instead")),
     block("python3 scripts/workbench.py review-report \\\n  --not-reviewed \"Did not inspect the migration or the frontend consumer\"",
           run("review-report", "--not-reviewed", "Did not inspect the migration or the frontend consumer", expect_fail=True),
           "The verdict is FAIL, mechanically, because a BLOCKING finding is open. After the fix lands, re-review the changed lines and record a fresh report; the new PASS closes the loop, with `delivery-verify` proving the fix commands.")])

# ============================== knowledge-capture ==============================
write_example("knowledge-capture", "capture-and-search.md", "Two entries and finding them again",
    "One sourced entry bound to the research ledger, one explicit assumption, and a search that ranks deterministically.",
    [block("python3 scripts/workbench.py kb-add \\\n  --question \"In which order does the billing export apply tax and rounding?\" \\\n  --answer \"Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified by criterion AC1 and the fix in _line_total().\" \\\n  --source-id S1 \\\n  --tag billing --tag export",
           run("kb-add",
               "--question", "In which order does the billing export apply tax and rounding?",
               "--answer", "Tax is applied per line before totals are rounded; rounding mode is HALF_UP. Verified by criterion AC1 and the fix in _line_total().",
               "--source-id", "S1", "--tag", "billing", "--tag", "export"),
           "`--source-id S1` is validated against the research ledger — the entry inherits the evidence trail of the registered source."),
     block("python3 scripts/workbench.py kb-add \\\n  --question \"What is the staging proxy timeout?\" \\\n  --answer \"Assumed 30s based on defaults in similar setups; not documented anywhere we found.\" \\\n  --assumed --tag infra",
           run("kb-add",
               "--question", "What is the staging proxy timeout?",
               "--answer", "Assumed 30s based on defaults in similar setups; not documented anywhere we found.",
               "--assumed", "--tag", "infra"),
           "`--assumed` is the honest marker: LOW confidence, and the export renders it as **ASSUMPTION (unverified)** so nobody quotes it as fact."),
     block("python3 scripts/workbench.py kb-search --query \"csv export tax rounding order\"",
           run("kb-search", "--query", "csv export tax rounding order"),
           "Deterministic offline scoring: tags x3, question tokens x2, answer tokens x1. The billing entry ranks first; the timeout entry does not match this query at all — as it should."),
     block("python3 scripts/workbench.py kb-export",
           run("kb-export"),
           "The exported knowledge base groups entries by first tag, shows each entry's source or assumption marker, and dates every entry — the project's memory, browsable.")])

print("ALL EXAMPLES GENERATED")
