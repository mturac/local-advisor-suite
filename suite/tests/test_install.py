"""Tests for install.py: host tables, rule blocks, install/uninstall across all six hosts."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import install  # noqa: E402


class InstallTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.suite = Path(self.tmp.name) / "suite"
        # A miniature suite: install.py only needs skills/<name>/SKILL.md files.
        for name in ("local-advisor", "deep-research", "spec-builder"):
            skill = self.suite / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: a test skill\n---\n\nsuite: local-advisor-suite\n",
                encoding="utf-8")
        # Templates the installer renders.
        for tpl in ("AGENTS.template.md", "CLAUDE.template.md",
                    "CURSOR_RULE.template.mdc", "CURSOR_COMMAND.template.md"):
            src = ROOT / tpl
            self.assertTrue(src.exists(), f"missing template {tpl}")
            (self.suite / tpl).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        # Point install.SRC at the miniature suite.
        self._orig_src = install.SRC
        self._orig_skills_src = install.SKILLS_SRC
        install.SRC = self.suite
        install.SKILLS_SRC = self.suite / "skills"
        self.proj = Path(self.tmp.name) / "proj"
        self.proj.mkdir()

    def tearDown(self):
        install.SRC = self._orig_src
        install.SKILLS_SRC = self._orig_skills_src

    def run_install(self, *args):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "install.py"), "--project", str(self.proj), *args],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        return proc

    def test_parse_hosts_accepts_all_six(self):
        hosts = install.parse_hosts("claude,codex,zcode,cursor,opencode,generic")
        self.assertEqual(set(hosts), {"claude", "codex", "zcode", "cursor", "opencode", "generic"})

    def test_parse_hosts_rejects_unknown(self):
        with self.assertRaises(install.InstallError):
            install.parse_hosts("claude,warp")

    def test_skill_dirs_per_host(self):
        dirs = install.skill_dirs(self.proj, ["claude", "codex", "zcode", "cursor"], is_global=False)
        self.assertEqual(dirs["claude"], self.proj / ".claude" / "skills")
        self.assertEqual(dirs["codex"], self.proj / ".agents" / "skills")
        self.assertEqual(dirs["zcode"], self.proj / ".zcode" / "skills")
        self.assertEqual(dirs["cursor"], self.proj / ".cursor" / "skills")

    def test_opencode_piggybacks_when_codex_present(self):
        dirs = install.skill_dirs(self.proj, ["codex", "opencode"], is_global=False)
        self.assertNotIn("opencode", dirs)
        dirs = install.skill_dirs(self.proj, ["opencode"], is_global=False)
        self.assertEqual(dirs["opencode"], self.proj / ".agents" / "skills")

    def test_global_dirs(self):
        dirs = install.skill_dirs(self.proj, ["claude", "zcode", "cursor"], is_global=True)
        self.assertEqual(dirs["claude"], Path.home() / ".claude" / "skills")
        self.assertEqual(dirs["zcode"], Path.home() / ".zcode" / "skills")
        self.assertNotIn("cursor", dirs)

    def test_render_block_substitutes_workbench(self):
        block = install.render_block("AGENTS.template.md", "skills/x/scripts/workbench.py")
        self.assertIn("skills/x/scripts/workbench.py", block)
        self.assertIn("local-advisor-suite:start", block)
        self.assertNotIn("{{WORKBENCH}}", block)

    def test_upsert_block_idempotent(self):
        p = self.proj / "AGENTS.md"
        block = install.render_block("AGENTS.template.md", "wb")
        first = install.upsert_block(p, block, dry=False)
        second = install.upsert_block(p, block, dry=False)
        self.assertEqual(first, "created")
        self.assertEqual(second, "unchanged")
        self.assertEqual(p.read_text(encoding="utf-8").count("local-advisor-suite:start"), 1)

    def test_remove_block_deletes_owned_file(self):
        p = self.proj / "AGENTS.md"
        p.write_text("# Mine\n\n" + install.render_block("AGENTS.template.md", "wb"), encoding="utf-8")
        install.remove_block(p, dry=False)
        self.assertTrue(p.exists())
        self.assertNotIn("local-advisor-suite", p.read_text(encoding="utf-8"))
        p.write_text(install.render_block("AGENTS.template.md", "wb"), encoding="utf-8")
        install.remove_block(p, dry=False)
        self.assertFalse(p.exists())

    def test_install_all_skill_hosts(self):
        proc = self.run_install("--hosts", "claude,codex,zcode", "--gitignore")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for rel in (".claude/skills/deep-research/SKILL.md",
                    ".agents/skills/spec-builder/SKILL.md",
                    ".zcode/skills/local-advisor/SKILL.md"):
            self.assertTrue((self.proj / rel).exists(), f"missing {rel}")
        for rules in ("CLAUDE.md", "AGENTS.md"):
            text = (self.proj / rules).read_text(encoding="utf-8")
            self.assertIn("local-advisor-suite:start", text)
        self.assertIn(".local-workbench/", (self.proj / ".gitignore").read_text(encoding="utf-8"))
        manifest = json.loads((self.proj / ".local-advisor-suite.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "4.1.2")
        self.assertGreater(len(manifest["skills"]), 0)

    def test_install_cursor_generates_rules_and_commands(self):
        proc = self.run_install("--hosts", "cursor")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rule = self.proj / ".cursor" / "rules" / "local-advisor-suite.mdc"
        self.assertTrue(rule.exists())
        text = rule.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---"))
        self.assertIn("alwaysApply: true", text)
        for name in ("local-advisor", "deep-research", "spec-builder"):
            cmd = self.proj / ".cursor" / "commands" / f"{name}.md"
            self.assertTrue(cmd.exists(), f"missing command {name}")
            body = cmd.read_text(encoding="utf-8")
            self.assertIn(f".cursor/skills/{name}/SKILL.md", body)
            self.assertIn("local-advisor-suite:command", body)
            self.assertTrue((self.proj / ".cursor" / "skills" / name / "SKILL.md").exists())
        self.assertIn("local-advisor-suite:start", (self.proj / "AGENTS.md").read_text(encoding="utf-8"))

    def test_generic_only_requires_rules_or_skill_host(self):
        proc = self.run_install("--hosts", "generic")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("generic", proc.stderr)
        proc = self.run_install("--hosts", "generic", "--no-rules")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_uninstall_removes_everything(self):
        self.assertEqual(self.run_install("--hosts", "claude,codex,zcode,cursor").returncode, 0)
        proc = self.run_install("--uninstall")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for rel in (".claude/skills", ".agents/skills", ".zcode/skills",
                    ".cursor/skills", ".cursor/commands"):
            self.assertFalse((self.proj / rel).exists(), f"{rel} still present")
        rule = self.proj / ".cursor" / "rules" / "local-advisor-suite.mdc"
        self.assertFalse(rule.exists())
        for rules in ("CLAUDE.md", "AGENTS.md"):
            p = self.proj / rules
            if p.exists():
                self.assertNotIn("local-advisor-suite", p.read_text(encoding="utf-8"))
        self.assertFalse((self.proj / ".local-advisor-suite.json").exists())

    def test_uninstall_preserves_user_content_in_rules(self):
        (self.proj / "AGENTS.md").write_text("# Project rules\n\nKeep me.\n", encoding="utf-8")
        self.assertEqual(self.run_install("--hosts", "codex").returncode, 0)
        self.assertIn("Keep me.", (self.proj / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(self.run_install("--uninstall").returncode, 0)
        text = (self.proj / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Keep me.", text)
        self.assertNotIn("local-advisor-suite", text)

    def test_dry_run_changes_nothing(self):
        proc = self.run_install("--hosts", "claude", "--dry-run")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("dry-run", proc.stdout)
        self.assertFalse((self.proj / ".claude").exists())
        self.assertFalse((self.proj / ".local-advisor-suite.json").exists())

    def test_list_lists_skills(self):
        proc = subprocess.run([sys.executable, str(ROOT / "install.py"), "--list"],
                              capture_output=True, text=True, timeout=60,
                              env={**os.environ, "PYTHONPATH": str(ROOT)})
        self.assertEqual(proc.returncode, 0)
        listed = set(proc.stdout.split())
        expected = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(listed, expected)

    def test_manifest_v21_still_loads(self):
        """A v2.1-era manifest (skills/rules only, no files key) must load and uninstall."""
        mpath = self.proj / ".local-advisor-suite.json"
        owned = self.proj / ".claude" / "skills" / "local-advisor"
        owned.mkdir(parents=True)
        (owned / "SKILL.md").write_text(
            "---\nname: local-advisor\ndescription: d\n---\nsuite: local-advisor-suite\n", encoding="utf-8")
        (self.proj / "CLAUDE.md").write_text(install.render_block("CLAUDE.template.md", "wb"), encoding="utf-8")
        mpath.write_text(json.dumps({
            "suite": "local-advisor-suite", "version": "2.1.0",
            "skills": [{"host": "claude", "skill": "local-advisor", "path": str(owned), "mode": "copy"}],
            "rules": [str(self.proj / "CLAUDE.md")],
        }), encoding="utf-8")
        proc = self.run_install("--uninstall")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(owned.exists())
        self.assertFalse((self.proj / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
