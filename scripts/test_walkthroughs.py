#!/usr/bin/env python3
"""Validate every walkthrough flow in scripts/walkthroughs.json end to end.

Seeds a throwaway workspace (.ws-wt-root/.workspace), then runs each flow's
steps in order — exactly like the "Run all" button does — asserting each
step's exit code (and expected status when declared) and that every pick
path resolves inside the step's JSON result. Also checks that declared
deliverable files really exist on disk afterwards.

Usage: python3 scripts/test_walkthroughs.py
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = ROOT / ".ws-wt-root"
FLOWS = ROOT / "scripts" / "walkthroughs.json"


def pick_path(obj, path):
    """Resolve a dot path like 'coverage.tasks' or 'sources.0.quality_score'."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur[part]
        else:
            return None
    return cur


TEMPLATE_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\.([A-Za-z0-9_.]+)\}\}")


def resolve_templates(argv, results_by_id):
    """Interpolate {{stepId.field}} against earlier step results, console-style."""
    out = []
    for a in argv:
        def sub(m):
            src = results_by_id.get(m.group(1)) or {}
            val = pick_path(src, m.group(2))
            if val is None:
                raise KeyError(f"template {m.group(0)} does not resolve")
            return str(val)
        out.append(TEMPLATE_RE.sub(sub, a))
    return out


def main() -> int:
    flows = json.loads(FLOWS.read_text(encoding="utf-8"))["flows"]

    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    (TEST_ROOT / "suite").symlink_to(ROOT / "suite", target_is_directory=True)

    print("Seeding throwaway workspace…")
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "seed_workspace.py"), str(TEST_ROOT)],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        print("SEED FAILED:", proc.stdout[-1500:], proc.stderr[-1500:])
        return 1
    print(f"Seed OK in {time.time() - t0:.1f}s")

    ws = TEST_ROOT / ".workspace"
    state = ws / ".local-workbench"
    workbench = ROOT / "suite" / "workbench.py"

    total_steps = 0
    failures = []
    deliverables = []
    results_by_id = {}

    for flow in flows:
        print(f"\n=== Flow: {flow['title']} ({len(flow['steps'])} steps) ===")
        for i, step in enumerate(flow["steps"], 1):
            if step.get("kind") == "firecrawl" and step.get("action") == "scrape":
                # The console scrapes the live page; later steps register it via
                # research-add-source using {{stepId.url}} / {{stepId.title}} /
                # {{stepId.excerpt}}. Offline we synthesize that result from the
                # step's own params: the verbatim quote becomes the excerpt, so
                # the real add-source and add-claim steps still verify.
                params = step.get("params", {})
                url = params.get("url", "")
                quote = params.get("quote", "")
                host = urlparse(url).netloc.replace("www.", "") or "source"
                slug = [p for p in urlparse(url).path.split("/") if p]
                title = f"{host} - {slug[-1]}" if slug else host
                results_by_id[step["id"]] = {
                    "url": url, "title": title, "excerpt": quote, "quoteFound": True,
                }
                print(f"  [SKIP] {i:2d}. {step['title']:<38} (scrape synthesized offline)")
                continue
            if "command" not in step:
                # Narrative explain steps and live firecrawl search steps have no
                # workbench command; only the console renders them.
                kind = step.get("kind", "non-command")
                print(f"  [SKIP] {i:2d}. {step['title']:<38} ({kind})")
                continue
            total_steps += 1
            try:
                step_argv = resolve_templates(step["argv"], results_by_id)
            except KeyError as exc:
                failures.append(f"{flow['id']} step {i} ({step['command']}): {exc}")
                print(f"  [FAIL] {i:2d}. {step['title']:<38} ({exc})")
                continue
            argv = [sys.executable, str(workbench), "--state-dir", str(state),
                    step["command"], *step_argv]
            t1 = time.time()
            proc = subprocess.run(argv, cwd=str(ws), capture_output=True,
                                  text=True, timeout=120)
            dt = (time.time() - t1) * 1000
            result = None
            status = None
            out = proc.stdout.strip()
            if out.startswith("{"):
                try:
                    result = json.loads(out)
                    status = result.get("status")
                except json.JSONDecodeError:
                    status = "PARSE_ERROR"

            if result is not None and step.get("id"):
                results_by_id[step["id"]] = result
            expect_status = step.get("expectStatus") or step.get("expect_status")
            expect_exit = step.get("expectExit", step.get("expect_exit"))
            ok_exit = (proc.returncode == expect_exit) if expect_exit is not None \
                else proc.returncode == 0
            ok_status = expect_status is None or status == expect_status
            picked = pick_path(result, step["pick"]) if (result and step.get("pick")) else None
            ok_pick = not step.get("pick") or picked is not None

            ok = ok_exit and ok_status and ok_pick
            mark = "PASS" if ok else "FAIL"
            print(f"  [{mark}] {i:2d}. {step['title']:<38} exit={proc.returncode} "
                  f"status={status} pick={picked!r} {dt:.0f}ms")
            if not ok:
                failures.append(f"{flow['id']} step {i} ({step['command']}): "
                                f"exit={proc.returncode} status={status} "
                                f"expect={expect_status} pick={picked!r}")
                if proc.stderr.strip():
                    print("       stderr:", proc.stderr.strip()[:400])
            if step.get("deliverable") and isinstance(result, dict):
                for key in ("evidence_pack", "artifact", "report", "adr", "handoff_file"):
                    if result.get(key):
                        deliverables.append((flow["id"], result[key]))

    # deliverable files must exist and be non-empty
    print("\n=== Deliverable files ===")
    for flow_id, rel in deliverables:
        p = ws / rel
        exists = p.is_file() and p.stat().st_size > 0
        print(f"  [{'PASS' if exists else 'FAIL'}] {flow_id}: {rel} "
              f"({p.stat().st_size if p.exists() else 0} bytes)")
        if not exists:
            failures.append(f"{flow_id}: deliverable missing/empty: {rel}")

    print(f"\n{'=' * 60}")
    print(f"{total_steps - len([f for f in failures])}/{total_steps} steps passed")
    if failures:
        print("Failures:")
        for f in failures:
            print("  -", f)
    shutil.rmtree(TEST_ROOT, ignore_errors=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
