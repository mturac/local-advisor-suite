---
description: "Local Advisor Suite: load the {{SKILL}} skill instructions and follow them for this request"
---
<!-- local-advisor-suite:command -->
Read the skill instructions at `.cursor/skills/{{SKILL}}/SKILL.md` in this repository, then follow them exactly to handle the user's request. The skill's `references/` and `templates/` subdirectories are part of the instructions; open them when the skill says so. The offline workbench runtime for any commands is `python3 .cursor/skills/{{SKILL}}/scripts/workbench.py` (state goes to `.local-workbench/`, which stays out of version control).
