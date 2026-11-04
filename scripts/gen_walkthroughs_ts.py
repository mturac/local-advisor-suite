#!/usr/bin/env python3
"""Generate src/lib/walkthroughs.ts from scripts/walkthroughs.json.

Keeps the UI walkthrough data in sync with the exact step sequences that
scripts/test_walkthroughs.py validates end to end.

Every flow and step carries English fields (title/explain/see) plus Turkish
fields (titleTr/explainTr/seeTr). The UI picks the active language at render
time and falls back to English when a Turkish field is missing.

Usage: python3 scripts/gen_walkthroughs_ts.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "walkthroughs.json"
DST = ROOT / "src" / "lib" / "walkthroughs.ts"


def ts_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    lines = [
        "// AUTO-GENERATED from scripts/walkthroughs.json by scripts/gen_walkthroughs_ts.py.",
        "// Every step sequence is validated end to end by scripts/test_walkthroughs.py",
        "// against a freshly seeded demo workspace. Edit the JSON, then regenerate.",
        "",
        "export interface WalkthroughStep {",
        "  title: string",
        "  /** Turkish title; falls back to `title` when absent. */",
        "  titleTr?: string",
        "  explain: string",
        "  explainTr?: string",
        "  /** One-line preview of the key output the user will see. */",
        "  see?: string",
        "  seeTr?: string",
        "  command: string",
        "  argv: string[]",
        "  /** Dot path into the JSON result shown as the step headline. */",
        "  pick?: string",
        "  pickLabel?: string",
        "  pickLabelTr?: string",
        "  /** Final artifact step — highlighted and badged in the UI. */",
        "  deliverable?: boolean",
        "  /** Exact status string the command must return (e.g. PASS). */",
        "  expectStatus?: string",
        "}",
        "",
        "export interface WalkthroughFlow {",
        "  id: string",
        "  icon: string",
        "  title: string",
        "  titleTr?: string",
        "  subtitle: string",
        "  subtitleTr?: string",
        "  outcome: string",
        "  outcomeTr?: string",
        "  /** Rough duration in minutes, shown as a hint in the UI. */",
        "  timeMin?: number",
        "  steps: WalkthroughStep[]",
        "}",
        "",
        "export const WALKTHROUGH_FLOWS: WalkthroughFlow[] = [",
    ]
    for flow in data["flows"]:
        lines.append("  {")
        lines.append(f"    id: {ts_str(flow['id'])},")
        lines.append(f"    icon: {ts_str(flow['icon'])},")
        lines.append(f"    title: {ts_str(flow['title'])},")
        if flow.get("title_tr"):
            lines.append(f"    titleTr: {ts_str(flow['title_tr'])},")
        lines.append(f"    subtitle: {ts_str(flow['subtitle'])},")
        if flow.get("subtitle_tr"):
            lines.append(f"    subtitleTr: {ts_str(flow['subtitle_tr'])},")
        lines.append(f"    outcome: {ts_str(flow['outcome'])},")
        if flow.get("outcome_tr"):
            lines.append(f"    outcomeTr: {ts_str(flow['outcome_tr'])},")
        if flow.get("time_min"):
            lines.append(f"    timeMin: {flow['time_min']},")
        lines.append("    steps: [")
        for s in flow["steps"]:
            fields = [
                f"title: {ts_str(s['title'])}",
                f"titleTr: {ts_str(s['title_tr'])}" if s.get("title_tr") else None,
                f"explain: {ts_str(s['explain'])}",
                f"explainTr: {ts_str(s['explain_tr'])}" if s.get("explain_tr") else None,
                f"see: {ts_str(s['see'])}" if s.get("see") else None,
                f"seeTr: {ts_str(s['see_tr'])}" if s.get("see_tr") else None,
                f"command: {ts_str(s['command'])}",
                f"argv: {json.dumps(s['argv'], ensure_ascii=False)}",
            ]
            if s.get("pick"):
                fields.append(f"pick: {ts_str(s['pick'])}")
            if s.get("pickLabel"):
                fields.append(f"pickLabel: {ts_str(s['pickLabel'])}")
            if s.get("pickLabel_tr"):
                fields.append(f"pickLabelTr: {ts_str(s['pickLabel_tr'])}")
            if s.get("deliverable"):
                fields.append("deliverable: true")
            if s.get("expectStatus"):
                fields.append(f"expectStatus: {ts_str(s['expectStatus'])}")
            lines.append("      { " + ", ".join(f for f in fields if f) + " },")
        lines.append("    ],")
        lines.append("  },")
    lines.append("]")
    lines.append("")
    DST.write_text("\n".join(lines), encoding="utf-8")
    steps = sum(len(f["steps"]) for f in data["flows"])
    print(f"wrote {DST} ({len(data['flows'])} flows, {steps} steps)")


if __name__ == "__main__":
    main()
