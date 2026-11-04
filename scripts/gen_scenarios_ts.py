#!/usr/bin/env python3
"""Generate src/lib/scenarios.ts from scripts/scenarios.json.

Keeps the UI scenario chips in sync with the exact argv combinations that
scripts/test_scenarios.py validates.

Usage: python3 scripts/gen_scenarios_ts.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "scenarios.json"
DST = ROOT / "src" / "lib" / "scenarios.ts"


def ts_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    lines = [
        "// AUTO-GENERATED from scripts/scenarios.json by scripts/gen_scenarios_ts.py.",
        "// Every argv below is validated by scripts/test_scenarios.py against a",
        "// freshly seeded demo workspace. Edit the JSON, then regenerate.",
        "",
        "export interface Scenario {",
        "  label: string",
        "  command: string",
        "  argv: string[]",
        "  note: string",
        "  /** Resets (wipes) its ledger before writing — shown amber in the UI. */",
        "  resets?: boolean",
        "  /** Exits non-zero on the seeded workspace by design (mechanical gate). */",
        "  expectFail?: boolean",
        "}",
        "",
        "export interface ScenarioGroup {",
        "  title: string",
        "  scenarios: Scenario[]",
        "}",
        "",
        "export const SCENARIO_GROUPS: ScenarioGroup[] = [",
    ]
    for group in data["groups"]:
        lines.append("  {")
        lines.append(f"    title: {ts_str(group['title'])},")
        lines.append("    scenarios: [")
        for s in group["scenarios"]:
            fields = [
                f"label: {ts_str(s['label'])}",
                f"command: {ts_str(s['command'])}",
                f"argv: {json.dumps(s['argv'], ensure_ascii=False)}",
                f"note: {ts_str(s['note'])}",
            ]
            if s.get("resets"):
                fields.append("resets: true")
            if s.get("expectFail"):
                fields.append("expectFail: true")
            lines.append("      { " + ", ".join(fields) + " },")
        lines.append("    ],")
        lines.append("  },")
    lines.append("]")
    lines.append("")
    total = sum(len(g["scenarios"]) for g in data["groups"])
    lines.append(f"export const SCENARIO_COUNT = {total}")
    lines.append("")
    DST.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {DST} ({total} scenarios)")


if __name__ == "__main__":
    main()
