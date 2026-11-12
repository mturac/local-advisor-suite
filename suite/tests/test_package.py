"""Package consistency tests: 17 skills, frontmatter contracts, generated-file drift, docs."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXPECTED_SKILLS = {
    "local-advisor", "decision-review", "local-debug", "web-search", "deep-research",
    "wide-search", "evidence-audit", "delivery-verify", "artifact-studio", "session-handoff",
    "spec-builder", "code-review", "knowledge-capture", "data-analysis", "devil-advocate",
    "question-contract", "decision-journal",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)


def frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km and km.group(2).strip() and not km.group(2).strip().startswith((">", "|")):
            fm[km.group(1)] = km.group(2).strip().strip('"')
    return fm


class TestSkillLayer(unittest.TestCase):
    def test_17_skills_present(self):
        found = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(found, EXPECTED_SKILLS, f"skill set mismatch: {found ^ EXPECTED_SKILLS}")

    def test_frontmatter_contract(self):
        """name matches the directory; description present, single-line, <= 1024 chars (ZCode)."""
        for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill_md.parent.name):
                text = skill_md.read_text(encoding="utf-8")
                fm = frontmatter(text)
                self.assertEqual(fm.get("name"), skill_md.parent.name)
                self.assertIn("description", fm)
                self.assertLessEqual(len(fm["description"]), 1024)
                self.assertIn("suite: local-advisor-suite", text)
                self.assertLessEqual(len(text), 100 * 1024)
                self.assertIn("compatibility:", text)

    def test_workbench_copies_match_root(self):
        root_wb = (ROOT / "workbench.py").read_bytes()
        for skill in sorted(EXPECTED_SKILLS):
            copy = ROOT / "skills" / skill / "scripts" / "workbench.py"
            self.assertTrue(copy.is_file(), f"missing workbench copy for {skill}")
            self.assertEqual(copy.read_bytes(), root_wb, f"drifted copy: {skill}")
            copy.chmod(0o755)

    def test_openai_yaml_present_and_valid(self):
        for skill in sorted(EXPECTED_SKILLS):
            yml = ROOT / "skills" / skill / "agents" / "openai.yaml"
            self.assertTrue(yml.is_file(), f"missing openai.yaml for {skill}")
            text = yml.read_text(encoding="utf-8")
            self.assertIn("display_name:", text)
            self.assertIn("allow_implicit_invocation: true", text)

    def test_references_present_per_skill(self):
        required = {
            "local-advisor": {"advisory-modes.md", "answer-standards.md"},
            "decision-review": {"scoring-guide.md", "reversibility-classes.md"},
            "local-debug": {"hypothesis-discipline.md", "escalation.md"},
            "web-search": {"host-tools.md", "quick-verification-protocol.md"},
            "deep-research": {"research-protocol.md", "source-quality.md", "synthesis-standard.md"},
            "wide-search": {"matrix-method.md"},
            "evidence-audit": {"audit-rules.md"},
            "delivery-verify": {"level-selection.md"},
            "artifact-studio": {"writing-standards.md"},
            "session-handoff": {"handoff-protocol.md", "state-inventory.md"},
            "spec-builder": {"acceptance-criteria.md", "task-breakdown.md"},
            "code-review": {"severity-model.md", "review-checklist.md"},
            "knowledge-capture": {"entry-standards.md", "lifecycle.md"},
            "data-analysis": {"dataset-intake.md", "computation-ledger.md", "pitfalls.md"},
            "devil-advocate": {"challenge-discipline.md", "attack-categories.md",
                           "premortem-protocol.md", "outside-view.md",
                           "second-order-effects.md", "falsification.md"},
            "question-contract": {"contract-fields.md", "vague-terms.md"},
            "decision-journal": {"journal-discipline.md", "calibration.md"},
        }
        for skill, refs in required.items():
            for ref in refs:
                p = ROOT / "skills" / skill / "references" / ref
                self.assertTrue(p.is_file(), f"missing {skill}/references/{ref}")
                self.assertGreater(len(p.read_text(encoding="utf-8")), 500, f"too thin: {ref}")

    def test_templates_present(self):
        pairs = [
            ("decision-review", "adr.md"),
            ("decision-review", "decision-spec.json"),
            ("artifact-studio", "technical-report.md"),
            ("artifact-studio", "executive-summary.md"),
            ("artifact-studio", "presentation-outline.md"),
            ("artifact-studio", "data-schema.md"),
            ("artifact-studio", "incident-postmortem.md"),
            ("local-advisor", "advisory-brief.md"),
            ("data-analysis", "analysis-report.md"),
            ("devil-advocate", "challenge-report.md"),
            ("question-contract", "question-contract.md"),
            ("decision-journal", "decision-entry.md"),
        ]
        for skill, tpl in pairs:
            self.assertTrue((ROOT / "skills" / skill / "templates" / tpl).is_file(),
                            f"missing {skill}/templates/{tpl}")

    def test_artifact_templates_start_with_purpose_comment(self):
        for tpl in sorted((ROOT / "skills" / "artifact-studio" / "templates").glob("*.md")):
            first = tpl.read_text(encoding="utf-8").lstrip().splitlines()[0]
            self.assertTrue(first.startswith("<!--"), f"{tpl.name} must start with a purpose comment")

    def test_examples_have_real_json_outputs(self):
        for skill in sorted(EXPECTED_SKILLS):
            examples = list((ROOT / "skills" / skill / "examples").glob("*.md"))
            self.assertGreaterEqual(len(examples), 1, f"{skill} has no examples")
            for ex in examples:
                text = ex.read_text(encoding="utf-8")
                self.assertIn("```json", text, f"{ex} has no JSON output block")
                blocks = re.findall(r"```json\n(.*?)```", text, re.S)
                self.assertGreaterEqual(len(blocks), 1)
                for b in blocks:
                    json.loads(b)  # every JSON block must parse

    def test_skill_md_commands_exist_in_workbench(self):
        """Every $WB command mentioned in SKILL.md bodies must be a real subcommand."""
        import workbench
        parser = workbench.build_parser()
        sub = [a for a in parser._actions if hasattr(a, "choices") and isinstance(a.choices, dict)][0]
        known = set(sub.choices.keys())
        for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
            text = skill_md.read_text(encoding="utf-8")
            for cmd in re.findall(r"\$WB\s+([a-z][a-z0-9-]+)", text):
                self.assertIn(cmd, known, f"{skill_md.parent.name} references unknown command '{cmd}'")


class TestSharedLayer(unittest.TestCase):
    def test_shared_references_exist(self):
        for ref in ("README.md", "architecture-and-boundaries.md", "evidence-ledger-schema.md",
                    "host-compatibility.md", "citation-and-reporting-standard.md"):
            self.assertTrue((ROOT / "references" / ref).is_file(), f"missing references/{ref}")

    def test_shared_templates_exist(self):
        for tpl in ("README.md", "AGENTS.snippet.md", "adr-template.md",
                    "executive-research-report.md", "wide-comparison-matrix.md",
                    "bug-escalation-brief.md"):
            self.assertTrue((ROOT / "templates" / tpl).is_file(), f"missing templates/{tpl}")

    def test_plugin_manifests(self):
        for mf in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                   ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"):
            p = ROOT / mf
            self.assertTrue(p.is_file(), f"missing {mf}")
            json.loads(p.read_text(encoding="utf-8"))  # must parse
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], "3.8.0")
        self.assertEqual(plugin["skills"], "./skills/")

    def test_host_compatibility_covers_six_hosts(self):
        text = (ROOT / "references" / "host-compatibility.md").read_text(encoding="utf-8")
        for host in ("Codex", "Claude Code", "ZCode", "Cursor", "OpenCode", "AGENTS.md"):
            self.assertIn(host, text)

    def test_evidence_schema_documents_v30_ledgers(self):
        text = (ROOT / "references" / "evidence-ledger-schema.md").read_text(encoding="utf-8")
        for ledger in ("spec_ledger.json", "review_ledger.json", "kb_ledger.json"):
            self.assertIn(ledger, text)


class TestVersionConsistency(unittest.TestCase):
    def test_versions_align_everywhere(self):
        import workbench
        import install
        self.assertEqual(workbench.VERSION, "3.8.0")
        self.assertEqual(install.VERSION, "3.8.0")
        gen = (ROOT / "tools" / "generate_shared.py").read_text(encoding="utf-8")
        self.assertIn('VERSION = "3.8.0"', gen)
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], "3.8.0")
        manifest_like = (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        self.assertIn("17", manifest_like)

    def test_cli_versions(self):
        for script in ("workbench.py", "install.py"):
            proc = subprocess.run([sys.executable, str(ROOT / script), "--version"],
                                  capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("3.8.0", proc.stdout + proc.stderr)


class TestDocs(unittest.TestCase):
    def test_readme_covers_all_skills_and_hosts(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for skill in EXPECTED_SKILLS:
            self.assertIn(f"`{skill}`", text, f"README missing skill {skill}")
        for host in ("claude", "codex", "zcode", "cursor", "opencode", "generic"):
            self.assertIn(host, text, f"README missing host {host}")

    def test_changelog_has_300_entry(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## 3.0.0", text)

    def test_rule_templates_routing_table_complete(self):
        for tpl in ("AGENTS.template.md", "CLAUDE.template.md", "CURSOR_RULE.template.mdc"):
            text = (ROOT / tpl).read_text(encoding="utf-8")
            for skill in EXPECTED_SKILLS:
                self.assertIn(skill, text, f"{tpl} routing table missing {skill}")
            self.assertIn("{{WORKBENCH}}", text)


if __name__ == "__main__":
    unittest.main()
