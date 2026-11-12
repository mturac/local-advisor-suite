#!/usr/bin/env python3
"""
install.py - install the local-advisor-suite skills into Claude Code, Codex,
ZCode, Cursor, OpenCode, or any AGENTS.md-compatible agent.

Standard library only. No network access. Every change is recorded in a manifest
(.local-advisor-suite.json) so `--uninstall` removes exactly what was installed.

Host map (v3.0)
  claude    .claude/skills/            ~/.claude/skills/            CLAUDE.md
  codex     .agents/skills/            ~/.agents/skills/            AGENTS.md / ~/.codex/AGENTS.md
  zcode     .zcode/skills/             ~/.zcode/skills/             AGENTS.md
  cursor    .cursor/skills/ + commands (project only)               .cursor/rules/*.mdc + AGENTS.md
  opencode  .agents/skills/ (shared)   ~/.config/opencode/skills/   AGENTS.md
  generic   no skill directories                                    AGENTS.md only

Examples
  python3 install.py --project ~/code/my-app                 # all five skill hosts
  python3 install.py --project . --hosts claude --link       # symlinks, Claude Code only
  python3 install.py --project . --hosts zcode,cursor        # ZCode + Cursor
  python3 install.py --global --hosts codex,opencode
  python3 install.py --project . --hosts generic --no-rules  # AGENTS.md block only
  python3 install.py --project . --skills local-debug,delivery-verify --dry-run
  python3 install.py --project . --uninstall
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

SUITE = "local-advisor-suite"
VERSION = "3.6.0"
SRC = Path(__file__).resolve().parent
SKILLS_SRC = SRC / "skills"
HOSTS = ("claude", "codex", "zcode", "cursor", "opencode", "generic")
SKILL_HOSTS = ("claude", "codex", "zcode", "cursor", "opencode")
DEFAULT_HOSTS = "claude,codex,zcode,cursor,opencode"
MANIFEST_NAME = ".local-advisor-suite.json"
START, END = "<!-- local-advisor-suite:start -->", "<!-- local-advisor-suite:end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
CURSOR_RULE = "local-advisor-suite.mdc"
CURSOR_COMMAND_MARKER = "<!-- local-advisor-suite:command -->"


class InstallError(Exception):
    pass


def available_skills() -> List[str]:
    return sorted(p.parent.name for p in SKILLS_SRC.glob("*/SKILL.md"))


def is_suite_skill(path: Path) -> bool:
    md = path / "SKILL.md"
    if not md.is_file():
        return False
    try:
        return f"suite: {SUITE}" in md.read_text(encoding="utf-8")
    except OSError:
        return False


def skill_dirs(base: Path, hosts: List[str], is_global: bool) -> Dict[str, Path]:
    """Map host -> skills directory, without creating duplicate installs.

    OpenCode reads .claude/skills and .agents/skills (project) and ~/.claude/skills,
    ~/.agents/skills (global), so in project mode it only gets its own directory
    when neither Claude Code nor Codex is selected. ZCode always gets .zcode/skills.
    Cursor has no auto-loaded skills directory: skills are copied to .cursor/skills
    (project only) and referenced by generated .cursor/commands/*.md files.
    """
    if is_global:
        home = Path.home()
        table = {
            "claude": home / ".claude" / "skills",
            "codex": home / ".agents" / "skills",
            "zcode": home / ".zcode" / "skills",
            "opencode": home / ".config" / "opencode" / "skills",
        }
    else:
        table = {
            "claude": base / ".claude" / "skills",
            "codex": base / ".agents" / "skills",
            "zcode": base / ".zcode" / "skills",
            "opencode": base / ".agents" / "skills",
        }
    out: Dict[str, Path] = {}
    for h in hosts:
        if h == "generic":
            continue
        if h == "cursor":
            if not is_global:
                out[h] = base / ".cursor" / "skills"
            continue
        if h == "opencode" and not is_global and ("claude" in hosts or "codex" in hosts):
            continue
        out[h] = table[h]
    return out


def rule_files(base: Path, hosts: List[str], is_global: bool) -> Dict[Path, str]:
    """Map rules file -> template name (deduplicated by path)."""
    files: Dict[Path, str] = {}
    if is_global:
        home = Path.home()
        if "claude" in hosts:
            files[home / ".claude" / "CLAUDE.md"] = "CLAUDE.template.md"
        if "codex" in hosts:
            files[Path(os.environ.get("CODEX_HOME", home / ".codex")) / "AGENTS.md"] = "AGENTS.template.md"
        if "zcode" in hosts:
            # ZCode discovers user skills by directory; AGENTS.md is project-level only.
            pass
        if "opencode" in hosts:
            files[home / ".config" / "opencode" / "AGENTS.md"] = "AGENTS.template.md"
    else:
        if "claude" in hosts:
            files[base / "CLAUDE.md"] = "CLAUDE.template.md"
        if any(h in hosts for h in ("codex", "zcode", "opencode", "generic", "cursor")):
            # Codex, ZCode, OpenCode, Cursor and generic AGENTS.md readers all
            # consume the same project-level AGENTS.md file.
            files[base / "AGENTS.md"] = "AGENTS.template.md"
    return files


def render_block(template: str, workbench: str) -> str:
    text = (SRC / template).read_text(encoding="utf-8")
    m = BLOCK_RE.search(text)
    if not m:
        raise InstallError(f"{template} has no {START} ... {END} block")
    return m.group(0).replace("{{WORKBENCH}}", workbench).rstrip("\n") + "\n"


def upsert_block(path: Path, block: str, dry: bool) -> str:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if BLOCK_RE.search(old):
        new = BLOCK_RE.sub(lambda _m: block, old, count=1)
        action = "updated"
    else:
        new = (old.rstrip("\n") + "\n\n" if old.strip() else "") + block
        action = "created" if not old else "appended"
    if new == old:
        return "unchanged"
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
    return action


def remove_block(path: Path, dry: bool) -> str:
    if not path.exists():
        return "missing"
    old = path.read_text(encoding="utf-8")
    if not BLOCK_RE.search(old):
        return "no block"
    new = BLOCK_RE.sub("", old).rstrip("\n")
    if not dry:
        if new.strip():
            path.write_text(new + "\n", encoding="utf-8")
        else:
            path.unlink()
    return "removed block" + ("" if new.strip() else " (file deleted, it only held the block)")


def remove_cursor_rule(path: Path, dry: bool) -> str:
    """Remove the suite block from a .mdc rule; delete the file if only frontmatter remains."""
    if not path.exists():
        return "missing"
    old = path.read_text(encoding="utf-8")
    if not BLOCK_RE.search(old):
        return "no block"
    remainder = BLOCK_RE.sub("", old)
    # A .mdc file is frontmatter + our block. If nothing but frontmatter/blank
    # lines remain, the file is entirely ours: delete it.
    stripped = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", remainder, flags=re.S).strip()
    if not dry:
        if not stripped:
            path.unlink()
        elif not remainder.strip():
            path.unlink()
        else:
            path.write_text(remainder.rstrip("\n") + "\n", encoding="utf-8")
    return "removed rule" + ("" if (not stripped and not remainder.strip()) else " (file kept, it had other content)")


def remove_path(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def install_skill(src: Path, dest: Path, link: bool, force: bool, dry: bool) -> str:
    if dest.is_symlink() or dest.exists():
        if dest.is_symlink() and dest.resolve() == src.resolve() and link:
            return "unchanged (link)"
        if not (is_suite_skill(dest) or force):
            raise InstallError(f"{dest} exists and is not a {SUITE} skill. Move it or pass --force.")
        if not dry:
            remove_path(dest)
        state = "replaced"
    else:
        state = "installed"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if link:
            dest.symlink_to(src.resolve(), target_is_directory=True)
        else:
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".local-workbench"))
            wb = dest / "scripts" / "workbench.py"
            if wb.exists():
                wb.chmod(0o755)
    return state + (" (link)" if link else " (copy)")


def cursor_command_text(skill: str) -> str:
    tpl = (SRC / "CURSOR_COMMAND.template.md").read_text(encoding="utf-8")
    return tpl.replace("{{SKILL}}", skill).replace("{{SUITE}}", SUITE)


def install_cursor_layer(base: Path, skills: List[str], workbench_rel: str, force: bool, dry: bool) -> List[Dict[str, str]]:
    """Install .cursor/rules/local-advisor-suite.mdc and .cursor/commands/<skill>.md."""
    created: List[Dict[str, str]] = []
    rules_dir = base / ".cursor" / "rules"
    commands_dir = base / ".cursor" / "commands"
    rule_path = rules_dir / CURSOR_RULE

    block = render_block("CURSOR_RULE.template.mdc", workbench_rel)
    frontmatter = (SRC / "CURSOR_RULE.template.mdc").read_text(encoding="utf-8").split(START)[0].rstrip("\n")
    if not frontmatter.lstrip().startswith("---"):
        raise InstallError("CURSOR_RULE.template.mdc must start with --- frontmatter before the block markers")
    content = frontmatter + "\n\n" + block
    old = rule_path.read_text(encoding="utf-8") if rule_path.exists() else ""
    if old == content:
        state = "unchanged"
    elif old and not (BLOCK_RE.search(old) or force):
        raise InstallError(f"{rule_path} exists and is not a {SUITE} rule. Move it or pass --force.")
    else:
        state = "updated" if old else "created"
    if not dry and state != "unchanged":
        rule_path.parent.mkdir(parents=True, exist_ok=True)
        rule_path.write_text(content, encoding="utf-8")
    print(f"{'[dry-run] ' if dry else ''}{'cursor rule ' + state:<22} {rule_path}")
    created.append({"kind": "cursor-rule", "path": str(rule_path)})

    for name in skills:
        cpath = commands_dir / f"{name}.md"
        text = cursor_command_text(name)
        old = cpath.read_text(encoding="utf-8") if cpath.exists() else ""
        if old == text:
            state = "unchanged"
        elif old and CURSOR_COMMAND_MARKER not in old and not force:
            raise InstallError(f"{cpath} exists and is not a {SUITE} command. Move it or pass --force.")
        else:
            state = "updated" if old else "created"
        if not dry and state != "unchanged":
            cpath.parent.mkdir(parents=True, exist_ok=True)
            cpath.write_text(text, encoding="utf-8")
        print(f"{'[dry-run] ' if dry else ''}{'cursor command ' + state:<22} {cpath}")
        created.append({"kind": "cursor-command", "path": str(cpath)})
    return created


def manifest_path(base: Path, is_global: bool) -> Path:
    return (Path.home() if is_global else base) / MANIFEST_NAME


def load_manifest(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise InstallError(f"Manifest {path} is unreadable; fix or delete it.")
    return {"suite": SUITE, "version": VERSION, "skills": [], "rules": [], "files": []}


def do_install(args: argparse.Namespace, base: Path) -> int:
    hosts = parse_hosts(args.hosts)
    skills = parse_skills(args.skills)
    dirs = skill_dirs(base, hosts, args.is_global)
    mpath = manifest_path(base, args.is_global)
    manifest = load_manifest(mpath)
    tag = "[dry-run] " if args.dry_run else ""
    if not skills:
        raise InstallError("No skills found to install; run tools/generate_shared.py first.")

    if "generic" in hosts and set(hosts) == {"generic"} and not args.no_rules:
        raise InstallError(
            "The 'generic' host only writes the AGENTS.md rules block, which must reference an installed "
            "workbench copy. Add at least one skill host (claude/codex/zcode/cursor/opencode) or pass --no-rules."
        )

    installed: List[Dict[str, str]] = []
    seen = set()
    for host, d in dirs.items():
        for name in skills:
            dest = d / name
            if dest in seen:
                continue
            seen.add(dest)
            state = install_skill(SKILLS_SRC / name, dest, args.link, args.force, args.dry_run)
            installed.append({"host": host, "skill": name, "path": str(dest), "mode": "link" if args.link else "copy"})
            print(f"{tag}{state:<22} {dest}")

    extra_files: List[Dict[str, str]] = []
    rules: List[str] = []
    if not args.no_rules:
        anchor = "local-advisor" if "local-advisor" in skills else skills[0]
        # Cursor layer (project mode only): rules .mdc + per-skill commands.
        if "cursor" in dirs:
            wb_rel = str(os.path.relpath(dirs["cursor"] / anchor / "scripts" / "workbench.py", base))
            extra_files += install_cursor_layer(base, skills, wb_rel, args.force, args.dry_run)

        for path, template in rule_files(base, hosts, args.is_global).items():
            if template == "CLAUDE.template.md":
                host_dir = dirs.get("claude")
            else:
                host_dir = dirs.get("codex") or dirs.get("zcode") or dirs.get("opencode") or dirs.get("cursor")
            if host_dir is None:
                host_dir = next(iter(dirs.values()))
            wb = host_dir / anchor / "scripts" / "workbench.py"
            wb_str = str(wb if args.is_global else os.path.relpath(wb, base))
            state = upsert_block(path, render_block(template, wb_str), args.dry_run)
            rules.append(str(path))
            print(f"{tag}{'rules ' + state:<22} {path}")

    both = "claude" in hosts and "codex" in hosts and not args.is_global
    if "opencode" in hosts and "opencode" not in dirs and not both:
        print("note: OpenCode reads the same skills from " + ", ".join(str(p) for p in dirs.values()) + " (no duplicate copy).")
    if both and "opencode" in hosts:
        print("note: OpenCode scans both .claude/skills and .agents/skills; with both installed it sees each skill twice "
              "(identical content). Use --hosts claude or --hosts codex if you only use OpenCode with one of them.")
    if "cursor" in hosts and args.is_global:
        print("note: Cursor manages user-level rules in-app; project install (.cursor/rules + commands) is the supported path.")
    if "zcode" in hosts and not args.is_global:
        print("note: ZCode also imports skills from Claude Code / Codex directories via Settings -> Skills -> Import.")

    if not args.dry_run:
        known = {s["path"] for s in manifest["skills"]}
        manifest["skills"] += [s for s in installed if s["path"] not in known]
        manifest["rules"] = sorted(set(manifest.get("rules", [])) | set(rules))
        known_files = {f["path"] for f in manifest.get("files", [])}
        manifest["files"] = manifest.get("files", []) + [f for f in extra_files if f["path"] not in known_files]
        manifest["version"] = VERSION
        mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"manifest               {mpath}")

    if not args.is_global:
        gi = base / ".gitignore"
        if args.gitignore:
            lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
            if ".local-workbench/" not in lines:
                if not args.dry_run:
                    gi.write_text("\n".join(lines + [".local-workbench/"]) + "\n", encoding="utf-8")
                print(f"{tag}gitignore updated      {gi}")
        elif not (gi.exists() and ".local-workbench/" in gi.read_text(encoding="utf-8")):
            print("hint: add '.local-workbench/' to .gitignore (or re-run with --gitignore).")
    return 0


def do_uninstall(args: argparse.Namespace, base: Path) -> int:
    mpath = manifest_path(base, args.is_global)
    if not mpath.exists():
        raise InstallError(f"No manifest at {mpath}; nothing recorded to uninstall.")
    manifest = load_manifest(mpath)
    tag = "[dry-run] " if args.dry_run else ""
    for entry in manifest.get("skills", []):
        p = Path(entry["path"])
        if p.is_symlink() or is_suite_skill(p):
            if not args.dry_run:
                remove_path(p)
            print(f"{tag}removed                {p}")
            parent = p.parent
            stop = Path.home() if args.is_global else base
            while not args.dry_run and parent != stop and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        elif p.exists():
            print(f"skipped (not ours)     {p}")
    for f in manifest.get("files", []):
        p = Path(f["path"])
        if not p.exists():
            continue
        if f.get("kind") == "cursor-rule":
            print(f"{tag}{remove_cursor_rule(p, args.dry_run):<22} {p}")
            parent = p.parent
            while not args.dry_run and parent != base and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
            continue
        if p.is_file() and (CURSOR_COMMAND_MARKER in p.read_text(encoding="utf-8", errors="replace")):
            if not args.dry_run:
                p.unlink()
            print(f"{tag}removed                {p}")
            parent = p.parent
            stop = base
            while not args.dry_run and parent != stop and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        elif p.exists():
            print(f"skipped (not ours)     {p}")
    for r in manifest.get("rules", []):
        print(f"{tag}{remove_block(Path(r), args.dry_run):<22} {r}")
    if not args.dry_run:
        mpath.unlink()
    print(f"{tag}manifest removed       {mpath}")
    return 0


def parse_hosts(value: str) -> List[str]:
    hosts = [h.strip().lower() for h in value.split(",") if h.strip()]
    bad = [h for h in hosts if h not in HOSTS]
    if bad or not hosts:
        raise InstallError(f"Unknown host(s) {bad}; choose from {', '.join(HOSTS)}.")
    return list(dict.fromkeys(hosts))


def parse_skills(value: str) -> List[str]:
    avail = available_skills()
    if value == "all":
        return avail
    wanted = [s.strip() for s in value.split(",") if s.strip()]
    bad = [s for s in wanted if s not in avail]
    if bad or not wanted:
        raise InstallError(f"Unknown skill(s) {bad}; available: {', '.join(avail)}.")
    return list(dict.fromkeys(wanted))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=f"Install {SUITE} {VERSION} skills for Claude Code, Codex, ZCode, Cursor, OpenCode and AGENTS.md-compatible agents.")
    where = p.add_mutually_exclusive_group()
    where.add_argument("--project", default=None, help="Project root to install into (default: current directory)")
    where.add_argument("--global", dest="is_global", action="store_true", help="Install into user-level skill directories")
    p.add_argument("--hosts", default=DEFAULT_HOSTS, help=f"Comma list: {','.join(HOSTS)} (default: {DEFAULT_HOSTS})")
    p.add_argument("--skills", default="all", help="'all' or a comma list of skill names")
    p.add_argument("--link", action="store_true", help="Symlink instead of copy (edits in this repo apply immediately)")
    p.add_argument("--force", action="store_true", help="Replace existing same-named skills that are not from this suite")
    p.add_argument("--no-rules", action="store_true", help="Do not write CLAUDE.md / AGENTS.md / .cursor rule blocks")
    p.add_argument("--gitignore", action="store_true", help="Append .local-workbench/ to the project .gitignore")
    p.add_argument("--dry-run", action="store_true", help="Print what would change, change nothing")
    p.add_argument("--uninstall", action="store_true", help="Remove everything recorded in the manifest")
    p.add_argument("--list", action="store_true", help="List available skills and exit")
    p.add_argument("--version", action="version", version=f"{SUITE} {VERSION}")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        for s in available_skills():
            print(s)
        return 0
    base = Path(args.project or os.getcwd()).expanduser().resolve()
    try:
        if not args.is_global and not base.is_dir():
            raise InstallError(f"Project directory does not exist: {base}")
        if not args.is_global and base == SRC:
            raise InstallError("Refusing to install into the suite's own directory; pass --project <your project>.")
        return do_uninstall(args, base) if args.uninstall else do_install(args, base)
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
