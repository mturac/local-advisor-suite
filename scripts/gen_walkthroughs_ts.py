#!/usr/bin/env python3
"""Generate src/lib/walkthroughs.ts from scripts/walkthroughs.json.

Keeps the UI walkthrough data in sync with the exact step sequences that
scripts/test_walkthroughs.py validates end to end.

Schema notes (v3 storytelling rewrite):
  - Flows carry `storyIntro`/`storyIntroTr` (the "you play the AI" setup)
    and `chapters` (acts that group the steps).
  - Steps carry `kind`: "workbench" (default; runs a real CLI command),
    "firecrawl" (runs a real web action via /api/firecrawl), or "explain"
    (a reading beat with bilingual body/example, nothing to run).
  - `id` on a step makes its result addressable: later steps may reference
    `{{stepId.field}}` inside argv — resolved at run time from the stored
    result (e.g. the scraped excerpt flows into research-add-source).
  - `expectExit` lets a step succeed on a non-zero exit when that is the
    expected outcome (e.g. adr-check deliberately returns FAIL / exit 2
    until a human fills the devil's advocate sections).

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
        "// Every workbench step sequence is validated end to end by scripts/test_walkthroughs.py",
        "// against a freshly seeded demo workspace (firecrawl steps hit the live web).",
        "// Edit scripts/build_walkthroughs.py, rebuild the JSON, then regenerate.",
        "",
        "export type StepKind = \"workbench\" | \"firecrawl\" | \"explain\"",
        "export type FirecrawlAction = \"search\" | \"scrape\" | \"map\" | \"extract\" | \"crawl\"",
        "",
        "export interface WalkthroughChapter {",
        "  title: string",
        "  titleTr?: string",
        "}",
        "",
        "export interface WalkthroughStep {",
        "  /** Stable step id; makes this step's result addressable as {{id.field}}. */",
        "  id?: string",
        "  /** 1-based index into the flow's chapters. */",
        "  chapter?: number",
        "  kind?: StepKind",
        "  title: string",
        "  titleTr?: string",
        "  explain?: string",
        "  explainTr?: string",
        "  /** One-line preview of the key output the user will see. */",
        "  see?: string",
        "  seeTr?: string",
        "  command?: string",
        "  argv?: string[]",
        "  /** Dot path into the JSON result shown as the step headline. */",
        "  pick?: string",
        "  pickLabel?: string",
        "  pickLabelTr?: string",
        "  /** Final artifact step — highlighted and badged in the UI. */",
        "  deliverable?: boolean",
        "  /** Exact status string the command must return (e.g. PASS / FAIL). */",
        "  expectStatus?: string",
        "  /** Expected exit code (default 0). adr-check deliberately exits 2 on FAIL. */",
        "  expectExit?: number",
        "  /** firecrawl steps: which web action to run. */",
        "  action?: FirecrawlAction",
        "  params?: Record<string, unknown>",
        "  /** explain steps: bilingual teaching card. */",
        "  body?: string",
        "  bodyTr?: string",
        "  example?: string",
        "  exampleTr?: string",
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
        "  storyIntro?: string",
        "  storyIntroTr?: string",
        "  chapters?: WalkthroughChapter[]",
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
        if flow.get("story_intro"):
            lines.append(f"    storyIntro: {ts_str(flow['story_intro'])},")
        if flow.get("story_intro_tr"):
            lines.append(f"    storyIntroTr: {ts_str(flow['story_intro_tr'])},")
        if flow.get("chapters"):
            lines.append("    chapters: [")
            for c in flow["chapters"]:
                entry = f"title: {ts_str(c['title'])}"
                if c.get("title_tr"):
                    entry += f", titleTr: {ts_str(c['title_tr'])}"
                lines.append(f"      {{ {entry} }},")
            lines.append("    ],")
        lines.append("    steps: [")
        for s in flow["steps"]:
            fields = [
                f"id: {ts_str(s['id'])}" if s.get("id") else None,
                f"chapter: {s['chapter']}" if s.get("chapter") else None,
                f"kind: {ts_str(s['kind'])}" if s.get("kind") else None,
                f"title: {ts_str(s['title'])}",
                f"titleTr: {ts_str(s['title_tr'])}" if s.get("title_tr") else None,
            ]
            if s.get("explain") is not None:
                fields.append(f"explain: {ts_str(s['explain'])}")
                if s.get("explain_tr"):
                    fields.append(f"explainTr: {ts_str(s['explain_tr'])}")
            if s.get("see"):
                fields.append(f"see: {ts_str(s['see'])}")
            if s.get("see_tr"):
                fields.append(f"seeTr: {ts_str(s['see_tr'])}")
            if s.get("command"):
                fields.append(f"command: {ts_str(s['command'])}")
            if "argv" in s:
                fields.append(f"argv: {json.dumps(s['argv'], ensure_ascii=False)}")
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
            if s.get("expectExit") is not None:
                fields.append(f"expectExit: {s['expectExit']}")
            if s.get("action"):
                fields.append(f"action: {ts_str(s['action'])}")
            if s.get("params"):
                fields.append(f"params: {json.dumps(s['params'], ensure_ascii=False)}")
            if s.get("body"):
                fields.append(f"body: {ts_str(s['body'])}")
            if s.get("body_tr"):
                fields.append(f"bodyTr: {ts_str(s['body_tr'])}")
            if s.get("example"):
                fields.append(f"example: {ts_str(s['example'])}")
            if s.get("example_tr"):
                fields.append(f"exampleTr: {ts_str(s['example_tr'])}")
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
