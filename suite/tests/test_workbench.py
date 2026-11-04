"""Tests for workbench.py: every command family, error paths, and v2.1 contract compatibility."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import workbench  # noqa: E402


def run_wb(state_dir, *args, project_cwd=None):
    """Run the CLI in-process; return (parsed_json_or_none, exit_code)."""
    argv = ["--state-dir", str(state_dir), *args]
    old_cwd = os.getcwd()
    if project_cwd:
        os.chdir(project_cwd)
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "workbench.py"), *argv],
            capture_output=True, text=True, timeout=60,
        )
    finally:
        os.chdir(old_cwd)
    out = proc.stdout if proc.stdout.strip() else proc.stderr
    try:
        return json.loads(out), proc.returncode
    except json.JSONDecodeError:
        return None, proc.returncode


class WorkbenchTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "st"
        self.state.mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def ok(self, *args, **kw):
        data, code = run_wb(self.state, *args, **kw)
        self.assertEqual(code, 0, f"expected OK for {args}: {data}")
        return data

    def nonzero(self, *args, **kw):
        data, code = run_wb(self.state, *args, **kw)
        self.assertNotEqual(code, 0, f"expected failure for {args}: {data}")
        return data

    def err(self, *args, **kw):
        data, code = run_wb(self.state, *args, **kw)
        self.assertEqual(code, 1, f"expected structured error for {args}: {data}")
        return data


class TestVersionAndContract(WorkbenchTestCase):
    def test_version_is_3_2_0(self):
        self.assertEqual(workbench.VERSION, "3.2.0")

    def test_v21_subcommands_still_exist(self):
        """Every v2.1 subcommand must keep working with the same name (backward compatibility)."""
        v21_commands = {
            "advise-intake", "decision-score", "scope-read", "scope-scan", "debug-hypothesis",
            "research-init", "research-log-query", "research-add-source", "research-add-claim",
            "research-add-gap", "research-status", "fetch-url", "audit-report",
            "verify-delivery", "handoff-pack", "research-score", "research-gaps",
            "research-resolve", "research-pack", "wide-table", "adr-new", "adr-check",
            "debug-report", "handoff-check", "artifact-list", "artifact-new", "selfcheck",
        }
        sub = self._subparser_choices()
        missing = v21_commands - set(sub.keys())
        self.assertFalse(missing, f"v2.1 commands missing: {missing}")

    def test_v30_additions_exist(self):
        sub = self._subparser_choices()
        for cmd in ("doctor", "spec-new", "spec-criterion", "spec-task", "spec-check",
                    "review-init", "review-finding", "review-report",
                    "kb-add", "kb-search", "kb-export"):
            self.assertIn(cmd, sub, f"missing v3.0 command {cmd}")

    @staticmethod
    def _subparser_choices():
        parser = workbench.build_parser()
        sub_actions = [a for a in parser._actions if hasattr(a, "choices") and isinstance(a.choices, dict)]
        assert sub_actions, "no subparsers found"
        return sub_actions[0].choices


class TestAdviseIntake(WorkbenchTestCase):
    def test_records_intake(self):
        data = self.ok("advise-intake", "--question", "Should we split the service?",
                       "--constraint", "no budget", "--non-goal", "no rewrite", "--mode", "architecture")
        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["intake"]["constraints"], ["no budget"])
        self.assertTrue((self.state / "advisory_intake.json").exists())

    def test_empty_question_rejected(self):
        self.err("advise-intake", "--question", "   ")


class TestDecisionScore(WorkbenchTestCase):
    def spec(self):
        p = Path(self.tmp.name) / "decision.json"
        p.write_text(json.dumps({
            "criteria": [{"id": "ops", "weight": 3, "min_score": 4}, {"id": "speed", "weight": 1}],
            "options": [
                {"name": "A", "scores": {"ops": 7, "speed": 5}},
                {"name": "B", "scores": {"ops": 3, "speed": 9}},  # disqualified by min_score
            ],
        }), encoding="utf-8")
        return p

    def test_scoring_and_disqualification(self):
        out = Path(self.tmp.name) / "res.json"
        data = self.ok("decision-score", "--spec-file", str(self.spec()), "--output", str(out))
        self.assertEqual(data["recommended_option"], "A")
        ranked = {o["name"]: o for o in data["ranked_options"]}
        self.assertTrue(ranked["B"]["disqualified"])
        self.assertIn("sensitivity", data)
        self.assertTrue(out.exists())

    def test_unknown_scores_flagged_in_sensitivity(self):
        p = Path(self.tmp.name) / "d2.json"
        p.write_text(json.dumps({
            "criteria": [{"id": "x", "weight": 1}],
            "options": [{"name": "A", "scores": {"x": 7}}, {"name": "B", "scores": {}}],
        }), encoding="utf-8")
        data = self.ok("decision-score", "--spec-file", str(p))
        self.assertTrue(any("unknown" in w.lower() for w in data["sensitivity"]["warnings"]))

    def test_invalid_spec_rejected(self):
        p = Path(self.tmp.name) / "bad.json"
        p.write_text("{}", encoding="utf-8")
        self.err("decision-score", "--spec-file", str(p))


class TestScope(WorkbenchTestCase):
    def setUp(self):
        super().setUp()
        self.proj = Path(self.tmp.name) / "proj"
        (self.proj / "pkg").mkdir(parents=True)
        (self.proj / "pkg" / "code.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
        (self.proj / ".env").write_text("SECRET=1\n", encoding="utf-8")

    def test_scope_read_numbered_lines(self):
        data = self.ok("scope-read", "--project-root", str(self.proj), "--file", "pkg/code.py")
        self.assertIn("1: x = 1", data["content"])
        self.assertEqual(data["total_lines"], 2)

    def test_scope_violation_blocked(self):
        self.err("scope-read", "--project-root", str(self.proj), "--file", "../outside.txt")

    def test_secret_file_blocked(self):
        self.err("scope-read", "--project-root", str(self.proj), "--file", ".env")

    def test_scope_scan_cap(self):
        for i in range(5):
            (self.proj / "pkg" / f"f{i}.py").write_text("pass\n", encoding="utf-8")
        data = self.ok("scope-scan", "--project-root", str(self.proj), "--subpath", "pkg",
                       "--pattern", "x = 1", "--max-files", "3")
        self.assertLessEqual(data["scanned_files"], 3)


class TestDebug(WorkbenchTestCase):
    def test_case_then_two_strikes(self):
        self.ok("debug-hypothesis", "--symptom", "total mismatch",
                "--target-file", "a.py", "--repro", "pytest -q")
        self.ok("debug-hypothesis", "--id", "H1", "--status", "PENDING",
                "--statement", "rounding order wrong", "--prediction", "value is 10.05",
                "--test-command", "true")
        self.ok("debug-hypothesis", "--id", "H1", "--status", "FALSIFIED", "--evidence", "no")
        data = self.ok("debug-hypothesis", "--id", "H2", "--status", "PENDING",
                       "--statement", "tax applied late", "--prediction", "value differs",
                       "--test-command", "true")
        self.assertFalse(data["circuit_breaker_tripped"])
        self.ok("debug-hypothesis", "--id", "H2", "--status", "FALSIFIED", "--evidence", "no")
        err = self.err("debug-hypothesis", "--id", "H3", "--status", "PENDING",
                       "--statement", "third guess", "--prediction", "x", "--test-command", "true")
        self.assertEqual(err["error_code"], "CIRCUIT_BREAKER_TRIPPED")

    def test_debug_report_renders(self):
        self.ok("debug-hypothesis", "--symptom", "s", "--target-file", "a.py")
        self.ok("debug-hypothesis", "--id", "H1", "--status", "CONFIRMED",
                "--statement", "root cause", "--prediction", "p", "--test-command", "c",
                "--evidence", "e")
        data = self.ok("debug-report", "--fix", "the fix")
        self.assertTrue(data["root_cause_confirmed"])
        self.assertTrue(Path(data["report"]).exists())

    def test_new_hypothesis_requires_statement(self):
        self.ok("debug-hypothesis", "--symptom", "s", "--target-file", "a.py")
        err = self.err("debug-hypothesis", "--id", "H9", "--status", "PENDING")
        self.assertEqual(err["error_code"], "STATEMENT_REQUIRED")


class TestResearchLedger(WorkbenchTestCase):
    def register_source(self, sid="S1", text="Alpha supports one read-write process or many read-only processes."):
        page = Path(self.tmp.name) / f"{sid}.txt"
        page.write_text(text, encoding="utf-8")
        return self.ok("research-add-source", "--source-id", sid,
                       "--url", f"https://example.com/{sid}",
                       "--title", f"Doc {sid}", "--tier", "PRIMARY",
                       "--published-date", "2026", "--content-file", str(page))

    def test_init_and_budget(self):
        self.ok("research-init", "--topic", "T", "--sub-question", "Q one", "--max-queries", "2")
        self.ok("research-log-query", "--query", "first query")
        self.ok("research-log-query", "--query", "second query")
        err = self.err("research-log-query", "--query", "third query")
        self.assertEqual(err["error_code"], "QUERY_BUDGET_EXHAUSTED")

    def test_duplicate_query_rejected(self):
        self.ok("research-init", "--topic", "T", "--max-queries", "5")
        self.ok("research-log-query", "--query", "same query")
        err = self.err("research-log-query", "--query", "same   query")
        self.assertEqual(err["error_code"], "DUPLICATE_QUERY")

    def test_source_requires_content(self):
        self.err("research-add-source", "--url", "https://x.com", "--title", "t")

    def test_claim_quote_verification(self):
        self.ok("research-init", "--topic", "T", "--sub-question", "sq")
        self.register_source()
        data = self.ok("research-add-claim", "--sub-question-id", "Q1",
                       "--statement", "Alpha has 1 RW process",
                       "--source-id", "S1",
                       "--quote", "one read-write process or many read-only processes")
        self.assertTrue(data["quote_verified_in_excerpt"])
        err = self.err("research-add-claim", "--sub-question-id", "Q1",
                       "--statement", "Fabricated", "--source-id", "S1",
                       "--quote", "this sentence is not in the page at all")
        self.assertEqual(err["error_code"], "QUOTE_NOT_IN_SOURCE")
        forced = self.ok("research-add-claim", "--sub-question-id", "Q1",
                         "--statement", "Provisional claim", "--source-id", "S1",
                         "--quote", "not in the page either", "--allow-unverified-quote")
        self.assertEqual(forced["claim"]["confidence"], "LOW")
        self.assertEqual(forced["claim"]["status"], "PROVISIONAL")

    def test_unknown_source_rejected(self):
        self.ok("research-init", "--topic", "T")
        err = self.err("research-add-claim", "--statement", "s", "--source-id", "S99",
                       "--quote", "0123456789")
        self.assertEqual(err["error_code"], "UNKNOWN_SOURCE_ID")

    def test_contradiction_detection_and_resolution(self):
        self.ok("research-init", "--topic", "T", "--sub-question", "sq")
        self.register_source("S1", "Alpha value is 1000 USD per month for the pro plan.")
        self.register_source("S2", "Alpha value is 1,000 usd monthly, per the 2026 price list.")
        self.register_source("S3", "Alpha value is 2000 USD per month.")
        self.ok("research-add-claim", "--entity", "Alpha", "--field", "price",
                "--statement", "1000", "--value", "1000 USD", "--source-id", "S1",
                "--quote", "value is 1000 USD per month")
        self.ok("research-add-claim", "--entity", "Alpha", "--field", "price",
                "--statement", "1000 (formatted)", "--value", "1,000 usd", "--source-id", "S2",
                "--quote", "value is 1,000 usd monthly")
        data = self.ok("research-status")
        # Normalized equal values are NOT a contradiction...
        self.assertEqual(len(data["contradictions"]), 0)
        self.ok("research-add-claim", "--entity", "Alpha", "--field", "price",
                "--statement", "2000", "--value", "2000 USD", "--source-id", "S3",
                "--quote", "value is 2000 USD per month")
        data = self.ok("research-status")
        self.assertEqual(len(data["contradictions"]), 1)
        resolved = self.ok("research-resolve", "--entity", "Alpha", "--field", "price",
                           "--winner-claim", "C1",
                           "--reason", "S1 is the current official price list")
        self.assertEqual(resolved["superseded_claims"], ["C3"])
        data = self.ok("research-status")
        self.assertEqual(len(data["contradictions"]), 0)

    def test_gaps_and_coverage(self):
        self.ok("research-init", "--topic", "T", "--sub-question", "unanswered question")
        self.ok("research-add-gap", "--sub-question-id", "Q1",
                "--description", "nothing found", "--query-tried", "q1", "--reason", "NO_PUBLIC_SOURCE")
        data = self.ok("research-gaps")
        self.assertEqual(data["coverage"][0]["coverage"], "GAP_RECORDED")

    def test_research_pack_writes_markdown(self):
        self.ok("research-init", "--topic", "Pack topic", "--sub-question", "sq")
        self.register_source()
        self.ok("research-add-claim", "--sub-question-id", "Q1", "--statement", "s",
                "--source-id", "S1", "--quote", "one read-write process or many read-only processes")
        data = self.ok("research-pack")
        text = Path(data["evidence_pack"]).read_text(encoding="utf-8")
        self.assertIn("Pack topic", text)
        self.assertIn("one read-write process", text)


class TestFetchUrl(WorkbenchTestCase):
    def test_network_requires_flag(self):
        err = self.err("fetch-url", "--url", "https://example.com")
        self.assertEqual(err["error_code"], "NETWORK_NOT_APPROVED")

    def test_https_only(self):
        err = self.err("fetch-url", "--url", "http://example.com", "--allow-network")
        self.assertEqual(err["error_code"], "HTTPS_REQUIRED")


class TestAudit(WorkbenchTestCase):
    def setUp(self):
        super().setUp()
        self.ok("research-init", "--topic", "T", "--sub-question", "sq")
        page = Path(self.tmp.name) / "p.txt"
        page.write_text("The measured latency is 42 ms under load.", encoding="utf-8")
        self.ok("research-add-source", "--source-id", "S1", "--url", "https://a.example/docs",
                "--title", "Docs", "--tier", "PRIMARY", "--published-date", "2026",
                "--content-file", str(page))

    def report(self, text):
        p = Path(self.tmp.name) / "report.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_unregistered_url_and_generic_anchor_flagged(self):
        p = self.report("Latency is 42 ms ([source](https://a.example/docs)) and see [this](https://never-opened.example/x).")
        data = self.nonzero("audit-report", "--report-file", str(p))
        types = {i["type"] for i in data["issues"]}
        self.assertIn("GENERIC_OR_RAW_ANCHOR", types)
        self.assertIn("UNREGISTERED_REPORT_URL", types)

    def test_unsupported_number_flagged(self):
        p = self.report("Latency is 99 ms ([Docs](https://a.example/docs)).")
        data = self.nonzero("audit-report", "--report-file", str(p))
        types = {i["type"] for i in data["issues"]}
        self.assertIn("UNSUPPORTED_NUMBER", types)

    def test_clean_passage_passes(self):
        p = self.report("The measured latency is 42 ms under load ([Docs](https://a.example/docs)).")
        data = self.ok("audit-report", "--report-file", str(p))
        self.assertEqual(data["status"], "PASS")

    def test_empty_ledger_still_flags_unregistered(self):
        empty = Path(self.tmp.name) / "empty-state"
        empty.mkdir()
        p = self.report("A claim with a link ([X](https://unregistered.example/y)).")
        data, code = run_wb(empty, "audit-report", "--report-file", str(p))
        self.assertEqual(data["status"], "FAIL")
        types = {i["type"] for i in data["issues"]}
        self.assertIn("UNREGISTERED_REPORT_URL", types)


class TestVerifyDelivery(WorkbenchTestCase):
    def setUp(self):
        super().setUp()
        self.proj = Path(self.tmp.name) / "vproj"
        self.proj.mkdir()
        (self.proj / "app.py").write_text("print('ok')\n", encoding="utf-8")

    def test_nothing_to_verify(self):
        err = self.err("verify-delivery")
        self.assertEqual(err["error_code"], "NOTHING_TO_VERIFY")

    def test_ladder_and_require(self):
        data = self.ok("verify-delivery", "--artifact", str(self.proj / "app.py"),
                       "--check", f"L2:python3 -m py_compile {self.proj}/app.py",
                       "--check", f"L3:python3 {self.proj}/app.py",
                       "--require", "L3", project_cwd=str(self.proj))
        self.assertEqual(data["achieved_level"], "L3")
        self.assertIn("L4", data["levels_not_checked"])

    def test_failing_check_fails(self):
        data = self.nonzero("verify-delivery",
                         "--check", "L3:python3 -c 'import sys; sys.exit(7)'",
                         project_cwd=str(self.proj))
        self.assertEqual(data["status"], "FAIL")

    def test_timeout_recorded(self):
        data = self.nonzero("verify-delivery", "--check", "L3:python3 -c 'import time; time.sleep(5)'",
                         "--timeout", "1", project_cwd=str(self.proj))
        cmd = data["commands"][0]
        self.assertTrue(cmd["timed_out"])
        self.assertEqual(cmd["exit_code"], 124)

    def test_invalid_check_spec(self):
        err = self.err("verify-delivery", "--check", "L9:nonsense", project_cwd=str(self.proj))
        self.assertEqual(err["error_code"], "INVALID_CHECK")


class TestHandoff(WorkbenchTestCase):
    def test_pack_then_check(self):
        self.ok("handoff-pack", "--title", "T", "--session-status", "PARTIAL",
                "--summary", "did things", "--next-step", "do more")
        data = self.ok("handoff-check")
        self.assertEqual(data["status"], "PASS")
        handoff = Path(self.tmp.name) / "st" / "HANDOFF.md"
        self.assertTrue(handoff.exists())

    def test_partial_without_steps_fails_check(self):
        self.ok("handoff-pack", "--title", "T", "--session-status", "PARTIAL", "--summary", "s")
        data = self.nonzero("handoff-check")
        self.assertTrue(any("next steps" in p for p in data["problems"]))


class TestArtifacts(WorkbenchTestCase):
    def test_list_and_new(self):
        listed = self.ok("artifact-list")
        types = {t["type"] for t in listed["templates"]}
        self.assertIn("technical-report", types)
        out = Path(self.tmp.name) / "report.md"
        data = self.ok("artifact-new", "--type", "technical-report",
                       "--title", "My report", "--output", str(out))
        self.assertTrue(out.exists())
        self.assertIn("TITLE", " ".join(data["placeholders_left"]) or [])

    def test_existing_output_requires_force(self):
        out = Path(self.tmp.name) / "r.md"
        out.write_text("existing", encoding="utf-8")
        self.err("artifact-new", "--type", "technical-report", "--title", "T", "--output", str(out))
        self.ok("artifact-new", "--type", "technical-report", "--title", "T", "--output", str(out), "--force")


class TestWideTable(WorkbenchTestCase):
    def test_matrix_states(self):
        self.ok("research-init", "--mode", "wide-matrix", "--topic", "T",
                "--entity", "A", "--entity", "B", "--field", "f1", "--field", "f2")
        page = Path(self.tmp.name) / "p.txt"
        page.write_text("A f1 value is 10 units.", encoding="utf-8")
        self.ok("research-add-source", "--source-id", "S1", "--url", "https://a.example/x",
                "--title", "X", "--tier", "PRIMARY", "--content-file", str(page))
        self.ok("research-add-claim", "--entity", "A", "--field", "f1",
                "--statement", "A f1 is 10", "--value", "10", "--source-id", "S1",
                "--quote", "A f1 value is 10 units")
        self.ok("research-add-gap", "--entity", "B", "--field", "f2",
                "--description", "not found", "--reason", "NO_PUBLIC_SOURCE")
        data = self.ok("wide-table")
        self.assertGreater(data["counts"]["missing"], 0)  # A/f2 and B/f1
        self.assertGreaterEqual(data["counts"]["verified"], 1)
        self.assertGreaterEqual(data["counts"]["na"], 1)
        strict = self.nonzero("wide-table", "--strict")
        self.assertEqual(strict["status"], "FAIL")


class TestSpecBuilder(WorkbenchTestCase):
    def test_full_spec_passes_check(self):
        self.ok("spec-new", "--goal", "Ship a verified CSV export for accountants",
                "--story", "As an accountant I export invoices",
                "--non-goal", "no PDF")
        self.ok("spec-criterion", "--story-id", "US1",
                "--given", "3 unpaid invoices", "--when", "export runs",
                "--then", "CSV has 3 rows")
        self.ok("spec-task", "--task", "Implement the export", "--verifies", "AC1")
        data = self.ok("spec-check")
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["coverage"]["criteria"], 1)
        self.assertEqual(data["coverage"]["criteria_without_tasks"], [])

    def test_goal_too_short(self):
        err = self.err("spec-new", "--goal", "short")
        self.assertEqual(err["error_code"], "GOAL_TOO_SHORT")

    def test_spec_exists_needs_force(self):
        self.ok("spec-new", "--goal", "First goal that is long enough")
        err = self.err("spec-new", "--goal", "Second goal that is long enough")
        self.assertEqual(err["error_code"], "SPEC_EXISTS")
        self.ok("spec-new", "--goal", "Second goal that is long enough", "--force")

    def test_unknown_story(self):
        self.ok("spec-new", "--goal", "A goal that is definitely long enough")
        err = self.err("spec-criterion", "--story-id", "US9",
                       "--given", "g", "--when", "w", "--then", "t")
        self.assertEqual(err["error_code"], "UNKNOWN_STORY")

    def test_incomplete_criterion_rejected(self):
        self.ok("spec-new", "--goal", "A goal that is definitely long enough", "--story", "s1")
        err = self.err("spec-criterion", "--story-id", "US1",
                       "--given", "valid given", "--when", "x", "--then", "valid then")
        self.assertEqual(err["error_code"], "INVALID_WHEN")

    def test_task_must_verify(self):
        self.ok("spec-new", "--goal", "A goal that is definitely long enough", "--story", "s1")
        self.ok("spec-criterion", "--story-id", "US1",
                "--given", "a valid given clause", "--when", "a valid when clause", "--then", "a valid then clause")
        err = self.err("spec-task", "--task", "Unverifiable work item")
        self.assertEqual(err["error_code"], "TASK_NOT_VERIFIABLE")
        err = self.err("spec-task", "--task", "Wrong reference", "--verifies", "AC99")
        self.assertEqual(err["error_code"], "UNKNOWN_CRITERION")

    def test_dependency_validation_and_cycles(self):
        self.ok("spec-new", "--goal", "A goal that is definitely long enough", "--story", "s1")
        self.ok("spec-criterion", "--story-id", "US1",
                "--given", "a valid given clause", "--when", "a valid when clause", "--then", "a valid then clause")
        err = self.err("spec-task", "--task", "Depends on the future", "--verifies", "AC1",
                       "--depends-on", "T5")
        self.assertEqual(err["error_code"], "UNKNOWN_TASK")
        # Build a 2-task acyclic chain: PASS; a self-referencing ledger is constructed manually.
        self.ok("spec-task", "--task", "First task", "--verifies", "AC1")
        self.ok("spec-task", "--task", "Second task", "--verifies", "AC1", "--depends-on", "T1")
        data = self.ok("spec-check")
        self.assertEqual(data["status"], "PASS")
        ledger_path = self.state / "spec_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["tasks"][0]["depends_on"] = ["T2"]  # create T1 <-> T2 cycle
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        data = self.nonzero("spec-check")
        self.assertTrue(any("cycle" in p for p in data["problems"]))

    def test_check_fails_on_missing_criteria(self):
        self.ok("spec-new", "--goal", "A goal that is definitely long enough", "--story", "empty story")
        data = self.nonzero("spec-check")
        self.assertTrue(any("no acceptance criteria" in p for p in data["problems"]))


class TestCodeReview(WorkbenchTestCase):
    def test_findings_and_fail_verdict(self):
        self.ok("review-init", "--title", "PR review", "--target", "src/x.py")
        self.ok("review-finding", "--file", "src/x.py", "--line", "10",
                "--severity", "BLOCKING", "--category", "correctness",
                "--description", "Wrong totals on multi-line invoices")
        self.ok("review-finding", "--file", "src/x.py",
                "--severity", "MINOR", "--category", "style",
                "--description", "Inconsistent naming in helpers")
        dup = self.err("review-finding", "--file", "src/x.py", "--line", "10",
                       "--severity", "BLOCKING", "--category", "correctness",
                       "--description", "Wrong totals on multi-line invoices")
        self.assertEqual(dup["error_code"], "DUPLICATE_FINDING")
        data = self.nonzero("review-report", "--not-reviewed", "the migration")
        self.assertEqual(data["verdict"], "FAIL")
        self.assertEqual(data["counts"]["BLOCKING"], 1)
        self.assertTrue(Path(data["report"]).exists())

    def test_pass_with_findings_verdict(self):
        self.ok("review-init", "--title", "Clean-ish", "--target", "src/y.py")
        self.ok("review-finding", "--file", "src/y.py", "--severity", "MINOR",
                "--category", "style", "--description", "Minor naming nit here")
        data = self.ok("review-report")
        self.assertEqual(data["verdict"], "PASS_WITH_FINDINGS")

    def test_init_validations(self):
        self.err("review-init", "--title", "ab", "--target", "x")
        self.err("review-init", "--title", "Valid title", "--target", "  ")
        self.ok("review-init", "--title", "Valid title", "--target", "src/z.py")
        err = self.err("review-init", "--title", "Another one", "--target", "src/z.py")
        self.assertEqual(err["error_code"], "REVIEW_EXISTS")


class TestKnowledgeBase(WorkbenchTestCase):
    def test_unsourced_entry_rejected(self):
        self.err("kb-add", "--question", "What is the timeout?",
                 "--answer", "It is 30 seconds in staging by default.")

    def test_sourced_and_assumed_entries(self):
        data = self.ok("kb-add", "--question", "What is the export row limit?",
                       "--answer", "10,000 rows per export in v1; documented in the spec.",
                       "--source-url", "https://example.com/spec", "--tag", "export")
        self.assertEqual(data["entry"]["confidence"], "MEDIUM")
        data = self.ok("kb-add", "--question", "What is the proxy timeout?",
                       "--answer", "Assumed 30s; not documented anywhere yet.",
                       "--assumed", "--tag", "infra")
        self.assertTrue(data["entry"]["assumed"])
        self.assertEqual(data["entry"]["confidence"], "LOW")

    def test_source_id_validated_against_ledger(self):
        self.ok("research-init", "--topic", "T")
        err = self.err("kb-add", "--question", "Is this claim in the ledger?",
                       "--answer", "References an unregistered source id.",
                       "--source-id", "S404")
        self.assertEqual(err["error_code"], "UNKNOWN_SOURCE_ID")

    def test_search_ranks_and_filters(self):
        self.ok("kb-add", "--question", "How does the CSV export handle taxes?",
                "--answer", "Tax is applied per line before totals are rounded.",
                "--source-url", "https://example.com/a", "--tag", "billing")
        self.ok("kb-add", "--question", "What is the proxy timeout?",
                "--answer", "Assumed 30 seconds in staging.",
                "--assumed", "--tag", "infra")
        data = self.ok("kb-search", "--query", "csv export tax")
        self.assertEqual(data["matched"], 1)
        self.assertEqual(data["results"][0]["id"], "K1")
        filtered = self.ok("kb-search", "--query", "proxy timeout", "--tag", "billing")
        self.assertEqual(filtered["matched"], 0)

    def test_duplicate_question_rejected(self):
        self.ok("kb-add", "--question", "Repeated question here?", "--answer", "First answer is long enough.",
                "--source-url", "https://example.com/x")
        err = self.err("kb-add", "--question", "Repeated question here?",
                       "--answer", "Second answer is also long enough.",
                       "--source-url", "https://example.com/y")
        self.assertEqual(err["error_code"], "DUPLICATE_QUESTION")

    def test_export_marks_assumptions(self):
        self.ok("kb-add", "--question", "What is the proxy timeout?",
                "--answer", "Assumed 30 seconds in staging.",
                "--assumed", "--tag", "infra")
        data = self.ok("kb-export")
        text = Path(data["knowledge_base"]).read_text(encoding="utf-8")
        self.assertIn("ASSUMPTION", text)


class TestDoctor(WorkbenchTestCase):
    def test_doctor_on_bare_project(self):
        proj = Path(self.tmp.name) / "proj"
        proj.mkdir()
        data = self.ok("doctor", "--project-root", str(proj))
        self.assertIn(data["status"], ("OK", "WARN"))
        self.assertEqual(data["hosts_detected"], [])
        ids = {c["id"] for c in data["checks"]}
        self.assertIn("python", ids)
        self.assertIn("state-dir", ids)

    def test_doctor_detects_install_and_flags_bad_frontmatter(self):
        proj = Path(self.tmp.name) / "proj2"
        skills = proj / ".claude" / "skills" / "demo-skill"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: " + "x" * 1100 + "\n---\n\nbody\n"
            "suite: local-advisor-suite\n", encoding="utf-8")
        (proj / "CLAUDE.md").write_text(
            "<!-- local-advisor-suite:start -->\nrules\n<!-- local-advisor-suite:end -->\n", encoding="utf-8")
        data, code = run_wb(self.state, "doctor", "--project-root", str(proj))
        self.assertEqual(code, 2, f"doctor must exit 2 on FAIL: {data}")
        self.assertIn("claude", data["hosts_detected"])
        skills_check = next(c for c in data["checks"] if c["id"] == "skills")
        self.assertEqual(skills_check["status"], "FAIL")
        self.assertIn("exceeds 1024", skills_check["detail"])

    def test_doctor_flags_stale_workbench_copy(self):
        proj = Path(self.tmp.name) / "proj3"
        skills = proj / ".zcode" / "skills" / "old-skill"
        (skills / "scripts").mkdir(parents=True)
        (skills / "SKILL.md").write_text(
            "---\nname: old-skill\ndescription: a demo skill\n---\nsuite: local-advisor-suite\n", encoding="utf-8")
        (skills / "scripts" / "workbench.py").write_text('VERSION = "2.1.0"\n', encoding="utf-8")
        data, code = run_wb(self.state, "doctor", "--project-root", str(proj))
        self.assertEqual(code, 2, f"doctor must exit 2 on FAIL: {data}")
        skills_check = next(c for c in data["checks"] if c["id"] == "skills")
        self.assertEqual(skills_check["status"], "FAIL")
        self.assertIn("v2.1.0", skills_check["detail"])


class TestSelfcheck(WorkbenchTestCase):
    def test_selfcheck_passes_on_suite_root(self):
        data = self.ok("selfcheck", "--path", str(ROOT))
        self.assertEqual(data["status"], "PASS")


class TestDataAnalysis(WorkbenchTestCase):
    """The data ledger: register -> findings with methods -> gaps -> grounded report."""

    def setUp(self):
        super().setUp()
        self.csv = Path(self.tmp.name) / "sales.csv"
        self.csv.write_text("month,sales\n2026-01,120\n2026-02,135\n2026-03,150\n", encoding="utf-8")

    def test_full_lifecycle_register_finding_gap_report(self):
        data = self.ok("data-register", "--path", str(self.csv),
                       "--question", "What is the monthly sales trend in this file?")
        self.assertEqual(data["dataset"]["bytes"], self.csv.stat().st_size)
        self.assertEqual(len(data["dataset"]["sha256"]), 64)
        self.assertFalse(data["content_drift"])
        f = self.ok("data-finding",
                    "--statement", "The file has 3 data rows",
                    "--method", "tail -n +2 sales.csv | wc -l",
                    "--result", "3 rows")
        self.assertEqual(f["finding"]["id"], "F1")
        f2 = self.ok("data-finding",
                     "--statement", "Monthly sales start at 120 and end at 150",
                     "--method", "cut -d, -f2 sales.csv | tail -n +2 | sed -n '1p;$p'",
                     "--result", "120 and 150")
        self.assertEqual(f2["finding"]["id"], "F2")
        g = self.ok("data-gap",
                    "--description", "Per-region breakdown is not computable from this file",
                    "--reason", "NO_DATA: no region column")
        self.assertEqual(g["gap"]["id"], "G1")
        r = self.ok("data-report",
                    "--answer", "Sales rose from 120 to 150 across 3 rows of months.")
        self.assertEqual(r["status"], "OK")
        self.assertFalse(r["contains_unverified_numbers"])
        self.assertFalse(r["dataset_drift"])
        report = Path(r["report"])
        self.assertTrue(report.is_file())
        text = report.read_text(encoding="utf-8")
        self.assertIn("wc -l", text)  # the method is printed, pipes escaped
        self.assertIn("NO_DATA: no region column", text)
        self.assertIn("## Declared gaps", text)

    def test_report_rejects_numbers_no_finding_supports(self):
        self.ok("data-register", "--path", str(self.csv),
                "--question", "What is the monthly sales trend in this file?")
        self.ok("data-finding", "--statement", "The file has 3 data rows",
                "--method", "tail -n +2 sales.csv | wc -l", "--result", "3 rows")
        data = self.err("data-report", "--answer", "Sales went from 120 to 999, trust me.")
        self.assertEqual(data["error_code"], "UNLEDGERED_NUMBERS")
        self.assertIn("999", data["details"]["unledgered"])
        escaped = self.ok("data-report", "--allow-unverified-numbers",
                          "--answer", "Sales went from 120 to 999, trust me.")
        self.assertEqual(escaped["status"], "WARN")
        self.assertTrue(escaped["contains_unverified_numbers"])
        self.assertIn("UNVERIFIED", Path(escaped["report"]).read_text(encoding="utf-8"))

    def test_finding_requires_a_real_method(self):
        self.ok("data-register", "--path", str(self.csv),
                "--question", "What is the monthly sales trend in this file?")
        data = self.err("data-finding", "--statement", "Total is 405",
                        "--method", "guessed", "--result", "405")
        self.assertEqual(data["error_code"], "METHOD_TOO_SHORT")

    def test_drift_is_refused_until_reregistered(self):
        self.ok("data-register", "--path", str(self.csv),
                "--question", "What is the monthly sales trend in this file?")
        self.ok("data-finding", "--statement", "The file has 3 data rows",
                "--method", "tail -n +2 sales.csv | wc -l", "--result", "3 rows")
        with self.csv.open("a", encoding="utf-8") as fh:
            fh.write("2026-04,170\n")
        data = self.err("data-finding", "--statement", "Now 4 data rows exist",
                        "--method", "tail -n +2 sales.csv | wc -l", "--result", "4 rows")
        self.assertEqual(data["error_code"], "DATASET_DRIFT")
        refreshed = self.ok("data-register", "--path", str(self.csv))
        self.assertTrue(refreshed["content_drift"])
        self.assertTrue(refreshed["warning"])
        after = self.ok("data-finding", "--statement", "Now 4 data rows exist",
                        "--method", "tail -n +2 sales.csv | wc -l", "--result", "4 rows")
        self.assertEqual(after["finding"]["id"], "F2")

    def test_switching_dataset_requires_force_and_resets(self):
        self.ok("data-register", "--path", str(self.csv),
                "--question", "What is the monthly sales trend in this file?")
        self.ok("data-finding", "--statement", "The file has 3 data rows",
                "--method", "tail -n +2 sales.csv | wc -l", "--result", "3 rows")
        other = Path(self.tmp.name) / "other.csv"
        other.write_text("x\n1\n", encoding="utf-8")
        data = self.err("data-register", "--path", str(other))
        self.assertEqual(data["error_code"], "DATASET_MISMATCH")
        switched = self.ok("data-register", "--path", str(other), "--force")
        self.assertTrue(switched["findings_reset"])
        self.assertEqual(switched["findings_count"], 0)

    def test_commands_before_register_fail_cleanly(self):
        data = self.err("data-finding", "--statement", "Anything at all here",
                        "--method", "some real command here", "--result", "42")
        self.assertEqual(data["error_code"], "NO_DATASET")
        data = self.err("data-report", "--answer", "No dataset was registered at all here.")
        self.assertEqual(data["error_code"], "NO_DATASET")

    def test_register_validates_question_and_file(self):
        data = self.err("data-register", "--path", str(self.csv), "--question", "trend?")
        self.assertEqual(data["error_code"], "QUESTION_TOO_SHORT")
        data = self.err("data-register", "--path", str(Path(self.tmp.name) / "nope.csv"),
                        "--question", "What is the monthly sales trend in this file?")
        self.assertEqual(data["error_code"], "FILE_NOT_FOUND")


class TestLoadSkills(WorkbenchTestCase):
    """Prompt → skill routing + the context brief (deterministic, TR and EN)."""

    def test_routes_turkish_comparison_prompt_to_wide_search(self):
        data = self.ok("load-skills",
                       "--prompt", "DuckDB mi SQLite mi, hangisi daha iyi, karşılaştır")
        top = data["routed"][0]
        self.assertEqual(top["brief"]["skill"], "wide-search")
        self.assertGreaterEqual(top["score"], 2)
        self.assertEqual(data["confidences"]["wide-search"], "HIGH")
        self.assertIn("matrix-method.md", " ".join(top["brief"]["read_in_order"]))

    def test_routes_turkish_bug_prompt_to_local_debug(self):
        data = self.ok("load-skills",
                       "--prompt", "src/app.py çalışmıyor, abc verince hata basıyor, neden patlıyor")
        top = data["routed"][0]
        self.assertEqual(top["brief"]["skill"], "local-debug")
        self.assertGreaterEqual(top["score"], 2)

    def test_routes_english_research_prompt_to_deep_research(self):
        data = self.ok("load-skills",
                       "--prompt", "Research whether WebAssembly threads are production ready, multiple sources")
        top = data["routed"][0]
        self.assertEqual(top["brief"]["skill"], "deep-research")

    def test_routes_turkish_data_prompt_to_data_analysis(self):
        data = self.ok("load-skills",
                       "--prompt", "bu csv dosyasını analiz et, aylık satış trendi ne")
        top = data["routed"][0]
        self.assertEqual(top["brief"]["skill"], "data-analysis")
        self.assertGreaterEqual(top["score"], 2)
        self.assertEqual(data["confidences"]["data-analysis"], "HIGH")
        self.assertIn("computation-ledger.md", " ".join(top["brief"]["read_in_order"]))
        self.assertIn("data-register", top["brief"]["first_command"])

    def test_routes_english_dataset_prompt_to_data_analysis(self):
        data = self.ok("load-skills",
                       "--prompt", "Analyze this dataset and tell me how many rows the spreadsheet has")
        top = data["routed"][0]
        self.assertEqual(top["brief"]["skill"], "data-analysis")
        self.assertGreaterEqual(top["score"], 2)

    def test_no_match_falls_back_to_local_advisor_with_reason(self):
        data = self.ok("load-skills", "--prompt", "bana bu konuda genel bir şey söyler misin acaba")
        self.assertIsNone(data["routed"][0].get("score"))
        self.assertEqual(data["fallback"]["skill"], "local-advisor")
        self.assertEqual(data["confidences"]["local-advisor"], "LOW")
        self.assertIn("no specific trigger matched", data["fallback"]["reason"])

    def test_direct_skill_load_returns_full_brief(self):
        data = self.ok("load-skills", "--skill", "decision-review")
        b = data["routed"][0]
        self.assertEqual(b["skill"], "decision-review")
        self.assertEqual(b["read_in_order"][0], "SKILL.md")
        self.assertEqual(data["confidences"]["decision-review"], "DIRECT")
        self.assertIn("decision-score", b["first_command"])

    def test_brief_text_contains_read_order_command_and_stop_rule(self):
        data = self.ok("load-skills", "--prompt", "research the topic with multiple sources please")
        bt = data["brief_text"]
        self.assertIn("# Skill brief", bt)
        self.assertIn("**Read in order**", bt)
        self.assertIn("**First command**", bt)
        self.assertIn("**Stop rule**", bt)

    def test_list_dumps_every_route_with_triggers(self):
        data = self.ok("load-skills", "--list")
        routes = data["routes"]
        self.assertEqual(len(routes), 14)
        by_skill = {r["skill"]: r for r in routes}
        self.assertTrue(by_skill["local-advisor"]["fallback"])
        self.assertFalse(by_skill["deep-research"]["fallback"])
        self.assertTrue(any("araştır" in t for t in by_skill["deep-research"]["triggers"]))

    def test_unknown_skill_is_structured_error(self):
        data = self.err("load-skills", "--skill", "nope")
        self.assertEqual(data["error_code"], "UNKNOWN_SKILL")

    def test_too_short_prompt_is_structured_error(self):
        data = self.err("load-skills", "--prompt", "kısa")
        self.assertEqual(data["error_code"], "PROMPT_TOO_SHORT")

    def test_routing_is_deterministic(self):
        p = "karşılaştır: DuckDB vs SQLite, hangisi daha iyi?"
        a = self.ok("load-skills", "--prompt", p)
        b = self.ok("load-skills", "--prompt", p)
        self.assertEqual([r["brief"]["skill"] for r in a["routed"]],
                         [r["brief"]["skill"] for r in b["routed"]])


if __name__ == "__main__":
    unittest.main()
