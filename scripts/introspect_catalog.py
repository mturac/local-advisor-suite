#!/usr/bin/env python3
"""Introspect suite/workbench.py argparse parser and emit a JSON command catalog.

Usage: python3 introspect_catalog.py [suite_dir]
Emits: {"version": str, "commands": [{name, help, usage, category, args: [...]}]}
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

CATEGORIES = {
    "advise-intake": "Advisory",
    "decision-score": "Advisory",
    "scope-read": "Scope",
    "scope-scan": "Scope",
    "debug-hypothesis": "Debug",
    "debug-report": "Debug",
    "research-init": "Research",
    "research-log-query": "Research",
    "research-add-source": "Research",
    "research-add-claim": "Research",
    "research-add-gap": "Research",
    "research-status": "Research",
    "research-score": "Research",
    "research-gaps": "Research",
    "research-resolve": "Research",
    "research-pack": "Research",
    "fetch-url": "Evidence",
    "audit-report": "Evidence",
    "verify-delivery": "Evidence",
    "wide-table": "Evidence",
    "handoff-pack": "Handoff",
    "handoff-check": "Handoff",
    "adr-new": "Decision",
    "adr-check": "Decision",
    "artifact-list": "Artifact",
    "artifact-new": "Artifact",
    "selfcheck": "Quality",
    "doctor": "Quality",
    "spec-new": "Spec",
    "spec-criterion": "Spec",
    "spec-task": "Spec",
    "spec-check": "Spec",
    "review-init": "Review",
    "review-finding": "Review",
    "review-report": "Review",
    "kb-add": "Knowledge",
    "kb-search": "Knowledge",
    "kb-export": "Knowledge",
}


def json_safe(v):
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    return str(v)


def classify(action):
    cls = type(action).__name__
    if not action.option_strings:
        return "positional"
    if cls in ("_StoreTrueAction", "_StoreFalseAction", "_StoreConstAction", "_CountAction"):
        return "switch"
    if cls.startswith("_Append") or action.nargs in ("*", "+"):
        return "multi"
    return "single"


def main():
    suite_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "suite").resolve()
    wb_path = suite_dir / "workbench.py"
    spec = importlib.util.spec_from_file_location("workbench", wb_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    parser = mod.build_parser()
    sub_action = parser._subparsers._group_actions[0]

    commands = []
    for name, sp in sorted(sub_action.choices.items()):
        args = []
        for a in sp._actions:
            if a.dest == "help":
                continue
            kind = classify(a)
            args.append({
                "flags": list(a.option_strings),
                "dest": a.dest,
                "kind": kind,
                "required": True if kind == "positional" else bool(a.required),
                "default": json_safe(a.default),
                "help": a.help or "",
                "type": getattr(a.type, "__name__", None) if a.type else None,
                "choices": list(a.choices) if a.choices else None,
                "metavar": a.metavar if isinstance(a.metavar, str) else None,
            })
        usage = sp.format_usage().strip()
        commands.append({
            "name": name,
            "help": (sp.description or "").strip() or "",
            "usage": usage,
            "category": CATEGORIES.get(name, "Other"),
            "args": args,
        })

    try:
        version = subprocess.run(
            [sys.executable, str(wb_path), "--version"],
            capture_output=True, text=True, timeout=15, check=True,
        ).stdout.strip()
    except Exception:
        version = getattr(mod, "VERSION", "unknown")

    print(json.dumps({"version": version, "commands": commands}, indent=1))


if __name__ == "__main__":
    main()
