#!/usr/bin/env python3
"""Validate every example scenario in scripts/scenarios.json.

Runs each scenario against a freshly seeded throwaway workspace
(.ws-test-root/.workspace) so the real demo workspace is never touched.
Non-destructive scenarios run first (display order), destructive ones last.

Usage: python3 scripts/test_scenarios.py
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = ROOT / ".ws-test-root"
SCENARIOS = ROOT / "scripts" / "scenarios.json"


def main() -> int:
    data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    all_scenarios = [
        (group["title"], s)
        for group in data["groups"]
        for s in group["scenarios"]
    ]
    commands = [s["command"] for _, s in all_scenarios]
    dupes = {c for c in commands if commands.count(c) > 1}
    if dupes:
        print(f"DUPLICATE commands in scenarios.json: {sorted(dupes)}")
        return 1
    print(f"{len(all_scenarios)} scenarios, {len(set(commands))} unique commands")

    # --- fresh seeded workspace -------------------------------------------------
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    (TEST_ROOT / "suite").symlink_to(ROOT / "suite", target_is_directory=True)

    print("Seeding throwaway workspace (6-host install + ledgers)…")
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "seed_workspace.py"), str(TEST_ROOT)],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        print("SEED FAILED:")
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        return 1
    seed = json.loads(proc.stdout)
    failed_steps = [f for f in seed.get("failures", [])]
    print(f"Seed OK in {time.time() - t0:.1f}s ({len(seed.get('steps', []))} steps, "
          f"{len(failed_steps)} failures)")
    if failed_steps:
        print(json.dumps(failed_steps, indent=1))

    ws = TEST_ROOT / ".workspace"
    state = ws / ".local-workbench"
    workbench = ROOT / "suite" / "workbench.py"

    # non-destructive first, destructive last
    ordered = [s for _, s in all_scenarios if not s.get("resets")] + \
              [s for _, s in all_scenarios if s.get("resets")]

    results = []
    for s in ordered:
        argv = [sys.executable, str(workbench), "--state-dir", str(state),
                s["command"], *s["argv"]]
        t1 = time.time()
        proc = subprocess.run(argv, cwd=str(ws), capture_output=True,
                              text=True, timeout=120)
        dt = (time.time() - t1) * 1000
        status = None
        out = proc.stdout.strip()
        if out.startswith("{"):
            try:
                status = json.loads(out).get("status")
            except json.JSONDecodeError:
                status = "PARSE_ERROR"
        expected_fail = bool(s.get("expectFail"))
        passed = (proc.returncode == 2) if expected_fail else (proc.returncode == 0)
        results.append((s["command"], passed, expected_fail, proc.returncode,
                        status, int(dt)))
        mark = "PASS" if passed else "FAIL"
        tag = " (expected FAIL)" if expected_fail else ""
        print(f"[{mark}]{tag} {s['command']:<22} exit={proc.returncode} "
              f"status={status} {dt:.0f}ms")
        if not passed and proc.stderr.strip():
            print("  stderr:", proc.stderr.strip()[:300])
        if not passed and status is None and out:
            print("  stdout:", out[:300])

    bad = [r for r in results if not r[1]]
    print()
    print(f"{'=' * 60}")
    print(f"{len(results) - len(bad)}/{len(results)} scenarios behaved as expected")
    if bad:
        print("Problems:")
        for name, _, ef, code, status, _ in bad:
            print(f"  - {name}: exit={code} status={status} expectFail={ef}")
    shutil.rmtree(TEST_ROOT, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
