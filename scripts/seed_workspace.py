#!/usr/bin/env python3
"""Seed (or reset) the demo workspace for the Local Advisor Suite web console.

Creates .workspace/ with:
  - a demo project (scope-read / scope-scan target)
  - a full 6-host install via install.py
  - populated research / spec / review / knowledge / debug / advisory ledgers
  - an ADR, an artifact and a handoff pack

Usage: python3 scripts/seed_workspace.py [app_root]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

APP = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SUITE = APP / "suite"
WS = APP / ".workspace"
STATE = WS / ".local-workbench"

DEMO_README = """# Demo Project

A tiny sample repository used as the target for `scope-read`, `scope-scan`,
`review-init` and `verify-delivery` demos in the Local Advisor Suite console.

- `src/app.py` — intentionally imperfect input parsing (review demo)
- `src/utils.py` — helpers without a docstring (MINOR style finding)
- `docs/notes.md` — plain notes for scope-scan pattern matches
"""

DEMO_APP = '''"""Demo application entry point."""


def parse_int(raw):
    """Parse user input into an int."""
    try:
        return int(raw)
    except ValueError:
        return 0  # BUG: silently hides bad input


def run(argv):
    limit = parse_int(argv[1]) if len(argv) > 1 else 10
    return [i * i for i in range(limit)]


if __name__ == "__main__":
    print(run(sys.argv))
'''

DEMO_UTILS = '''def slugify(text):
    """Return a lowercase slug."""
    return "-".join(text.lower().split())


def truncate(text, width=80):
    return text[:width]
'''

DEMO_NOTES = """# Notes

- The workbench stores ledgers under .local-workbench/
- doctor checks installation health across hosts
- kb-search performs deterministic offline keyword search
"""

DECISION_MATRIX = {
    "title": "Console execution model",
    "criteria": [
        {"id": "inspectability", "weight": 3, "min_score": 5},
        {"id": "effort", "weight": 2},
        {"id": "reversibility", "weight": 1},
    ],
    "options": [
        {
            "name": "shared workspace",
            "scores": {"inspectability": 9, "effort": 8, "reversibility": 7},
            "risks": ["concurrent runs share ledger state"],
        },
        {
            "name": "isolated sandbox per run",
            "scores": {"inspectability": 6, "effort": 4, "reversibility": 9},
            "risks": ["state feels empty on every run"],
        },
        {
            "name": "ephemeral containers",
            "scores": {"inspectability": 4, "effort": 2, "reversibility": 9},
            "risks": ["slow cold starts", "needs container runtime"],
        },
    ],
}


def wb(*args):
    """Run a workbench command inside the workspace; return parsed JSON."""
    proc = subprocess.run(
        [sys.executable, str(SUITE / "workbench.py"), "--state-dir", str(STATE), *args],
        cwd=str(WS), capture_output=True, text=True, timeout=60,
    )
    try:
        out = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        out = {"status": "PARSE_ERROR", "stdout": proc.stdout[:400]}
    out["_exit"] = proc.returncode
    return out


def seed():
    results = {"steps": [], "failures": []}

    def step(name, fn):
        try:
            payload = fn()
            status = payload.get("status") if isinstance(payload, dict) else None
            ok = status in (None, "OK", "PASS")
            results["steps"].append({"name": name, "ok": ok, "status": status})
            if not ok:
                results["failures"].append(
                    {"name": name, "error": payload.get("error_code") or status or "unknown"}
                )
            return payload
        except Exception as exc:  # noqa: BLE001
            results["failures"].append({"name": name, "error": str(exc)})
            results["steps"].append({"name": name, "ok": False, "status": "EXCEPTION"})
            return {}

    if WS.exists():
        shutil.rmtree(WS)
    (STATE).mkdir(parents=True, exist_ok=True)

    demo = WS / "demo-project"
    (demo / "src").mkdir(parents=True)
    (demo / "docs").mkdir(parents=True)
    (demo / "README.md").write_text(DEMO_README, encoding="utf-8")
    (demo / "src" / "app.py").write_text(DEMO_APP, encoding="utf-8")
    (demo / "src" / "utils.py").write_text(DEMO_UTILS, encoding="utf-8")
    (demo / "docs" / "notes.md").write_text(DEMO_NOTES, encoding="utf-8")
    (WS / "decision-matrix.json").write_text(
        json.dumps(DECISION_MATRIX, indent=2), encoding="utf-8"
    )
    results["steps"].append({"name": "demo-project files", "ok": True})

    def do_install():
        proc = subprocess.run(
            [sys.executable, str(SUITE / "install.py"), "--project", str(WS),
             "--hosts", "claude,codex,zcode,cursor,opencode,generic", "--gitignore"],
            cwd=str(APP), capture_output=True, text=True, timeout=300,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr[-400:] or "install.py failed")

    step("install 6 hosts", do_install)

    # ---- research ledger -------------------------------------------------
    init = step("research-init", lambda: wb(
        "research-init",
        "--topic", "Cross-host portability of agent skill suites",
        "--sub-question", "Which directory layout does each host expect?",
        "--sub-question", "Which frontmatter limits apply per host?",
        "--sub-question", "How do commands map to host UIs?",
        "--entity", "Claude Code", "--entity", "Codex", "--entity", "ZCode",
        "--entity", "Cursor",
        "--field", "skills directory", "--field", "frontmatter limit",
        "--field", "command surface",
    )) or {}

    step("research-log-query #1", lambda: wb(
        "research-log-query", "--query",
        "agent skills specification frontmatter limits"))
    step("research-log-query #2", lambda: wb(
        "research-log-query", "--query",
        "cursor rules mdc directory layout"))

    def add_sources():
        s1 = wb("research-add-source", "--url", "https://agentskills.io/specification",
                "--title", "Agent Skills Specification", "--publisher", "agentskills.io",
                "--tier", "PRIMARY",
                "--excerpt", "A skill is a folder with a SKILL.md file; name and description are required.")
        s2 = wb("research-add-source", "--url", "https://cursor.com/docs/rules",
                "--title", "Cursor Rules documentation", "--publisher", "Cursor",
                "--tier", "PRIMARY",
                "--excerpt", "Project rules live in .cursor/rules as .mdc files.")
        return {"s1": s1.get("source_id"), "s2": s2.get("source_id")}

    src = step("research-add-source x2", add_sources) or {}
    sid1 = src.get("s1") or "S1"
    sid2 = src.get("s2") or "S2"

    step("research-add-claim #1", lambda: wb(
        "research-add-claim",
        "--statement", "An Agent Skill is a folder with a SKILL.md that requires name and description",
        "--source-id", sid1,
        "--quote", "A skill is a folder with a SKILL.md file; name and description are required",
        "--entity", "Agent Skills standard", "--field", "skills directory",
        "--value", "SKILL.md folder", "--confidence", "HIGH"))
    step("research-add-claim #2 (unverified)", lambda: wb(
        "research-add-claim",
        "--statement", "Claude Code discovers skills in .claude/skills at project scope",
        "--source-id", sid1,
        "--quote", "place them in ~/.claude/skills/ (personal) or .claude/skills/ (project)",
        "--entity", "Claude Code", "--field", "skills directory",
        "--value", ".claude/skills", "--allow-unverified-quote"))
    step("research-add-claim #3", lambda: wb(
        "research-add-claim",
        "--statement", "Cursor project rules live in .cursor/rules as .mdc files",
        "--source-id", sid2,
        "--quote", "Project rules live in .cursor/rules as .mdc files",
        "--entity", "Cursor", "--field", "command surface",
        "--value", ".cursor/rules/*.mdc"))
    step("research-add-gap", lambda: wb(
        "research-add-gap",
        "--description", "No public source confirms ZCode frontmatter truncation behavior",
        "--entity", "ZCode", "--field", "frontmatter limit",
        "--query-tried", "zcode skills frontmatter limit",
        "--reason", "NO_PUBLIC_SOURCE"))

    # ---- spec ledger -----------------------------------------------------
    spec = step("spec-new", lambda: wb(
        "spec-new",
        "--goal", "Ship a cross-host agent suite that installs cleanly into six hosts",
        "--story", "As a developer I want one install command per project so all my agents share the same skills",
        "--story", "As a reviewer I want a mechanical gate so unfinished work cannot be reported as done",
        "--non-goal", "Supporting hosts beyond the six documented ones")) or {}
    story_ids = [s for s in (spec.get("stories") or []) if isinstance(s, str)]
    s1 = story_ids[0] if story_ids else "US1"
    s2 = story_ids[1] if len(story_ids) > 1 else s1

    crit1 = step("spec-criterion #1", lambda: wb(
        "spec-criterion", "--story-id", s1,
        "--given", "a clean project directory",
        "--when", "install.py --project . runs",
        "--then", "all six host markers exist and doctor reports OK")) or {}
    crit2 = step("spec-criterion #2", lambda: wb(
        "spec-criterion", "--story-id", s2,
        "--given", "a review ledger with an open BLOCKING finding",
        "--when", "review-report runs",
        "--then", "the verdict is FAIL")) or {}

    def find_crit_id(payload, fallback):
        crit = payload.get("criterion") or {}
        return crit.get("id") or payload.get("criterion_id") or fallback

    c1 = find_crit_id(crit1, "AC1")
    c2 = find_crit_id(crit2, "AC2")

    task1 = step("spec-task #1", lambda: wb(
        "spec-task", "--task", "Write install smoke test for all hosts",
        "--verifies", c1)) or {}
    t1 = (task1.get("task") or {}).get("id") or task1.get("task_id") or "T1"
    step("spec-task #2", lambda: wb(
        "spec-task", "--task", "Add BLOCKING gate to review-report",
        "--verifies", c2, "--depends-on", t1))

    # ---- review ledger ---------------------------------------------------
    step("review-init", lambda: wb(
        "review-init", "--title", "Console demo review",
        "--target", "demo-project/src/app.py",
        "--focus", "correctness", "--focus", "security"))
    step("review-finding #1", lambda: wb(
        "review-finding", "--file", "demo-project/src/app.py", "--line", "12",
        "--severity", "MAJOR", "--category", "correctness",
        "--description", "parse_int() swallows ValueError and returns 0, hiding bad input",
        "--suggestion", "Let the exception propagate or return None explicitly"))
    step("review-finding #2", lambda: wb(
        "review-finding", "--file", "demo-project/src/utils.py",
        "--severity", "MINOR", "--category", "style",
        "--description", "Module has no docstring"))

    # ---- knowledge base --------------------------------------------------
    step("kb-add #1", lambda: wb(
        "kb-add",
        "--question", "Where does Claude Code look for project skills?",
        "--answer", "Claude Code loads skills from .claude/skills/ at project scope and ~/.claude/skills/ at personal scope, per the Agent Skills standard.",
        "--source-url", "https://agentskills.io/specification",
        "--tag", "claude", "--tag", "skills"))
    step("kb-add #2", lambda: wb(
        "kb-add",
        "--question", "What is the safest default state directory?",
        "--answer", "The workbench stores ledgers under .local-workbench/ in the project root; install.py --gitignore adds it to .gitignore.",
        "--tag", "workbench", "--assumed"))
    step("kb-add #3", lambda: wb(
        "kb-add",
        "--question", "How are Cursor commands exposed?",
        "--answer", "install.py generates .cursor/commands/*.md files plus rules so slash commands map to workbench invocations.",
        "--source-id", sid2, "--tag", "cursor"))

    # ---- data analysis ---------------------------------------------------
    step("data-register", lambda: wb(
        "data-register",
        "--path", "demo-project/README.md",
        "--question", "How many lines and words does the demo README have?"))
    step("data-finding #1", lambda: wb(
        "data-finding",
        "--statement", "The demo README has 8 lines",
        "--method", "wc -l demo-project/README.md",
        "--result", "8 lines"))
    step("data-finding #2", lambda: wb(
        "data-finding",
        "--statement", "The demo README has 52 words",
        "--method", "wc -w demo-project/README.md",
        "--result", "52 words"))
    step("data-gap", lambda: wb(
        "data-gap",
        "--description", "A per-section word split is not computable from the README",
        "--reason", "AMBIGUOUS_DEFINITION: section boundaries are not machine-marked"))

    # ---- devil's advocate -------------------------------------------------
    step("devil-open", lambda: wb(
        "devil-open",
        "--claim", "Replace the demo console's shared workspace with an isolated sandbox per run",
        "--steelman", "Isolated runs cannot contaminate each other's ledger state, "
                      "so every scenario is reproducible from a clean start"))
    step("devil-challenge #1", lambda: wb(
        "devil-challenge",
        "--assumption", "an empty ledger on every run is acceptable",
        "--attack", "Ledger history is what makes the console instructive; a fresh sandbox "
                    "shows empty state on every click, so users never see a filled ledger",
        "--category", "second-order-effect", "--severity", "SERIOUS",
        "--defeater", "a side-by-side view that shows the seeded ledgers next to the fresh run"))
    step("devil-challenge #2 (FATAL)", lambda: wb(
        "devil-challenge",
        "--assumption", "isolated sandboxes cost nothing extra",
        "--attack", "Cold-starting a sandbox per command adds seconds to every click and an "
                    "ops dependency the console does not have today",
        "--category", "cost-complexity", "--severity", "FATAL",
        "--defeater", "a warm pool that serves any command in under 500ms"))
    step("devil-rebuttal", lambda: wb(
        "devil-rebuttal", "--id", "C2",
        "--rebuttal", "The console runs commands against local directories, not containers; "
                      "isolation is a folder wipe that costs milliseconds",
        "--basis", "constraint: commands run in-process against --state-dir"))

    # ---- advisory, decision, debug, adr, artifact, handoff ---------------
    step("advise-intake", lambda: wb(
        "advise-intake",
        "--question", "Should the console run commands against a shared workspace or isolated sandboxes?",
        "--context", "Web test console for the suite",
        "--constraint", "Keep ledger state inspectable",
        "--non-goal", "Multi-user authentication",
        "--mode", "architecture"))
    step("decision-score", lambda: wb(
        "decision-score", "--spec-file", "decision-matrix.json"))
    step("debug-hypothesis", lambda: wb(
        "debug-hypothesis",
        "--symptom", "doctor reports 0 hosts after install",
        "--statement", "Manifest is written but doctor reads a different project root",
        "--prediction", "doctor --project-root . detects the hosts",
        "--test-command", "python3 workbench.py doctor --project-root .",
        "--status", "PENDING", "--target-file", "install.py"))
    step("adr-new", lambda: wb(
        "adr-new", "--title", "Use a single shared demo workspace for the test console",
        "--decision-result", "APPROVED", "--dir", "docs/adr", "--owner", "console-team"))
    step("artifact-new", lambda: wb(
        "artifact-new", "--type", "technical-report",
        "--title", "Console demo report", "--output", "artifacts/demo-report.md"))
    step("handoff-pack", lambda: wb(
        "handoff-pack", "--title", "Console demo session", "--session-status", "DONE",
        "--summary", "Seeded demo workspace with research, spec, review and knowledge ledgers",
        "--completed", "research ledger initialized with 2 sources and 3 claims",
        "--completed", "spec with 2 criteria and 2 tasks",
        "--next-step", "Run review-report and wide-table from the console"))

    results["ok"] = not results["failures"]
    print(json.dumps(results, indent=1))
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    sys.exit(seed())
