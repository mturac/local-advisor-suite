#!/usr/bin/env python3
"""
Generator for the Local Advisor & Deep Research Suite (v3.0).

Creates the shared layer used by all 13 skills: plugin manifests (Claude Code,
Codex), marketplace entries, LICENSE, cross-skill references/ and templates/,
plus the per-skill agents/openai.yaml and scripts/workbench.py copies.

Zero external research-vendor dependencies. Re-run after editing workbench.py
or any shared file; tests/test_package.py fails if the committed files drift
from this generator.

Also validates the ZCode frontmatter contract: a SKILL.md whose description
exceeds 1024 characters is dropped by ZCode, so the generator refuses to
produce one.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
VERSION = "4.1.3"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")


def build_openai_yaml(display_name: str, short_desc: str) -> str:
    return f"""interface:
  display_name: "{display_name}"
  short_description: "{short_desc}"
policy:
  allow_implicit_invocation: true
"""


def generate_shared_files() -> None:
    # .claude-plugin/plugin.json
    write_file(
        ROOT / ".claude-plugin" / "plugin.json",
        json.dumps(
            {
                "name": "local-advisor-suite",
                "version": VERSION,
                "description": "Portable Local Advisor, Deep Research, Scoped Debugging, Spec Building, Code Review, Knowledge Capture, Data Analysis, Devil's Advocate and Evidence Audit skills for Claude Code, Codex, ZCode, Cursor and OpenCode. Zero external vendor dependencies.",
                "author": {"name": "Local Advisor Workbench"},
                "license": "Apache-2.0",
                "skills": "./skills/",
            },
            indent=2,
        )
        + "\n",
    )

    # .codex-plugin/plugin.json
    write_file(
        ROOT / ".codex-plugin" / "plugin.json",
        json.dumps(
            {
                "name": "local-advisor-suite",
                "version": VERSION,
                "description": "Portable Local Advisor, Deep Research, Scoped Debugging, Spec Building, Code Review, Knowledge Capture and Evidence Audit skills for Codex CLI/IDE.",
                "skills": "./skills/",
            },
            indent=2,
        )
        + "\n",
    )

    # Marketplace entries: lets users install the repo root as a plugin in one command.
    write_file(
        ROOT / ".claude-plugin" / "marketplace.json",
        json.dumps(
            {
                "name": "local-advisor-suite",
                "description": "Local advisor, decision review, scoped debugging, research, spec, review and verification skills.",
                "owner": {"name": "Local Advisor Workbench"},
                "plugins": [
                    {
                        "name": "local-advisor-suite",
                        "source": "./",
                        "description": f"{len(SKILL_INTERFACES)} provider-neutral skills backed by an offline workbench.py runtime.",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_file(
        ROOT / ".agents" / "plugins" / "marketplace.json",
        json.dumps(
            {
                "name": "local-advisor-suite",
                "interface": {"displayName": "Local Advisor Suite"},
                "plugins": [
                    {
                        "name": "local-advisor-suite",
                        "source": {"source": "local", "path": "./"},
                        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                        "category": "Productivity",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )

    write_file(
        ROOT / "LICENSE",
        """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
""",
    )

    # Shared references/
    write_file(
        ROOT / "references" / "README.md",
        """# Shared Reference Architecture

This directory holds cross-skill reference specifications used across the Local Advisor & Deep Research Suite:

1. `architecture-and-boundaries.md` — The zero-vendor architecture, conversation-first advisory rule, scoped filesystem guardrails, and cost/budget discipline.
2. `evidence-ledger-schema.md` — Formal JSON schema and lifecycle rules for every ledger in `.local-workbench/` (research, debug, delivery, spec, review, knowledge base, data analysis, devil's advocate).
3. `host-compatibility.md` — Exact discovery paths, frontmatter rules, and invocation syntax for OpenAI Codex CLI/IDE, Anthropic Claude Code, ZCode, Cursor, OpenCode, and generic AGENTS.md readers.
4. `citation-and-reporting-standard.md` — Rules for GitHub-Flavored Markdown reports, inline `[Source Name](URL)` citations, wide-table `n.a.` handling, and contradiction resolution.
""",
    )

    write_file(
        ROOT / "references" / "architecture-and-boundaries.md",
        """# Architecture & Operational Boundaries

## 1. Zero Hidden Vendor Dependencies
- This suite never connects to any proprietary research API, remote MCP endpoint, or paid background agent service.
- All reasoning, synthesis, and planning are executed by the model already active in your host (Claude Code, Codex, ZCode, Cursor, OpenCode, or any AGENTS.md-compatible agent).
- All state tracking, URL canonicalization, quote verification, and scope checks run locally via `scripts/workbench.py` using only the Python 3 standard library.

## 2. Conversation-First Advisory Rule
- When the user asks an architecture, design, strategy, or trade-off question (`local-advisor`, `decision-review`), the agent **must not** run `find`, `rg`, `grep`, `ls -R`, or glob searches across the machine.
- The agent answers from the conversation context first.
- Repository files are read **only** when the user explicitly names a file/directory or asks to inspect the current repository.

## 3. Strict Project-Root Containment
- When local file access is needed (`local-debug`, `code-review`, or repo-grounded `local-advisor`), file reads and searches must stay strictly inside the explicit `--project-root`.
- Parent traversal (`..`), symlinks pointing outside the repo, home directory sweeps (`~`), `.git/`, `node_modules/`, virtual environments, binary files, and secret files (`.env`, `.pem`, `.key`, `id_rsa`, `.aws`, `.ssh`) are blocked by `workbench.py scope-read` and `scope-scan`.

## 4. Two-Strike Debugging Circuit Breaker
- During debugging (`local-debug`), every hypothesis must be logged with a testable prediction before editing code.
- If **2 hypotheses** are falsified (`status=FALSIFIED`), the circuit breaker trips (`circuit_breaker_tripped=true`).
- Once tripped, the agent must stop guessing, refrain from widening its search scope, and report the falsified hypotheses and missing telemetry to the user.

## 5. Local Deep Research Discipline
- Search results and snippets are discovery leads, never final evidence.
- Every material claim requires:
  1. A registered source (`research-add-source`) from a fetched page or local document with a SHA-256 content hash.
  2. An atomic claim entry (`research-add-claim`) with a verbatim quote (`>= 10` characters) verified against the stored source excerpt.
- Unverified attributes in wide comparisons are recorded as explicit knowledge gaps (`research-add-gap`) and rendered as `n.a.` in tables — never guessed from model memory.

## 6. Testability and Verifiability Boundaries (v3.0)
- Work enters a plan only bound to an acceptance criterion (`spec-task --verifies`); `spec-check` PASS is the gate before implementation.
- Review verdicts are mechanical: `review-report` is FAIL while any BLOCKING finding is open, and every review declares what was **not** inspected.
- Delivery claims are level-bound: `verify-delivery` records the L0-L4 level actually observed, and wording never exceeds that level.
- Knowledge entries are sourced or explicitly marked `--assumed`; assumptions export visibly as unverified and are never quoted as fact.

## 7. Number-Grounded Data Analysis (v3.2)
- Analysis work starts by registering the exact file (`data-register`): path, byte size and SHA-256 are pinned in `data_ledger.json`, binding every later number to a dataset version.
- Every number presented to the user is logged as a finding (`data-finding`) that carries the re-runnable command, query or formula which produced it; a number without a method is rejected.
- What the file cannot answer is declared as a gap (`data-gap` with a reason), never guessed or interpolated.
- `data-report` lints the answer against the findings (`UNLEDGERED_NUMBERS`) and refuses to render numbers no finding supports; the `--allow-unverified-numbers` escape hatch publishes them visibly marked UNVERIFIED.
- Findings computed on content that no longer matches the registered hash are refused (`DATASET_DRIFT`) until the dataset is re-registered and the affected findings redone.

## 8. Adversarial Challenge Discipline (v3.3)
- A plan under stress-test gets its best case stated honestly first (`devil-open` steelman, min 30 chars) — an attack on a strawman is refused by design.
- Every challenge (`devil-challenge`) names the load-bearing assumption it attacks, what specifically breaks, its category, its severity (FATAL / SERIOUS / MINOR) and its defeater — the observation that would prove the attack wrong. An attack with no defeater is rejected: it is dogma, not criticism.
- A sound rebuttal (`devil-rebuttal`) answers the argument and names its basis (evidence, experience, constraint); it removes the challenge from the verdict. Rebuttals that wave at the argument are worse than silence and are visibly recorded either way.
- The verdict (`devil-verdict`) is mechanical: BLOCK while any FATAL challenge stands (exit 2), PROCEED_WITH_GUARDS while any SERIOUS one does, PROCEED only when every attack is answered. No verdict is computed without pre-committed, observable kill criteria.
- Guards and kill criteria survive the session: they belong in the ADR rollback trigger or the spec's acceptance criteria, so the challenge remains checkable after enthusiasm returns.
""",
    )

    write_file(
        ROOT / "references" / "evidence-ledger-schema.md",
        """# Evidence & State Ledger Schemas

All deterministic state files live inside `.local-workbench/` (configurable via `--state-dir`). Every command returns JSON; exit codes are `0` OK/PASS, `2` FAIL, `1` error.

## 1. Research Ledger (`research_ledger.json`)

```json
{
  "topic": "Compare embedded analytical databases for local Python workloads",
  "mode": "deep-research",
  "max_queries": 12,
  "queries_executed": 2,
  "sub_questions": [
    {"id": "Q1", "question": "What are the licensing and concurrency models?", "status": "ANSWERED"},
    {"id": "Q2", "question": "What are the memory limits and benchmarks?", "status": "GAP_RECORDED"}
  ],
  "entities": ["DuckDB", "SQLite"],
  "query_log": [
    {
      "id": "QRY-1",
      "query": "DuckDB concurrency multiprocess file locking documentation",
      "sub_question_id": "Q1",
      "tool_used": "host-web-search",
      "executed_at": "2026-11-02T12:00:00+00:00"
    }
  ],
  "sources": {
    "S1": {
      "id": "S1",
      "url": "https://duckdb.org/docs/connect/concurrency",
      "canonical_url": "https://duckdb.org/docs/connect/concurrency",
      "title": "Concurrency - DuckDB Documentation",
      "publisher": "DuckDB Foundation",
      "published_date": "2026",
      "source_tier": "PRIMARY",
      "content_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "excerpt": "DuckDB supports two concurrency models: one process with read-write access, or multiple processes with read-only access.",
      "fetched_at": "2026-11-02T12:01:00+00:00"
    }
  },
  "claims": [
    {
      "id": "C1",
      "sub_question_id": "Q1",
      "entity": "DuckDB",
      "field": "process_concurrency",
      "statement": "DuckDB allows either a single read-write process or multiple read-only processes.",
      "value": "1 RW or N RO processes",
      "source_ids": ["S1"],
      "quote": "one process with read-write access, or multiple processes with read-only access",
      "quote_verified_in_excerpt": true,
      "confidence": "HIGH",
      "status": "VERIFIED",
      "created_at": "2026-11-02T12:02:00+00:00"
    }
  ],
  "gaps": [
    {
      "id": "G1",
      "sub_question_id": "Q2",
      "entity": "DuckDB",
      "field": "encrypted_swap_overhead",
      "description": "Official docs do not publish a fixed percentage overhead for encrypted spill-to-disk.",
      "queries_tried": ["DuckDB encrypted spill to disk benchmark overhead"],
      "reason": "NO_PUBLIC_SOURCE",
      "created_at": "2026-11-02T12:03:00+00:00"
    }
  ]
}
```

Additional keys: `fields` (wide-matrix columns), `time_sensitive` (enables recency penalties), `resolutions` (`"<entity>::<field>" -> {winner_claim, value, losing_claims, reason}`), and per-source `quality_score` / `quality_reasons` written by `research-score`. Claims whose quote is not found in the stored excerpt are rejected unless `--allow-unverified-quote` is passed, which forces `LOW` / `PROVISIONAL`.

## 2. Debug Ledger (`debug_ledger.json`)

Tracks root-cause hypotheses and enforces the 2-strike circuit breaker:
- `failed_attempts`: integer count of `FALSIFIED` hypotheses.
- `circuit_breaker_tripped`: boolean (`true` when `failed_attempts >= 2`).
- `hypotheses`: ordered array of `{id, statement, prediction, test_command, status, evidence, updated_at}`.
- `target_files`: files the user named; `scope-read --debug-scope` refuses anything else.
- `repro_command`: the command that reproduces the symptom.

## 3. Delivery Verification Record (`delivery_verification.json`)

Tracks observable verification levels:
- `achieved_level` follows the L0-L4 ladder: `L0` claimed only, `L1` artifact exists (`--artifact`), `L2` static checks (`--check L2:<cmd>`), `L3` execution (`--command` or `--check L3:<cmd>`), `L4` acceptance (`--check L4:<cmd>`).
- A level counts only if every declared check at that level passed and no lower declared level failed. Levels with no checks are listed in `levels_not_checked`.
- `verification_level` keeps the legacy labels: `L1_ARTIFACT_EXISTENCE_ONLY`, `L2_STATIC_VERIFIED`, `L3_EXECUTION_VERIFIED`, `L4_ACCEPTANCE_VERIFIED`, `L0_UNVERIFIED`, or `VERIFICATION_FAILED`.
- `git.head` / `git.dirty` record exactly which code was verified. Timeouts are recorded as exit `124` with `timed_out: true`.

## 4. Spec Ledger (`spec_ledger.json`, v3.0)

```json
{
  "title": "Verified CSV export for accountants",
  "goal": "Ship a verified CSV export of invoices for enterprise accountants",
  "non_goals": ["No PDF export in v1"],
  "stories": [
    {
      "id": "US1",
      "text": "As an accountant I export all unpaid invoices to CSV",
      "status": "SPECIFIED",
      "criteria": [
        {
          "id": "AC1",
          "story_id": "US1",
          "given": "an account with 3 unpaid invoices totaling 10.06",
          "when": "the accountant runs the CSV export",
          "then": "the CSV contains exactly 3 rows and the total column sums to 10.06"
        }
      ]
    }
  ],
  "tasks": [
    {"id": "T1", "task": "Implement the CSV serialization", "verifies": ["AC1"], "depends_on": [], "created_at": "..."}
  ]
}
```

Lifecycle: `spec-new` (goal >= 20 chars, `--force` restarts) -> `spec-criterion` (Given/When/Then, each >= 5 chars) -> `spec-task` (must `--verifies` existing criteria; `--depends-on` existing tasks) -> `spec-check` (PASS gate: complete GWT clauses, no cycles; warnings for uncovered criteria and missing non-goals).

## 5. Review Ledger (`review_ledger.json`, v3.0)

```json
{
  "title": "Billing export PR #142",
  "target": "PR #142: src/billing/export.py",
  "focus": ["correctness", "error-handling"],
  "findings": [
    {
      "id": "F1",
      "file": "src/billing/export.py",
      "line": 42,
      "severity": "BLOCKING",
      "category": "correctness",
      "description": "Totals are rounded per line before tax is applied",
      "suggestion": "Apply tax before rounding in _line_total()",
      "created_at": "..."
    }
  ]
}
```

Severities: `BLOCKING` / `MAJOR` / `MINOR` / `INFO`. Categories: `correctness`, `security`, `performance`, `maintainability`, `tests`, `style`. `review-report` renders REVIEW.md; its verdict is `FAIL` while any BLOCKING finding is open, `PASS_WITH_FINDINGS` with majors/minors, else `PASS`.

## 6. Knowledge Base Ledger (`kb_ledger.json`, v3.0)

```json
{
  "entries": [
    {
      "id": "K1",
      "question": "In which order does the billing export apply tax and rounding?",
      "answer": "Tax is applied per line before totals are rounded; mode HALF_UP.",
      "source_url": "https://example.com/billing/export-spec",
      "source_id": "",
      "tags": ["billing", "export"],
      "assumed": false,
      "confidence": "MEDIUM",
      "created_at": "..."
    }
  ]
}
```

Every entry is sourced (`source_url` or `source_id` validated against the research ledger) or explicitly `assumed` (LOW confidence). `kb-search` scores deterministic token overlap (tags x3, question x2, answer x1); `kb-export` renders grouped Markdown with visible ASSUMPTION markers.

## 7. Data Analysis Ledger (`data_ledger.json`, v3.2)

```json
{
  "question": "What is the monthly sales trend in this file?",
  "dataset": {
    "path": "sales.csv",
    "bytes": 72,
    "sha256": "a5289da978c9db43d66ceff99ace993fa6c61cd74ade4674f64d655d2f4b302b",
    "registered_at": "2026-11-04T14:34:35+00:00"
  },
  "findings": [
    {
      "id": "F1",
      "statement": "The file has 5 data rows, one per month from 2026-01 to 2026-05",
      "method": "tail -n +2 sales.csv | wc -l",
      "result": "5 rows",
      "created_at": "..."
    }
  ],
  "gaps": [
    {"id": "G1", "description": "Per-region breakdown is not computable from this file",
     "reason": "NO_DATA: the file has no region column", "created_at": "..."}
  ]
}
```

Lifecycle: `data-register` (pins the dataset by path + size + SHA-256; one dataset per ledger; switching requires `--force` and resets findings) -> `data-finding` (statement + re-runnable method + result; refuses when the file drifted from its hash) -> `data-gap` (what could not be computed, and why) -> `data-report` (renders ANALYSIS.md; numbers in the answer that no finding supports are rejected with `UNLEDGERED_NUMBERS` unless `--allow-unverified-numbers` publishes them visibly marked UNVERIFIED).

## 8. Devil's Advocate Ledger (`devil_ledger.json`, v3.3)

```json
{
  "claim": "Split the monolith into microservices this quarter to speed up deploys",
  "steelman": "Independent deploys end the release train: each team ships daily, failures stay inside one service, and the org already runs containers in production",
  "status": "DECIDED",
  "challenges": [
    {
      "id": "C1",
      "assumption": "each team ships daily once split",
      "attack": "Deploy frequency is currently limited by review capacity, not by the release train; splitting adds coordination overhead that makes daily deploys less likely, not more",
      "category": "second-order-effect",
      "severity": "SERIOUS",
      "defeater": "deploy frequency per team rises within 6 weeks of each split",
      "status": "OPEN",
      "rebuttal": null,
      "rebuttal_basis": null,
      "created_at": "..."
    },
    {
      "id": "C4",
      "assumption": "the quarter timeline holds",
      "attack": "The estimate assumes zero migration of the reporting layer, which reads all 9 shared tables directly",
      "category": "unfounded-assumption",
      "severity": "MINOR",
      "defeater": "reporting reads confirmed via a single view during migration",
      "status": "ANSWERED",
      "rebuttal": "The reporting layer already goes through a nightly export view; checked the code before answering",
      "rebuttal_basis": "evidence: grep of the reporting repo, zero direct table references",
      "answered_at": "...",
      "created_at": "..."
    }
  ],
  "verdict": {
    "verdict": "PROCEED_WITH_GUARDS",
    "open_counts": {"FATAL": 0, "SERIOUS": 1, "MINOR": 0},
    "answered_count": 1,
    "guards": [{"challenge": "C1", "guard": "each team ships daily once split", "watch": "deploy frequency per team rises within 6 weeks of each split"}],
    "kill_criteria": ["per-team deploy frequency not above baseline 6 weeks after each split"],
    "decided_at": "..."
  },
  "created_at": "...",
  "updated_at": "..."
}
```

Lifecycle: `devil-open` (claim + honest steelman, min 30 chars; one session per ledger, restarting requires `--force` and wipes challenges) -> `devil-challenge` (assumption + attack + category + severity + defeater; an attack with no defeater is rejected) -> `devil-rebuttal` (answers an OPEN challenge with a basis; ANSWERED challenges leave the verdict) -> `devil-verdict` (mechanical gate: BLOCK while an open FATAL stands — JSON status FAIL, exit 2; PROCEED_WITH_GUARDS while an open SERIOUS stands — WARN; PROCEED when all answered — PASS; requires >= 1 observable kill criterion; renders CHALLENGE.md). Categories: unfounded-assumption, missing-evidence, second-order-effect, alternative-explanation, cost-complexity, reversibility, timing, external-risk.
""",
    )

    write_file(
        ROOT / "references" / "host-compatibility.md",
        """# Host Compatibility Matrix (Codex, Claude Code, ZCode, Cursor, OpenCode, AGENTS.md)

This suite adheres to the open Agent Skills specification (`SKILL.md` with `name`, `description`, `license`, `compatibility`, and string-valued `metadata`). Descriptions are single-line and under 1024 characters because ZCode drops a skill whose description exceeds that limit, and bodies stay under 100KB (ZCode's truncation bound).

| Feature | OpenAI Codex CLI / IDE | Anthropic Claude Code | ZCode | Cursor | OpenCode |
|---|---|---|---|---|---|
| **Project Skill Path** | `.agents/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.zcode/skills/<name>/SKILL.md` | `.cursor/skills/<name>/SKILL.md` (read on demand by generated commands) | `.agents/skills/` shared with Codex; `.opencode/skills/` when alone |
| **Personal Skill Path** | `~/.agents/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` | `~/.zcode/skills/<name>/SKILL.md` | project-level only (user rules are in-app) | `~/.config/opencode/skills/<name>/SKILL.md` |
| **Explicit Invocation** | `$skill-name` or `/skills` | `/skill-name` (plugin install: `/local-advisor-suite:skill-name`) | `$skill-name` in the input box; also in the `/` menu | `/<skill-name>` via generated `.cursor/commands/<name>.md` | Ask for it by name; loaded by the native `skill` tool |
| **Auto-Discovery** | Yes (via `description`; `agents/openai.yaml` sets `allow_implicit_invocation`) | Yes (via `description`) | Yes (via `description`; frontmatter `name` + `description` required, description <= 1024 chars) | Rules via `.cursor/rules/*.mdc` frontmatter; commands are manual | Yes (via `description` and native `skill` tool) |
| **Plugin / Distribution** | `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` | plugin marketplace with custom sources (GitHub, git URL, local dir); the repo root's flat `skills/<name>/SKILL.md` layout is a valid source; Settings -> Skills -> Import also scans Claude Code / Codex directories | project files in version control | Native directory scan (no plugin needed) |
| **Skill Permissions** | n/a | `permissions` in `settings.json` | per-skill enable switches in Settings -> Skills | rules are always-on or agent-selected by frontmatter | `permission.skill` patterns in `opencode.json` |
| **Native Web Tools** | `web_search` (`cached` default, `live`, `disabled`) | `WebSearch` + `WebFetch` | built-in agent web search | agent web search | `webfetch`; `websearch` only with the OpenCode provider or `OPENCODE_ENABLE_EXA=1` |
| **Instruction File** | `AGENTS.md` | `CLAUDE.md` (also reads `AGENTS.md`) | `AGENTS.md` | `AGENTS.md` (native) + `.cursor/rules/*.mdc` | `AGENTS.md` |

## Generic AGENTS.md hosts

Any agent that reads a project `AGENTS.md` (Gemini CLI, Amp, and similar) works through the `generic` host: `install.py --hosts generic` writes the operating-rules block only. The block references an installed workbench copy, so combine `generic` with at least one skill host, or pass `--no-rules`.

## Avoiding Duplicate Skill Entries

Because OpenCode scans `.agents/skills` and `.claude/skills`, and ZCode can also import from those directories:

- Use `--hosts <one host>` when targeting a single harness.
- `install.py` skips OpenCode's own directory when Claude or Codex is installed (they share `.agents/skills`), and notes when ZCode could import the same skills.
- ZCode keeps its own `.zcode/skills` directory so its Settings -> Skills page shows exactly one copy per skill.

## Cursor specifics

Cursor has no auto-loaded skills directory, so the installer generates:

- `.cursor/rules/local-advisor-suite.mdc` — the operating rules with `alwaysApply: true`.
- `.cursor/commands/<skill>.md` — one command per skill; invoking `/<skill>` in Agent chat instructs the agent to read `.cursor/skills/<skill>/SKILL.md` and follow it.
- `.cursor/skills/<skill>/` — the skill folders the commands reference.

Cursor also reads the project `AGENTS.md`, so the standard block is written there as well.
""",
    )

    write_file(
        ROOT / "references" / "citation-and-reporting-standard.md",
        """# Citation & Reporting Standard

When writing research syntheses, decision memos, or wide comparison tables:

1. **Natural Inline Citations**:
   - Every factual claim derived from a source must carry an inline Markdown link immediately after the sentence or table cell.
   - Anchor text must name the specific publisher, documentation, or paper — never generic words like `[source](...)`, `[link](...)`, `[here](...)`, or raw URLs.
   - Example: `SQLite runs in-process without a separate server daemon ([SQLite Architecture Docs](https://www.sqlite.org/arch.html)).`

2. **Ledger Grounding**:
   - Every URL cited in a Markdown report must exist in `.local-workbench/research_ledger.json` under `sources`.
   - Run `python3 scripts/workbench.py audit-report --report-file <report.md>` before delivering any research report.

3. **Missing Data (`n.a.`)**:
   - In wide entity comparisons, if a field cannot be verified from a fetched primary or reputable secondary source within the query budget, write `n.a.` in the table cell and log a gap with `research-add-gap`.
   - Never guess or interpolate missing numbers from model training memory.

4. **Contradiction Handling**:
   - When two reputable sources disagree on a figure or policy, register both sources and claims, then explain the discrepancy (e.g., different benchmark dates, editions, or scope definitions) instead of silently picking one.

5. **Verification Wording** (v3.0):
   - Delivery wording is level-bound to the L0-L4 ladder; never claim above the level `verify-delivery` recorded.
   - Spec work is criterion-bound: a task is done when its acceptance criterion's observable outcome is demonstrated, not when the code is written.
   - Assumptions are marked: knowledge entries added with `--assumed` export as **ASSUMPTION (unverified)** and must never be cited as fact.
""",
    )

    # Shared templates/
    write_file(
        ROOT / "templates" / "README.md",
        """# Shared Deliverable Templates

These templates provide reusable scaffolding across workflows:

- `AGENTS.snippet.md` — Drop-in project rules for `AGENTS.md` / `CLAUDE.md` enforcing conversation-first advisory, scoped file reads, spec/review discipline, and local deep research discipline.
- `adr-template.md` — Architecture Decision Record template.
- `executive-research-report.md` — Standalone GitHub-Flavored Markdown research report template.
- `wide-comparison-matrix.md` — Multi-entity comparison table and claim-ledger template.
- `bug-escalation-brief.md` — Diagnostic handoff template when the 2-strike debugging circuit breaker trips.

Per-skill templates (ADR instantiation, artifact-studio document skeletons) live under `skills/<name>/templates/`.
""",
    )

    write_file(
        ROOT / "templates" / "AGENTS.snippet.md",
        """<!-- BEGIN LOCAL-ADVISOR-SUITE RULES -->
## Local Advisor & Research Operating Rules

1. **Conversation-First Advisory (`local-advisor`, `decision-review`)**:
   - Answer architecture, design, planning, and trade-off questions directly from the conversation context first.
   - NEVER scan local directories, run broad `find`/`rg`/`grep` sweeps, or inspect unrelated files unless the user explicitly names a file path or asks to inspect this repository.

2. **Strict Repository Scope (`local-debug`, `code-review`)**:
   - Restrict all file reads and code searches strictly to the current project root.
   - Never traverse `..`, follow external symlinks, or read `.env`, SSH keys, or credential files.
   - Stop after **2 falsified debugging hypotheses** and report the evidence instead of guessing or widening search scope.

3. **Zero External Vendor Lock-In (`web-search`, `deep-research`, `wide-search`)**:
   - Never call third-party research APIs or MCP servers the user did not configure, and never switch search providers silently.
   - Use only the host environment's native search/fetch tools or user-supplied documents, and record every source, verbatim quote, and knowledge gap in `.local-workbench/research_ledger.json`.
   - Separate "file created" (`L1`) from "tests/commands verified" (`L3`).

4. **Testability and Verdicts (`spec-builder`, `code-review`, `delivery-verify`)**:
   - No task enters a plan without a verifying acceptance criterion; `spec-check` PASS gates implementation.
   - A review verdict is FAIL while any BLOCKING finding is open; declare what was not reviewed.
   - Report the achieved verification level and never claim wording above it.
<!-- END LOCAL-ADVISOR-SUITE RULES -->
""",
    )

    write_file(
        ROOT / "templates" / "adr-template.md",
        """# ADR-{{NUMBER}}: {{TITLE}}

- **Date**: {{DATE}}
- **Status**: {{PROPOSED_ACCEPTED_SUPERSEDED}}
- **Decision Owner**: {{OWNER}}

## Context & Problem Statement
{{PROBLEM_STATEMENT}}

## Hard Constraints & Non-Goals
- **Hard Constraints**:
  - {{CONSTRAINT_1}}
  - {{CONSTRAINT_2}}
- **Non-Goals**:
  - {{NON_GOAL_1}}

## Evaluated Options
| Option | Weighted Score | Disqualified? | Key Strength | Primary Risk |
|---|---:|---|---|---|
| {{OPTION_A}} | {{SCORE_A}} | {{DISQ_A}} | {{STRENGTH_A}} | {{RISK_A}} |
| {{OPTION_B}} | {{SCORE_B}} | {{DISQ_B}} | {{STRENGTH_B}} | {{RISK_B}} |

## Decision
We choose **{{SELECTED_OPTION}}** because {{RATIONALE}}.

## Steelman Counter-Argument (Why This Could Be Wrong)
{{STEELMAN_COUNTERARGUMENT}}

## Reversibility
- **Class**: {{R0_R1_R2_R3}} (R0 trivial undo, R1 cheap undo within a sprint, R2 costly migration, R3 effectively irreversible)
- **Cost to reverse**: {{REVERSAL_COST}}
- **Point of no return**: {{POINT_OF_NO_RETURN}}

## Pre-mortem
Assume it is 12 months later and this decision failed. The most likely causes:
1. {{FAILURE_MODE_1}} - early signal: {{SIGNAL_1}} - mitigation: {{MITIGATION_1}}
2. {{FAILURE_MODE_2}} - early signal: {{SIGNAL_2}} - mitigation: {{MITIGATION_2}}

## Operational Consequences & Rollback Trigger
- **Positive**: {{POSITIVE_CONSEQUENCES}}
- **Negative / Trade-offs**: {{NEGATIVE_CONSEQUENCES}}
- **Reversal Trigger**: Re-evaluate this decision if {{REVERSAL_CONDITION}}.
""",
    )

    write_file(
        ROOT / "templates" / "executive-research-report.md",
        """# {{REPORT_TITLE}}

## Executive Summary
{{DIRECT_SYNTHESIS_WITH_INLINE_CITATIONS}}

## Scope & Methodology
- **Primary Question**: {{TOPIC}}
- **Sub-Questions Investigated**: {{SUB_QUESTIONS_COUNT}}
- **Queries Executed**: {{QUERIES_EXECUTED}} / {{MAX_QUERIES}}
- **Verified Primary/Secondary Sources**: {{SOURCES_COUNT}}

## Key Findings by Sub-Question

### {{SUB_QUESTION_1_TITLE}}
{{ANALYSIS_WITH_NAMED_INLINE_CITATIONS}}

### {{SUB_QUESTION_2_TITLE}}
{{ANALYSIS_WITH_NAMED_INLINE_CITATIONS}}

## Comparative Matrix
| Entity / Dimension | {{FIELD_1}} | {{FIELD_2}} | {{FIELD_3}} | Primary Evidence |
|---|---|---|---|---|
| {{ENTITY_1}} | {{VAL_1_1}} | {{VAL_1_2}} | {{VAL_1_3}} | [{{PUBLISHER_1}}]({{URL_1}}) |
| {{ENTITY_2}} | {{VAL_2_1}} | `n.a.` | {{VAL_2_3}} | [{{PUBLISHER_2}}]({{URL_2}}) |

## Contradictions & Source Discrepancies
{{CONTRADICTION_ANALYSIS_OR_NONE}}

## Explicit Knowledge Gaps (`n.a.`)
| Gap ID | Entity / Field | What Could Not Be Verified | Queries Attempted | Reason |
|---|---|---|---|---|
| {{GAP_ID}} | {{ENTITY_FIELD}} | {{GAP_DESCRIPTION}} | `{{QUERIES_TRIED}}` | `{{REASON}}` |

## Actionable Recommendations
1. **{{RECOMMENDATION_1}}** — {{EVIDENCE_LINKED_JUSTIFICATION}}
2. **{{RECOMMENDATION_2}}** — {{EVIDENCE_LINKED_JUSTIFICATION}}
""",
    )

    write_file(
        ROOT / "templates" / "wide-comparison-matrix.md",
        """# Wide Comparison Matrix: {{TOPIC}}

## Field Definitions & Normalization Rules
- **{{FIELD_1}}**: {{DEFINITION_AND_UNIT_1}}
- **{{FIELD_2}}**: {{DEFINITION_AND_UNIT_2}}
- **Missing Value Policy**: Any unverified cell is marked `n.a.` and logged in the Gap Register below.

## Entity Comparison Table
| Entity | {{FIELD_1}} | {{FIELD_2}} | {{FIELD_3}} | Verification Status |
|---|---|---|---|---|
| **{{ENTITY_A}}** | {{VAL_A1}} ([{{SRC_A1}}]({{URL_A1}})) | {{VAL_A2}} ([{{SRC_A2}}]({{URL_A2}})) | `n.a.` | Partial (`1` gap) |
| **{{ENTITY_B}}** | {{VAL_B1}} ([{{SRC_B1}}]({{URL_B1}})) | {{VAL_B2}} ([{{SRC_B2}}]({{URL_B2}})) | {{VAL_B3}} ([{{SRC_B3}}]({{URL_B3}})) | Complete |

## Gap Register (`n.a.` Audit Trail)
- **{{ENTITY_A}} / {{FIELD_3}}**: Marked `n.a.` after searching `{{QUERY_TRIED}}` (`{{REASON}}`).
""",
    )

    write_file(
        ROOT / "templates" / "bug-escalation-brief.md",
        """# Diagnostic Escalation Brief: {{SYMPTOM_TITLE}}

- **Project Root**: `{{PROJECT_ROOT}}`
- **Circuit Breaker Status**: `TRIPPED (2 Falsified Hypotheses)`

## Observed Symptom & Reproduction
- **Command / Action**: `{{REPRO_COMMAND}}`
- **Exact Error / Traceback**:
```text
{{ERROR_OUTPUT}}
```

## Falsified Hypotheses Ledger
| ID | Hypothesis Statement | Testable Prediction | Command Run | Observed Evidence (Why Falsified) |
|---|---|---|---|---|
| `H1` | {{H1_STATEMENT}} | {{H1_PREDICTION}} | `{{H1_CMD}}` | {{H1_EVIDENCE}} |
| `H2` | {{H2_STATEMENT}} | {{H2_PREDICTION}} | `{{H2_CMD}}` | {{H2_EVIDENCE}} |

## Scoped Files Inspected
- `{{FILE_1}}` (lines {{LINES_1}})
- `{{FILE_2}}` (lines {{LINES_2}})

## What Is Needed to Unblock
- {{MISSING_TELEMETRY_OR_USER_DECISION}}
""",
    )


SKILL_INTERFACES = {
    "local-advisor": ("Local Advisor", "Senior technical advisor that works from the conversation, not by scanning files"),
    "decision-review": ("Decision Review", "Trade-off matrix, sensitivity, reversibility class, pre-mortem and ADR"),
    "local-debug": ("Local Debug", "Scoped debugger: target file only, 2-hypothesis circuit breaker, root-cause report"),
    "web-search": ("Web Search", "Fast source-verified answers with the host's own search and fetch tools"),
    "deep-research": ("Deep Research", "Multi-step research with evidence ledger, scoring, contradictions and gaps"),
    "wide-search": ("Wide Search", "Entity x field comparison tables where every cell links to a verified URL"),
    "evidence-audit": ("Evidence Audit", "Audit drafts for unopened links, unsupported numbers and overclaims"),
    "delivery-verify": ("Delivery Verify", "Prove delivery with real commands on an L0-L4 verification ladder"),
    "artifact-studio": ("Artifact Studio", "Templates for technical reports, ADRs, exec summaries, decks and schemas"),
    "session-handoff": ("Session Handoff", "Pack and validate session state so the next agent resumes without loss"),
    "spec-builder": ("Spec Builder", "Turn requests into testable specs: GWT acceptance criteria and verifying tasks"),
    "code-review": ("Code Review", "Severity-graded findings with locations and a deterministic FAIL verdict"),
    "knowledge-capture": ("Knowledge Capture", "Sourced or explicitly-assumed Q&A entries with offline search and export"),
    "data-analysis": ("Data Analysis", "Grounded analysis of a user-provided data file with a computation ledger"),
    "devil-advocate": ("Devil's Advocate", "Adversarial stress-test: premortem, outside view, severity-graded challenges with defeaters, second-order chains, mechanical verdict"),
    "question-contract": ("Question Contract", "Pin the question, the decision it informs and the consumer before spending tokens; vague-term scan; assumptions on record"),
    "decision-journal": ("Decision Journal", "Log decisions with falsifiable predictions and confidences; resolve against reality; calibration report flags overconfidence"),
    "get-more-perspective": ("Get More Perspective", "Convene a virtual advisory panel — five independent seats with role-mandated fields and evidence-backed skeptic/finance voices; mechanical synthesis that never manufactures agreement"),
}

FRONTMATTER_DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)


def validate_skill_frontmatter(skill_md: Path) -> str:
    """Return the description line; refuse descriptions over 1024 chars (ZCode drops the skill)."""
    text = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_DESC_RE.search(text)
    if not m:
        raise SystemExit(f"missing frontmatter description: {skill_md}")
    desc = m.group(1).strip()
    if len(desc) > 1024:
        raise SystemExit(
            f"description exceeds 1024 chars ({len(desc)}): {skill_md} — ZCode drops such skills; shorten it"
        )
    if len(text) > 100 * 1024:
        raise SystemExit(f"SKILL.md body exceeds 100KB: {skill_md} — ZCode truncates at 100KB")
    return desc


def generate_skill_layer() -> None:
    """Per-skill files derived from the root: agents/openai.yaml and scripts/workbench.py copies."""
    source = ROOT / "workbench.py"
    for name, (display, short) in SKILL_INTERFACES.items():
        skill = SKILLS_DIR / name
        if not (skill / "SKILL.md").is_file():
            raise SystemExit(f"missing skills/{name}/SKILL.md")
        validate_skill_frontmatter(skill / "SKILL.md")
        write_file(skill / "agents" / "openai.yaml", build_openai_yaml(display, short))
        dest = skill / "scripts" / "workbench.py"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        dest.chmod(0o755)


if __name__ == "__main__":
    generate_shared_files()
    generate_skill_layer()
    print(f"Shared files generated for {len(SKILL_INTERFACES)} skills (v{VERSION}).")
