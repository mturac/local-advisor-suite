# Verifying a fix on the L0-L4 ladder

A bugfix verified with declared checks at L1, L2 and L3, plus an explicit L4 gap. The record keeps the commands, outcomes and git state.

```bash
$ python3 scripts/workbench.py verify-delivery \
  --artifact app.py \
  --check "L2:python3 -m py_compile app.py" \
  --check "L3:python3 -c \"from app import total; assert total([3.35, 3.35, 3.35]) == 10.06\"" \
  --require L3 \
  --not-run "L4: the accountant's manual flow in staging"
```

```json
{
  "status": "PASS",
  "verification_level": "L3_EXECUTION_VERIFIED",
  "achieved_level": "L3",
  "required_level": "L3",
  "levels_not_checked": [
    "L4"
  ],
  "git": {
    "head": null,
    "dirty": null
  },
  "artifacts": [
    {
      "artifact": "app.py",
      "exists": true,
      "size_bytes": 82,
      "level": "L1_ARTIFACT_PRESENT"
    }
  ],
  "commands": [
    {
      "command": "python3 -m py_compile app.py",
      "exit_code": 0,
      "passed": true,
      "timed_out": false,
      "duration_seconds": 0.03,
      "stdout_preview": "",
      "stderr_preview": "",
      "level": "L2"
    },
    {
      "command": "python3 -c \"from app import total; assert total([3.35, 3.35, 3.35]) == 10.06\"",
      "exit_code": 0,
      "passed": true,
      "timed_out": false,
      "duration_seconds": 0.01,
      "stdout_preview": "",
      "stderr_preview": "",
      "level": "L3"
    }
  ],
  "not_run": [
    "L4: the accountant's manual flow in staging"
  ],
  "verified_at": "2026-11-04T09:52:21+00:00"
}
```

Achieved L3 with the required level met. The honest delivery wording is: "the fix compiles and the targeted test passes (L3); your manual flow in staging was not run (declared)." `levels_not_checked: ["L4"]` is part of the record.

