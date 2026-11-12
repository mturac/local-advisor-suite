#!/usr/bin/env python3
"""
Local Advisor & Deep Research Workbench (Zero-External-Vendor Edition).

A deterministic, zero-dependency Python 3 CLI runtime that supports portable
skills across Codex CLI, Claude Code, ZCode, Cursor, OpenCode, and any
AGENTS.md-compatible agent without connecting to any hosted research vendor
or hidden third-party API.

Capabilities:
1. Advisory & Decision Engine:
   - Structured intake, option matrix scoring, sensitivity checks, ADR generation.
2. Scoped Local File Inspector & Debugger:
   - Strictly bounded to an explicit `--project-root`.
   - Rejects home-directory sweeps, parent traversal (`..`), symlink escapes,
     secret files (`.env`, `.ssh`, keys), and binary dumps.
   - Hypothesis ledger with a hard 2-failed-attempt circuit breaker.
3. Local Deep Research & Evidence Ledger:
   - Research plan initialization with sub-questions, entity matrix, and query budgets.
   - Canonical URL normalization and deduplication.
   - Source registration (from host-fetched pages or local files) with SHA-256 content hashing.
   - Atomic claim extraction with mandatory quote spans, source IDs, and confidence tiers.
   - Contradiction detection and explicit knowledge-gap tracking.
   - Safe public HTTPS URL fetching (`fetch-url`) with private-IP/SSRF blocking and caching.
4. Evidence Audit & Delivery Verification:
   - Automated verification that every claim maps to a fetched source and non-empty quote.
   - Markdown report citation linter (verifies inline `[Anchor](URL)` links against ledger).
   - Observable command verification runner for delivery gates.
5. v2.1 extensions (same JSON contract, same --state-dir):
   - research-score / research-gaps / research-resolve / research-pack
   - wide-table (entity x field matrix, every cell bound to a ledger claim)
   - decision-score sensitivity block, adr-new / adr-check
   - verify-delivery L0-L4 ladder (--check LEVEL:CMD, --require)
   - debug-report, handoff-check, artifact-list / artifact-new, selfcheck
6. v3.0 additions (additive only; every v2.1 command and flag still works):
   - doctor (environment + installation health check across all six hosts)
   - spec-builder ledger: spec-new / spec-criterion / spec-task / spec-check
     (goal -> user stories -> Given/When/Then acceptance criteria -> tasks
      that must verify at least one criterion each)
   - code-review ledger: review-init / review-finding / review-report
     (severity-graded findings with a deterministic FAIL verdict when any
      BLOCKING finding is open)
   - knowledge base: kb-add / kb-search / kb-export
     (sourced or explicitly-assumed Q&A entries, offline deterministic
      keyword search, markdown export)
7. v3.2 additions (additive only):
   - data analysis ledger: data-register / data-finding / data-gap /
     data-report (dataset pinned by SHA-256, every number logged as a
     finding carrying the re-runnable command or formula that produced
     it, gaps declared instead of guessed, answer numbers linted
     against the findings before the report renders)
8. v3.4 additions (additive only):
   - load-skills depth system: --core renders a run-from-this-card brief
     (skill + 3-step core loop + first command + stop rule, zero file
     reading) so quick asks skip the full protocol; every prompt routing
     also returns a deterministic suggested_depth (core / compact / full)
     so the agent spends context only when the ask is worth it
9. v3.5 additions (additive only):
   - devil-advocate red-team protocols: devil-plan (archetype attack
     plans for build / launch / migrate / hire / buy / process),
     devil-premortem (the failure story, written before the challenges),
     devil-outside (reference class + base rate; a bad base rate with no
     argued adjustment auto-opens a SERIOUS optimism-bias challenge),
     devil-consequence (L1 -> L2 -> L3 'and then what?' chains). The
     CHALLENGE.md verdict now renders premortem, outside view and
     second-order sections plus a protocols_used summary.
10. v3.6 additions (additive only):
   - question-contract ledger: qc-pin / qc-check / qc-assume (pin the
     question, the decision it informs and the consumer before spending
     tokens; deterministic vague-term scan with the clarifying question
     each vague word demands; a READY / NEEDS_INPUT gate; assumptions
     recorded where the question was ambiguous, to be stated in the
     answer's caveat)
11. v3.7 additions (additive only):
   - decision journal: journal-log / journal-resolve / journal-report
     (decisions logged with falsifiable predictions, confidence and a
     review date; resolved HIT / MISS / PARTIAL against reality with the
     lesson; calibration report per confidence band with an
     overconfidence verdict and overdue-entry tracking)
12. v3.8 additions (additive only):
   - playbooks: playbook-list / playbook-show — five pre-composed skill
     chains (decide, investigate, build, launch, debug) with per-step
     gates and handoff rules; orchestration without a state machine

Network policy: the only command that can open a socket is `fetch-url`, and only
with --allow-network. Every other command is offline and deterministic.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html.parser
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


VERSION = "3.8.0"
DEFAULT_STATE_DIR = ".local-workbench"
MAX_FILE_BYTES = 512 * 1024  # 512 KB cap for scoped local file reads
MAX_SCAN_FILES = 200
MAX_FETCH_BYTES = 1024 * 1024  # 1 MB cap for explicit URL fetches

FORBIDDEN_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".idea",
    ".vscode",
}

SENSITIVE_FILE_PATTERNS = (
    r"^\.env(\..+)?$",
    r".*\.pem$",
    r".*\.key$",
    r"^id_rsa.*",
    r"^id_ed25519.*",
    r"^\.netrc$",
    r"^\.npmrc$",
    r"^\.pypirc$",
    r"^credentials\.json$",
    r"^secrets\..*$",
)


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash a file in 1 MiB chunks (used to pin dataset identity)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonicalize_url(raw_url: str) -> str:
    """Normalize URL for deduplication while preserving meaningful query params."""
    parsed = urllib.parse.urlsplit(raw_url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = re.sub(r"/+", "/", parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    # Drop tracking parameters
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered_pairs = [
        (k, v)
        for (k, v) in query_pairs
        if not k.lower().startswith(("utm_", "fbclid", "gclid", "mc_cid", "mc_eid"))
    ]
    filtered_pairs.sort()
    query = urllib.parse.urlencode(filtered_pairs)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


class WorkbenchError(Exception):
    """Structured error for predictable CLI failures."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class HTMLTextExtractor(html.parser.HTMLParser):
    """Minimal HTML-to-clean-text extractor using Python standard library."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "head", "template"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.title: str = ""
        self._in_title = False
        self._chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        if t in self.SKIP_TAGS:
            self._skip_depth += 1
        elif t == "title":
            self._in_title = True
        elif t in {"p", "div", "section", "article", "br", "li", "tr", "h1", "h2", "h3", "h4"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif t == "title":
            self._in_title = False
        elif t in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title and not self.title:
            self.title = " ".join(data.split()).strip()
        if self._skip_depth == 0:
            cleaned = " ".join(data.split())
            if cleaned:
                self._chunks.append(cleaned + " ")

    def get_text(self) -> str:
        raw = "".join(self._chunks)
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        non_empty = [line for line in lines if line]
        return "\n".join(non_empty)


def ensure_state_dir(state_dir: Path) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    tmp.replace(path)


def validate_scoped_path(project_root: Path, target_path: Path) -> Path:
    """
    Enforce strict project-root containment:
    - Target must resolve inside resolved project_root.
    - Reject symlink escapes.
    - Reject sensitive credential files.
    """
    root_resolved = project_root.resolve(strict=True)
    # Check raw relative components for parent traversal before resolving
    try:
        candidate = (project_root / target_path) if not target_path.is_absolute() else target_path
    except Exception as exc:
        raise WorkbenchError("INVALID_PATH", f"Invalid path: {target_path}") from exc

    if candidate.is_symlink():
        raise WorkbenchError(
            "SYMLINK_BLOCKED",
            f"Refusing to read symlink directly: {candidate}",
            {"path": str(candidate)},
        )

    resolved = candidate.resolve(strict=False)
    try:
        rel = resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise WorkbenchError(
            "SCOPE_VIOLATION",
            f"Path '{target_path}' escapes project root '{root_resolved}'. Never scan outside the active repository.",
            {"project_root": str(root_resolved), "attempted_path": str(resolved)},
        ) from exc

    for part in rel.parts:
        if part in {".ssh", ".aws", ".gnupg"}:
            raise WorkbenchError(
                "SENSITIVE_DIR_BLOCKED",
                f"Access to sensitive directory '{part}' is prohibited.",
                {"path": str(rel)},
            )

    filename = resolved.name
    for pattern in SENSITIVE_FILE_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            raise WorkbenchError(
                "SENSITIVE_FILE_BLOCKED",
                f"Access to sensitive file '{filename}' is prohibited.",
                {"path": str(rel)},
            )

    return resolved


def is_binary_bytes(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    non_text = sum(1 for b in sample if b < 9 or (13 < b < 32))
    return (non_text / len(sample)) > 0.30


def check_public_ip(hostname: str) -> None:
    """Block localhost, private networks, link-local, and metadata IPs (SSRF guard)."""
    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise WorkbenchError("PRIVATE_HOST_BLOCKED", f"Host '{hostname}' is local and blocked.")
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise WorkbenchError("DNS_RESOLUTION_FAILED", f"Could not resolve host '{hostname}': {exc}") from exc

    for info in infos:
        ip_str = info[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            raise WorkbenchError(
                "PRIVATE_IP_BLOCKED",
                f"Host '{hostname}' resolved to non-public IP '{ip_str}'. Refusing connection.",
                {"hostname": hostname, "ip": ip_str},
            )


# ============================================================================
# Subcommand Implementations
# ============================================================================


def cmd_advise_intake(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    intake_path = state_dir / "advisory_intake.json"
    record = {
        "question": args.question.strip(),
        "context_summary": (args.context or "").strip(),
        "constraints": [c.strip() for c in (args.constraint or []) if c.strip()],
        "non_goals": [n.strip() for n in (args.non_goal or []) if n.strip()],
        "mode": args.mode,
        "requires_repo_inspection": bool(args.requires_repo_inspection),
        "created_at": utc_now_iso(),
    }
    if not record["question"]:
        raise WorkbenchError("EMPTY_QUESTION", "Advisory question cannot be empty.")
    save_json(intake_path, record)
    return {
        "status": "OK",
        "artifact": str(intake_path),
        "policy": (
            "CONVERSATION_FIRST: Do not scan local files unless requires_repo_inspection=true "
            "and the user named a target path or error."
        ),
        "intake": record,
    }


def cmd_decision_score(args: argparse.Namespace) -> Dict[str, Any]:
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        raise WorkbenchError("FILE_NOT_FOUND", f"Decision spec file not found: {spec_path}")
    spec = load_json(spec_path, {})
    criteria = spec.get("criteria", [])
    options = spec.get("options", [])
    if not criteria or not options:
        raise WorkbenchError(
            "INVALID_DECISION_SPEC",
            "Decision spec must include non-empty 'criteria' and 'options' lists.",
        )

    total_weight = sum(float(c.get("weight", 0)) for c in criteria)
    if total_weight <= 0:
        raise WorkbenchError("INVALID_WEIGHTS", "Sum of criterion weights must be > 0.")

    scored_options = []
    for opt in options:
        opt_name = opt.get("name", "Unnamed")
        scores = opt.get("scores", {})
        hard_fails = []
        weighted_sum = 0.0
        unknown_criteria = []
        breakdown = {}

        for crit in criteria:
            c_id = crit["id"]
            weight = float(crit.get("weight", 0)) / total_weight
            min_pass = crit.get("min_score")
            raw_val = scores.get(c_id)
            if raw_val is None or raw_val == "unknown":
                unknown_criteria.append(c_id)
                # Conservative neutral score for unknown (5.0 on 0-10 scale)
                numeric_val = 5.0
            else:
                numeric_val = float(raw_val)
                if min_pass is not None and numeric_val < float(min_pass):
                    hard_fails.append(f"{c_id} ({numeric_val} < min {min_pass})")

            weighted_sum += weight * numeric_val
            breakdown[c_id] = {
                "raw": raw_val if raw_val is not None else "unknown",
                "normalized_weight": round(weight, 4),
                "weighted_contribution": round(weight * numeric_val, 4),
            }

        scored_options.append(
            {
                "name": opt_name,
                "weighted_score": round(weighted_sum, 3),
                "disqualified": len(hard_fails) > 0,
                "disqualification_reasons": hard_fails,
                "unknown_criteria": unknown_criteria,
                "breakdown": breakdown,
                "risks": opt.get("risks", []),
            }
        )

    scored_options.sort(key=lambda x: (not x["disqualified"], x["weighted_score"]), reverse=True)
    eligible = [o for o in scored_options if not o["disqualified"]]
    recommended = eligible[0]["name"] if eligible else None

    result = {
        "status": "OK",
        "title": spec.get("title", "Decision Evaluation"),
        "recommended_option": recommended,
        "ranked_options": scored_options,
        "evaluated_at": utc_now_iso(),
    }
    result["sensitivity"] = decision_sensitivity(spec)
    if args.output:
        save_json(Path(args.output), result)
    return result


def cmd_scope_read(args: argparse.Namespace) -> Dict[str, Any]:
    project_root = Path(args.project_root)
    if not project_root.exists() or not project_root.is_dir():
        raise WorkbenchError("INVALID_PROJECT_ROOT", f"Project root does not exist: {project_root}")

    resolved = validate_scoped_path(project_root, Path(args.file))
    if args.debug_scope:
        enforce_debug_target(Path(args.state_dir), project_root, resolved)
    if not resolved.exists() or not resolved.is_file():
        raise WorkbenchError("FILE_NOT_FOUND", f"File not found inside project scope: {args.file}")

    size = resolved.stat().st_size
    if size > MAX_FILE_BYTES:
        raise WorkbenchError(
            "FILE_TOO_LARGE",
            f"File exceeds {MAX_FILE_BYTES} bytes ({size} bytes). Use narrow line ranges.",
            {"size": size, "max_bytes": MAX_FILE_BYTES},
        )

    raw_bytes = resolved.read_bytes()
    if is_binary_bytes(raw_bytes[:4096]):
        raise WorkbenchError("BINARY_FILE_BLOCKED", f"Refusing to read binary file: {args.file}")

    text = raw_bytes.decode("utf-8", errors="replace")
    all_lines = text.splitlines()
    start_line = max(1, int(args.start_line or 1))
    end_line = min(len(all_lines), int(args.end_line or len(all_lines)))
    if start_line > end_line and len(all_lines) > 0:
        raise WorkbenchError("INVALID_LINE_RANGE", f"start_line ({start_line}) > end_line ({end_line})")

    selected = all_lines[start_line - 1 : end_line]
    numbered = [f"{idx}: {line}" for idx, line in enumerate(selected, start=start_line)]
    return {
        "status": "OK",
        "project_root": str(project_root.resolve()),
        "file": str(resolved.relative_to(project_root.resolve())),
        "start_line": start_line,
        "end_line": end_line,
        "total_lines": len(all_lines),
        "sha256": sha256_text(text),
        "content": "\n".join(numbered),
    }


def cmd_scope_scan(args: argparse.Namespace) -> Dict[str, Any]:
    project_root = Path(args.project_root)
    if not project_root.exists() or not project_root.is_dir():
        raise WorkbenchError("INVALID_PROJECT_ROOT", f"Project root does not exist: {project_root}")
    root_resolved = project_root.resolve(strict=True)

    subpath = validate_scoped_path(root_resolved, Path(args.subpath or "."))
    if not subpath.exists() or not subpath.is_dir():
        raise WorkbenchError("SUBPATH_NOT_FOUND", f"Directory not found in scope: {args.subpath}")

    pattern = args.pattern
    regex = re.compile(pattern, re.IGNORECASE if args.ignore_case else 0) if pattern else None
    glob_filter = args.glob or "*"

    cap = max(1, min(int(getattr(args, "max_files", None) or MAX_SCAN_FILES), MAX_SCAN_FILES))
    matched_files: List[Dict[str, Any]] = []
    scanned_count = 0

    for dirpath, dirnames, filenames in os.walk(subpath, followlinks=False):
        if scanned_count >= cap:
            break
        # Prune forbidden directories in-place
        dirnames[:] = [
            d for d in sorted(dirnames) if d not in FORBIDDEN_DIR_NAMES and not d.startswith(".git")
        ]
        for fname in sorted(filenames):
            if scanned_count >= cap:
                break
            fpath = Path(dirpath) / fname
            if fpath.is_symlink():
                continue
            if not fpath.match(glob_filter):
                continue
            try:
                validate_scoped_path(root_resolved, fpath)
            except WorkbenchError:
                continue

            scanned_count += 1
            rel_str = str(fpath.relative_to(root_resolved))
            if regex is None:
                matched_files.append({"file": rel_str, "size": fpath.stat().st_size})
            else:
                if fpath.stat().st_size > MAX_FILE_BYTES:
                    continue
                raw = fpath.read_bytes()
                if is_binary_bytes(raw[:2048]):
                    continue
                lines = raw.decode("utf-8", errors="replace").splitlines()
                hits = []
                for idx, line in enumerate(lines, start=1):
                    if regex.search(line):
                        hits.append({"line": idx, "text": line[:200]})
                        if len(hits) >= 10:
                            break
                if hits:
                    matched_files.append({"file": rel_str, "matches": hits})

    return {
        "status": "OK",
        "project_root": str(root_resolved),
        "subpath": str(subpath.relative_to(root_resolved)),
        "scanned_files": scanned_count,
        "scan_cap": cap,
        "cap_reached": scanned_count >= cap,
        "results": matched_files,
    }


def cmd_debug_hypothesis(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    ledger_path = state_dir / "debug_ledger.json"
    ledger = load_json(
        ledger_path,
        {
            "symptom": "",
            "failed_attempts": 0,
            "circuit_breaker_tripped": False,
            "hypotheses": [],
        },
    )

    if args.symptom:
        ledger["symptom"] = args.symptom.strip()
    if args.target_file:
        ledger["target_files"] = sorted(set(ledger.get("target_files", [])) | {t.strip() for t in args.target_file if t.strip()})
    if args.repro:
        ledger["repro_command"] = args.repro.strip()

    if ledger["circuit_breaker_tripped"] and args.status == "PENDING":
        raise WorkbenchError(
            "CIRCUIT_BREAKER_TRIPPED",
            "Two hypotheses have already been falsified. Stop guessing, summarize the evidence, and escalate or request missing telemetry.",
            {"failed_attempts": ledger["failed_attempts"], "hypotheses": ledger["hypotheses"]},
        )

    if args.status is None:
        if not (args.symptom or args.target_file or args.repro):
            raise WorkbenchError("NOTHING_TO_RECORD", "Pass --status with a hypothesis, or --symptom/--target-file/--repro to record the case.")
        save_json(ledger_path, ledger)
        return {"status": "OK", "ledger_path": str(ledger_path), "case_recorded": True,
                "symptom": ledger.get("symptom", ""), "target_files": ledger.get("target_files", []),
                "repro_command": ledger.get("repro_command", ""),
                "next_action": "Run the repro, read the target with scope-read --debug-scope, then log H1 with --status PENDING.",
                "failed_attempts": ledger["failed_attempts"], "circuit_breaker_tripped": ledger["circuit_breaker_tripped"]}
    if not args.statement and not any(h["id"] == args.id for h in ledger["hypotheses"]):
        raise WorkbenchError("STATEMENT_REQUIRED", "A new hypothesis needs --statement (and --prediction).")

    hyp_id = args.id or f"H{len(ledger['hypotheses']) + 1}"
    existing = next((h for h in ledger["hypotheses"] if h["id"] == hyp_id), None)
    entry = {
        "id": hyp_id,
        "statement": args.statement or (existing["statement"] if existing else ""),
        "prediction": args.prediction or (existing["prediction"] if existing else ""),
        "test_command": args.test_command or (existing["test_command"] if existing else ""),
        "status": args.status,
        "evidence": args.evidence or (existing.get("evidence", "") if existing else ""),
        "updated_at": utc_now_iso(),
    }
    if existing:
        idx = ledger["hypotheses"].index(existing)
        ledger["hypotheses"][idx] = entry
    else:
        ledger["hypotheses"].append(entry)

    failed_count = sum(1 for h in ledger["hypotheses"] if h["status"] == "FALSIFIED")
    ledger["failed_attempts"] = failed_count
    ledger["circuit_breaker_tripped"] = failed_count >= 2

    save_json(ledger_path, ledger)
    return {
        "status": "OK",
        "ledger_path": str(ledger_path),
        "target_files": ledger.get("target_files", []),
        "next_action": (
            "STOP: run `debug-report` and hand the escalation brief to the user."
            if ledger["circuit_breaker_tripped"]
            else "Run the test command, then record CONFIRMED or FALSIFIED with --evidence."
        ),
        "failed_attempts": ledger["failed_attempts"],
        "circuit_breaker_tripped": ledger["circuit_breaker_tripped"],
        "active_hypothesis": entry,
    }


# ============================================================================
# Local Deep Research & Evidence Ledger Commands
# ============================================================================


def _load_ledger(state_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    ensure_state_dir(state_dir)
    path = state_dir / "research_ledger.json"
    ledger = load_json(
        path,
        {
            "topic": "",
            "mode": "deep-research",
            "max_queries": 12,
            "queries_executed": 0,
            "sub_questions": [],
            "entities": [],
            "query_log": [],
            "sources": {},
            "claims": [],
            "gaps": [],
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        },
    )
    return path, ledger


def cmd_research_init(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = Path(args.state_dir)
    path, _ = _load_ledger(state_dir)
    sub_questions = [
        {"id": f"Q{i+1}", "question": q.strip(), "status": "OPEN"}
        for i, q in enumerate(args.sub_question or [])
        if q.strip()
    ]
    entities = [e.strip() for e in (args.entity or []) if e.strip()]
    ledger = {
        "topic": args.topic.strip(),
        "mode": args.mode,
        "max_queries": int(args.max_queries),
        "queries_executed": 0,
        "sub_questions": sub_questions,
        "entities": entities,
        "fields": [f.strip() for f in (args.field or []) if f.strip()],
        "time_sensitive": bool(args.time_sensitive),
        "query_log": [],
        "sources": {},
        "claims": [],
        "gaps": [],
        "resolutions": {},
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    if not ledger["topic"]:
        raise WorkbenchError("EMPTY_TOPIC", "Research topic cannot be empty.")
    save_json(path, ledger)
    return {
        "status": "OK",
        "ledger_path": str(path),
        "topic": ledger["topic"],
        "max_queries": ledger["max_queries"],
        "sub_questions": sub_questions,
        "entities": entities,
    }


def cmd_research_log_query(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    if ledger["queries_executed"] >= ledger["max_queries"]:
        raise WorkbenchError(
            "QUERY_BUDGET_EXHAUSTED",
            f"Query budget reached ({ledger['queries_executed']}/{ledger['max_queries']}). Stop searching and synthesize findings or record remaining gaps.",
            {
                "queries_executed": ledger["queries_executed"],
                "max_queries": ledger["max_queries"],
            },
        )

    q_norm = " ".join(args.query.strip().lower().split())
    duplicate = any(
        " ".join(item["query"].lower().split()) == q_norm for item in ledger["query_log"]
    )
    if duplicate and not args.allow_duplicate:
        raise WorkbenchError(
            "DUPLICATE_QUERY",
            f"Query '{args.query}' was already executed in this session. Reformulate with distinct terms or facet filters.",
        )

    entry = {
        "id": f"QRY-{len(ledger['query_log']) + 1}",
        "query": args.query.strip(),
        "sub_question_id": args.sub_question_id or "",
        "tool_used": args.tool_used or "host-native-search",
        "executed_at": utc_now_iso(),
    }
    ledger["query_log"].append(entry)
    ledger["queries_executed"] = len(ledger["query_log"])
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "query_entry": entry,
        "queries_executed": ledger["queries_executed"],
        "queries_remaining": ledger["max_queries"] - ledger["queries_executed"],
    }


def cmd_research_add_source(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    raw_url = args.url.strip()
    if not raw_url:
        raise WorkbenchError("EMPTY_URL", "Source URL or URI cannot be empty.")

    canonical = canonicalize_url(raw_url) if raw_url.startswith(("http://", "https://")) else raw_url

    content_text = ""
    if args.content_file:
        cf = Path(args.content_file)
        if not cf.exists():
            raise WorkbenchError("FILE_NOT_FOUND", f"Content file not found: {cf}")
        content_text = cf.read_text(encoding="utf-8", errors="replace")
    elif args.excerpt:
        content_text = args.excerpt.strip()

    if not content_text:
        raise WorkbenchError(
            "EMPTY_SOURCE_CONTENT",
            "Source registration requires either --excerpt or --content-file from a fetched page. Search snippets alone are not authoritative.",
        )

    # Deduplicate by canonical URL if already present
    existing_id = None
    for sid, sdata in ledger["sources"].items():
        if sdata.get("canonical_url") == canonical:
            existing_id = sid
            break

    source_id = args.source_id or existing_id or f"S{len(ledger['sources']) + 1}"
    source_record = {
        "id": source_id,
        "url": raw_url,
        "canonical_url": canonical,
        "title": args.title.strip(),
        "publisher": (args.publisher or "").strip(),
        "published_date": (args.published_date or "unknown").strip(),
        "source_tier": args.tier,
        "content_sha256": sha256_text(content_text),
        "excerpt": content_text[:4000],
        "fetched_at": utc_now_iso(),
    }
    ledger["sources"][source_id] = source_record
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "source_id": source_id,
        "deduplicated": existing_id is not None,
        "canonical_url": canonical,
        "content_sha256": source_record["content_sha256"],
    }


def cmd_research_add_claim(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    source_ids = [s.strip() for s in (args.source_id or []) if s.strip()]
    if not source_ids:
        raise WorkbenchError("MISSING_SOURCE_ID", "Every claim must reference at least one registered --source-id.")

    missing = [sid for sid in source_ids if sid not in ledger["sources"]]
    if missing:
        raise WorkbenchError(
            "UNKNOWN_SOURCE_ID",
            f"Claim references unregistered source IDs: {missing}. Register fetched sources first.",
            {"missing_source_ids": missing},
        )

    quote = (args.quote or "").strip()
    if len(quote) < 10:
        raise WorkbenchError(
            "QUOTE_TOO_SHORT",
            "Every claim requires a verbatim supporting quote (--quote) of at least 10 characters from the fetched source.",
        )

    # Check if quote appears in at least one referenced source excerpt (unless overridden)
    quote_norm = " ".join(quote.lower().split())
    quote_verified_in_excerpt = any(
        quote_norm in " ".join(ledger["sources"][sid].get("excerpt", "").lower().split())
        for sid in source_ids
    )

    if not quote_verified_in_excerpt and not args.allow_unverified_quote:
        raise WorkbenchError(
            "QUOTE_NOT_IN_SOURCE",
            "The quote does not appear verbatim in the stored excerpt of any referenced source. "
            "Copy the exact sentence from the fetched page, re-register the source with a longer excerpt, "
            "or pass --allow-unverified-quote (the claim is then forced to LOW / PROVISIONAL).",
            {"source_ids": source_ids, "quote": quote},
        )
    confidence = args.confidence
    claim_status = args.status
    if not quote_verified_in_excerpt:
        confidence, claim_status = "LOW", "PROVISIONAL"

    claim_id = args.claim_id or f"C{len(ledger['claims']) + 1}"
    claim_record = {
        "id": claim_id,
        "sub_question_id": args.sub_question_id or "",
        "entity": (args.entity or "").strip(),
        "field": (args.field or "").strip(),
        "statement": args.statement.strip(),
        "value": (args.value or "").strip(),
        "source_ids": source_ids,
        "quote": quote,
        "quote_verified_in_excerpt": quote_verified_in_excerpt,
        "confidence": confidence,
        "status": claim_status,
        "created_at": utc_now_iso(),
    }
    ledger["claims"].append(claim_record)

    # Mark sub-question as ANSWERED if specified
    if args.sub_question_id:
        for sq in ledger["sub_questions"]:
            if sq["id"] == args.sub_question_id:
                sq["status"] = "ANSWERED"

    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "claim_id": claim_id,
        "quote_verified_in_excerpt": quote_verified_in_excerpt,
        "claim": claim_record,
    }


def cmd_research_add_gap(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    gap_id = args.gap_id or f"G{len(ledger['gaps']) + 1}"
    gap_record = {
        "id": gap_id,
        "sub_question_id": args.sub_question_id or "",
        "entity": (args.entity or "").strip(),
        "field": (args.field or "").strip(),
        "description": args.description.strip(),
        "queries_tried": [q.strip() for q in (args.query_tried or []) if q.strip()],
        "reason": args.reason,
        "created_at": utc_now_iso(),
    }
    ledger["gaps"].append(gap_record)
    if args.sub_question_id:
        for sq in ledger["sub_questions"]:
            if sq["id"] == args.sub_question_id and sq["status"] == "OPEN":
                sq["status"] = "GAP_RECORDED"
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {"status": "OK", "gap_id": gap_id, "gap": gap_record}


def cmd_research_status(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    sources = ledger["sources"]
    claims = ledger["claims"]
    gaps = ledger["gaps"]
    sub_questions = ledger["sub_questions"]

    # Detect contradictions: same (entity, field) with non-empty distinct values
    by_entity_field: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for c in claims:
        ent = c.get("entity", "")
        fld = c.get("field", "")
        if ent and fld:
            by_entity_field.setdefault((ent, fld), []).append(c)

    contradictions = []
    for (ent, fld), group in by_entity_field.items():
        if f"{ent}::{fld}" in ledger.get("resolutions", {}):
            continue
        active = [g for g in group if not g.get("superseded_by")]
        distinct_vals = {}
        for g in active:
            if g.get("value", ""):
                distinct_vals.setdefault(normalize_value(g["value"]), g["value"])
        if len(distinct_vals) > 1:
            distinct_vals = set(distinct_vals.values())
            contradictions.append(
                {
                    "entity": ent,
                    "field": fld,
                    "values": sorted(distinct_vals),
                    "claim_ids": [g["id"] for g in group],
                }
            )

    unresolved_sq = [
        sq["id"] for sq in sub_questions if sq["status"] not in {"ANSWERED", "GAP_RECORDED"}
    ]
    ready_to_synthesize = (
        len(unresolved_sq) == 0 and (len(claims) > 0 or len(gaps) > 0) and not contradictions
    )
    coverage = compute_coverage(ledger)

    return {
        "status": "OK",
        "ledger_path": str(path),
        "topic": ledger["topic"],
        "queries_executed": ledger["queries_executed"],
        "max_queries": ledger["max_queries"],
        "sources_count": len(sources),
        "claims_count": len(claims),
        "gaps_count": len(gaps),
        "unresolved_sub_questions": unresolved_sq,
        "contradictions": contradictions,
        "resolved_contradictions": sorted(ledger.get("resolutions", {}).keys()),
        "weak_sub_questions": [c["id"] for c in coverage if c["coverage"] in {"WEAK", "OPEN"}],
        "ready_to_synthesize": ready_to_synthesize,
    }


def cmd_fetch_url(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.allow_network:
        raise WorkbenchError(
            "NETWORK_NOT_APPROVED",
            "Network fetch requires explicit --allow-network flag. Prefer host-native fetch tools first.",
        )

    raw_url = args.url.strip()
    parsed = urllib.parse.urlsplit(raw_url)
    if parsed.scheme.lower() != "https":
        raise WorkbenchError("HTTPS_REQUIRED", f"Only https:// URLs are permitted (got '{parsed.scheme}').")
    if not parsed.hostname:
        raise WorkbenchError("INVALID_URL", f"Missing hostname in URL: {raw_url}")

    check_public_ip(parsed.hostname)

    state_dir = ensure_state_dir(Path(args.state_dir))
    cache_dir = state_dir / "fetch_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    canonical = canonicalize_url(raw_url)
    cache_key = sha256_text(canonical)[:24]
    cache_file = cache_dir / f"{cache_key}.json"

    if cache_file.exists() and not args.no_cache:
        cached = load_json(cache_file, {})
        cached["from_cache"] = True
        return cached

    req = urllib.request.Request(
        raw_url,
        headers={
            "User-Agent": "LocalAdvisorWorkbench/2.0 (+https://localhost; research-ledger)",
            "Accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.5",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=float(args.timeout)) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw_bytes = resp.read(MAX_FETCH_BYTES + 1)
            if len(raw_bytes) > MAX_FETCH_BYTES:
                raise WorkbenchError("RESPONSE_TOO_LARGE", f"Response exceeded {MAX_FETCH_BYTES} bytes.")
            charset = resp.headers.get_content_charset() or "utf-8"
            body = raw_bytes.decode(charset, errors="replace")
    except urllib.error.URLError as exc:
        raise WorkbenchError("FETCH_FAILED", f"Failed to fetch {raw_url}: {exc}") from exc

    title = parsed.hostname
    if "html" in content_type.lower() or "<html" in body[:500].lower():
        parser = HTMLTextExtractor()
        parser.feed(body)
        cleaned = parser.get_text()
        if parser.title:
            title = parser.title
    else:
        cleaned = body.strip()

    payload = {
        "status": "OK",
        "url": raw_url,
        "canonical_url": canonical,
        "title": title,
        "content_type": content_type,
        "content_sha256": sha256_text(cleaned),
        "text_length": len(cleaned),
        "excerpt": cleaned[: int(args.max_chars)],
        "fetched_at": utc_now_iso(),
        "from_cache": False,
    }
    save_json(cache_file, payload)
    return payload


def cmd_audit_report(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    sources = ledger.get("sources", {})
    claims = ledger.get("claims", [])

    issues: List[Dict[str, Any]] = []

    # 1. Check ledger internal integrity
    for c in claims:
        cid = c.get("id", "?")
        sids = c.get("source_ids", [])
        if not sids:
            issues.append({"type": "CLAIM_WITHOUT_SOURCE", "claim_id": cid})
        for sid in sids:
            if sid not in sources:
                issues.append({"type": "DANGLING_SOURCE_REF", "claim_id": cid, "source_id": sid})
        if not c.get("quote") or len(c.get("quote", "").strip()) < 10:
            issues.append({"type": "MISSING_OR_WEAK_QUOTE", "claim_id": cid})
        if c.get("confidence") == "HIGH" and not c.get("quote_verified_in_excerpt"):
            issues.append(
                {
                    "type": "HIGH_CONFIDENCE_UNVERIFIED_QUOTE",
                    "claim_id": cid,
                    "detail": "Quote was not matched verbatim in stored source excerpt.",
                }
            )

    # 2. If a markdown report is provided, audit inline links and prohibited generic anchors
    report_findings: Dict[str, Any] = {}
    if args.report_file:
        rp = Path(args.report_file)
        if not rp.exists():
            raise WorkbenchError("FILE_NOT_FOUND", f"Report file not found: {rp}")
        md = rp.read_text(encoding="utf-8", errors="replace")
        link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)")
        matches = link_pattern.findall(md)

        registered_canonicals = {
            sdata.get("canonical_url") for sdata in sources.values() if sdata.get("canonical_url")
        }
        generic_anchors = {"source", "link", "here", "url", "website", "article", "click here"}

        unregistered_urls = []
        bad_anchors = []
        for anchor, url in matches:
            a_clean = anchor.strip().lower()
            if a_clean in generic_anchors or a_clean.startswith("http"):
                bad_anchors.append({"anchor": anchor, "url": url})
            c_url = canonicalize_url(url)
            if c_url not in registered_canonicals:
                unregistered_urls.append({"anchor": anchor, "url": url, "canonical": c_url})

        for item in bad_anchors:
            issues.append({"type": "GENERIC_OR_RAW_ANCHOR", **item})
        for item in unregistered_urls:
            issues.append({"type": "UNREGISTERED_REPORT_URL", **item})

        content_issues = audit_report_content(md, ledger, int(args.max_age_days))
        issues.extend(content_issues)
        report_findings = {
            "report_file": str(rp),
            "inline_citations_count": len(matches),
            "generic_anchor_violations": len(bad_anchors),
            "unregistered_url_violations": len(unregistered_urls),
            "content_issues": len(content_issues),
        }

    for item in issues:
        item.setdefault("severity", "warning" if item["type"] in AUDIT_WARNING_TYPES else "blocking")
    blocking = [i for i in issues if i["severity"] == "blocking"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    passed = not blocking and not (args.strict and warnings)
    return {
        "status": "PASS" if passed else "FAIL",
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
        "ledger_path": str(path),
        "sources_checked": len(sources),
        "claims_checked": len(claims),
        "report_audit": report_findings,
        "issues_count": len(issues),
        "issues": issues,
        "audited_at": utc_now_iso(),
    }


def cmd_verify_delivery(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    artifacts_status = []
    all_passed = True

    for art in args.artifact or []:
        p = Path(art)
        exists = p.exists() and p.is_file()
        size = p.stat().st_size if exists else 0
        ok = exists and size > 0
        if not ok:
            all_passed = False
        artifacts_status.append(
            {
                "artifact": str(p),
                "exists": exists,
                "size_bytes": size,
                "level": "L1_ARTIFACT_PRESENT" if ok else "MISSING_OR_EMPTY",
            }
        )

    checks: List[Tuple[str, str]] = [("L3", c) for c in (args.command or [])]
    for spec in args.check or []:
        level, sep, cmd_str = spec.partition(":")
        level = level.strip().upper()
        if not sep or level not in VERIFY_LEVELS[1:] or level == "L1" or not cmd_str.strip():
            raise WorkbenchError(
                "INVALID_CHECK",
                f"--check must look like 'L2:<command>', 'L3:<command>' or 'L4:<command>' (got {spec!r}). "
                "Use --artifact for L1.",
            )
        checks.append((level, cmd_str.strip()))
    if not artifacts_status and not checks:
        raise WorkbenchError(
            "NOTHING_TO_VERIFY",
            "Declare at least one --artifact, --command or --check. A delivery with no observable check is L0 (claimed only).",
        )

    cmd_results = []
    for level, cmd_str in sorted(checks, key=lambda x: x[0]):
        res = run_observed(cmd_str, int(args.timeout), args.cwd)
        res["level"] = level
        if not res["passed"]:
            all_passed = False
        cmd_results.append(res)

    achieved, not_checked = ladder_level(artifacts_status, cmd_results)
    if not all_passed:
        overall_level = "VERIFICATION_FAILED"
    else:
        overall_level = {
            "L4": "L4_ACCEPTANCE_VERIFIED",
            "L3": "L3_EXECUTION_VERIFIED",
            "L2": "L2_STATIC_VERIFIED",
            "L1": "L1_ARTIFACT_EXISTENCE_ONLY",
        }.get(achieved, "L0_UNVERIFIED")
    status_ok = all_passed
    if args.require and VERIFY_LEVELS.index(achieved) < VERIFY_LEVELS.index(args.require):
        status_ok = False

    record = {
        "status": "PASS" if status_ok else "FAIL",
        "verification_level": overall_level,
        "achieved_level": achieved,
        "required_level": args.require or "",
        "levels_not_checked": not_checked,
        "git": git_snapshot(args.cwd),
        "artifacts": artifacts_status,
        "commands": cmd_results,
        "not_run": args.not_run or [],
        "verified_at": utc_now_iso(),
    }
    save_json(state_dir / "delivery_verification.json", record)
    return record


def cmd_handoff_pack(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    handoff_file = Path(args.output or (state_dir / "HANDOFF.md"))

    _, research = _load_ledger(state_dir)
    debug_ledger = load_json(state_dir / "debug_ledger.json", {})
    delivery = load_json(state_dir / "delivery_verification.json", {})

    completed = [c.strip() for c in (args.completed or []) if c.strip()]
    next_steps = [n.strip() for n in (args.next_step or []) if n.strip()]
    blockers = [b.strip() for b in (args.blocker or []) if b.strip()]

    lines = [
        f"# Session Handoff: {args.title}",
        "",
        f"- **Generated At**: `{utc_now_iso()}`",
        f"- **Current Status**: `{args.session_status}`",
        f"- **State Directory**: `{state_dir}`",
        f"- **Git HEAD**: `{(git_snapshot(None).get('head') or 'none')[:12]}`"
        + (" (uncommitted changes)" if git_snapshot(None).get("dirty") else ""),
        "",
        "## 1. Objective & Current State",
        "",
        args.summary.strip(),
        "",
        "## 2. Completed Work",
        "",
    ]
    if completed:
        lines.extend(f"- [x] {item}" for item in completed)
    else:
        lines.append("- None recorded.")

    lines.extend(["", "## 3. Pending Next Steps", ""])
    if next_steps:
        lines.extend(f"- [ ] {item}" for item in next_steps)
    else:
        lines.append("- None remaining.")

    lines.extend(["", "## 4. Active Blockers & Constraints", ""])
    if blockers:
        lines.extend(f"- **BLOCKER**: {item}" for item in blockers)
    else:
        lines.append("- No active blockers.")

    lines.extend(
        [
            "",
            "## 5. Evidence & Verification Snapshot",
            "",
            f"- **Research Topic**: {research.get('topic') or 'N/A'}",
            f"- **Queries Executed**: {research.get('queries_executed', 0)} / {research.get('max_queries', 0)}",
            f"- **Registered Sources**: {len(research.get('sources', {}))}",
            f"- **Extracted Claims**: {len(research.get('claims', []))}",
            f"- **Recorded Knowledge Gaps**: {len(research.get('gaps', []))}",
            f"- **Debug Failed Hypotheses**: {debug_ledger.get('failed_attempts', 0)} (Circuit Breaker: {debug_ledger.get('circuit_breaker_tripped', False)})",
            f"- **Last Delivery Verification Level**: {delivery.get('verification_level', 'NOT_RUN')}"
            + (f" (achieved `{delivery['achieved_level']}`)" if delivery.get("achieved_level") else ""),
            "",
            "## 6. Decisions & Open Questions",
            "",
        ]
    )
    decisions = [d.strip() for d in (args.decision or []) if d.strip()]
    questions = [q.strip() for q in (args.open_question or []) if q.strip()]
    lines.extend(f"- **DECISION**: {d}" for d in decisions)
    lines.extend(f"- **OPEN**: {q}" for q in questions)
    if not decisions and not questions:
        lines.append("- None recorded.")
    lines.extend(
        [
            "",
            "## 7. Resume Instructions",
            "",
            "1. Read this file completely before touching anything.",
            f"2. Run `python3 <skill>/scripts/workbench.py --state-dir {state_dir} handoff-check --file {handoff_file}`.",
            "3. Trust completed work only up to the verification level shown in section 5.",
            "4. Start with the first unchecked item in section 3. Do not redo section 2.",
            "",
        ]
    )

    handoff_file.parent.mkdir(parents=True, exist_ok=True)
    handoff_file.write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": "OK",
        "handoff_file": str(handoff_file),
        "session_status": args.session_status,
    }


# ============================================================================
# v2.1 extensions. Same contract as the core: offline, deterministic, JSON out.
# ============================================================================

VERIFY_LEVELS = ["L0", "L1", "L2", "L3", "L4"]
VERIFY_LEVEL_MEANING = {
    "L0": "claimed only - nothing observable was checked",
    "L1": "artifact exists and is non-empty",
    "L2": "static checks pass (syntax, lint, type-check, build)",
    "L3": "execution verified (tests or real commands exit 0)",
    "L4": "acceptance verified (end-to-end / target environment / acceptance criteria)",
}
AUDIT_WARNING_TYPES = {"OVERCLAIM_LANGUAGE", "STALE_CURRENTNESS_CLAIM", "UNDATED_EVIDENCE", "SINGLE_SOURCE_RELIANCE"}

_SLD = {"co", "com", "org", "net", "gov", "edu", "ac", "bel", "k12", "gen", "web", "av", "biz", "info", "tv", "ne", "or"}
_HIGH_TRUST_SUFFIX = (".gov", ".gov.tr", ".gov.uk", ".edu", ".edu.tr", ".ac.uk", ".int", ".mil", "europa.eu")
_STANDARD_HOSTS = ("ietf.org", "rfc-editor.org", "w3.org", "iso.org", "ecma-international.org", "unicode.org",
                   "whatwg.org", "oecd.org", "worldbank.org", "imf.org", "who.int")
_LOW_TRUST_HOSTS = ("reddit.com", "quora.com", "news.ycombinator.com", "stackexchange.com", "stackoverflow.com",
                    "x.com", "twitter.com", "facebook.com", "linkedin.com", "tiktok.com", "youtube.com",
                    "pinterest.com", "medium.com", "substack.com", "dev.to", "blogspot.com", "wordpress.com")
_TIER_BASE = {"PRIMARY": 4.0, "SECONDARY": 3.0, "TERTIARY": 2.0}

OVERCLAIM_RE = re.compile(
    r"\b(always|never|guarantee[sd]?|proven|proves|definitive(?:ly)?|certainly|undoubtedly|unquestionably|"
    r"the (?:best|fastest|cheapest|only|safest|most secure)|everyone|nobody|no one|zero risk|risk[- ]free|"
    r"impossible|all (?:users|companies|cases|teams)|will (?:definitely|certainly|surely)|100 ?%)",
    re.IGNORECASE,
)
CURRENTNESS_RE = re.compile(r"\b(currently|current|latest|as of|today|now|newest|most recent|this year|right now)\b", re.I)
YEAR_RE = re.compile(r"\b(19[5-9]\d|20\d\d|2100)\b")
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)")
EXEMPT_SECTION_RE = re.compile(r"(method|scope|knowledge gaps?|gap register|appendix|metadata|verification|changelog)", re.I)


def normalize_value(value: Any) -> str:
    s = " ".join(str(value or "").casefold().split())
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    return s.strip(" .;:")


def registrable_domain(url: str) -> str:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if re.fullmatch(r"[\d.]+", host):
        return host
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in _SLD and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def parse_loose_date(value: str) -> Optional[dt.date]:
    value = (value or "").strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
        try:
            return dt.datetime.strptime(value[:n], fmt).date()
        except ValueError:
            continue
    return None


def score_source(src: Dict[str, Any], time_sensitive: bool, today: Optional[dt.date] = None) -> Tuple[float, List[str]]:
    """Deterministic 0-5 quality score. Rules are documented in deep-research/references/source-quality.md."""
    today = today or dt.date.today()
    tier = src.get("source_tier", "SECONDARY")
    score = _TIER_BASE.get(tier, 2.0)
    reasons = [f"tier {tier} base {score:g}"]
    url = src.get("canonical_url") or src.get("url") or ""
    host = (urllib.parse.urlsplit(url).hostname or "").lower() if url.startswith("http") else ""
    if host:
        if host.endswith(_HIGH_TRUST_SUFFIX) or any(host == h or host.endswith("." + h) for h in _STANDARD_HOSTS):
            score += 1.0
            reasons.append("government/academic/standards domain +1")
        elif host.startswith(("docs.", "developer.", "developers.")) and tier == "PRIMARY":
            score += 0.5
            reasons.append("official documentation host +0.5")
        if any(host == h or host.endswith("." + h) for h in _LOW_TRUST_HOSTS):
            score -= 1.5
            reasons.append("forum/social/self-publishing host -1.5")
    else:
        reasons.append("local document (no domain adjustment)")
    excerpt = (src.get("excerpt") or "").strip()
    if len(excerpt) < 80:
        score -= 0.5
        reasons.append("excerpt shorter than 80 chars -0.5")
    published = parse_loose_date(src.get("published_date", ""))
    if time_sensitive:
        if not published:
            score -= 0.5
            reasons.append("undated on a time-sensitive topic -0.5")
        else:
            age = (today - published).days
            if age > 730:
                score -= 1.0
                reasons.append(f"{age} days old on a time-sensitive topic -1")
            elif age > 365:
                score -= 0.5
                reasons.append(f"{age} days old on a time-sensitive topic -0.5")
    score = max(0.0, min(5.0, score))
    return round(score, 2), reasons


def compute_coverage(ledger: Dict[str, Any], min_sources: int = 2) -> List[Dict[str, Any]]:
    sources = ledger.get("sources", {})
    out = []
    for sq in ledger.get("sub_questions", []):
        claims = [c for c in ledger.get("claims", []) if c.get("sub_question_id") == sq["id"] and not c.get("superseded_by")]
        sids = sorted({sid for c in claims for sid in c.get("source_ids", []) if sid in sources})
        domains = sorted({registrable_domain(sources[s]["canonical_url"]) or sources[s]["canonical_url"] for s in sids})
        verified = [c for c in claims if c.get("quote_verified_in_excerpt") and c.get("status") == "VERIFIED"]
        tiers = {sources[s].get("source_tier") for s in sids}
        best = max((sources[s].get("quality_score", score_source(sources[s], ledger.get("time_sensitive", False))[0]) for s in sids), default=0)
        gaps = [g["id"] for g in ledger.get("gaps", []) if g.get("sub_question_id") == sq["id"]]
        reasons, actions = [], []
        if not claims and gaps:
            cov = "GAP_RECORDED"
        elif not claims:
            cov = "OPEN"
            reasons.append("no claims")
            actions.append("search, fetch, register the source, then research-add-claim")
        else:
            cov = "STRONG"
            if len(domains) < min_sources:
                cov = "WEAK"
                reasons.append(f"{len(domains)}/{min_sources} independent domains")
                actions.append("find an independent source from a different organisation")
            if "PRIMARY" not in tiers and best < 4:
                cov = "WEAK"
                reasons.append("no primary source and best quality < 4")
                actions.append("look for the official document, dataset, filing, changelog or standard")
            if not verified:
                cov = "WEAK"
                reasons.append("no VERIFIED claim with a quote matched in the excerpt")
                actions.append("re-register the source with a longer excerpt that contains the quote")
        out.append({
            "id": sq["id"], "question": sq["question"], "coverage": cov, "claims": len(claims),
            "verified_claims": len(verified), "sources": sids, "independent_domains": domains,
            "best_quality": best, "gaps": gaps, "reasons": reasons, "next_actions": actions,
        })
    return out


def cmd_research_score(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    ts = bool(args.time_sensitive or ledger.get("time_sensitive"))
    rows = []
    for sid, src in ledger["sources"].items():
        score, reasons = score_source(src, ts)
        src["quality_score"], src["quality_reasons"] = score, reasons
        rows.append({"source_id": sid, "domain": registrable_domain(src.get("canonical_url", "")), "tier": src.get("source_tier"),
                     "published_date": src.get("published_date"), "quality_score": score, "reasons": reasons})
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    rows.sort(key=lambda r: -r["quality_score"])
    return {"status": "OK", "time_sensitive": ts, "sources": rows,
            "low_quality": [r["source_id"] for r in rows if r["quality_score"] < 2.5]}


def cmd_research_gaps(args: argparse.Namespace) -> Dict[str, Any]:
    _, ledger = _load_ledger(Path(args.state_dir))
    cov = compute_coverage(ledger, int(args.min_sources))
    weak = [c["id"] for c in cov if c["coverage"] in {"WEAK", "OPEN"}]
    budget_left = ledger.get("max_queries", 0) - ledger.get("queries_executed", 0)
    if weak and budget_left <= 0:
        advice = "Query budget exhausted: record remaining weak/open sub-questions with research-add-gap (reason BUDGET_REACHED) and synthesize."
    elif weak:
        advice = f"{len(weak)} sub-question(s) need more evidence; {budget_left} queries left."
    else:
        advice = "Coverage sufficient: resolve contradictions (research-status), build the evidence pack, synthesize, then audit-report."
    status = "FAIL" if (args.strict and weak) else "OK"
    return {"status": status, "min_independent_sources": int(args.min_sources), "queries_remaining": budget_left,
            "weak_or_open": weak, "coverage": cov, "advice": advice}


def cmd_research_resolve(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_ledger(Path(args.state_dir))
    claims = {c["id"]: c for c in ledger["claims"]}
    win = claims.get(args.winner_claim)
    if not win:
        raise WorkbenchError("UNKNOWN_CLAIM", f"Claim {args.winner_claim} is not in the ledger.")
    if win.get("entity") != args.entity or win.get("field") != args.field:
        raise WorkbenchError("CLAIM_MISMATCH", f"{args.winner_claim} is ({win.get('entity')}, {win.get('field')}), not ({args.entity}, {args.field}).")
    if len(args.reason.strip()) < 15:
        raise WorkbenchError("REASON_TOO_SHORT", "Explain the resolution (scope, date, edition, primary vs secondary) in at least 15 characters.")
    losers = []
    for c in ledger["claims"]:
        if c["id"] != win["id"] and c.get("entity") == args.entity and c.get("field") == args.field \
                and normalize_value(c.get("value")) != normalize_value(win.get("value")):
            c["status"], c["superseded_by"] = "CONTESTED", win["id"]
            losers.append(c["id"])
    ledger.setdefault("resolutions", {})[f"{args.entity}::{args.field}"] = {
        "winner_claim": win["id"], "value": win.get("value"), "losing_claims": losers,
        "reason": args.reason.strip(), "resolved_at": utc_now_iso()}
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {"status": "OK", "entity": args.entity, "field": args.field, "winner_claim": win["id"],
            "value": win.get("value"), "superseded_claims": losers}


def _anchor(src: Dict[str, Any]) -> str:
    name = (src.get("publisher") or src.get("title") or registrable_domain(src.get("url", "")) or src.get("id", "")).strip()
    return name.replace("[", "(").replace("]", ")").replace("|", "/")


def cmd_research_pack(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = Path(args.state_dir)
    _, ledger = _load_ledger(state_dir)
    src = ledger["sources"]
    out = Path(args.output or state_dir / "evidence_pack.md")
    L = [f"# Evidence Pack: {ledger.get('topic') or 'untitled'}", "",
         f"- Generated: `{utc_now_iso()}` | sources {len(src)} | claims {len(ledger['claims'])} | gaps {len(ledger['gaps'])}",
         "- Use only these claims in the synthesis. Cite with the anchor and URL shown. Quotes are verbatim.", ""]
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for c in ledger["claims"]:
        groups.setdefault(c.get("sub_question_id") or "-", []).append(c)
    order = [sq["id"] for sq in ledger["sub_questions"]] + [k for k in groups if k not in {sq["id"] for sq in ledger["sub_questions"]}]
    sq_text = {sq["id"]: sq["question"] for sq in ledger["sub_questions"]}
    for sid in order:
        L.append(f"## {sid}: {sq_text.get(sid, '(unassigned)')}")
        items = groups.get(sid, [])
        if not items:
            L.append("- No claims. Treat as a gap.")
        for c in items:
            cites = ", ".join(f"[{_anchor(src[s])}]({src[s]['url']})" for s in c["source_ids"] if s in src)
            flag = "" if c.get("status") == "VERIFIED" and c.get("quote_verified_in_excerpt") else f" **[{c.get('status')}/{c.get('confidence')}]**"
            if c.get("superseded_by"):
                flag = f" **[SUPERSEDED by {c['superseded_by']} - do not use]**"
            L.append(f"- **{c['id']}**{flag} {c['statement']} {cites}")
            L.append(f"  > {c['quote']}")
        for g in [g for g in ledger["gaps"] if (g.get("sub_question_id") or "-") == sid]:
            L.append(f"- **{g['id']} GAP** ({g['reason']}): {g['description']}")
        L.append("")
    if ledger.get("resolutions"):
        L.append("## Resolved contradictions")
        for k, r in ledger["resolutions"].items():
            L.append(f"- `{k}` -> {r['winner_claim']} = {r['value']!r}: {r['reason']}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return {"status": "OK", "evidence_pack": str(out), "claims": len(ledger["claims"]), "gaps": len(ledger["gaps"])}


def cmd_wide_table(args: argparse.Namespace) -> Dict[str, Any]:
    _, ledger = _load_ledger(Path(args.state_dir))
    src = ledger["sources"]
    entities = [e for e in (args.entity or ledger.get("entities") or []) if e]
    fields = [f for f in (args.field or ledger.get("fields") or []) if f]
    if not fields:
        fields = sorted({c["field"] for c in ledger["claims"] if c.get("field")})
    if not entities or not fields:
        raise WorkbenchError("EMPTY_MATRIX", "Provide entities/fields via research-init --entity/--field or wide-table --entity/--field.")
    counts = {"verified": 0, "unverified": 0, "conflict": 0, "na": 0, "missing": 0}
    rows_md, rows_csv, problems = [], [], []
    for e in entities:
        cells = []
        for f in fields:
            claims = [c for c in ledger["claims"] if c.get("entity") == e and c.get("field") == f and not c.get("superseded_by")]
            gaps = [g for g in ledger["gaps"] if g.get("entity") == e and g.get("field") == f]
            good = [c for c in claims if c.get("status") == "VERIFIED" and c.get("quote_verified_in_excerpt")]
            values = {normalize_value(c.get("value") or c["statement"]) for c in good}
            if good and len(values) == 1:
                c = good[0]
                links = ", ".join(f"[{_anchor(src[s])}]({src[s]['url']})" for s in c["source_ids"] if s in src)
                text, state = f"{c.get('value') or c['statement']} ({links})", "verified"
            elif good:
                text, state = "CONFLICT: " + " / ".join(sorted({c.get("value") or c["statement"] for c in good})), "conflict"
                problems.append(f"{e} / {f}: conflicting values - run research-resolve")
            elif claims:
                c = claims[0]
                text, state = f"{c.get('value') or c['statement']} (unverified)", "unverified"
                problems.append(f"{e} / {f}: only unverified claims")
            elif gaps:
                text, state = "n.a.", "na"
            else:
                text, state = "?", "missing"
                problems.append(f"{e} / {f}: no claim and no recorded gap")
            counts[state] += 1
            cells.append(text.replace("|", "/"))
            rows_csv.append([e, f, text, state])
        rows_md.append(f"| **{e}** | " + " | ".join(cells) + " |")
    md = ["| Entity | " + " | ".join(fields) + " |", "|---|" + "---|" * len(fields)] + rows_md
    gaps = [g for g in ledger["gaps"] if g.get("entity") in entities and g.get("field") in fields]
    if gaps:
        md += ["", "**Gap register (`n.a.`)**", ""]
        md += [f"- {g['entity']} / {g['field']}: {g['description']} (tried: {', '.join(g['queries_tried']) or 'not recorded'}; {g['reason']})" for g in gaps]
    total = sum(counts.values())
    md += ["", f"Cells: {total} | verified {counts['verified']} | unverified {counts['unverified']} | conflict {counts['conflict']} | n.a. {counts['na']} | missing {counts['missing']}"]
    text = "\n".join(md) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
    if args.csv:
        import csv as _csv
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(["entity", "field", "cell", "state"])
            w.writerows(rows_csv)
    bad = counts["unverified"] + counts["conflict"] + counts["missing"]
    return {"status": "FAIL" if (args.strict and bad) else "OK", "counts": counts,
            "verified_ratio": round(counts["verified"] / total, 3) if total else 0.0,
            "problems": problems, "output": args.output or "", "markdown": text}


# ---------------------------------------------------------------- report content audit
def _report_units(md: str) -> List[Tuple[int, str, str]]:
    """(line, text, section) for prose sentences, list items and table rows. Skips code and headings."""
    units, in_code, section = [], False, ""
    for i, raw in enumerate(md.splitlines(), 1):
        line = raw.strip()
        if line.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            continue
        if line.startswith((">", "<!--")) or re.fullmatch(r"\|?[\s:|-]+\|?", line):
            continue
        line = re.sub(r"^([-*+]|\d+[.)])\s+", "", line)
        if line.startswith("|"):
            units.append((i, line, section))
            continue
        dot = "\u2024"
        protected = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + dot + m.group(2), line)
        protected = re.sub(r"\b(e\.g|i\.e|vs|etc|approx|Inc|Ltd)\.", lambda m: m.group(0).replace(".", dot), protected)
        for part in re.split(r"(?<=[.!?])\s+(?=[A-Z\[(*`\"])", protected):
            if part.strip():
                units.append((i, part.replace("\u2024", ".").strip(), section))
    return units


def _numbers(text: str) -> List[str]:
    text = LINK_RE.sub(" ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)
    return [m.group(0) for m in re.finditer(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", text) if not YEAR_RE.fullmatch(m.group(0))]


def audit_report_content(md: str, ledger: Dict[str, Any], max_age_days: int) -> List[Dict[str, Any]]:
    sources = ledger.get("sources", {})
    by_canon = {s.get("canonical_url"): s for s in sources.values()}
    claims_by_src: Dict[str, List[Dict[str, Any]]] = {}
    for c in ledger.get("claims", []):
        for sid in c.get("source_ids", []):
            claims_by_src.setdefault(sid, []).append(c)
    today = dt.date.today()
    issues: List[Dict[str, Any]] = []
    cited_domains: List[str] = []
    for line, text, section in _report_units(md):
        exempt = bool(EXEMPT_SECTION_RE.search(section))
        cited = [by_canon[canonicalize_url(u)] for _, u in LINK_RE.findall(text) if canonicalize_url(u) in by_canon]
        cited_domains += [registrable_domain(s["canonical_url"]) for s in cited]
        has_link = bool(LINK_RE.search(text))
        nums = _numbers(text)
        years = sorted({int(y) for y in YEAR_RE.findall(LINK_RE.sub(" ", text))})
        if not has_link:
            if (nums or years) and not exempt and "n.a." not in text:
                issues.append({"type": "UNCITED_NUMERIC_CLAIM", "line": line, "text": text[:200],
                               "fix": "Cite the registered source that states this number/date, or remove it."})
            m = OVERCLAIM_RE.search(text)
            if m and not exempt:
                issues.append({"type": "OVERCLAIM_LANGUAGE", "line": line, "text": text[:200], "term": m.group(0),
                               "fix": "Remove the absolute wording or back it with independent primary sources."})
            continue
        if not cited:
            continue  # unregistered URLs are already reported by the link check
        evidence = " ".join(
            [s.get("excerpt", "") for s in cited]
            + [f"{c.get('statement', '')} {c.get('value', '')} {c.get('quote', '')}" for s in cited for c in claims_by_src.get(s["id"], [])]
        )
        evidence = re.sub(r"(?<=\d),(?=\d{3}\b)", "", evidence)
        ev_nums = set(re.findall(r"\d+(?:\.\d+)?", evidence))
        for n in nums:
            variants = {n, n.rstrip("0").rstrip(".") if "." in n else n}
            if not variants & ev_nums:
                issues.append({"type": "UNSUPPORTED_NUMBER", "line": line, "text": text[:200], "number": n,
                               "fix": "Use the number exactly as the cited source states it, or cite the source that contains it."})
        dates = [d for d in (parse_loose_date(s.get("published_date", "")) for s in cited) if d]
        newest = max(dates) if dates else None
        ev_years = {int(y) for y in YEAR_RE.findall(evidence)}
        for y in years:
            if y in ev_years:
                continue
            if newest and y > newest.year:
                issues.append({"type": "DATE_AHEAD_OF_EVIDENCE", "line": line, "text": text[:200], "year": y,
                               "newest_evidence": newest.isoformat(),
                               "fix": "Find evidence published in or after that year, or restate 'as of <evidence date>'."})
            elif not newest:
                issues.append({"type": "UNDATED_EVIDENCE", "line": line, "text": text[:200], "year": y,
                               "fix": "Record --published-date for the cited source."})
        if CURRENTNESS_RE.search(text):
            if not newest:
                issues.append({"type": "UNDATED_EVIDENCE", "line": line, "text": text[:200],
                               "fix": "A 'current/latest' claim needs a dated source, or write 'as of <access date>'."})
            elif (today - newest).days > max_age_days:
                issues.append({"type": "STALE_CURRENTNESS_CLAIM", "line": line, "text": text[:200],
                               "newest_evidence": newest.isoformat(),
                               "fix": "Search for a newer source or qualify the sentence with the evidence date."})
        m = OVERCLAIM_RE.search(LINK_RE.sub(lambda x: x.group(1), text))
        if m:
            doms = {registrable_domain(s["canonical_url"]) for s in cited}
            prim = any(s.get("source_tier") == "PRIMARY" for s in cited)
            if len(doms) < 2 or not prim:
                issues.append({"type": "OVERCLAIM_LANGUAGE", "line": line, "text": text[:200], "term": m.group(0),
                               "fix": "Calibrate the wording ('according to X', 'in the cited benchmark') or add independent primary evidence."})
    if len(cited_domains) >= 5:
        top = max(set(cited_domains), key=cited_domains.count)
        if cited_domains.count(top) / len(cited_domains) > 0.5:
            issues.append({"type": "SINGLE_SOURCE_RELIANCE", "line": 0, "text": top,
                           "fix": f"{cited_domains.count(top)}/{len(cited_domains)} citations use {top}; corroborate key claims independently."})
    return issues


# ---------------------------------------------------------------- decision sensitivity
def _rank(criteria: List[Dict[str, Any]], options: List[Dict[str, Any]], weights: Dict[str, float],
          overrides: Optional[Dict[Tuple[str, str], float]] = None) -> Tuple[Optional[str], Dict[str, Optional[float]]]:
    total_w = sum(weights.values()) or 1.0
    totals: Dict[str, Optional[float]] = {}
    for opt in options:
        name = opt.get("name", "Unnamed")
        s, dq = 0.0, False
        for c in criteria:
            raw = (overrides or {}).get((name, c["id"]), opt.get("scores", {}).get(c["id"]))
            val = 5.0 if raw in (None, "unknown") else float(raw)
            if c.get("min_score") is not None and raw not in (None, "unknown") and val < float(c["min_score"]):
                dq = True
            s += weights[c["id"]] / total_w * val
        totals[name] = None if dq else s
    ok = {k: v for k, v in totals.items() if v is not None}
    return (max(ok, key=ok.get) if ok else None), totals


def decision_sensitivity(spec: Dict[str, Any]) -> Dict[str, Any]:
    criteria, options = spec["criteria"], spec["options"]
    w0 = {c["id"]: float(c.get("weight", 0)) for c in criteria}
    winner, totals = _rank(criteria, options, w0)
    ranked = sorted([k for k, v in totals.items() if v is not None], key=lambda k: -totals[k])
    margin = round(totals[ranked[0]] - totals[ranked[1]], 3) if len(ranked) > 1 else None
    weight_flips, score_flips = [], []
    for c in criteria:
        for step in range(0, 51):
            w = dict(w0)
            w[c["id"]] = (w0[c["id"]] or 1.0) * step / 10
            if sum(w.values()) <= 0:
                continue
            new, _ = _rank(criteria, options, w)
            if new and new != winner:
                weight_flips.append({"criterion": c["id"], "from": w0[c["id"]], "flip_at": round(w[c["id"]], 2), "new_winner": new})
                break
    for opt in options:
        for c in criteria:
            raw = opt.get("scores", {}).get(c["id"])
            if raw in (None, "unknown"):
                continue
            for d in (-1, 1):
                nv = min(10.0, max(0.0, float(raw) + d))
                if nv == float(raw):
                    continue
                new, _ = _rank(criteria, options, w0, {(opt.get("name", "Unnamed"), c["id"]): nv})
                if new and new != winner:
                    score_flips.append({"option": opt.get("name"), "criterion": c["id"], "from": raw, "to": nv, "new_winner": new})
    robustness = "fragile" if (margin is not None and margin < 0.5) or len(score_flips) >= 3 else \
        "moderate" if (score_flips or weight_flips) else "robust"
    warnings = []
    if margin is not None and margin < 0.5:
        warnings.append("Margin < 0.5 on a 0-10 scale: the recommendation depends on assumptions more than on scores. Confirm the flip points with the user.")
    unknown = sorted({c["id"] for o in options for c in criteria if o.get("scores", {}).get(c["id"]) in (None, "unknown")})
    if unknown:
        warnings.append(f"Unknown scores were treated as neutral 5.0 for: {', '.join(unknown)}. Research them before committing.")
    return {"winner": winner, "margin": margin, "robustness": robustness, "weight_flips": weight_flips,
            "score_flips": score_flips[:20], "warnings": warnings}


# ---------------------------------------------------------------- templates / ADR
def find_template(name: str, skill: Optional[str] = None) -> Optional[Path]:
    here = Path(__file__).resolve().parent
    candidates = [here.parent / "templates" / name]
    if skill:
        candidates += [here.parent.parent / skill / "templates" / name, here / "skills" / skill / "templates" / name]
    candidates += [here / "templates" / name, here.parent.parent.parent / "templates" / name]
    for c in candidates:
        if c.is_file():
            return c
    return None


ADR_REQUIRED_SECTIONS = ["Context & Problem Statement", "Hard Constraints & Non-Goals", "Evaluated Options", "Decision",
                         "Steelman Counter-Argument", "Reversibility", "Pre-mortem", "Operational Consequences & Rollback Trigger"]


def cmd_adr_new(args: argparse.Namespace) -> Dict[str, Any]:
    tpl = find_template("adr.md", "decision-review") or find_template("adr-template.md")
    if not tpl:
        raise WorkbenchError("TEMPLATE_NOT_FOUND", "ADR template not found (decision-review/templates/adr.md).")
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for f in d.glob("*.md") for m in [re.match(r"(\d{4})-", f.name)] if m]
    number = f"{(max(nums) + 1) if nums else 1:04d}"
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:60] or "decision"
    text = tpl.read_text(encoding="utf-8")
    fill = {"NUMBER": number, "TITLE": args.title.strip(), "DATE": dt.date.today().isoformat(),
            "OWNER": args.owner or "{{OWNER}}", "PROPOSED_ACCEPTED_SUPERSEDED": "Proposed"}
    if args.decision_result:
        res = load_json(Path(args.decision_result), {})
        ranked = res.get("ranked_options", [])
        rows = "\n".join(
            f"| {o['name']} | {o['weighted_score']} | {'yes: ' + '; '.join(o['disqualification_reasons']) if o['disqualified'] else 'no'} "
            f"| {{{{STRENGTH}}}} | {('; '.join(o.get('risks', [])) or '{{RISK}}')} |" for o in ranked)
        text = re.sub(r"(\| Option \| Weighted Score.*\n\|[-:| ]+\|\n)(?:\|.*\{\{OPTION_[AB]\}\}.*\n)+", lambda m: m.group(1) + rows + "\n", text)
        if res.get("recommended_option"):
            fill["SELECTED_OPTION"] = res["recommended_option"]
        sens = res.get("sensitivity")
        if sens:
            text += ("\n## Sensitivity (from decision-score)\n"
                     f"- Margin: {sens.get('margin')} | robustness: **{sens.get('robustness')}**\n"
                     + "".join(f"- Weight flip: {f['criterion']} {f['from']} -> {f['flip_at']} makes {f['new_winner']} win\n" for f in sens.get("weight_flips", []))
                     + "".join(f"- Warning: {w}\n" for w in sens.get("warnings", [])))
    for k, v in fill.items():
        text = text.replace("{{" + k + "}}", v)
    out = d / f"{number}-{slug}.md"
    out.write_text(text, encoding="utf-8")
    return {"status": "OK", "adr": str(out), "number": number,
            "placeholders_left": sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)))}


def cmd_adr_check(args: argparse.Namespace) -> Dict[str, Any]:
    text = Path(args.file).read_text(encoding="utf-8")
    heads = [h.strip() for h in re.findall(r"^##\s+(.+?)\s*$", text, re.M)]
    problems = []
    for s in ADR_REQUIRED_SECTIONS:
        match = next((h for h in heads if h.lower().startswith(s.lower())), None)
        if not match:
            problems.append(f"missing section: {s}")
            continue
        body = re.search(rf"^##\s+{re.escape(match)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if not body or len(re.sub(r"[\s|*:-]+", "", body.group(1))) < 10:
            problems.append(f"empty section: {s}")
    left = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)))
    if left:
        problems.append("unfilled placeholders: " + ", ".join(left))
    if not re.search(r"\bR[0-3]\b", text):
        problems.append("Reversibility must state a class R0-R3")
    opts = re.search(r"^##\s+Evaluated Options\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if opts and len([l for l in opts.group(1).splitlines() if l.strip().startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|?", l.strip())]) < 3:
        problems.append("Evaluated Options needs at least two option rows")
    return {"status": "PASS" if not problems else "FAIL", "file": args.file, "problems": problems}


# ---------------------------------------------------------------- debug report / scope
def enforce_debug_target(state_dir: Path, project_root: Path, resolved: Path) -> None:
    dbg = load_json(state_dir / "debug_ledger.json", {})
    targets = dbg.get("target_files") or []
    if not targets:
        raise WorkbenchError("NO_DEBUG_TARGET", "No target file recorded. Use debug-hypothesis --target-file <file the user named>.")
    root = project_root.resolve()
    allowed = {(root / t).resolve() if not Path(t).is_absolute() else Path(t).resolve() for t in targets}
    if resolved not in allowed:
        raise WorkbenchError("OUT_OF_DEBUG_SCOPE",
                             f"{resolved} is not a debug target. Ask the user before reading other files.",
                             {"targets": sorted(str(a) for a in allowed)})


def cmd_debug_report(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = Path(args.state_dir)
    dbg = load_json(state_dir / "debug_ledger.json", None)
    if not dbg:
        raise WorkbenchError("NO_DEBUG_LEDGER", "No debug ledger. Start with debug-hypothesis --symptom ... --target-file ...")
    hyps = dbg.get("hypotheses", [])
    confirmed = [h for h in hyps if h["status"] == "CONFIRMED"]
    tripped = dbg.get("circuit_breaker_tripped", False)
    L = [f"# {'Diagnostic Escalation Brief' if not confirmed else 'Root-Cause Report'}: {dbg.get('symptom') or 'unnamed symptom'}", "",
         f"- **Generated At**: `{utc_now_iso()}`",
         f"- **Target Files**: {', '.join(f'`{t}`' for t in dbg.get('target_files', [])) or 'not recorded'}",
         f"- **Circuit Breaker**: `{'TRIPPED' if tripped else 'not tripped'}` ({dbg.get('failed_attempts', 0)} falsified)", "",
         "## Observed Symptom & Reproduction", f"- **Symptom**: {dbg.get('symptom') or 'not recorded'}",
         f"- **Repro**: `{dbg.get('repro_command') or 'not recorded'}`", "",
         "## Hypotheses Ledger", "| ID | Statement | Prediction | Test | Status | Evidence |", "|---|---|---|---|---|---|"]
    for h in hyps:
        cell = lambda x: (x or "-").replace("|", "/").replace("\n", " ")
        L.append(f"| `{h['id']}` | {cell(h['statement'])} | {cell(h['prediction'])} | `{cell(h['test_command'])}` | {h['status']} | {cell(h.get('evidence'))} |")
    L += ["", "## Root Cause", (f"{confirmed[-1]['statement']} (confirmed by `{confirmed[-1]['id']}`: {confirmed[-1].get('evidence') or 'see ledger'})"
                                 if confirmed else "Not established within the hypothesis budget."), "",
          "## Fix Applied", args.fix or "None.", "", "## Not Checked / Open Risks", args.open_risk or "List what was not verified.", "",
          "## What Is Needed to Unblock" if not confirmed else "## Verification",
          args.needed or ("Missing telemetry, a decision from the user, or permission to widen scope." if not confirmed
                          else "Re-run the repro command and record the result with verify-delivery."), ""]
    text = "\n".join(L)
    out = Path(args.output or state_dir / "DEBUG_REPORT.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return {"status": "OK", "report": str(out), "root_cause_confirmed": bool(confirmed), "circuit_breaker_tripped": tripped}


# ---------------------------------------------------------------- verify helpers
def run_observed(cmd_str: str, timeout: int, cwd: Optional[str]) -> Dict[str, Any]:
    start = dt.datetime.now()
    try:
        proc = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd or None)
        code, out, err, timed_out = proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        dec = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
        code, out, err, timed_out = 124, dec(exc.stdout), dec(exc.stderr) + f"\nTIMEOUT after {timeout}s", True
    return {"command": cmd_str, "exit_code": code, "passed": code == 0, "timed_out": timed_out,
            "duration_seconds": round((dt.datetime.now() - start).total_seconds(), 2),
            "stdout_preview": out[-1000:], "stderr_preview": err[-1000:]}


def ladder_level(artifacts: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    achieved, not_checked = "L0", []
    for lv in VERIFY_LEVELS[1:]:
        if lv == "L1":
            checks = [a["level"] != "MISSING_OR_EMPTY" for a in artifacts]
        else:
            checks = [r["passed"] for r in results if r.get("level") == lv]
        if not checks:
            not_checked.append(lv)
            continue
        if all(checks):
            achieved = lv
        else:
            break
    return achieved, not_checked


def git_snapshot(cwd: Optional[str]) -> Dict[str, Any]:
    def g(*a: str) -> str:
        try:
            return subprocess.run(["git", *a], cwd=cwd or None, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return ""
    head = g("rev-parse", "HEAD")
    return {"head": head or None, "dirty": bool(g("status", "--porcelain")) if head else None}


# ---------------------------------------------------------------- handoff check
HANDOFF_REQUIRED = ["Objective & Current State", "Completed Work", "Pending Next Steps", "Active Blockers",
                    "Evidence & Verification Snapshot", "Decisions & Open Questions", "Resume Instructions"]


def cmd_handoff_check(args: argparse.Namespace) -> Dict[str, Any]:
    path = Path(args.file or Path(args.state_dir) / "HANDOFF.md")
    if not path.exists():
        raise WorkbenchError("FILE_NOT_FOUND", f"Handoff file not found: {path}")
    text = path.read_text(encoding="utf-8")
    problems, warnings = [], []
    for s in HANDOFF_REQUIRED:
        m = re.search(rf"^##\s+(?:\d+\.\s+)?{re.escape(s)}[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if not m:
            problems.append(f"missing section: {s}")
        elif len(m.group(1).strip()) < 3:
            problems.append(f"empty section: {s}")
    if re.search(r"^- None remaining\.", text, re.M) and re.search(r"`(PARTIAL|BLOCKED)`", text):
        problems.append("status is PARTIAL/BLOCKED but no next steps are listed")
    m = re.search(r"Generated At\*\*: `([^`]+)`", text)
    if m:
        try:
            age_h = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(m.group(1))).total_seconds() / 3600
            if age_h > float(args.max_age_hours):
                warnings.append(f"handoff is {age_h:.0f}h old: re-verify state before acting")
        except ValueError:
            warnings.append("unparseable Generated At timestamp")
    m = re.search(r"Git HEAD\*\*: `([0-9a-f]{7,40}|none)`", text)
    if m and m.group(1) != "none":
        cur = git_snapshot(None).get("head")
        if cur and not cur.startswith(m.group(1)):
            warnings.append(f"git HEAD moved since handoff ({m.group(1)} -> {cur[:12]}): read the diff first")
    return {"status": "PASS" if not problems else "FAIL", "file": str(path), "problems": problems, "warnings": warnings}


# ---------------------------------------------------------------- artifacts
def _artifact_dir() -> Optional[Path]:
    t = find_template("technical-report.md", "artifact-studio")
    return t.parent if t else None


def cmd_artifact_list(args: argparse.Namespace) -> Dict[str, Any]:
    d = _artifact_dir()
    if not d:
        raise WorkbenchError("TEMPLATE_NOT_FOUND", "artifact-studio/templates not found next to this workbench copy.")
    items = []
    for f in sorted(d.iterdir()):
        if f.is_file():
            first = next((l for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("<!--")), "")
            items.append({"type": f.stem, "file": str(f), "purpose": first.strip("<!-> ")})
    return {"status": "OK", "templates": items}


def cmd_artifact_new(args: argparse.Namespace) -> Dict[str, Any]:
    d = _artifact_dir()
    if not d:
        raise WorkbenchError("TEMPLATE_NOT_FOUND", "artifact-studio/templates not found next to this workbench copy.")
    match = [f for f in d.iterdir() if f.is_file() and (f.stem == args.type or f.name == args.type)]
    if not match:
        raise WorkbenchError("UNKNOWN_ARTIFACT_TYPE", f"Unknown type {args.type!r}.", {"available": sorted(f.stem for f in d.iterdir() if f.is_file())})
    out = Path(args.output)
    if out.exists() and not args.force:
        raise WorkbenchError("FILE_EXISTS", f"{out} exists (use --force).")
    text = match[0].read_text(encoding="utf-8").replace("{{TITLE}}", args.title).replace("{{DATE}}", dt.date.today().isoformat())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return {"status": "OK", "artifact": str(out), "type": match[0].stem,
            "placeholders_left": sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)))}


# ---------------------------------------------------------------- provider neutrality
_BANNED_HEX = ("706572706c6578697479", "70706c78", "736f6e6172")


def scan_vendor_references(base: Path) -> List[Dict[str, Any]]:
    """Return hits of banned research-vendor references under base (used by selfcheck and doctor)."""
    words = [bytes.fromhex(h).decode() for h in _BANNED_HEX]
    pat = re.compile(rf"({re.escape(words[0])}|{re.escape(words[1])}[-_]|\b{words[2]}\b)", re.IGNORECASE)
    hits = []
    for f in sorted(base.rglob("*")):
        if not f.is_file() or any(p in {".git", "__pycache__", ".local-workbench"} for p in f.parts) or f.suffix in {".pyc", ".zip"}:
            continue
        try:
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pat.search(line):
                    hits.append({"file": str(f.relative_to(base)), "line": i, "text": line.strip()[:120]})
        except OSError:
            continue
    return hits


def cmd_selfcheck(args: argparse.Namespace) -> Dict[str, Any]:
    base = Path(args.path or Path(__file__).resolve().parent)
    hits = scan_vendor_references(base)
    return {"status": "PASS" if not hits else "FAIL", "scanned_root": str(base), "violations": hits[:100]}


# ============================================================================
# v3.0 additions: doctor, spec-builder, code-review, knowledge base
# ============================================================================

SPEC_LEDGER_NAME = "spec_ledger.json"
REVIEW_LEDGER_NAME = "review_ledger.json"
KB_LEDGER_NAME = "kb_ledger.json"
DATA_LEDGER_NAME = "data_ledger.json"
MAX_DATASET_BYTES = 64 * 1024 * 1024  # 64 MB cap for dataset hashing
DEVIL_LEDGER_NAME = "devil_ledger.json"
QC_LEDGER_NAME = "qc_ledger.json"
JOURNAL_LEDGER_NAME = "journal_ledger.json"
JOURNAL_OUTCOMES = ("HIT", "MISS", "PARTIAL")
JOURNAL_BANDS = ((50, 69), (70, 84), (85, 100))

# Vague terms: the words that make an answer unjudgeable. Each maps to the
# clarifying question it demands (v3.6 question-contract).
QC_VAGUE_TERMS: Dict[str, str] = {
    "better": "better by which measure (speed, cost, maintainability, ...)?",
    "best": "best by which measure, and for whom?",
    "optimal": "optimal against which constraints?",
    "improve": "improve which metric, from what to what?",
    "faster": "faster by how much, measured where?",
    "cheaper": "cheaper on which cost line (license, ops, engineering time)?",
    "modernize": "modernize which property — the stack, the interface, the ops?",
    "efficient": "efficient in which resource — time, money, tokens, attention?",
    "scalable": "scale to what load, measured how?",
    "robust": "robust against which failure class?",
    "user-friendly": "friendly for which user doing which task?",
    "clean": "clean by which rule — style guide, architecture boundary, dead code?",
    "simple": "simple for whom — the writer or the next reader?",
    "production-ready": "ready by whose definition — traffic, on-call, compliance?",
    "daha iyi": "hangi ölçüte göre daha iyi (hız, maliyet, bakım, ...)?",
    "en iyi": "hangi ölçüte ve kime göre en iyi?",
    "verimli": "hangi kaynakta verimli — zaman, para, emek, dikkat?",
    "hızlı": "ne kadar hızlı, nerede ve nasıl ölçülecek?",
    "temiz": "hangi kurala göre temiz — stil, mimari sınırı, ölü kod?",
    "basit": "kimin için basit — yazan için mi, okuyan için mi?",
    "kullanışlı": "hangi kullanıcı, hangi iş için kullanışlı bulacak?",
    "ölçeklenebilir": "hangi yüke kadar, nasıl ölçülecek?",
}

DEVIL_SEVERITIES = ("FATAL", "SERIOUS", "MINOR")
DEVIL_CATEGORIES = (
    "unfounded-assumption",      # the plan rests on a belief nobody verified
    "missing-evidence",          # a load-bearing claim has no source or measurement
    "second-order-effect",       # the immediate effect is fine; the follow-on is not
    "alternative-explanation",   # the same observations support a different conclusion
    "cost-complexity",           # the plan is possible but costs more than claimed
    "reversibility",             # once done, undoing it is slow, expensive or impossible
    "timing",                    # right plan, wrong moment (too early / too late)
    "external-risk",             # success depends on a party or event outside your control
)

# Attack plans per plan archetype (v3.5): which assumptions to attack first,
# which premortem questions prime real divergence, what reference class the
# outside view should reach for, and which kill signals fit the archetype.
DEVIL_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "build": {
        "label": "Build a system, feature or tool",
        "attack_order": [
            "complexity-budget — the plan's true scope vs the time and skill actually available; "
            "the last 20% of scope eats the first 80% of the calendar",
            "hidden-workload — edge cases, error paths, migrations, docs, ops: the unglamorous "
            "majority that the pitch slide never shows",
            "dependency-risk — every external piece: what breaks, who fixes it, when it dies",
            "skill-assumption — the plan assumes abilities nobody in the room has demonstrated",
            "integration-seam — where the new thing meets the old thing is where it fails first",
            "abandonment-risk — who maintains this in month six, and does that person exist",
        ],
        "premortem_prompts": [
            "It shipped late and over budget — which underestimated part ate the calendar?",
            "It works in the demo and fails in production — which seam broke?",
            "Six months on, nobody touches it — why did it stop being maintained?",
        ],
        "base_rate_hint": "software projects of similar scope: delivered on time and complete",
        "kill_signals": [
            "two consecutive weeks with the same blocking defect unresolved",
            "scope grows past the agreed non-goals without a new decision",
        ],
    },
    "launch": {
        "label": "Launch a product, feature, campaign or public release",
        "attack_order": [
            "demand-evidence — is there evidence anyone wants this, or only enthusiasm",
            "timing-window — too early (no market) vs too late (entrenched winner)",
            "single-point-failure — the one review, approval or dependency that can stall it",
            "reversibility — what is permanently on the record the day after launch",
            "success-capacity — if it works, can you serve/fulfill/support the volume",
            "narrative-risk — how the worst plausible misreading spreads, and the response",
        ],
        "premortem_prompts": [
            "The launch landed and nobody came — where did the audience assumption break?",
            "It worked too well and buckled — which capacity assumption failed?",
            "Day three: the one screenshot everyone is quoting — what is it?",
        ],
        "base_rate_hint": "launches of this type: they moved their target metric",
        "kill_signals": [
            "pre-committed adoption/engagement threshold not hit by the review date",
            "top user complaint becomes the product's public identity",
        ],
    },
    "migrate": {
        "label": "Migrate: platform, database, cloud, provider or rewrite",
        "attack_order": [
            "rollback-path — can you actually get back, and has anyone tested that path",
            "data-loss-surface — every transformation, encoding and edge record that can silently break",
            "parallel-run-cost — running both systems at once: money, sanity, drift",
            "freeze-fallacy — 'we will not touch the old system during the migration' never holds",
            "estimation-anchor — migrations average several times their first estimate; what is yours",
            "exit-trigger — the observable point where the right move is to stop and undo",
        ],
        "premortem_prompts": [
            "Cutover week: what specifically broke that 'just needed a script'?",
            "Six months later you are back on the old system — what dragged you back?",
            "The data checked out and the business numbers didn't — which transformation lied?",
        ],
        "base_rate_hint": "comparable migrations: completed without material incident",
        "kill_signals": [
            "parallel-run discrepancy above the agreed threshold after two checks",
            "rollback rehearsal (not the plan — the rehearsal) fails",
        ],
    },
    "hire": {
        "label": "Add people: hire, partner, co-founder or outsource",
        "attack_order": [
            "problem-fit — is the actual bottleneck a missing person, or something a person cannot fix",
            "key-person-risk — the plan works only if this specific human performs",
            "ramp-reality — the months before contribution exceeds cost",
            "incentive-alignment — what this person is optimizing for, honestly",
            "chemistry-evidence — the specific past collaboration that proves it works with this team",
            "unmake-decision — how expensive is it to undo this in 90 days",
        ],
        "premortem_prompts": [
            "90 days in and it is not working — what did the interviews never test?",
            "It worked, then they left — what made the role a launchpad instead of a home?",
            "The output is fine and the team is worse — what broke below the surface?",
        ],
        "base_rate_hint": "similar hires/partnerships: still delivering value at the one-year mark",
        "kill_signals": [
            "agreed 90-day deliverables missed with no credible recovery plan",
            "alignment conversation happened twice and changed nothing",
        ],
    },
    "buy": {
        "label": "Buy or adopt a tool, service or vendor",
        "attack_order": [
            "problem-existence — the workflow this tool fixes: does it actually cost what you think",
            "lock-in-surface — data, formats, integrations: the cost of leaving in 18 months",
            "tco-honesty — licenses are the small number; setup, training, ops, drift are the big one",
            "vendor-mortality — what happens to you if they are acquired, pivot or die",
            "integration-reality — the promised connector vs your actual edge cases",
            "adoption-risk — the tool works and nobody uses it: the default failure mode",
        ],
        "premortem_prompts": [
            "Twelve months in, the old tool is still the real one — why did adoption fail?",
            "The renewal price tripled and you paid it — what made leaving unthinkable?",
            "The vendor's roadmap diverged from your needs — which promised feature never came?",
        ],
        "base_rate_hint": "tool adoptions of this kind: still the primary tool two years later",
        "kill_signals": [
            "adoption below the agreed usage threshold at the 90-day review",
            "migration-out cost estimate exceeds the value the tool has delivered",
        ],
    },
    "process": {
        "label": "Change how the team works: methodology, reorg or policy",
        "attack_order": [
            "problem-evidence — the pain this process fixes: measured, or remembered inaccurately",
            "adoption-friction — every extra step is a tax; who pays it and will they revolt",
            "ceremony-vs-value — the parts that feel productive and change nothing",
            "metric-gaming — what this process rewards people for optimizing, and how they will",
            "transition-trough — the productivity dip before the gain; can the team survive it",
            "reversal-plan — how you admit it failed and go back without losing face",
        ],
        "premortem_prompts": [
            "Everyone signed up and nobody changed — where did the daily reality win?",
            "The numbers improved because the numbers were redefined — what was gamed?",
            "The good parts survived and the meetings doubled — what calcified?",
        ],
        "base_rate_hint": "process changes of this type: still in force, unmodified, a year later",
        "kill_signals": [
            "the named problem the process fixes is still occurring at review date",
            "two consecutive retros call out the same part of the process as net-negative",
        ],
    },
}

REVIEW_SEVERITIES = ("BLOCKING", "MAJOR", "MINOR", "INFO")
REVIEW_CATEGORIES = ("correctness", "security", "performance", "maintainability", "tests", "style")
KB_STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "and", "or", "is", "are", "for", "how", "what",
    "does", "do", "with", "on", "can", "i", "we", "you", "it", "be", "was", "when", "which",
}


def _load_named_ledger(state_dir: Path, name: str, error_code: str, hint: str) -> Tuple[Path, Dict[str, Any]]:
    ensure_state_dir(state_dir)
    path = state_dir / name
    if not path.exists():
        raise WorkbenchError(error_code, f"No {name} at {path}. {hint}")
    return path, load_json(path, {})


# ---------------------------------------------------------------- spec builder


def cmd_spec_new(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    path = state_dir / SPEC_LEDGER_NAME
    goal = args.goal.strip()
    if len(goal) < 20:
        raise WorkbenchError(
            "GOAL_TOO_SHORT",
            "State the goal in at least 20 characters so success is later testable.",
            {"current_length": len(goal)},
        )
    if path.exists() and not args.force:
        raise WorkbenchError("SPEC_EXISTS", f"{path} already exists. Pass --force to restart the spec from scratch.")
    stories = [
        {"id": f"US{i + 1}", "text": s.strip(), "criteria": [], "status": "DRAFT"}
        for i, s in enumerate(args.story or [])
        if s.strip()
    ]
    ledger = {
        "title": (args.title or goal[:80]).strip(),
        "goal": goal,
        "non_goals": [n.strip() for n in (args.non_goal or []) if n.strip()],
        "stories": stories,
        "tasks": [],
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    save_json(path, ledger)
    return {
        "status": "OK",
        "spec_path": str(path),
        "title": ledger["title"],
        "stories": [s["id"] for s in stories],
        "next_action": "Add testable acceptance criteria: spec-criterion --story-id US1 --given ... --when ... --then ...",
    }


def cmd_spec_criterion(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_named_ledger(
        Path(args.state_dir), SPEC_LEDGER_NAME, "NO_SPEC",
        "Start with spec-new --goal ... --story ... --non-goal ...",
    )
    story = next((s for s in ledger.get("stories", []) if s.get("id") == args.story_id), None)
    if not story:
        raise WorkbenchError(
            "UNKNOWN_STORY",
            f"Story {args.story_id} not found in this spec.",
            {"known_stories": [s.get("id") for s in ledger.get("stories", [])]},
        )
    for label, val in (("given", args.given), ("when", args.when), ("then", args.then)):
        if not val or len(val.strip()) < 5:
            raise WorkbenchError(
                f"INVALID_{label.upper()}",
                f"--{label} is required for a testable criterion (at least 5 characters).",
            )
    n = sum(len(s.get("criteria", [])) for s in ledger.get("stories", [])) + 1
    crit = {
        "id": f"AC{n}",
        "story_id": story["id"],
        "given": args.given.strip(),
        "when": args.when.strip(),
        "then": args.then.strip(),
    }
    story.setdefault("criteria", []).append(crit)
    if story.get("status") == "DRAFT":
        story["status"] = "SPECIFIED"
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "criterion": crit,
        "story": story["id"],
        "criteria_in_story": len(story["criteria"]),
        "next_action": "Keep adding criteria, then break the work down with spec-task --task ... --verifies AC1.",
    }


def cmd_spec_task(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_named_ledger(
        Path(args.state_dir), SPEC_LEDGER_NAME, "NO_SPEC",
        "Start with spec-new --goal ... --story ... --non-goal ...",
    )
    task_text = args.task.strip()
    if len(task_text) < 10:
        raise WorkbenchError("TASK_TOO_SHORT", "Describe the task in at least 10 characters.")
    verifies = [v.strip() for v in (args.verifies or []) if v.strip()]
    if not verifies:
        raise WorkbenchError(
            "TASK_NOT_VERIFIABLE",
            "Every task must --verifies at least one acceptance criterion ID (e.g. --verifies AC1). "
            "Work that verifies nothing does not belong in the plan.",
        )
    known_crits = {c["id"] for s in ledger.get("stories", []) for c in s.get("criteria", [])}
    missing = [v for v in verifies if v not in known_crits]
    if missing:
        raise WorkbenchError(
            "UNKNOWN_CRITERION",
            f"Task references unknown criterion IDs: {missing}.",
            {"known_criteria": sorted(known_crits)},
        )
    deps = [d.strip() for d in (args.depends_on or []) if d.strip()]
    known_tasks = {t["id"] for t in ledger.get("tasks", [])}
    missing_deps = [d for d in deps if d not in known_tasks]
    if missing_deps:
        raise WorkbenchError(
            "UNKNOWN_TASK",
            f"--depends-on references unknown task IDs: {missing_deps} (dependencies must already exist).",
            {"known_tasks": sorted(known_tasks)},
        )
    tid = f"T{len(ledger.get('tasks', [])) + 1}"
    entry = {"id": tid, "task": task_text, "verifies": verifies, "depends_on": deps, "created_at": utc_now_iso()}
    ledger.setdefault("tasks", []).append(entry)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "task": entry,
        "next_action": "After implementing each task, prove it with verify-delivery and reference the criterion ID in the summary.",
    }


def _spec_cycle_exists(tasks: List[Dict[str, Any]]) -> bool:
    graph = {t["id"]: list(t.get("depends_on", [])) for t in tasks}
    visiting: set = set()
    done: set = set()

    def visit(node: str) -> bool:
        if node in done:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        for dep in graph.get(node, []):
            if visit(dep):
                return True
        visiting.discard(node)
        done.add(node)
        return False

    return any(visit(t) for t in graph)


def cmd_spec_check(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_named_ledger(
        Path(args.state_dir), SPEC_LEDGER_NAME, "NO_SPEC",
        "Start with spec-new --goal ... --story ... --non-goal ...",
    )
    problems: List[str] = []
    warnings: List[str] = []
    if len(ledger.get("goal", "").strip()) < 20:
        problems.append("goal is shorter than 20 characters")
    stories = ledger.get("stories", [])
    if not stories:
        problems.append("no user stories recorded")
    for s in stories:
        if not s.get("text", "").strip():
            problems.append(f"{s['id']}: empty story text")
        if not s.get("criteria"):
            problems.append(f"{s['id']}: no acceptance criteria (spec-criterion --story-id {s['id']})")
        for c in s.get("criteria", []):
            for part in ("given", "when", "then"):
                if len(c.get(part, "").strip()) < 5:
                    problems.append(f"{c['id']} ({s['id']}): incomplete '{part}' clause")
    if not ledger.get("non_goals"):
        warnings.append("no non-goals recorded: state what is explicitly out of scope")
    tasks = ledger.get("tasks", [])
    known_crits = {c["id"] for s in stories for c in s.get("criteria", [])}
    covered = {v for t in tasks for v in t.get("verifies", [])}
    crits_without_tasks = sorted(known_crits - covered)
    if known_crits and crits_without_tasks:
        warnings.append(f"criteria with no implementing task: {', '.join(crits_without_tasks)}")
    if tasks and not crits_without_tasks and known_crits:
        pass
    if _spec_cycle_exists(tasks):
        problems.append("task dependency cycle detected")
    status = "PASS" if not problems else "FAIL"
    return {
        "status": status,
        "spec_path": str(path),
        "problems": problems,
        "warnings": warnings,
        "coverage": {
            "stories": len(stories),
            "criteria": len(known_crits),
            "tasks": len(tasks),
            "covered_criteria": sorted(covered),
            "criteria_without_tasks": crits_without_tasks,
        },
        "checked_at": utc_now_iso(),
    }


# ---------------------------------------------------------------- code review


def cmd_review_init(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    path = state_dir / REVIEW_LEDGER_NAME
    if len(args.title.strip()) < 5:
        raise WorkbenchError("TITLE_TOO_SHORT", "Give the review a title of at least 5 characters.")
    if not args.target.strip():
        raise WorkbenchError("EMPTY_TARGET", "State what is being reviewed (file, PR, diff range, module).")
    if path.exists() and not args.force:
        raise WorkbenchError("REVIEW_EXISTS", f"{path} already exists. Pass --force to restart the review.")
    ledger = {
        "title": args.title.strip(),
        "target": args.target.strip(),
        "focus": [f.strip() for f in (args.focus or []) if f.strip()],
        "findings": [],
        "started_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    save_json(path, ledger)
    return {
        "status": "OK",
        "review_path": str(path),
        "target": ledger["target"],
        "next_action": "Inspect only the declared target. Record findings with review-finding --file ... --description ...",
    }


def cmd_review_finding(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_named_ledger(
        Path(args.state_dir), REVIEW_LEDGER_NAME, "NO_REVIEW",
        "Start with review-init --title ... --target ...",
    )
    if not args.file.strip():
        raise WorkbenchError("EMPTY_FILE", "--file is required so every finding is locatable.")
    description = args.description.strip()
    if len(description) < 10:
        raise WorkbenchError("DESCRIPTION_TOO_SHORT", "Describe the finding in at least 10 characters.")
    line = int(args.line) if args.line is not None else None
    if line is not None and line < 1:
        raise WorkbenchError("INVALID_LINE", "--line must be >= 1.")
    duplicate = any(
        f.get("file") == args.file.strip()
        and f.get("line") == line
        and f.get("description") == description
        for f in ledger.get("findings", [])
    )
    if duplicate and not args.allow_duplicate:
        raise WorkbenchError("DUPLICATE_FINDING", "This exact finding (file, line, description) is already recorded.")
    fid = f"F{len(ledger.get('findings', [])) + 1}"
    entry = {
        "id": fid,
        "file": args.file.strip(),
        "line": line,
        "severity": args.severity,
        "category": args.category,
        "description": description,
        "suggestion": (args.suggestion or "").strip(),
        "created_at": utc_now_iso(),
    }
    ledger.setdefault("findings", []).append(entry)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    counts = _review_counts(ledger)
    return {
        "status": "OK",
        "finding": entry,
        "open_blocking": counts["BLOCKING"],
        "next_action": ("Fix BLOCKING findings before any delivery claim." if counts["BLOCKING"]
                        else "Continue the review or render it with review-report."),
    }


def _review_counts(ledger: Dict[str, Any]) -> Dict[str, int]:
    counts = {sev: 0 for sev in REVIEW_SEVERITIES}
    for f in ledger.get("findings", []):
        counts[f.get("severity", "INFO")] = counts.get(f.get("severity", "INFO"), 0) + 1
    return counts


def cmd_review_report(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_named_ledger(
        Path(args.state_dir), REVIEW_LEDGER_NAME, "NO_REVIEW",
        "Start with review-init --title ... --target ...",
    )
    findings = ledger.get("findings", [])
    counts = _review_counts(ledger)
    verdict = (
        "FAIL" if counts["BLOCKING"]
        else "PASS_WITH_FINDINGS" if (counts["MAJOR"] or counts["MINOR"])
        else "PASS"
    )
    sev_rank = {sev: i for i, sev in enumerate(REVIEW_SEVERITIES)}
    ordered = sorted(findings, key=lambda f: (sev_rank.get(f.get("severity"), 99), f.get("file", ""), f.get("line") or 0))
    lines = [
        f"# Code Review: {ledger.get('title', 'untitled')}",
        "",
        f"- **Generated At**: `{utc_now_iso()}`",
        f"- **Target**: `{ledger.get('target', 'not recorded')}`",
        f"- **Focus**: {', '.join(ledger.get('focus', [])) or 'not recorded'}",
        f"- **Verdict**: **{verdict}** (blocking {counts['BLOCKING']}, major {counts['MAJOR']}, minor {counts['MINOR']}, info {counts['INFO']})",
        "",
        "## Findings",
        "",
    ]
    if not ordered:
        lines.append("- No findings recorded.")
    for f in ordered:
        loc = f"`{f['file']}`" + (f":{f['line']}" if f.get("line") else "")
        lines.append(f"- **{f['id']} [{f['severity']}/{f['category']}]** {loc} — {f['description']}")
        if f.get("suggestion"):
            lines.append(f"  - Suggestion: {f['suggestion']}")
    lines += [
        "",
        "## Severity Model",
        "",
        "- BLOCKING: incorrect, insecure, or loses data. Must be fixed before merge; verdict is FAIL while any is open.",
        "- MAJOR: correct code that will bite soon (missing test on changed behavior, unclear API contract).",
        "- MINOR: worth fixing in passing (naming, small duplication, stale comment).",
        "- INFO: observation, no change requested.",
        "",
        "## Not Reviewed",
        "",
        args.not_reviewed or "Declare what was not inspected so the reader can judge the verdict.",
        "",
    ]
    text = "\n".join(lines)
    out = Path(args.output or Path(args.state_dir) / "REVIEW.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return {
        "status": "FAIL" if verdict == "FAIL" else "OK",
        "verdict": verdict,
        "counts": counts,
        "findings_count": len(findings),
        "report": str(out),
    }


# ---------------------------------------------------------------- knowledge base


def _load_kb(state_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    """Load the knowledge base; create an empty ledger on first kb-add."""
    ensure_state_dir(state_dir)
    path = state_dir / KB_LEDGER_NAME
    if not path.exists():
        ledger = {"entries": [], "created_at": utc_now_iso(), "updated_at": utc_now_iso()}
        save_json(path, ledger)
        return path, ledger
    ledger = load_json(path, {})
    ledger.setdefault("entries", [])
    return path, ledger


def _kb_tokens(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) > 1 and t not in KB_STOPWORDS]


def cmd_kb_add(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_kb(Path(args.state_dir))
    question = args.question.strip()
    answer = args.answer.strip()
    if len(question) < 10:
        raise WorkbenchError("QUESTION_TOO_SHORT", "State the question in at least 10 characters.")
    if len(answer) < 20:
        raise WorkbenchError("ANSWER_TOO_SHORT", "Answers must carry their reasoning: at least 20 characters.")
    if not (args.source_url or args.source_id or args.assumed):
        raise WorkbenchError(
            "UNSOURCED_ENTRY",
            "Every knowledge entry needs --source-url, --source-id (a registered research source), or --assumed "
            "to record an explicit assumption.",
        )
    if args.source_id:
        _, research = _load_ledger(Path(args.state_dir))
        if args.source_id not in research.get("sources", {}):
            raise WorkbenchError(
                "UNKNOWN_SOURCE_ID",
                f"--source-id {args.source_id} is not registered in the research ledger.",
                {"known_source_ids": sorted(research.get("sources", {}).keys())},
            )
    dup = any(" ".join(e.get("question", "").lower().split()) == " ".join(question.lower().split()) for e in ledger["entries"])
    if dup and not args.force:
        raise WorkbenchError("DUPLICATE_QUESTION", "This question is already in the knowledge base (pass --force to add anyway).")
    eid = f"K{len(ledger['entries']) + 1}"
    entry = {
        "id": eid,
        "question": question,
        "answer": answer,
        "source_url": (args.source_url or "").strip(),
        "source_id": (args.source_id or "").strip(),
        "tags": sorted({t.strip().lower() for t in (args.tag or []) if t.strip()}),
        "assumed": bool(args.assumed),
        "confidence": "LOW" if args.assumed else "MEDIUM",
        "created_at": utc_now_iso(),
    }
    ledger["entries"].append(entry)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "entry": entry,
        "entries_count": len(ledger["entries"]),
        "warning": ("Recorded as an explicit assumption (LOW confidence). Revisit with evidence before relying on it."
                    if args.assumed else ""),
    }


def cmd_kb_search(args: argparse.Namespace) -> Dict[str, Any]:
    _, ledger = _load_kb(Path(args.state_dir))
    q_tokens = _kb_tokens(args.query)
    if not q_tokens:
        raise WorkbenchError("EMPTY_QUERY", "The query has no searchable tokens after stop-word removal.")
    results = []
    for e in ledger["entries"]:
        if args.tag and args.tag.lower() not in e.get("tags", []):
            continue
        q_hit = set(_kb_tokens(e.get("question", "")))
        a_hit = set(_kb_tokens(e.get("answer", "")))
        t_hit = set(_kb_tokens(" ".join(e.get("tags", []))))
        score = 3 * len(t_hit & set(q_tokens)) + 2 * len(q_hit & set(q_tokens)) + len(a_hit & set(q_tokens))
        if score > 0:
            results.append({
                "id": e["id"], "score": score, "question": e["question"], "answer": e["answer"],
                "tags": e.get("tags", []), "source_url": e.get("source_url", ""),
                "source_id": e.get("source_id", ""), "assumed": e.get("assumed", False),
            })
    results.sort(key=lambda r: (-r["score"], r["id"]))
    return {
        "status": "OK",
        "query": args.query,
        "matched": len(results),
        "results": results[:20],
        "note": "Deterministic offline keyword match. Open the cited source before quoting an entry in a deliverable.",
    }


def cmd_kb_export(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = Path(args.state_dir)
    _, ledger = _load_kb(state_dir)
    entries = ledger.get("entries", [])
    out = Path(args.output or state_dir / "KNOWLEDGE_BASE.md")
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        key = e.get("tags", [])[0] if e.get("tags") else "general"
        groups.setdefault(key, []).append(e)
    lines = [
        f"# Knowledge Base: {ledger.get('topic', 'project knowledge') if ledger.get('topic') else 'project knowledge'}",
        "",
        f"- Generated: `{utc_now_iso()}` | entries {len(entries)} | assumptions {sum(1 for e in entries if e.get('assumed'))}",
        "- Entries marked ASSUMPTION have no source. Verify before relying on them.",
        "",
    ]
    for key in sorted(groups):
        lines.append(f"## {key}")
        lines.append("")
        for e in groups[key]:
            lines.append(f"### {e['id']}: {e['question']}")
            lines.append("")
            lines.append(e["answer"])
            if e.get("source_url"):
                lines.append(f"- Source: {e['source_url']}")
            elif e.get("source_id"):
                lines.append(f"- Source: research ledger `{e['source_id']}`")
            else:
                lines.append("- **ASSUMPTION** (unverified)")
            lines.append(f"- Recorded: {e.get('created_at', 'unknown')} | confidence {e.get('confidence', 'MEDIUM')}")
            lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return {"status": "OK", "knowledge_base": str(out), "entries": len(entries)}


# ---------------------------------------------------------------- data analysis
# Grounded analysis of a user-provided data file. The ledger pins the dataset
# identity (path, size, SHA-256); every number in the final report must come
# from a logged finding that carries the exact command or formula which
# produced it. A number without a method is a guess, and guesses become gaps.


def _load_data_ledger(state_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    """Load the data analysis ledger; create an empty one on first register."""
    ensure_state_dir(state_dir)
    path = state_dir / DATA_LEDGER_NAME
    if not path.exists():
        ledger = {"dataset": None, "question": "", "findings": [], "gaps": [],
                  "created_at": utc_now_iso(), "updated_at": utc_now_iso()}
        save_json(path, ledger)
        return path, ledger
    ledger = load_json(path, {})
    ledger.setdefault("dataset", None)
    ledger.setdefault("question", "")
    ledger.setdefault("findings", [])
    ledger.setdefault("gaps", [])
    return path, ledger


def _dataset_drifted(ledger: Dict[str, Any]) -> bool:
    """True when the registered file is gone or no longer matches its hash."""
    ds = ledger.get("dataset") or {}
    p = Path(ds.get("path", ""))
    try:
        return (not p.is_file()) or sha256_file(p) != ds.get("sha256")
    except OSError:
        return True


def cmd_data_register(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_data_ledger(Path(args.state_dir))
    question = (args.question or "").strip() or ledger.get("question", "").strip()
    if len(question) < 15:
        raise WorkbenchError("QUESTION_TOO_SHORT",
                             "State the analytical question in at least 15 characters.")
    file_path = Path(args.path).expanduser()
    if not file_path.is_file():
        raise WorkbenchError("FILE_NOT_FOUND", f"{args.path} is not a file.")
    size = file_path.stat().st_size
    if size > MAX_DATASET_BYTES:
        raise WorkbenchError("FILE_TOO_LARGE",
                             f"{file_path.name} is {size} bytes; the cap is {MAX_DATASET_BYTES}. "
                             "Register a representative sample instead and say so in the report.")
    digest = sha256_file(file_path)
    same_path = bool(ledger["dataset"]) and ledger["dataset"].get("path") == str(file_path)
    if ledger["dataset"] and not same_path and not args.force:
        raise WorkbenchError("DATASET_MISMATCH",
                             f"This ledger already tracks {ledger['dataset'].get('path')}. "
                             "Registering a different dataset resets findings and gaps; pass --force.",
                             {"registered_path": ledger["dataset"].get("path")})
    reset = bool(ledger["dataset"]) and not same_path
    if reset:
        ledger["findings"] = []
        ledger["gaps"] = []
    drift = same_path and ledger["dataset"].get("sha256") != digest
    ledger["dataset"] = {
        "path": str(file_path),
        "bytes": size,
        "sha256": digest,
        "registered_at": utc_now_iso(),
    }
    ledger["question"] = question
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "dataset": ledger["dataset"],
        "question": question,
        "findings_reset": reset,
        "content_drift": drift,
        "findings_count": len(ledger["findings"]),
        "warning": ("Dataset content changed since the last registration; earlier findings may no "
                    "longer hold — re-run their methods or drop them." if drift else ""),
    }


def cmd_data_finding(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_data_ledger(Path(args.state_dir))
    if not ledger["dataset"]:
        raise WorkbenchError("NO_DATASET", "Register the dataset first: data-register --path FILE --question ...")
    statement = args.statement.strip()
    method = args.method.strip()
    result = args.result.strip()
    if len(statement) < 10:
        raise WorkbenchError("STATEMENT_TOO_SHORT", "State the finding in at least 10 characters.")
    if len(method) < 10:
        raise WorkbenchError("METHOD_TOO_SHORT",
                             "Every finding needs its method: the exact command, query or formula that "
                             "produced the number (min 10 characters).")
    if not result:
        raise WorkbenchError("EMPTY_RESULT", "Record the observed result — the value you measured.")
    if _dataset_drifted(ledger):
        raise WorkbenchError("DATASET_DRIFT",
                             "The dataset no longer matches its registered SHA-256. Re-run data-register "
                             "(same path refreshes the hash) and redo the affected findings.")
    fid = f"F{len(ledger['findings']) + 1}"
    finding = {
        "id": fid,
        "statement": statement,
        "method": method,
        "result": result,
        "created_at": utc_now_iso(),
    }
    ledger["findings"].append(finding)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {"status": "OK", "finding": finding, "findings_count": len(ledger["findings"])}


def cmd_data_gap(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_data_ledger(Path(args.state_dir))
    if not ledger["dataset"]:
        raise WorkbenchError("NO_DATASET", "Register the dataset first: data-register --path FILE --question ...")
    description = args.description.strip()
    if len(description) < 15:
        raise WorkbenchError("GAP_TOO_SHORT", "Describe what could not be computed and why (min 15 characters).")
    gid = f"G{len(ledger['gaps']) + 1}"
    gap = {"id": gid, "description": description, "reason": (args.reason or "").strip(),
           "created_at": utc_now_iso()}
    ledger["gaps"].append(gap)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {"status": "OK", "gap": gap, "gaps_count": len(ledger["gaps"])}


def _md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def cmd_data_report(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_data_ledger(Path(args.state_dir))
    if not ledger["dataset"]:
        raise WorkbenchError("NO_DATASET", "Register the dataset first: data-register --path FILE --question ...")
    if not ledger["findings"]:
        raise WorkbenchError("NO_FINDINGS",
                             "An analysis report needs at least one logged finding: "
                             "data-finding --statement ... --method ... --result ...")
    answer = (args.answer or "").strip()
    if len(answer) < 20:
        raise WorkbenchError("ANSWER_TOO_SHORT",
                             "Answer the registered question in at least 20 characters, or the report "
                             "has no synthesis.")
    ledger_numbers: set = set()
    for f in ledger["findings"]:
        ledger_numbers.update(_numbers(f["statement"]))
        ledger_numbers.update(_numbers(f["result"]))
    unledgered = sorted(set(_numbers(answer)) - ledger_numbers)
    if unledgered and not args.allow_unverified_numbers:
        raise WorkbenchError("UNLEDGERED_NUMBERS",
                             f"Numbers in the answer that no finding supports: {', '.join(unledgered)}. "
                             "Log the finding that produces each number, or pass --allow-unverified-numbers "
                             "to publish them marked UNVERIFIED.",
                             {"unledgered": unledgered})
    drift = _dataset_drifted(ledger)
    ds = ledger["dataset"]
    lines: List[str] = [
        "# Data Analysis Report",
        "",
        f"**Question**: {ledger['question']}",
        f"**Dataset**: `{ds['path']}` ({ds['bytes']} bytes, SHA-256 `{ds['sha256'][:16]}...`)",
        f"**Findings**: {len(ledger['findings'])} | **Gaps**: {len(ledger['gaps'])}",
    ]
    if drift:
        lines += ["", "> **WARNING**: the dataset file no longer matches its registered hash; "
                  "the numbers below were computed on the earlier content."]
    if unledgered:
        lines += ["", f"> **WARNING**: {len(unledgered)} number(s) in the answer are not backed by a "
                  "logged finding and are marked UNVERIFIED."]
    lines += ["", "## Answer", "", answer, "", "## Findings", "",
              "| ID | Finding | Method (re-runnable) | Result |",
              "|---|---|---|---|"]
    for f in ledger["findings"]:
        lines.append(f"| {f['id']} | {_md_cell(f['statement'])} | `{_md_cell(f['method'])}` | {_md_cell(f['result'])} |")
    if ledger["gaps"]:
        lines += ["", "## Declared gaps", "", "| ID | What could not be computed | Reason |", "|---|---|---|"]
        for g in ledger["gaps"]:
            lines.append(f"| {g['id']} | {_md_cell(g['description'])} | {_md_cell(g['reason'] or '-')} |")
    lines.append("")
    out = Path(args.output) if args.output else path.parent / "ANALYSIS.md"
    if out.exists() and not args.force:
        raise WorkbenchError("FILE_EXISTS", f"{out} exists (use --force).")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": "WARN" if (drift or unledgered) else "OK",
        "report": str(out),
        "findings_count": len(ledger["findings"]),
        "gaps_count": len(ledger["gaps"]),
        "dataset_drift": drift,
        "contains_unverified_numbers": bool(unledgered),
        "unverified_numbers": unledgered,
    }


# ------------------------------------------------------------ devil-advocate
# The adversarial second opinion: steelman the plan fairly, attack its
# load-bearing assumptions with severities, answer what can be answered,
# and let the unanswered attacks decide the verdict mechanically.
# BLOCK while a FATAL challenge stands — overconfidence has no exit hatch.


def _load_devil_ledger(state_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    ensure_state_dir(state_dir)
    path = state_dir / DEVIL_LEDGER_NAME
    if not path.exists():
        raise WorkbenchError(
            "NO_DEVIL_SESSION",
            "No devil's advocate session is open. Start one: devil-open --claim \"the plan in "
            "one sentence\" --steelman \"its best case, stated honestly\".",
        )
    return path, load_json(path, {})


def cmd_devil_open(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    path = state_dir / DEVIL_LEDGER_NAME
    claim = args.claim.strip()
    steelman = args.steelman.strip()
    if len(claim) < 20:
        raise WorkbenchError("CLAIM_TOO_SHORT",
                             "State the claim under attack in at least 20 characters.")
    if len(steelman) < 30:
        raise WorkbenchError(
            "STEELMAN_TOO_SHORT",
            "State the plan's best case honestly in at least 30 characters — an attack on a "
            "strawman is worthless, and the steelman is what makes this challenge fair.",
        )
    if path.exists() and not args.force:
        raise WorkbenchError(
            "DEVIL_SESSION_EXISTS",
            f"{path} already holds an open session. Pass --force to start over (challenges "
            "and verdict are wiped).",
        )
    ledger = {
        "claim": claim,
        "steelman": steelman,
        "status": "OPEN",
        "challenges": [],
        "verdict": None,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    save_json(path, ledger)
    return {
        "status": "OK",
        "claim": claim,
        "steelman": steelman,
        "next": "devil-challenge --assumption ... --attack ... --defeater ...",
    }


def cmd_devil_challenge(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    assumption = args.assumption.strip()
    attack = args.attack.strip()
    defeater = args.defeater.strip()
    if len(assumption) < 10:
        raise WorkbenchError(
            "ASSUMPTION_TOO_SHORT",
            "Name the load-bearing assumption you are attacking in at least 10 characters.",
        )
    if len(attack) < 20:
        raise WorkbenchError(
            "ATTACK_TOO_SHORT",
            "An attack shorter than 20 characters is a quibble, not a challenge — say what "
            "specifically breaks and why.",
        )
    if len(defeater) < 10:
        raise WorkbenchError(
            "DEFEATER_TOO_SHORT",
            "Every attack must name its defeater: the observation or argument that would "
            "prove it wrong (min 10 characters). An attack with no possible defeater is "
            "dogma, not criticism.",
        )
    cid = f"C{len(ledger['challenges']) + 1}"
    challenge = {
        "id": cid,
        "assumption": assumption,
        "attack": attack,
        "category": args.category,
        "severity": args.severity,
        "defeater": defeater,
        "status": "OPEN",
        "rebuttal": None,
        "rebuttal_basis": None,
        "created_at": utc_now_iso(),
    }
    ledger["challenges"].append(challenge)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "challenge": challenge,
        "open_counts": _devil_open_counts(ledger),
        "answered_count": sum(1 for c in ledger["challenges"] if c["status"] == "ANSWERED"),
    }


def _devil_open_counts(ledger: Dict[str, Any]) -> Dict[str, int]:
    counts = {s: 0 for s in DEVIL_SEVERITIES}
    for c in ledger["challenges"]:
        if c.get("status") == "OPEN":
            counts[c.get("severity", "MINOR")] = counts.get(c.get("severity", "MINOR"), 0) + 1
    return counts


def cmd_devil_rebuttal(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    rebuttal = args.rebuttal.strip()
    if len(rebuttal) < 20:
        raise WorkbenchError(
            "REBUTTAL_TOO_SHORT",
            "Answer the attack in at least 20 characters — a rebuttal must engage the "
            "argument, not wave it away.",
        )
    target = None
    for c in ledger["challenges"]:
        if c["id"] == args.id:
            target = c
            break
    if target is None:
        raise WorkbenchError(
            "UNKNOWN_CHALLENGE",
            f"No challenge with id {args.id}.",
            {"known": [c["id"] for c in ledger["challenges"]]},
        )
    if target["status"] == "ANSWERED":
        raise WorkbenchError(
            "CHALLENGE_ANSWERED",
            f"{args.id} is already answered by: {target.get('rebuttal', '')[:80]}",
        )
    target["status"] = "ANSWERED"
    target["rebuttal"] = rebuttal
    target["rebuttal_basis"] = (args.basis or "reasoning").strip()
    target["answered_at"] = utc_now_iso()
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "challenge": target,
        "open_counts": _devil_open_counts(ledger),
        "answered_count": sum(1 for c in ledger["challenges"] if c["status"] == "ANSWERED"),
    }


def cmd_devil_verdict(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    if not ledger["challenges"]:
        raise WorkbenchError(
            "CHALLENGE_FIRST",
            "An unexamined plan gets no verdict — log at least one challenge first "
            "(devil-challenge), or this is approval theater.",
        )
    kill_criteria = [k.strip() for k in (args.kill_criterion or []) if k.strip()]
    if not kill_criteria:
        raise WorkbenchError(
            "KILL_CRITERIA_REQUIRED",
            "Committing to a plan requires at least one kill criterion: the observable, "
            "pre-committed signal that would falsify it later (--kill-criterion, repeatable).",
        )
    for k in kill_criteria:
        if len(k) < 10:
            raise WorkbenchError("KILL_CRITERION_TOO_SHORT",
                                 f"Kill criteria must be observable signals, not vibes: '{k}' "
                                 "is under 10 characters.")
    counts = _devil_open_counts(ledger)
    open_challenges = [c for c in ledger["challenges"] if c["status"] == "OPEN"]
    if counts["FATAL"] > 0:
        verdict = "BLOCK"
    elif counts["SERIOUS"] > 0:
        verdict = "PROCEED_WITH_GUARDS"
    else:
        verdict = "PROCEED"
    guards = [
        {"challenge": c["id"], "guard": c["assumption"], "watch": c["defeater"]}
        for c in open_challenges if c["severity"] == "SERIOUS"
    ]
    ledger["verdict"] = {
        "verdict": verdict,
        "open_counts": counts,
        "answered_count": sum(1 for c in ledger["challenges"] if c["status"] == "ANSWERED"),
        "guards": guards,
        "kill_criteria": kill_criteria,
        "decided_at": utc_now_iso(),
    }
    ledger["status"] = "DECIDED"
    ledger["updated_at"] = utc_now_iso()

    out = Path(args.output) if args.output else path.parent / "CHALLENGE.md"
    if out.exists() and not args.force:
        raise WorkbenchError("FILE_EXISTS", f"{out} exists (use --force).")
    lines: List[str] = [
        "# Devil's Advocate Verdict",
        "",
        f"**Claim under attack**: {ledger['claim']}",
        "",
    ]
    if ledger.get("archetype"):
        arch = DEVIL_ARCHETYPES.get(ledger["archetype"], {})
        lines += [f"**Plan archetype**: {ledger['archetype']}"
                  + (f" — {arch.get('label', '')}" if arch else ""), ""]
    lines += [
        "## The steelman (the plan's best case, stated honestly)",
        "",
        ledger["steelman"],
        "",
    ]
    premortem = ledger.get("premortem")
    if premortem:
        lines += ["## Premortem (it is 12 months later and the plan failed)", "",
                  premortem["failure_story"], "", "Named causes:", ""]
        for c in premortem["causes"]:
            lines.append(f"- {c}")
        lines.append("")
    outside = ledger.get("outside_view")
    if outside:
        lines += ["## Outside view (the reference class, before the plan's own story)", "",
                  f"Reference class: {outside['reference_class']} — "
                  f"~{outside['base_rate']}% of them succeed.", "",
                  f"Inside-view adjustment: {outside['adjustment']}", ""]
    consequences = ledger.get("consequences") or []
    if consequences:
        lines += ["## Second-order effects (and then what?)", ""]
        for i, cq in enumerate(consequences, 1):
            chain = f"L1 {cq['l1']} -> L2 {cq['l2']}"
            if cq.get("l3"):
                chain += f" -> L3 {cq['l3']}"
            lines.append(f"{i}. {chain}")
        lines.append("")
    protocols_used = {
        "premortem": bool(premortem),
        "outside_view": bool(outside),
        "second_order": bool(consequences),
    }
    lines += [f"## Verdict: {verdict}", ""]
    if verdict == "BLOCK":
        lines.append(f"BLOCKED — {counts['FATAL']} FATAL challenge(s) stand unanswered. "
                     "Answer them or change the plan; do not proceed and do not soften them.")
    elif verdict == "PROCEED_WITH_GUARDS":
        lines.append(f"Proceed, but under guard — {counts['SERIOUS']} SERIOUS challenge(s) "
                     "remain open. Watch the guard signals below; the first one that fires "
                     "stops the plan.")
    else:
        lines.append("Proceed — every challenge stands answered. The kill criteria below "
                     "remain armed regardless.")
    lines += ["", "## Challenges", "",
              "| ID | Assumption attacked | Attack | Category | Severity | Status |",
              "|---|---|---|---|---|---|"]
    for c in ledger["challenges"]:
        lines.append(
            f"| {c['id']} | {_md_cell(c['assumption'])} | {_md_cell(c['attack'])} "
            f"| {c['category']} | {c['severity']} | {c['status']} |"
        )
    answered = [c for c in ledger["challenges"] if c["status"] == "ANSWERED"]
    if answered:
        lines += ["", "## Answered challenges", ""]
        for c in answered:
            lines += [f"### {c['id']} — answered on the basis of {c.get('rebuttal_basis') or 'reasoning'}",
                      "",
                      f"> Attack: {c['attack']}", "",
                      f"Rebuttal: {c['rebuttal']}", "",
                      f"(Defeater on record: {c['defeater']})", ""]
    if guards:
        lines += ["## Guards (open SERIOUS challenges)", "",
                  "| Challenge | Guard: assumption to watch | Signal: what defeats the attack |",
                  "|---|---|---|"]
        for g in guards:
            lines.append(f"| {g['challenge']} | {_md_cell(g['guard'])} | {_md_cell(g['watch'])} |")
    lines += ["", "## Kill criteria (pre-committed, observable)", ""]
    for i, k in enumerate(kill_criteria, 1):
        lines.append(f"{i}. {k}")
    lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    save_json(path, ledger)
    status = {"BLOCK": "FAIL", "PROCEED_WITH_GUARDS": "WARN", "PROCEED": "PASS"}[verdict]
    result = {
        "status": status,
        "verdict": verdict,
        "report": str(out),
        "open_counts": counts,
        "answered_count": ledger["verdict"]["answered_count"],
        "guards": guards,
        "kill_criteria": kill_criteria,
        "protocols_used": protocols_used,
    }
    if not premortem:
        # Not a gate (the v3.3 contract stands), but the record shows the
        # cheapest high-value protocol was skipped.
        result["premortem_missing"] = True
        result["premortem_note"] = ("No premortem on record — the failure story was never "
                                    "written. Next session, run devil-premortem before the "
                                    "challenges.")
    return result


def cmd_devil_plan(args: argparse.Namespace) -> Dict[str, Any]:
    """The archetype attack plan: which assumptions to attack first for this kind
    of plan, which premortem questions prime real divergence, the reference class
    the outside view should reach for, and archetype-appropriate kill signals.
    Works without an open session (pure reference); records the archetype on an
    open session so the verdict can show which plan was attacked."""
    archetype = DEVIL_ARCHETYPES.get(args.archetype)
    if archetype is None:
        raise WorkbenchError("UNKNOWN_ARCHETYPE",
                             f"Unknown archetype '{args.archetype}'.",
                             {"known": sorted(DEVIL_ARCHETYPES)})
    result: Dict[str, Any] = {
        "status": "OK",
        "archetype": args.archetype,
        "label": archetype["label"],
        "attack_order": archetype["attack_order"],
        "premortem_prompts": archetype["premortem_prompts"],
        "base_rate_hint": archetype["base_rate_hint"],
        "kill_signal_candidates": archetype["kill_signals"],
        "workflow": [
            "devil-open --claim ... --steelman ...  (fair hearing first)",
            "devil-premortem --failure-story ... --cause ...  (it failed — write the story)",
            "devil-outside --reference-class ... --base-rate N  (what happens to most who try)",
            "devil-challenge ...  (attack in the order above; every attack names its defeater)",
            "devil-consequence --l1 ... --l2 ...  (and then what? for the top risks)",
            "devil-rebuttal --id Cn ...  (answer what can be answered)",
            "devil-verdict --kill-criterion ...  (the gate decides, not the mood)",
        ],
    }
    path = Path(args.state_dir) / DEVIL_LEDGER_NAME
    if path.exists():
        _, ledger = _load_devil_ledger(Path(args.state_dir))
        if ledger.get("status") == "OPEN":
            ledger["archetype"] = args.archetype
            ledger["updated_at"] = utc_now_iso()
            save_json(path, ledger)
            result["recorded_on_session"] = True
    return result


def cmd_devil_premortem(args: argparse.Namespace) -> Dict[str, Any]:
    """The premortem (Klein): it is 12 months later and the plan has failed —
    write the story. Run BEFORE the challenges: asking 'why did it fail' primes
    genuinely divergent thinking in a way 'what might go wrong' never does,
    because failure is already assumed and defending the plan is pointless."""
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    if ledger.get("status") != "OPEN":
        raise WorkbenchError("SESSION_DECIDED",
                             "The session already has a verdict. Open a new session (devil-open "
                             "--force) before running another premortem.")
    if ledger.get("premortem"):
        raise WorkbenchError(
            "PREMORTEM_EXISTS",
            "This session already has a premortem. One per session — a second story is a "
            "rewrite of the first, not fresh divergence.",
        )
    story = args.failure_story.strip()
    if len(story) < 40:
        raise WorkbenchError(
            "FAILURE_STORY_TOO_SHORT",
            "Write the actual failure story in at least 40 characters — concrete, past tense, "
            "no hedging ('unforeseen difficulties' is not a cause, it is a placeholder).",
        )
    causes = [c.strip() for c in (args.cause or []) if c.strip()]
    if not causes:
        raise WorkbenchError(
            "CAUSES_REQUIRED",
            "A premortem story needs at least one named cause (--cause, repeatable) — specific "
            "enough that someone could go check whether it is already forming.",
        )
    for c in causes:
        if len(c) < 10:
            raise WorkbenchError("CAUSE_TOO_SHORT",
                                 f"Each cause must be at least 10 characters: '{c}' is not a cause.")
    ledger["premortem"] = {
        "failure_story": story,
        "causes": causes,
        "recorded_at": utc_now_iso(),
    }
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    suggestions = [
        f'devil-challenge --assumption "{c[:60]}..." --attack "the premortem cause: {c[:60]}..." '
        f'--category unfounded-assumption --severity SERIOUS --defeater "..."'
        for c in causes
    ]
    return {
        "status": "OK",
        "premortem": ledger["premortem"],
        "cause_count": len(causes),
        "next": "Turn each cause into a challenge (or answer it), then devil-outside. "
                "Suggested commands:",
        "suggested_challenges": suggestions,
    }


def cmd_devil_outside(args: argparse.Namespace) -> Dict[str, Any]:
    """The outside view (Kahneman): before trusting the plan's own story, find
    the reference class — everyone who has tried something like this — and its
    base rate. The inside view is where optimism lives; the base rate is where
    the truth usually is. A bad base rate with no adjustment is recorded as a
    SERIOUS challenge automatically: optimism bias must be argued, not assumed."""
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    if ledger.get("status") != "OPEN":
        raise WorkbenchError("SESSION_DECIDED",
                             "The session already has a verdict. Open a new session (devil-open "
                             "--force) before recording another outside view.")
    reference_class = args.reference_class.strip()
    if len(reference_class) < 10:
        raise WorkbenchError(
            "REFERENCE_CLASS_TOO_SHORT",
            "Name the reference class in at least 10 characters — 'comparable tool adoptions of "
            "this kind', not 'everyone'.",
        )
    base_rate = args.base_rate
    if not 0 <= base_rate <= 100:
        raise WorkbenchError("BASE_RATE_RANGE", "Base rate is a percentage: 0-100.")
    adjustment = (args.adjustment or "none").strip()
    if base_rate <= 50 and adjustment.lower() in ("none", "", "-"):
        # Mechanical optimism-bias flag: the reference class says most fail, and
        # nobody argued why this case differs. That is a SERIOUS open challenge.
        cid = f"C{len(ledger['challenges']) + 1}"
        challenge = {
            "id": cid,
            "assumption": "this case beats the reference class",
            "attack": f"The outside view says only ~{base_rate}% of {reference_class} succeed, "
                      "and no adjustment was argued for why this attempt differs. The plan "
                      "proceeds on optimism, not evidence.",
            "category": "unfounded-assumption",
            "severity": "SERIOUS",
            "defeater": "a concrete, checkable reason this attempt differs from the class "
                        "(not 'we will try harder')",
            "status": "OPEN",
            "rebuttal": None,
            "rebuttal_basis": None,
            "auto": "outside-view",
            "created_at": utc_now_iso(),
        }
        ledger["challenges"].append(challenge)
    ledger["outside_view"] = {
        "reference_class": reference_class,
        "base_rate": base_rate,
        "adjustment": adjustment,
        "recorded_at": utc_now_iso(),
    }
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    result: Dict[str, Any] = {
        "status": "OK",
        "outside_view": ledger["outside_view"],
        "open_counts": _devil_open_counts(ledger),
        "optimism_bias_flagged": bool(
            base_rate <= 50 and adjustment.lower() in ("none", "", "-")),
    }
    if result["optimism_bias_flagged"]:
        result["note"] = ("Bad base rate + no adjustment → an auto SERIOUS challenge is now open: "
                          "the plan must beat the reference class, and that is now an assumption "
                          "under attack. Rebut it with the concrete reason this case differs, or "
                          "change the plan.")
    return result


def cmd_devil_consequence(args: argparse.Namespace) -> Dict[str, Any]:
    """Second-order effects: 'and then what?'. First-order thinking stops at the
    plan's intended effect; the interesting failures live one and two levels
    later — what the effect causes, and what that causes. Three levels, each a
    full sentence, forced before the verdict so 'we did not see it coming' is
    on record as a choice."""
    path, ledger = _load_devil_ledger(Path(args.state_dir))
    if ledger.get("status") != "OPEN":
        raise WorkbenchError("SESSION_DECIDED",
                             "The session already has a verdict. Open a new session (devil-open "
                             "--force) before mapping more consequences.")
    l1 = args.l1.strip()
    l2 = args.l2.strip()
    l3 = (args.l3 or "").strip()
    if len(l1) < 15 or len(l2) < 15:
        raise WorkbenchError(
            "LEVELS_TOO_SHORT",
            "Each consequence level is a full sentence (min 15 chars): what happens (L1), what "
            "that causes (L2), what that causes (L3). 'Chaos' is not a consequence.",
        )
    if l3 and len(l3) < 15:
        raise WorkbenchError("L3_TOO_SHORT",
                             "L3 is optional, but if present it is a full sentence (min 15 chars).")
    entry = {
        "l1": l1,
        "l2": l2,
        "l3": l3 or None,
        "recorded_at": utc_now_iso(),
    }
    ledger.setdefault("consequences", []).append(entry)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "consequence": entry,
        "consequence_count": len(ledger["consequences"]),
        "next": "Map the top risks this deep, then challenge any level with no owner: "
                "devil-challenge --category second-order-effect ...",
    }


# ------------------------------------------------------- decision-journal
# The feedback loop: log decisions with falsifiable predictions and
# confidences, resolve them against reality, and read the calibration
# report. Advice that is never scored is advice that cannot improve.

def _load_journal(state_dir: Path, required: bool = True) -> Tuple[Path, Dict[str, Any]]:
    ensure_state_dir(state_dir)
    path = state_dir / JOURNAL_LEDGER_NAME
    if required and not path.exists():
        raise WorkbenchError(
            "NO_JOURNAL",
            "No decision journal exists yet. Start one: journal-log --decision ... "
            "--prediction ... --confidence N --review-by YYYY-MM-DD.",
        )
    return path, (load_json(path, {"entries": []}) if path.exists() else {"entries": []})


def cmd_journal_log(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    path, journal = _load_journal(state_dir, required=False)
    decision = args.decision.strip()
    prediction = args.prediction.strip()
    if len(decision) < 15:
        raise WorkbenchError(
            "DECISION_TOO_SHORT",
            "Name the decision in at least 15 characters — what was chosen, not that a choice happened.",
        )
    if len(prediction) < 15:
        raise WorkbenchError(
            "PREDICTION_TOO_SHORT",
            "State the falsifiable prediction in at least 15 characters — something reality can "
            "later grade, not an aspiration ('it will go well' cannot be graded).",
        )
    if not 0 <= args.confidence <= 100:
        raise WorkbenchError("CONFIDENCE_RANGE", "Confidence is a percentage: 0-100.")
    try:
        review_by = dt.date.fromisoformat(args.review_by.strip())
    except ValueError:
        raise WorkbenchError("BAD_DATE", "Review date must be YYYY-MM-DD.")
    entry = {
        "id": f"J{len(journal['entries']) + 1}",
        "decision": decision,
        "prediction": prediction,
        "confidence": args.confidence,
        "review_by": args.review_by.strip(),
        "mind_changer": (args.mind_changer or "").strip() or None,
        "context": (args.context or "").strip() or None,
        "status": "OPEN",
        "outcome": None,
        "lesson": None,
        "logged_at": utc_now_iso(),
        "resolved_at": None,
    }
    journal["entries"].append(entry)
    journal["updated_at"] = utc_now_iso()
    save_json(path, journal)
    return {
        "status": "OK",
        "entry": entry,
        "open_count": sum(1 for e in journal["entries"] if e["status"] == "OPEN"),
        "next": ("When the review date arrives (or reality answers first): "
                 f"journal-resolve --id {entry['id']} --outcome HIT|MISS|PARTIAL --lesson '...'"),
    }


def cmd_journal_resolve(args: argparse.Namespace) -> Dict[str, Any]:
    path, journal = _load_journal(Path(args.state_dir))
    target = None
    for e in journal["entries"]:
        if e["id"] == args.id:
            target = e
            break
    if target is None:
        raise WorkbenchError("UNKNOWN_ENTRY",
                             f"No journal entry with id {args.id}.",
                             {"known": [e["id"] for e in journal["entries"]]})
    if target["status"] == "RESOLVED":
        raise WorkbenchError(
            "ENTRY_RESOLVED",
            f"{args.id} is already resolved as {target['outcome']}: {target['lesson'][:80]}",
        )
    lesson = args.lesson.strip()
    if len(lesson) < 15:
        raise WorkbenchError(
            "LESSON_TOO_SHORT",
            "Write the lesson in at least 15 characters — what you would do differently, not "
            "what happened (the outcome field already records that).",
        )
    target["status"] = "RESOLVED"
    target["outcome"] = args.outcome
    target["lesson"] = lesson
    target["resolved_at"] = utc_now_iso()
    journal["updated_at"] = utc_now_iso()
    save_json(path, journal)
    return {
        "status": "OK",
        "entry": target,
        "open_count": sum(1 for e in journal["entries"] if e["status"] == "OPEN"),
    }


def cmd_journal_report(args: argparse.Namespace) -> Dict[str, Any]:
    path, journal = _load_journal(Path(args.state_dir), required=False)
    entries = journal["entries"]
    if not entries:
        raise WorkbenchError(
            "EMPTY_JOURNAL",
            "The journal has no entries. Log one: journal-log --decision ... --prediction ... "
            "--confidence N --review-by YYYY-MM-DD.",
        )
    resolved = [e for e in entries if e["status"] == "RESOLVED"]
    today = dt.date.today().isoformat()
    overdue = [e for e in entries
               if e["status"] == "OPEN" and e["review_by"] < today]

    def band_of(conf: int) -> Optional[Tuple[int, int]]:
        for band in JOURNAL_BANDS:
            if band[0] <= conf <= band[1]:
                return band
        return None

    bands: List[Dict[str, Any]] = []
    for lo, hi in JOURNAL_BANDS:
        members = [e for e in resolved if lo <= e["confidence"] <= hi]
        if not members:
            continue
        score = sum(1.0 if e["outcome"] == "HIT" else 0.5 if e["outcome"] == "PARTIAL" else 0.0
                    for e in members)
        hit_rate = round(score / len(members) * 100)
        avg_conf = round(sum(e["confidence"] for e in members) / len(members))
        bands.append({
            "band": f"{lo}-{hi}%",
            "resolved": len(members),
            "avg_confidence": avg_conf,
            "hit_rate": hit_rate,
            "gap": avg_conf - hit_rate,
            "overconfident": avg_conf - hit_rate > 15,
        })
    overall: Optional[Dict[str, Any]] = None
    overconfidence_flag = False
    if resolved:
        score = sum(1.0 if e["outcome"] == "HIT" else 0.5 if e["outcome"] == "PARTIAL" else 0.0
                    for e in resolved)
        hit_rate = round(score / len(resolved) * 100)
        avg_conf = round(sum(e["confidence"] for e in resolved) / len(resolved))
        overconfidence_flag = avg_conf - hit_rate > 15
        overall = {
            "resolved": len(resolved),
            "open": len(entries) - len(resolved),
            "avg_confidence": avg_conf,
            "hit_rate": hit_rate,
            "gap": avg_conf - hit_rate,
            "overconfident": overconfidence_flag,
        }
    return {
        "status": "OK",
        "entries_total": len(entries),
        "resolved": len(resolved),
        "open": len(entries) - len(resolved),
        "overdue": [{"id": e["id"], "decision": e["decision"], "review_by": e["review_by"]}
                    for e in overdue],
        "overdue_count": len(overdue),
        "bands": bands,
        "overall": overall,
        "verdict_note": (
            "Overconfident: when you say 85%+, be right 85 times out of 100. Widen your "
            "confidence spread or sharpen your predictions — the next decision is priced "
            "off these numbers."
        ) if overconfidence_flag else
        ("Calibration is honest within 15 points. Keep resolving on evidence, not on hope." if resolved
         else "No resolved entries yet — the calibration math starts after the first resolution."),
    }


# ------------------------------------------------------------ playbooks
# Orchestration without a state machine: pre-composed skill chains for the
# recurring work shapes. Each step names the skill, what it contributes, and
# the gate that must pass before the next step starts. Deterministic — the
# same playbook always renders the same chain.

PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "decide": {
        "purpose": "Options on the table, a commitment to make — from vague ask to journaled decision",
        "steps": [
            {"skill": "question-contract",
             "does": "pin the question, the decision it informs, the consumer, decided vs open",
             "gate": "qc-check returns READY — never compare options for an unpinned question"},
            {"skill": "decision-review",
             "does": "score the 2-3 real options on 3-5 weighted criteria; name the reversibility class",
             "gate": "the winning option is known and the flip criterion is named"},
            {"skill": "wide-search",
             "does": "optional: comparison table when option facts are thin (every cell sourced or a declared gap)",
             "gate": "no ? cells left in the matrix feeding the decision"},
            {"skill": "devil-advocate",
             "does": "attack the WINNER: plan, premortem, outside view, challenges, consequences",
             "gate": "verdict is not BLOCK — open SERIOUS challenges become guards on record"},
            {"skill": "decision-journal",
             "does": "log the decision with its falsifiable prediction, confidence and review date",
             "gate": "the entry exists and its mind-changer is named"},
            {"skill": "artifact-studio",
             "does": "write the ADR: options, decision, guards as rollback triggers, kill criteria",
             "gate": "adr-check passes on the written ADR"},
        ],
    },
    "investigate": {
        "purpose": "A question that needs evidence, not opinion — from topic to cited synthesis",
        "steps": [
            {"skill": "question-contract",
             "does": "pin the question and the decision it informs; budget the queries",
             "gate": "qc-check returns READY"},
            {"skill": "web-search",
             "does": "the whole playbook if the question is one fact needing 1-3 sources",
             "gate": "one authoritative page opened and quoted verbatim — else escalate down"},
            {"skill": "deep-research",
             "does": "sub-questions, ledger, sources, claims with quotes, contradictions, gaps",
             "gate": "query budget respected; gaps declared instead of silently narrowed"},
            {"skill": "evidence-audit",
             "does": "every claim in the draft maps to an opened source with a quote",
             "gate": "audit-report PASS — deliver nothing on FAIL"},
            {"skill": "artifact-studio",
             "does": "the report: answer first, evidence behind, gaps stated",
             "gate": "report reads answer-first for the named consumer"},
            {"skill": "knowledge-capture",
             "does": "save the reusable Q&A so this research is never done twice",
             "gate": "kb-search finds the entry on the obvious keywords"},
        ],
    },
    "build": {
        "purpose": "Make a thing — from request to delivered, verified work",
        "steps": [
            {"skill": "question-contract",
             "does": "pin the goal, non-goals and the consumer of the result",
             "gate": "qc-check READY — non-goals exist (a build without non-goals grows until it dies)"},
            {"skill": "spec-builder",
             "does": "stories into Given/When/Then criteria; tasks that verify criteria",
             "gate": "spec-check PASS before any implementation"},
            {"skill": "local-debug",
             "does": "when stuck: repro, one falsifiable hypothesis at a time",
             "gate": "two falsified hypotheses → stop, debug-report, ask for what is missing"},
            {"skill": "code-review",
             "does": "the diff: findings with locations, severities, fixes",
             "gate": "no open BLOCKING finding — the verdict is mechanical"},
            {"skill": "delivery-verify",
             "does": "prove it works at the level the claim requires",
             "gate": "'done' is never said above the observed level"},
            {"skill": "knowledge-capture",
             "does": "save the decisions and gotchas the next builder needs",
             "gate": "kb-search hits on the obvious keywords"},
        ],
    },
    "launch": {
        "purpose": "Put something in front of real users — with the failure story written first",
        "steps": [
            {"skill": "question-contract",
             "does": "pin the launch question, the success metric and the audience",
             "gate": "qc-check READY"},
            {"skill": "delivery-verify",
             "does": "prove the thing works before anyone argues about launching it",
             "gate": "verification at the level the launch claim implies"},
            {"skill": "devil-advocate",
             "does": "archetype launch: premortem (day-three screenshot), outside view, demand evidence",
             "gate": "verdict is not BLOCK; guards and kill criteria on record"},
            {"skill": "decision-journal",
             "does": "log the adoption prediction with confidence and the review date",
             "gate": "kill criteria double as the review trigger — dated and owned"},
            {"skill": "artifact-studio",
             "does": "the announcement: what it is, for whom, what changes for them",
             "gate": "reads in 60 seconds by the named audience"},
            {"skill": "knowledge-capture",
             "does": "post-launch: what the first users actually did vs the prediction",
             "gate": "the journal entry gets resolved on evidence, on its date"},
        ],
    },
    "debug": {
        "purpose": "Something is broken — from symptom to fixed, proven, and learned-from",
        "steps": [
            {"skill": "local-debug",
             "does": "smallest repro, the named file only, one falsifiable hypothesis at a time",
             "gate": "root cause found within two hypotheses, or debug-report escalates"},
            {"skill": "code-review",
             "does": "the fix diff: does it fix the cause or paint over the symptom",
             "gate": "no open BLOCKING finding on the fix"},
            {"skill": "delivery-verify",
             "does": "prove the fix: the original repro now passes at the right level",
             "gate": "observed evidence, not 'should work now'"},
            {"skill": "knowledge-capture",
             "does": "root cause as Q&A: the symptom phrased the way the next person will hit it",
             "gate": "kb-search hits on the symptom keywords"},
            {"skill": "decision-journal",
             "does": "if the root cause implies a process decision (not just a bug): log it",
             "gate": "prediction + review date exist, or the step is honestly skipped"},
        ],
    },
}


def cmd_playbook_list(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "status": "OK",
        "playbooks": [
            {"name": name, "purpose": pb["purpose"],
             "steps": [s["skill"] for s in pb["steps"]]}
            for name, pb in sorted(PLAYBOOKS.items())
        ],
        "next": "playbook-show --name NAME renders the chain with gates and handoffs.",
    }


def cmd_playbook_show(args: argparse.Namespace) -> Dict[str, Any]:
    pb = PLAYBOOKS.get(args.name)
    if pb is None:
        raise WorkbenchError("UNKNOWN_PLAYBOOK",
                             f"Unknown playbook '{args.name}'.",
                             {"known": sorted(PLAYBOOKS)})
    lines: List[str] = [
        f"# Playbook: {args.name}",
        "",
        pb["purpose"],
        "",
        "Run the steps in order. A gate that fails stops the chain — fix the gate or "
        "explicitly record why you are skipping the step; a skipped gate silently is "
        "the difference between a pipeline and a vibe.",
        "",
    ]
    for i, step in enumerate(pb["steps"], 1):
        lines.append(f"## {i}. {step['skill']}")
        lines.append(f"- Does: {step['does']}")
        lines.append(f"- Gate: {step['gate']}")
        lines.append("")
    lines.append("## Handoffs that make the chain work")
    lines.append("")
    lines.append("- The contract is every step's intake: no step re-asks what qc-pin settled.")
    lines.append("- Guards and kill criteria from devil-advocate land in the ADR's rollback triggers.")
    lines.append("- The journal closes the loop: the prediction written at launch is the lesson read later.")
    return {
        "status": "OK",
        "name": args.name,
        "purpose": pb["purpose"],
        "steps": pb["steps"],
        "handoffs": [
            "the contract is every step's intake",
            "guards and kill criteria land in the ADR rollback triggers",
            "the journal prediction closes the loop",
        ],
        "rendered": "\n".join(lines),
    }


# ------------------------------------------------------ question-contract
# Pin the question before spending tokens on it: the decision it informs,
# who consumes the answer, what is already decided and what is genuinely
# open. The most expensive AI failure is a brilliant answer to the wrong
# question, and it is also the most preventable.

def _qc_scan_vague(question: str) -> List[Dict[str, str]]:
    """Deterministic vague-term scan: every vague word found in the pinned
    question, each with the clarifying question it demands."""
    text = " " + question.lower() + " "
    hits: List[Dict[str, str]] = []
    for term, ask in sorted(QC_VAGUE_TERMS.items()):
        pattern = _WORD_START + re.escape(term)
        if re.search(pattern, text):
            hits.append({"term": term, "ask": ask})
    return hits


def _load_qc_ledger(state_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    ensure_state_dir(state_dir)
    path = state_dir / QC_LEDGER_NAME
    if not path.exists():
        raise WorkbenchError(
            "NO_QC_SESSION",
            "No question contract is pinned. Start one: qc-pin --question \"...\" "
            "--decision \"what this answer will inform\".",
        )
    return path, load_json(path, {})


def cmd_qc_pin(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = ensure_state_dir(Path(args.state_dir))
    path = state_dir / QC_LEDGER_NAME
    question = args.question.strip()
    decision = args.decision.strip()
    if len(question) < 15:
        raise WorkbenchError(
            "QUESTION_TOO_SHORT",
            "State the question in at least 15 characters — a question that short is a topic, "
            "not a question, and topics do not have answers.",
        )
    if len(decision) < 10:
        raise WorkbenchError(
            "DECISION_TOO_SHORT",
            "Name the decision this answer will inform in at least 10 characters. If no decision "
            "is informed, the answer is trivia; pin what the answer is FOR.",
        )
    if path.exists() and not args.force:
        raise WorkbenchError(
            "QC_SESSION_EXISTS",
            f"{path} already holds a contract. Pass --force to re-pin (assumptions are wiped).",
        )
    consumer = (args.consumer or "").strip()
    ledger = {
        "question": question,
        "decision": decision,
        "consumer": consumer or None,
        "budget": (args.budget or "").strip() or None,
        "decided": [d.strip() for d in (args.decided or []) if d.strip()],
        "open": [o.strip() for o in (args.open or []) if o.strip()],
        "assumptions": [],
        "status": "OPEN",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    save_json(path, ledger)
    vague = _qc_scan_vague(question)
    result: Dict[str, Any] = {
        "status": "OK",
        "contract": ledger,
        "vague_terms": vague,
        "next": "qc-check (the gate) — then research, analyze or build against the contract.",
    }
    if vague:
        result["note"] = ("Vague terms found in the question. Each one makes the answer "
                          "unjudgeable; ask the single most answer-changing question before "
                          "proceeding, or record assumptions with qc-assume.")
    return result


def cmd_qc_check(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_qc_ledger(Path(args.state_dir))
    missing: List[str] = []
    if len(ledger.get("question", "")) < 15:
        missing.append("question (min 15 chars)")
    if len(ledger.get("decision", "")) < 10:
        missing.append("decision (what this answer informs, min 10 chars)")
    if not ledger.get("consumer"):
        missing.append("consumer (who reads this answer, and in what form)")
    vague = _qc_scan_vague(ledger.get("question", ""))
    ledger["checked_at"] = utc_now_iso()
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    if missing:
        return {
            "status": "FAIL",
            "gate": "NEEDS_INPUT",
            "missing": missing,
            "vague_terms": vague,
            "exit_hint": 2,
            "next": "Ask the user for the missing fields (one message), re-pin with --force, "
                    "or proceed and record the guesses as assumptions with qc-assume.",
        }
    return {
        "status": "OK",
        "gate": "READY",
        "missing": [],
        "vague_terms": vague,
        "clarify_opportunities": [v["ask"] for v in vague][:3],
        "next": "Answer against the contract. If a vague term survives, qc-assume the "
                "interpretation you chose and state it in the answer's caveat.",
    }


def cmd_qc_assume(args: argparse.Namespace) -> Dict[str, Any]:
    path, ledger = _load_qc_ledger(Path(args.state_dir))
    assumptions = [a.strip() for a in (args.assumption or []) if a.strip()]
    if not assumptions:
        raise WorkbenchError(
            "ASSUMPTIONS_REQUIRED",
            "Record at least one assumption (--assumption, repeatable) — the interpretation "
            "you chose where the question was ambiguous.",
        )
    for a in assumptions:
        if len(a) < 10:
            raise WorkbenchError("ASSUMPTION_TOO_SHORT",
                                 f"An assumption is a full statement (min 10 chars): '{a}' is not one.")
    ledger["assumptions"].extend(assumptions)
    ledger["updated_at"] = utc_now_iso()
    save_json(path, ledger)
    return {
        "status": "OK",
        "assumptions": ledger["assumptions"],
        "assumption_count": len(ledger["assumptions"]),
        "next": "State every assumption in the answer's caveat — an unstated assumption is "
                "a landmine the next reader steps on.",
    }


# ---------------------------------------------------------- load-skills
# Deterministic prompt → skill routing. Given the user's request text this
# decides which skills to load and emits the brief the agent should follow:
# read order, template to fill, first command, stop rule. No LLM, no
# network — the same request always routes the same way (testable).

SKILL_ROUTES: Dict[str, Dict[str, Any]] = {
    "local-advisor": {
        "wants": "Advice, design review, 'what should I do', architecture or planning help",
        "wants_tr": "Danışma, tasarım incelemesi, 'ne yapmalıyım', mimari/planlama yardımı",
        "core": "1) Restate the ask as a decision or design question. 2) Answer from what is already in the conversation: recommendation first, then the top risk and the one fact that would change it. 3) If stakes are high or two options are close, hand off to decision-review instead of padding the answer.",
        "triggers": ["advice", "should i", "what should", "recommend", "opinion", "architecture",
                     "plan ", "planning", "help me decide how", "ne yapmalı", "öner", "tavsiye", "fikrin",
                     "mimari", "değerlendirir misin"],
        "read": ["SKILL.md", "references/advisory-modes.md", "references/answer-standards.md"],
        "template": "templates/advisory-brief.md",
        "first_command": "advise-intake --question ... --context ... --mode planning",
        "stop_rule": "ask one precise question when context is missing; do not scan files by default",
        "also_consider": ["question-contract", "decision-review", "devil-advocate"],
        "fallback": True,
    },
    "decision-review": {
        "wants": "Choose between options, an ADR, a trade-off matrix, a pre-mortem",
        "wants_tr": "Seçenekler arasında seçim, ADR, ödünleşim matrisi, ön-ötüp",
        "core": "1) List the options and the hard constraints. 2) Score the top 2-3 options on 3-5 weighted criteria. 3) Name the reversibility class and the single criterion whose score could flip the winner.",
        "triggers": ["choose", "decide", "decision", "adr", "trade-off", "pre-mortem", "option",
                     "which option", "hangisini seç", "karar", "kararsız", "tercih etmeli",
                     "seçenek"],
        "read": ["SKILL.md", "references/scoring-guide.md", "references/reversibility-classes.md"],
        "template": "templates/adr.md",
        "first_command": "decision-score --spec-file decision.json",
        "stop_rule": "the decision is not final until the ADR passes adr-check",
        "also_consider": ["wide-search", "devil-advocate", "decision-journal"],
    },
    "local-debug": {
        "wants": "A bug, failing test or stack trace in a named file",
        "wants_tr": "İsimlendirilmiş bir dosyada hata, düşen test veya stack trace",
        "core": "1) Reproduce with the smallest case; read only the named file. 2) State one falsifiable hypothesis and test it. 3) Two failed hypotheses → stop, run debug-report, ask for the missing information.",
        "triggers": ["bug", "error", "stack trace", "traceback", "exception", "fails", "failing",
                     "broken", "crash", "neden", "hata", "çalışmıyor", "patlıyor", "çöküyor",
                     "düşüyor"],
        "read": ["SKILL.md", "references/hypothesis-discipline.md", "references/escalation.md"],
        "template": "templates/root-cause-report.md",
        "first_command": "debug-hypothesis --symptom ... --target-file ... --repro ...",
        "stop_rule": "stop after 2 falsified hypotheses; run debug-report and ask for the missing information",
        "also_consider": ["code-review"],
    },
    "web-search": {
        "wants": "One factual answer that needs 1-3 sources (version, price, limit, date)",
        "wants_tr": "1-3 kaynak gerektiren tek bilgisel cevap (sürüm, fiyat, limit, tarih)",
        "core": "1) Search once for the exact fact. 2) Open one authoritative page and quote it verbatim. 3) Answer with quote + link, or declare the gap — never cite from memory.",
        "triggers": ["what is the latest", "which version", "how much does", "current price",
                     "release date", "supports", "sürüm", "fiyat", "kaç para", "destekliyor mu",
                     "güncel"],
        "read": ["SKILL.md", "references/quick-verification-protocol.md", "references/host-tools.md"],
        "template": "templates/search-log.md",
        "first_command": "none (use the host's own search tool, then log the query)",
        "stop_rule": "cite a page only after opening it; quote it verbatim in the log",
        "also_consider": ["deep-research"],
    },
    "deep-research": {
        "wants": "Research with several sources and a synthesis",
        "wants_tr": "Birden çok kaynak ve sentez gerektiren araştırma",
        "core": "1) Split the topic into 3-5 sub-questions with a query budget. 2) For each: search, open the page, register source + claim with its quote. 3) Synthesize only from registered claims; what is missing stays a declared gap.",
        "triggers": ["research", "investigate", "deep dive", "multiple sources", "synthesis",
                     "evidence for", "araştır", "kaynak", "literatür", "derinlemesine",
                     "kanıtlarla"],
        "read": ["SKILL.md", "references/research-protocol.md", "references/source-quality.md",
                 "references/synthesis-standard.md"],
        "template": "templates/research-notebook.md",
        "first_command": "research-init --topic ... --sub-question ... --max-queries 8",
        "stop_rule": "stop at the query budget; record remaining gaps instead of continuing silently",
        "also_consider": ["question-contract", "web-search", "evidence-audit"],
    },
    "wide-search": {
        "wants": "Compare many entities across the same fields, as a table",
        "wants_tr": "Birden çok varlığı aynı alanlarda tablo olarak karşılaştırma",
        "core": "1) Fix the entity × field matrix before searching. 2) Fill each cell from a page you actually opened. 3) Every remaining '?' becomes a sourced value or a declared gap.",
        "triggers": ["compare", "comparison", " vs ", "versus", "which is better", "alternatives",
                     "matrix", "karşılaştır", "hangisi daha", "alternatif", "matris",
                     "tablo olarak"],
        "read": ["SKILL.md", "references/matrix-method.md"],
        "template": "templates/wide-comparison-matrix.md",
        "first_command": "research-init --mode wide-matrix --entity ... --field ...",
        "stop_rule": "a ? cell is not acceptable in the final matrix — search, or declare a gap",
        "also_consider": ["deep-research", "decision-review"],
    },
    "evidence-audit": {
        "wants": "Check a draft's sources, numbers and claims",
        "wants_tr": "Bir taslağın kaynaklarını, sayılarını ve iddialarını denetleme",
        "core": "1) Extract every claim and number from the draft. 2) Check each against an opened source (link + verbatim quote). 3) Verdict is PASS only when every claim is grounded; otherwise list exactly what to fix.",
        "triggers": ["audit", "fact-check", "check the claims", "verify sources", "citations",
                     "denetle", "denetim", "iddiaları kontrol", "kaynakları kontrol"],
        "read": ["SKILL.md", "references/audit-rules.md"],
        "template": "templates/audit-verdict.md",
        "first_command": "audit-report --report-file FILE",
        "stop_rule": "deliver only on PASS; a FAIL lists exactly what must be fixed",
        "also_consider": ["deep-research"],
    },
    "delivery-verify": {
        "wants": "Prove that a change works before saying 'done'",
        "wants_tr": "'Bitti' demeden önce değişikliğin çalıştığını kanıtlama",
        "core": "1) Pick the verification level the claim requires. 2) Run the real command and capture its output. 3) Report at the observed level only — 'tested' means the test ran.",
        "triggers": ["prove", "verify delivery", "does it work", "is it done", "tested",
                     "before merging", "kanıtla", "teslim", "çalıştığını göster",
                     "test edildi mi"],
        "read": ["SKILL.md", "references/level-selection.md"],
        "template": "templates/delivery-evidence.md",
        "first_command": "verify-delivery --check L2:... --command ...",
        "stop_rule": "never say 'done' or 'tested' above the level you observed",
        "also_consider": ["evidence-audit"],
    },
    "artifact-studio": {
        "wants": "Write a report, ADR, executive summary, slide outline or data schema",
        "wants_tr": "Rapor, ADR, yönetici özeti, sunum iskeleti veya veri şeması yazma",
        "core": "1) Pick the template matching the artifact type. 2) Fill every section from logged facts. 3) No invented content — sections without material stay marked TODO with the reason.",
        "triggers": ["write a report", "document", "executive summary", "presentation",
                     "postmortem", "data schema", "rapor yaz", "rapor hazırla", "doküman",
                     "özet çıkar", "sunum", "şema"],
        "read": ["SKILL.md", "references/writing-standards.md"],
        "template": "templates/technical-report.md",
        "first_command": "artifact-new --type ... --title ... --output ...",
        "stop_rule": "no pre-written content — the template provides structure, you provide substance",
        "also_consider": ["evidence-audit"],
    },
    "session-handoff": {
        "wants": "End, switch tools, delegate or resume work",
        "wants_tr": "Oturumu bitirme, araç değiştirme, devretme veya kaldığı yerden devam",
        "core": "1) List the state: done / in flight / blocked, each with file paths and the next command. 2) Write the handoff pack. 3) Reader test: the next agent must be able to start without asking anything.",
        "triggers": ["handoff", "end the session", "switch tools", "resume", "pick up tomorrow",
                     "devir", "devret", "oturumu bitir", "kaldığım yerden", "yarın devam"],
        "read": ["SKILL.md", "references/handoff-protocol.md", "references/state-inventory.md"],
        "template": "templates/handoff-pack.md",
        "first_command": "handoff-pack --title ... --session-status ...",
        "stop_rule": "a handoff that forces the reader to ask 'where is the context?' has failed",
        "also_consider": [],
    },
    "spec-builder": {
        "wants": "Turn a request into a testable spec with acceptance criteria",
        "wants_tr": "Bir talebi kabul kriterli, sınanabilir bir tarif dosyasına çevirme",
        "core": "1) Write goal and non-goals as one-liners. 2) Turn stories into Given/When/Then criteria. 3) Break into tasks that each verify at least one criterion; spec-check must pass before code.",
        "triggers": ["spec", "specification", "acceptance criteria", "user story", "requirements",
                     "spesifikasyon", "kabul kriteri", "gereksinim", "istenenleri tarif"],
        "read": ["SKILL.md", "references/acceptance-criteria.md", "references/task-breakdown.md"],
        "template": "templates/spec.md",
        "first_command": "spec-new --goal ... --story ... --non-goal ...",
        "stop_rule": "spec-check must PASS before implementation starts",
        "also_consider": ["delivery-verify", "devil-advocate"],
    },
    "code-review": {
        "wants": "A structured, severity-graded review of named files or a diff",
        "wants_tr": "İsimlendirilmiş dosyaların veya diff'in yapılandırılmış, dereceli incelemesi",
        "core": "1) Read the diff only. 2) Report findings with file:line, severity and the fix. 3) The verdict stays FAIL while a BLOCKING finding is open.",
        "triggers": ["code review", "review my code", "review the diff", "pr review", "severity",
                     "kod incele", "kod incelemesi", "gözden geçir", "diff'i incele"],
        "read": ["SKILL.md", "references/severity-model.md", "references/review-checklist.md"],
        "template": "templates/findings-report.md",
        "first_command": "review-init --title ... --target ...",
        "stop_rule": "the verdict is FAIL while any BLOCKING finding is open",
        "also_consider": ["local-debug"],
    },
    "knowledge-capture": {
        "wants": "Save, find and reuse reusable project knowledge as sourced Q&A",
        "wants_tr": "Yeniden kullanılabilir proje bilgisini kaynaklı soru-cevap olarak saklama",
        "core": "1) Write the question as the future user will phrase it. 2) Answer in ≤5 sentences, sourced or explicitly marked assumed. 3) Verify findability: kb-search must hit on the obvious keywords.",
        "triggers": ["remember this", "save this", "knowledge base", "reusable", "we decided",
                     "kaydet", "unutma", "bilgi tabanı", "tekrar kullan", "kararımızı kaydet"],
        "read": ["SKILL.md", "references/entry-standards.md", "references/lifecycle.md"],
        "template": "templates/kb-entry.md",
        "first_command": "kb-add --question ... --answer ... --source-url ...",
        "stop_rule": "entries are sourced or explicitly marked assumed — never present an assumption as fact",
        "also_consider": [],
    },
    "data-analysis": {
        "wants": "Analyze a data file the user provides (CSV, TSV, JSON, logs) with traceable numbers",
        "wants_tr": "Kullanıcının verdiği veri dosyasını (CSV, TSV, JSON, log) izlenebilir sayılarla analiz",
        "core": "1) Register the dataset (hash + question). 2) Log every number as a finding with the command or formula that produced it. 3) Answer only with logged findings; declare gaps instead of guessing.",
        "triggers": ["analyze", "analysis", "dataset", "csv", "tsv", "json file", "spreadsheet",
                     "data file", "how many rows", "trend in", "analiz", "veri seti", "verileri",
                     "kaç satır", "excel"],
        "read": ["SKILL.md", "references/dataset-intake.md", "references/computation-ledger.md",
                 "references/pitfalls.md"],
        "template": "templates/analysis-report.md",
        "first_command": "data-register --path FILE --question ...",
        "stop_rule": "never present a number that is not a logged finding — compute it or declare a gap",
        "also_consider": ["wide-search", "evidence-audit"],
    },
    "devil-advocate": {
        "wants": "Stress-test a plan, decision or spec before committing — the adversarial second opinion",
        "wants_tr": "Bir planı, kararı veya spesifikasyonu taahhüt öncesi stres testine sokma — advers ikinci görüş",
        "core": "1) Steelman the plan honestly. 2) Attack the 2-3 load-bearing assumptions, each with severity and what would defeat it. 3) The verdict is mechanical: BLOCK while a FATAL stands, GUARDS while a SERIOUS stands.",
        "triggers": ["devil's advocate", "devil advocate", "play devil", "what could go wrong",
                     "what's wrong with", "poke holes", "stress test", "stress-test",
                     "second opinion", "convince me this is wrong", "challenge this plan",
                     "too good to be true", "şeytanın avukat", "avukatlığını", "avukatını oyna",
                     "delik bul", "delik aç", "stres testi", "ikinci görüş", "neden yanlış",
                     "nereden yanıl", "zayıf nokta", "karşı argüman", "itiraz et"],
        "read": ["SKILL.md", "references/challenge-discipline.md", "references/attack-categories.md",
                 "references/premortem-protocol.md", "references/outside-view.md"],
        "template": "templates/challenge-report.md",
        "first_command": "devil-plan --archetype build|launch|migrate|hire|buy|process, then devil-open --claim \"the plan in one sentence\" --steelman \"its best case, honestly\"",
        "stop_rule": "the verdict is BLOCK while any FATAL challenge is unanswered — answer it or change the plan",
        "also_consider": ["decision-review", "evidence-audit", "decision-journal"],
    },
    "question-contract": {
        "wants": "Pin what the question actually is — the decision it informs, the consumer, the budget — before research, analysis or building",
        "wants_tr": "Sorunun gerçekte ne olduğunu sabitleme — hangi karara girdi verecek, kim okuyacak, bütçe ne — araştırma/analiz/yapım öncesi",
        "core": "1) Restate the ask as the question, the decision it informs and who consumes the answer. 2) Scan for vague terms; ask the ONE question that would most change the answer, if any. 3) Proceed with qc-assume'd stated assumptions when nobody can answer; never silently guess scope.",
        "triggers": ["clarify", "before we start", "before you research", "what i actually need",
                     "real question", "scope it", "tam olarak ne", "gerçek soru", "önce netleştir",
                     "netleştirir misin", "kapsamı netleştir"],
        "read": ["SKILL.md", "references/contract-fields.md", "references/vague-terms.md"],
        "template": "templates/question-contract.md",
        "first_command": "qc-pin --question \"...\" --decision \"what this answer will inform\"",
        "stop_rule": "never answer a question whose decision and consumer are unpinned; proceed with qc-assume'd assumptions when the user cannot answer",
        "also_consider": ["local-advisor", "deep-research"],
    },
    "decision-journal": {
        "wants": "Log decisions with falsifiable predictions and confidences, resolve them against reality, read the calibration report",
        "wants_tr": "Kararları çürütülebilir tahmin ve güven düzeyiyle kaydetme, gerçeğe göre sonuçlandırma, kalibrasyon raporu okuma",
        "core": "1) Log the decision, its falsifiable prediction, your confidence (0-100) and a review date. 2) On the review date, resolve it HIT/MISS/PARTIAL with the lesson. 3) Read journal-report: confidence minus hit rate over 15 points means you are overconfident — spread your confidences.",
        "triggers": ["journal", "track this decision", "log the prediction", "how good were our calls",
                     "were we right", "calibration", "track record", "karar defteri",
                     "tahmini kaydet", "tahminler ne kadar tuttu", "haklı çıktık mı", "izleme kaydı"],
        "read": ["SKILL.md", "references/journal-discipline.md", "references/calibration.md"],
        "template": "templates/decision-entry.md",
        "first_command": "journal-log --decision ... --prediction ... --confidence N --review-by YYYY-MM-DD",
        "stop_rule": "resolve on evidence, not on hope; an overdue OPEN entry is a debt to reality",
        "also_consider": ["decision-review", "devil-advocate"],
    },
}

_WORD_START = r"(?<![a-z0-9çğıöşüâîû])"


def _trigger_hits(prompt: str, triggers: List[str]) -> List[str]:
    """Return the subset of triggers present in the prompt (word-start anchored,
    prefix matching so 'compare' also matches 'comparison' / 'comparing')."""
    text = " " + prompt.lower() + " "
    hits: List[str] = []
    for trig in triggers:
        needle = trig.lower()
        pattern = _WORD_START + re.escape(needle)
        if re.search(pattern, text):
            hits.append(trig)
    return hits


def _route_prompt(prompt: str) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for skill, route in SKILL_ROUTES.items():
        hits = _trigger_hits(prompt, route["triggers"])
        if hits:
            scored.append({"skill": skill, "score": len(hits), "hits": hits})
    scored.sort(key=lambda r: (-r["score"], r["skill"]))
    return scored


def _brief_for(skill: str) -> Dict[str, Any]:
    route = SKILL_ROUTES.get(skill)
    if not route:
        raise WorkbenchError("UNKNOWN_SKILL", f"no route for skill '{skill}'",
                             {"known": sorted(SKILL_ROUTES)})
    return {
        "skill": skill,
        "wants": route["wants"],
        "wants_tr": route["wants_tr"],
        "core": route["core"],
        "read_in_order": route["read"],
        "fill_template": route["template"],
        "first_command": route["first_command"],
        "stop_rule": route["stop_rule"],
        "also_consider": route["also_consider"],
    }


def _render_brief_text(prompt: Optional[str], briefs: List[Dict[str, Any]],
                       confidences: Dict[str, str]) -> str:
    lines: List[str] = ["# Skill brief — load into context, then follow the read order", ""]
    if prompt:
        lines.append(f"Routed from prompt: \"{prompt}\"")
        lines.append("")
    for i, b in enumerate(briefs, 1):
        conf = confidences.get(b["skill"], "")
        lines.append(f"## {i}) {b['skill']} ({conf})")
        lines.append("")
        lines.append(f"- **Use when**: {b['wants']} / {b['wants_tr']}")
        read = " → ".join(b["read_in_order"])
        lines.append(f"- **Read in order**: {read}")
        lines.append(f"- **Fill template**: {b['fill_template']}")
        lines.append(f"- **First command**: `$WB {b['first_command']}`"
                     if not b["first_command"].startswith("none")
                     else f"- **First command**: {b['first_command']}")
        lines.append(f"- **Stop rule**: {b['stop_rule']}")
        if b["also_consider"]:
            lines.append(f"- **Also consider**: {', '.join(b['also_consider'])}")
        lines.append("")
    lines.append("Follow progressive disclosure: read SKILL.md fully, open references only when")
    lines.append("the step needs them, fill the template only when writing the deliverable.")
    return "\n".join(lines)


def _render_brief_compact(prompt: Optional[str], briefs: List[Dict[str, Any]],
                          confidences: Dict[str, str]) -> str:
    """One line per skill: read order compressed to SKILL.md + counts, first command, stop rule.
    For routing passes where the full brief would cost more tokens than it saves."""
    lines: List[str] = ["# Skill brief (compact)"]
    if prompt:
        lines.append(f'Routed from prompt: "{prompt}"')
    for i, b in enumerate(briefs, 1):
        conf = confidences.get(b["skill"], "")
        refs = [r for r in b["read_in_order"] if r != "SKILL.md"]
        read = f"SKILL.md + {len(refs)} refs" if refs else "SKILL.md"
        first = b["first_command"]
        lines.append(
            f"{i}) {b['skill']} ({conf}): read {read} — first: {first} — stop: {b['stop_rule']}"
        )
    lines.append("Load the full brief (drop --compact) when the work itself begins.")
    return "\n".join(lines)


def _render_brief_core(prompt: Optional[str], briefs: List[Dict[str, Any]],
                       confidences: Dict[str, str]) -> str:
    """The run-from-this-card brief: skill, 3-step core loop, first command, stop rule.
    Zero file reading — for quick asks where the full protocol would cost more
    context than it saves. The core loop is the skill, distilled; escalate to
    full depth when a stop rule fires, a gate fails, or the stakes are high."""
    lines: List[str] = ["# Skill brief (core) — run from this card; read nothing else"]
    if prompt:
        lines.append(f'Routed from prompt: "{prompt}"')
    for i, b in enumerate(briefs, 1):
        conf = confidences.get(b["skill"], "")
        lines.append(f"{i}) {b['skill']} ({conf})")
        lines.append(f"   Core loop: {b['core']}")
        first = b["first_command"]
        if not first.startswith("none"):
            lines.append(f"   First: $WB {first}")
        lines.append(f"   Stop: {b['stop_rule']}")
    lines.append("Escalate to full depth (drop --core) when a stop rule fires, a gate")
    lines.append("fails, or the stakes are high. Do not read SKILL.md for a core ask.")
    return "\n".join(lines)


def _suggest_depth(prompt: str, top: List[Dict[str, Any]],
                   confidences: Dict[str, str]) -> str:
    """Deterministic depth recommendation so the agent spends context only when
    the ask is worth it: a single HIGH-confidence route on a short prompt is a
    quick ask (core); several routed skills need coordination first (compact);
    everything else — long prompts, fallbacks, low confidence — earns full depth."""
    if not top:
        return "full"
    if len(top) == 1 and confidences.get(top[0]["skill"]) == "HIGH" and len(prompt) <= 120:
        return "core"
    if len(top) > 1:
        return "compact"
    return "full"


def cmd_load_skills(args: argparse.Namespace) -> Dict[str, Any]:
    if args.list:
        return {
            "status": "OK",
            "routes": [
                {"skill": s, "wants": r["wants"], "wants_tr": r["wants_tr"],
                 "triggers": r["triggers"], "fallback": r.get("fallback", False)}
                for s, r in sorted(SKILL_ROUTES.items())
            ],
        }

    if args.skill:
        brief = _brief_for(args.skill)
        confidences = {args.skill: "DIRECT"}
        if args.core:
            brief_text = _render_brief_core(None, [brief], confidences)
        elif args.compact:
            brief_text = _render_brief_compact(None, [brief], confidences)
        else:
            brief_text = _render_brief_text(None, [brief], confidences)
        return {"status": "OK", "requested": args.skill, "routed": [brief],
                "confidences": confidences, "brief_text": brief_text,
                "compact": bool(args.compact), "core": bool(args.core),
                "depth": "core" if args.core else ("compact" if args.compact else "full")}

    prompt = (args.prompt or "").strip()
    if not prompt:
        raise WorkbenchError("NO_INPUT", "provide --prompt TEXT or --skill NAME (or --list)")

    if len(prompt) < 8:
        raise WorkbenchError("PROMPT_TOO_SHORT",
                             "the prompt is too short to route reliably (min 8 characters)")

    scored = _route_prompt(prompt)
    top = scored[: max(1, args.max)]
    confidences: Dict[str, str] = {}
    for r in scored:
        confidences[r["skill"]] = "HIGH" if r["score"] >= 2 else "MEDIUM"

    fallback = None
    if top:
        briefs = [_brief_for(r["skill"]) for r in top]
        routed = [{"score": r["score"], "hits": r["hits"], "brief": b}
                  for r, b in zip(top, briefs)]
    else:
        # No trigger matched: fall back to the advisory route, reason on record.
        fallback = {
            "skill": "local-advisor", "score": 0, "hits": [],
            "reason": "no specific trigger matched — defaulting to the advisory route; "
                      "answer from the conversation and ask one precise question if context is missing",
        }
        briefs = [_brief_for("local-advisor")]
        # No trigger matched, so no score is claimed: the fallback entry
        # carries only the brief (routed[0].get("score") is None).
        routed = [{"hits": [], "brief": briefs[0]}]
        confidences = {"local-advisor": "LOW"}

    brief_text = (_render_brief_core(prompt, briefs, confidences)
                  if args.core else
                  _render_brief_compact(prompt, briefs, confidences)
                  if args.compact else _render_brief_text(prompt, briefs, confidences))
    suggested = _suggest_depth(prompt, top, confidences)
    return {
        "status": "OK",
        "prompt": prompt,
        "routed": routed,
        "confidences": confidences,
        "fallback": fallback,
        "brief_text": brief_text,
        "compact": bool(args.compact),
        "core": bool(args.core),
        "depth": "core" if args.core else ("compact" if args.compact else "full"),
        "suggested_depth": suggested,
    }


# ---------------------------------------------------------------- doctor


def _parse_simple_frontmatter(text: str) -> Dict[str, str]:
    """Extract single-line top-level frontmatter keys from a SKILL.md-style file."""
    fm: Dict[str, str] = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km and not km.group(2).strip().startswith((">", "|")):
            fm[km.group(1)] = km.group(2).strip().strip('"')
    return fm


def cmd_doctor(args: argparse.Namespace) -> Dict[str, Any]:
    state_dir = Path(args.state_dir)
    project_root = Path(args.project_root).expanduser().resolve()
    checks: List[Dict[str, Any]] = []

    def add(cid: str, status: str, detail: str) -> None:
        checks.append({"id": cid, "status": status, "detail": detail})

    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 9):
        add("python", "OK", f"Python {py} (>= 3.9 required)")
    else:
        add("python", "FAIL", f"Python {py} is too old; 3.9+ required")

    try:
        ensure_state_dir(state_dir)
        probe = state_dir / ".doctor_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        add("state-dir", "OK", f"state dir writable: {state_dir}")
    except OSError as exc:
        add("state-dir", "FAIL", f"state dir not writable: {exc}")

    suite_root = Path(__file__).resolve().parent
    vendor_hits = scan_vendor_references(suite_root)
    add("vendor-neutrality", "FAIL" if vendor_hits else "OK",
        f"{len(vendor_hits)} banned reference(s) near this runtime" if vendor_hits else "no banned vendor references")

    home = Path.home()
    host_dirs = {
        "claude": (project_root / ".claude" / "skills", home / ".claude" / "skills"),
        "codex": (project_root / ".agents" / "skills", home / ".agents" / "skills"),
        "zcode": (project_root / ".zcode" / "skills", home / ".zcode" / "skills"),
        "opencode": (project_root / ".opencode" / "skills", home / ".config" / "opencode" / "skills"),
    }
    detected: List[str] = []
    for host, (proj, usr) in host_dirs.items():
        where = "project" if proj.is_dir() else ("user" if usr.is_dir() else None)
        if where:
            detected.append(host)
            add(f"host:{host}", "OK", f"skills directory found ({where}: {proj if where == 'project' else usr})")
    cursor_rules = project_root / ".cursor" / "rules"
    cursor_commands = project_root / ".cursor" / "commands"
    if cursor_rules.is_dir() or cursor_commands.is_dir():
        detected.append("cursor")
        mdc = cursor_rules / "local-advisor-suite.mdc"
        n_cmd = len(list(cursor_commands.glob("*.md"))) if cursor_commands.is_dir() else 0
        add("host:cursor", "OK" if mdc.is_file() else "WARN",
            f"rules={'present' if mdc.is_file() else 'missing local-advisor-suite.mdc'}; {n_cmd} command(s)")

    # Rules blocks
    for name, rel in (("CLAUDE.md", project_root / "CLAUDE.md"), ("AGENTS.md", project_root / "AGENTS.md")):
        if rel.exists():
            text = rel.read_text(encoding="utf-8", errors="replace")
            add(f"rules:{name}", "OK" if "local-advisor-suite:start" in text else "WARN",
                "suite block present" if "local-advisor-suite:start" in text else "file exists but no suite block")

    # Skill sanity in every detected directory
    skill_issues: List[str] = []
    installed = 0
    scanned: set = set()
    search_dirs = [project_root / ".claude" / "skills", project_root / ".agents" / "skills",
                   project_root / ".zcode" / "skills", project_root / ".opencode" / "skills",
                   project_root / ".cursor" / "skills", home / ".claude" / "skills",
                   home / ".agents" / "skills", home / ".zcode" / "skills",
                   home / ".config" / "opencode" / "skills"]
    for d in search_dirs:
        if not d.is_dir():
            continue
        for skill_md in sorted(d.glob("*/SKILL.md")):
            if skill_md in scanned:
                continue
            scanned.add(skill_md)
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "suite: local-advisor-suite" not in text:
                continue
            installed += 1
            fm = _parse_simple_frontmatter(text)
            if not fm.get("name"):
                skill_issues.append(f"{skill_md.parent.name}: frontmatter has no name")
            if not fm.get("description"):
                skill_issues.append(f"{skill_md.parent.name}: frontmatter has no description")
            elif len(fm["description"]) > 1024:
                skill_issues.append(f"{skill_md.parent.name}: description exceeds 1024 chars (ZCode drops the skill)")
            if len(text) > 100 * 1024:
                skill_issues.append(f"{skill_md.parent.name}: body exceeds 100KB (ZCode truncates)")
            wb = skill_md.parent / "scripts" / "workbench.py"
            if not wb.is_file():
                skill_issues.append(f"{skill_md.parent.name}: scripts/workbench.py missing")
            else:
                m = re.search(r'^VERSION\s*=\s*"([^"]+)"', wb.read_text(encoding="utf-8", errors="replace"), re.M)
                if m and m.group(1) != VERSION:
                    skill_issues.append(f"{skill_md.parent.name}: workbench copy is v{m.group(1)}, runtime is v{VERSION} (run tools/generate_shared.py)")
    add("skills", "FAIL" if skill_issues else ("OK" if installed else "WARN"),
        f"{installed} suite skill(s) checked; {len(skill_issues)} issue(s)"
        + ("" if not skill_issues else ": " + "; ".join(skill_issues[:8])))

    manifest = project_root / ".local-advisor-suite.json"
    add("manifest", "OK" if manifest.is_file() else "WARN",
        "install manifest present" if manifest.is_file() else "no install manifest in this project (skills may be linked or absent)")

    try:
        import shutil as _shutil
        has_git = bool(_shutil.which("git"))
    except Exception:
        has_git = False
    add("git", "OK" if has_git else "WARN", "git available for snapshots" if has_git else "git not found; verification snapshots lose HEAD info")

    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "OK")
    return {
        "status": status,
        "runtime_version": VERSION,
        "project_root": str(project_root),
        "hosts_detected": detected,
        "skills_installed": installed,
        "checks": checks,
        "advice": (
            "Fix every FAIL before relying on this installation. WARN entries are informational."
            if status != "OK" else "Installation healthy across every detected host."
        ),
        "checked_at": utc_now_iso(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workbench.py",
        description="Local Advisor & Deep Research Workbench (zero external vendor, host-neutral runtime)",
    )
    parser.add_argument(
        "--state-dir",
        default=DEFAULT_STATE_DIR,
        help="Directory for storing local JSON ledgers and caches (default: .local-workbench)",
    )
    parser.add_argument("--version", action="version", version=f"workbench {VERSION}")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # advise-intake
    p_intake = sub.add_parser("advise-intake", help="Record an advisory intake brief without scanning files")
    p_intake.add_argument("--question", required=True, help="Core advisory question")
    p_intake.add_argument("--context", default="", help="User-supplied context summary")
    p_intake.add_argument("--constraint", action="append", help="Explicit constraint (repeatable)")
    p_intake.add_argument("--non-goal", action="append", help="Explicit non-goal (repeatable)")
    p_intake.add_argument(
        "--mode",
        choices=["architecture", "tradeoff", "code-review", "planning", "general"],
        default="general",
    )
    p_intake.add_argument(
        "--requires-repo-inspection",
        action="store_true",
        help="Set only when user explicitly requested inspecting local repository files",
    )
    p_intake.set_defaults(func=cmd_advise_intake)

    # decision-score
    p_dec = sub.add_parser("decision-score", help="Score a multi-criteria decision matrix with hard constraints")
    p_dec.add_argument("--spec-file", required=True, help="Path to decision JSON specification")
    p_dec.add_argument("--output", help="Optional path to write scored JSON output")
    p_dec.set_defaults(func=cmd_decision_score)

    # scope-read
    p_read = sub.add_parser("scope-read", help="Safely read a file strictly inside --project-root")
    p_read.add_argument("--project-root", required=True, help="Explicit project root directory")
    p_read.add_argument("--file", required=True, help="Relative path to file inside project root")
    p_read.add_argument("--start-line", type=int, default=1)
    p_read.add_argument("--end-line", type=int, default=200)
    p_read.add_argument(
        "--debug-scope",
        action="store_true",
        help="Also require the file to be one of the debug ledger target files",
    )
    p_read.set_defaults(func=cmd_scope_read)

    # scope-scan
    p_scan = sub.add_parser("scope-scan", help="Safely scan files strictly inside --project-root")
    p_scan.add_argument("--project-root", required=True, help="Explicit project root directory")
    p_scan.add_argument("--subpath", default=".", help="Subdirectory inside project root")
    p_scan.add_argument("--glob", default="*", help="Filename glob filter (e.g. '*.py')")
    p_scan.add_argument("--pattern", help="Optional regex pattern to match inside files")
    p_scan.add_argument("--ignore-case", action="store_true")
    p_scan.add_argument("--max-files", type=int, default=MAX_SCAN_FILES, help=f"Stop after this many files (max {MAX_SCAN_FILES})")
    p_scan.set_defaults(func=cmd_scope_scan)

    # debug-hypothesis
    p_dbg = sub.add_parser("debug-hypothesis", help="Log or update a debugging hypothesis with 2-strike breaker")
    p_dbg.add_argument("--id", help="Hypothesis ID (e.g. H1)")
    p_dbg.add_argument("--symptom", help="Observed bug symptom or traceback summary")
    p_dbg.add_argument("--statement", help="Root cause hypothesis statement")
    p_dbg.add_argument("--prediction", help="Testable prediction if hypothesis is true")
    p_dbg.add_argument("--test-command", help="Minimal command or check used to test hypothesis")
    p_dbg.add_argument(
        "--status",
        choices=["PENDING", "CONFIRMED", "FALSIFIED"],
        help="Hypothesis status; omit to record only the case (--symptom/--target-file/--repro)",
    )
    p_dbg.add_argument("--evidence", help="Observed result from running the test")
    p_dbg.add_argument("--target-file", action="append", help="File the user named as the debugging target (repeatable)")
    p_dbg.add_argument("--repro", help="Command that reproduces the symptom")
    p_dbg.set_defaults(func=cmd_debug_hypothesis)

    # research-init
    p_rinit = sub.add_parser("research-init", help="Initialize a local deep research ledger")
    p_rinit.add_argument("--topic", required=True, help="Primary research question or topic")
    p_rinit.add_argument(
        "--mode",
        choices=["quick-verify", "deep-research", "wide-matrix"],
        default="deep-research",
    )
    p_rinit.add_argument("--max-queries", type=int, default=12, help="Query budget cap")
    p_rinit.add_argument("--sub-question", action="append", help="Decomposed sub-question (repeatable)")
    p_rinit.add_argument("--entity", action="append", help="Target entity for wide matrix research (repeatable)")
    p_rinit.add_argument("--field", action="append", help="Target field for wide matrix research (repeatable)")
    p_rinit.add_argument(
        "--time-sensitive",
        action="store_true",
        help="Recency matters (prices, versions, policies): enables age penalties in research-score",
    )
    p_rinit.set_defaults(func=cmd_research_init)

    # research-log-query
    p_rlog = sub.add_parser("research-log-query", help="Record a search query against the session budget")
    p_rlog.add_argument("--query", required=True, help="Search query string")
    p_rlog.add_argument("--sub-question-id", help="Target sub-question ID (e.g. Q1)")
    p_rlog.add_argument("--tool-used", default="host-native-search", help="Name of host search tool used")
    p_rlog.add_argument("--allow-duplicate", action="store_true")
    p_rlog.set_defaults(func=cmd_research_log_query)

    # research-add-source
    p_rsrc = sub.add_parser("research-add-source", help="Register a fetched primary/secondary source in the ledger")
    p_rsrc.add_argument("--source-id", help="Optional custom ID (e.g. S1)")
    p_rsrc.add_argument("--url", required=True, help="Full source URL or local document URI")
    p_rsrc.add_argument("--title", required=True, help="Source document title")
    p_rsrc.add_argument("--publisher", default="", help="Publisher or organization name")
    p_rsrc.add_argument("--published-date", default="unknown", help="ISO date or year")
    p_rsrc.add_argument(
        "--tier",
        choices=["PRIMARY", "SECONDARY", "TERTIARY"],
        default="PRIMARY",
    )
    p_rsrc.add_argument("--excerpt", help="Cleaned text excerpt from the fetched source")
    p_rsrc.add_argument("--content-file", help="Path to file containing fetched text")
    p_rsrc.set_defaults(func=cmd_research_add_source)

    # research-add-claim
    p_rclm = sub.add_parser("research-add-claim", help="Register an evidence-backed claim linked to source IDs")
    p_rclm.add_argument("--claim-id", help="Optional custom claim ID (e.g. C1)")
    p_rclm.add_argument("--sub-question-id", help="Sub-question ID (e.g. Q1)")
    p_rclm.add_argument("--entity", default="", help="Entity name (for wide tables/comparisons)")
    p_rclm.add_argument("--field", default="", help="Attribute/field name (e.g. 'pricing', 'license')")
    p_rclm.add_argument("--statement", required=True, help="Clear factual claim statement")
    p_rclm.add_argument("--value", default="", help="Normalized short value for table cells")
    p_rclm.add_argument("--source-id", action="append", required=True, help="Supporting source ID (repeatable)")
    p_rclm.add_argument("--quote", required=True, help="Verbatim quote from the fetched source")
    p_rclm.add_argument("--confidence", choices=["HIGH", "MEDIUM", "LOW"], default="HIGH")
    p_rclm.add_argument(
        "--status",
        choices=["VERIFIED", "CONTESTED", "PROVISIONAL"],
        default="VERIFIED",
    )
    p_rclm.add_argument(
        "--allow-unverified-quote",
        action="store_true",
        help="Accept a quote not found in the stored excerpt (forces LOW / PROVISIONAL)",
    )
    p_rclm.set_defaults(func=cmd_research_add_claim)

    # research-add-gap
    p_rgap = sub.add_parser("research-add-gap", help="Record an explicit knowledge gap (`n.a.`) when evidence is absent")
    p_rgap.add_argument("--gap-id", help="Optional gap ID (e.g. G1)")
    p_rgap.add_argument("--sub-question-id", help="Sub-question ID")
    p_rgap.add_argument("--entity", default="", help="Entity name")
    p_rgap.add_argument("--field", default="", help="Missing field name")
    p_rgap.add_argument("--description", required=True, help="What could not be verified")
    p_rgap.add_argument("--query-tried", action="append", help="Queries attempted before declaring gap")
    p_rgap.add_argument(
        "--reason",
        choices=["NO_PUBLIC_SOURCE", "PAYWALL", "CONFLICTING_UNRESOLVED", "BUDGET_REACHED"],
        default="NO_PUBLIC_SOURCE",
    )
    p_rgap.set_defaults(func=cmd_research_add_gap)

    # research-status
    p_rstat = sub.add_parser("research-status", help="Inspect ledger completeness, contradictions, and budget")
    p_rstat.set_defaults(func=cmd_research_status)

    # fetch-url
    p_fetch = sub.add_parser("fetch-url", help="Safely fetch and clean a public HTTPS URL with SSRF protection")
    p_fetch.add_argument("--url", required=True, help="Public HTTPS URL to read")
    p_fetch.add_argument("--allow-network", action="store_true", help="Explicit confirmation to allow network call")
    p_fetch.add_argument("--no-cache", action="store_true", help="Bypass local disk cache")
    p_fetch.add_argument("--timeout", type=float, default=15.0)
    p_fetch.add_argument("--max-chars", type=int, default=8000)
    p_fetch.set_defaults(func=cmd_fetch_url)

    # audit-report
    p_audit = sub.add_parser("audit-report", help="Audit research ledger and markdown report citations")
    p_audit.add_argument("--report-file", help="Optional path to Markdown report to lint inline links")
    p_audit.add_argument("--max-age-days", type=int, default=365, help="Freshness window for 'current/latest' claims")
    p_audit.add_argument("--strict", action="store_true", help="Treat warnings (overclaim, staleness) as failures")
    p_audit.set_defaults(func=cmd_audit_report)

    # verify-delivery
    p_ver = sub.add_parser("verify-delivery", help="Run observable verification commands and check artifacts")
    p_ver.add_argument("--artifact", action="append", help="Expected deliverable file path (repeatable)")
    p_ver.add_argument("--command", action="append", help="Verification shell command to execute (repeatable)")
    p_ver.add_argument("--not-run", action="append", help="Explicitly declare checks that were not executed")
    p_ver.add_argument("--check", action="append", help="Levelled check 'L2:<cmd>' | 'L3:<cmd>' | 'L4:<cmd>' (repeatable)")
    p_ver.add_argument("--require", choices=VERIFY_LEVELS, help="Fail unless this level is achieved")
    p_ver.add_argument("--cwd", help="Working directory for commands (default: current)")
    p_ver.add_argument("--timeout", type=int, default=60)
    p_ver.set_defaults(func=cmd_verify_delivery)

    # handoff-pack
    p_hand = sub.add_parser("handoff-pack", help="Compile a structured session handoff document from state ledgers")
    p_hand.add_argument("--title", required=True, help="Session or task title")
    p_hand.add_argument(
        "--session-status",
        choices=["DONE", "PARTIAL", "BLOCKED"],
        required=True,
    )
    p_hand.add_argument("--summary", required=True, help="Concise executive summary of current state")
    p_hand.add_argument("--completed", action="append", help="Completed item (repeatable)")
    p_hand.add_argument("--next-step", action="append", help="Next actionable step (repeatable)")
    p_hand.add_argument("--blocker", action="append", help="Active blocker (repeatable)")
    p_hand.add_argument("--decision", action="append", help="Decision taken this session (repeatable)")
    p_hand.add_argument("--open-question", action="append", help="Open question for the next session (repeatable)")
    p_hand.add_argument("--output", help="Output markdown path")
    p_hand.set_defaults(func=cmd_handoff_pack)

    # ---- v2.1 extensions
    p = sub.add_parser("research-score", help="Score every registered source 0-5 (tier, domain, excerpt, recency)")
    p.add_argument("--time-sensitive", action="store_true", help="Apply recency penalties even if the ledger is not flagged")
    p.set_defaults(func=cmd_research_score)

    p = sub.add_parser("research-gaps", help="Per sub-question coverage: STRONG / WEAK / OPEN / GAP_RECORDED + next actions")
    p.add_argument("--min-sources", type=int, default=2, help="Independent domains required for STRONG")
    p.add_argument("--strict", action="store_true", help="Return FAIL while any sub-question is WEAK or OPEN")
    p.set_defaults(func=cmd_research_gaps)

    p = sub.add_parser("research-resolve", help="Record which claim wins a contradiction and why")
    p.add_argument("--entity", required=True)
    p.add_argument("--field", required=True)
    p.add_argument("--winner-claim", required=True)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_research_resolve)

    p = sub.add_parser("research-pack", help="Write a Markdown evidence pack (claims + quotes + citations) for synthesis")
    p.add_argument("--output", help="Default: <state-dir>/evidence_pack.md")
    p.set_defaults(func=cmd_research_pack)

    p = sub.add_parser("wide-table", help="Render the entity x field matrix from ledger claims and gaps")
    p.add_argument("--entity", action="append")
    p.add_argument("--field", action="append")
    p.add_argument("--output", help="Markdown output path")
    p.add_argument("--csv", help="CSV output path")
    p.add_argument("--strict", action="store_true", help="FAIL if any cell is unverified, conflicting or missing")
    p.set_defaults(func=cmd_wide_table)

    p = sub.add_parser("adr-new", help="Create a numbered ADR from decision-review/templates/adr.md")
    p.add_argument("--title", required=True)
    p.add_argument("--dir", default="docs/adr")
    p.add_argument("--owner")
    p.add_argument("--decision-result", help="JSON written by decision-score --output")
    p.set_defaults(func=cmd_adr_new)

    p = sub.add_parser("adr-check", help="Check an ADR for required sections, R0-R3 class and unfilled placeholders")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_adr_check)

    p = sub.add_parser("debug-report", help="Render the root-cause report or escalation brief from the debug ledger")
    p.add_argument("--fix", help="What was changed (if anything)")
    p.add_argument("--open-risk", help="What was not checked")
    p.add_argument("--needed", help="What the user must provide to unblock")
    p.add_argument("--output", help="Default: <state-dir>/DEBUG_REPORT.md")
    p.set_defaults(func=cmd_debug_report)

    p = sub.add_parser("handoff-check", help="Validate a handoff file before resuming from it")
    p.add_argument("--file", help="Default: <state-dir>/HANDOFF.md")
    p.add_argument("--max-age-hours", type=float, default=72)
    p.set_defaults(func=cmd_handoff_check)

    p = sub.add_parser("artifact-list", help="List artifact-studio templates")
    p.set_defaults(func=cmd_artifact_list)

    p = sub.add_parser("artifact-new", help="Instantiate an artifact-studio template")
    p.add_argument("--type", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_artifact_new)

    p = sub.add_parser("selfcheck", help="Fail if any file under PATH references a banned research vendor")
    p.add_argument("--path", help="Default: directory containing this script")
    p.set_defaults(func=cmd_selfcheck)

    # ---- v3.0 additions (additive; the v2.1 contract above is unchanged)
    p = sub.add_parser("doctor", help="Check environment and installation health across all supported hosts")
    p.add_argument("--project-root", default=".", help="Project root to inspect (default: current directory)")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("spec-new", help="Start a specification ledger: goal, user stories, non-goals")
    p.add_argument("--goal", required=True, help="The goal in at least 20 characters")
    p.add_argument("--title", help="Optional spec title (defaults to the goal)")
    p.add_argument("--story", action="append", help="User story text (repeatable)")
    p.add_argument("--non-goal", action="append", help="Explicit non-goal (repeatable)")
    p.add_argument("--force", action="store_true", help="Replace an existing spec ledger")
    p.set_defaults(func=cmd_spec_new)

    p = sub.add_parser("spec-criterion", help="Add a Given/When/Then acceptance criterion to a story")
    p.add_argument("--story-id", required=True, help="Story ID (e.g. US1)")
    p.add_argument("--given", required=True, help="Precondition / context")
    p.add_argument("--when", required=True, help="Action or event")
    p.add_argument("--then", required=True, help="Observable outcome")
    p.set_defaults(func=cmd_spec_criterion)

    p = sub.add_parser("spec-task", help="Add a task that must verify at least one criterion")
    p.add_argument("--task", required=True, help="Task description (at least 10 characters)")
    p.add_argument("--verifies", action="append",
                   help="Criterion ID this task verifies (repeatable; at least one required)")
    p.add_argument("--depends-on", action="append", help="Task ID this task depends on (repeatable)")
    p.set_defaults(func=cmd_spec_task)

    p = sub.add_parser("spec-check", help="Validate the spec: criteria coverage, completeness, dependency cycles")
    p.set_defaults(func=cmd_spec_check)

    p = sub.add_parser("review-init", help="Start a code review ledger for a declared target")
    p.add_argument("--title", required=True, help="Review title (at least 5 characters)")
    p.add_argument("--target", required=True, help="What is being reviewed (file, PR, diff range, module)")
    p.add_argument("--focus", action="append", help="Review focus area (repeatable)")
    p.add_argument("--force", action="store_true", help="Replace an existing review ledger")
    p.set_defaults(func=cmd_review_init)

    p = sub.add_parser("review-finding", help="Record a severity-graded finding with a location")
    p.add_argument("--file", required=True, help="File the finding is about")
    p.add_argument("--line", type=int, help="Line number (optional)")
    p.add_argument("--severity", choices=REVIEW_SEVERITIES, default="MAJOR")
    p.add_argument("--category", choices=REVIEW_CATEGORIES, default="correctness")
    p.add_argument("--description", required=True, help="What is wrong (at least 10 characters)")
    p.add_argument("--suggestion", help="Concrete fix or follow-up")
    p.add_argument("--allow-duplicate", action="store_true")
    p.set_defaults(func=cmd_review_finding)

    p = sub.add_parser("review-report", help="Render the review with counts and a deterministic verdict")
    p.add_argument("--output", help="Default: <state-dir>/REVIEW.md")
    p.add_argument("--not-reviewed", help="Declare what was not inspected")
    p.set_defaults(func=cmd_review_report)

    p = sub.add_parser("kb-add", help="Add a sourced (or explicitly assumed) Q&A entry")
    p.add_argument("--question", required=True, help="The question in at least 10 characters")
    p.add_argument("--answer", required=True, help="The answer in at least 20 characters")
    p.add_argument("--source-url", help="URL backing the answer")
    p.add_argument("--source-id", help="Registered research-ledger source ID")
    p.add_argument("--tag", action="append", help="Tag (repeatable, lowercased)")
    p.add_argument("--assumed", action="store_true", help="Record an explicit assumption (LOW confidence)")
    p.add_argument("--force", action="store_true", help="Allow duplicate questions")
    p.set_defaults(func=cmd_kb_add)

    p = sub.add_parser("kb-search", help="Deterministic offline keyword search over knowledge entries")
    p.add_argument("--query", required=True, help="Free-text query")
    p.add_argument("--tag", help="Restrict to this tag")
    p.set_defaults(func=cmd_kb_search)

    p = sub.add_parser("kb-export", help="Render the knowledge base as Markdown")
    p.add_argument("--output", help="Default: <state-dir>/KNOWLEDGE_BASE.md")
    p.set_defaults(func=cmd_kb_export)

    p = sub.add_parser("data-register", help="Register the dataset to analyze (path, size, SHA-256)")
    p.add_argument("--path", required=True, help="Path to the data file (CSV, TSV, JSON, log, ...)")
    p.add_argument("--question", help="The analytical question (kept if omitted on re-register)")
    p.add_argument("--force", action="store_true", help="Allow switching datasets (resets findings and gaps)")
    p.set_defaults(func=cmd_data_register)

    p = sub.add_parser("data-finding", help="Log a finding with the exact command or formula behind it")
    p.add_argument("--statement", required=True, help="What was observed (min 10 characters)")
    p.add_argument("--method", required=True, help="The re-runnable command, query or formula (min 10 characters)")
    p.add_argument("--result", required=True, help="The measured value(s)")
    p.set_defaults(func=cmd_data_finding)

    p = sub.add_parser("data-gap", help="Declare something that could not be computed, and why")
    p.add_argument("--description", required=True, help="What could not be computed (min 15 characters)")
    p.add_argument("--reason", help="Why (NO_DATA, AMBIGUOUS_DEFINITION, OUT_OF_SCOPE, ...)")
    p.set_defaults(func=cmd_data_gap)

    p = sub.add_parser("data-report", help="Render the analysis report from the ledger")
    p.add_argument("--answer", required=True, help="Synthesis answering the registered question (min 20 characters)")
    p.add_argument("--output", help="Default: <state-dir>/ANALYSIS.md")
    p.add_argument("--allow-unverified-numbers", action="store_true",
                   help="Publish numbers not backed by a finding, marked UNVERIFIED")
    p.add_argument("--force", action="store_true", help="Overwrite an existing report file")
    p.set_defaults(func=cmd_data_report)

    p = sub.add_parser("devil-open", help="Open a devil's advocate session: the claim under attack and its honest steelman")
    p.add_argument("--claim", required=True, help="The plan/decision/spec under attack, in one sentence (min 20 chars)")
    p.add_argument("--steelman", required=True, help="The plan's best case, stated honestly (min 30 chars)")
    p.add_argument("--force", action="store_true", help="Replace an existing session (wipes challenges and verdict)")
    p.set_defaults(func=cmd_devil_open)

    p = sub.add_parser("devil-challenge", help="Attack a load-bearing assumption of the plan")
    p.add_argument("--assumption", required=True, help="The assumption being attacked (min 10 chars)")
    p.add_argument("--attack", required=True, help="What specifically breaks, and why (min 20 chars)")
    p.add_argument("--category", choices=DEVIL_CATEGORIES, default="unfounded-assumption")
    p.add_argument("--severity", choices=DEVIL_SEVERITIES, default="SERIOUS")
    p.add_argument("--defeater", required=True,
                   help="The observation or argument that would defeat this attack (min 10 chars)")
    p.set_defaults(func=cmd_devil_challenge)

    p = sub.add_parser("devil-rebuttal", help="Answer an open challenge; a sound rebuttal takes it out of the verdict")
    p.add_argument("--id", required=True, help="Challenge id (e.g. C1)")
    p.add_argument("--rebuttal", required=True, help="The answer to the attack (min 20 chars)")
    p.add_argument("--basis", help="What the rebuttal rests on: evidence, experience, constraint, ...")
    p.set_defaults(func=cmd_devil_rebuttal)

    p = sub.add_parser("devil-verdict", help="Mechanical gate: BLOCK while a FATAL challenge stands; render CHALLENGE.md")
    p.add_argument("--kill-criterion", action="append",
                   help="Observable, pre-committed signal that would falsify the plan (repeatable, min 1)")
    p.add_argument("--output", help="Default: <state-dir>/CHALLENGE.md")
    p.add_argument("--force", action="store_true", help="Overwrite an existing report file")
    p.set_defaults(func=cmd_devil_verdict)

    p = sub.add_parser("devil-plan",
                       help="Archetype attack plan: which assumptions to attack first for build/launch/migrate/hire/buy/process")
    p.add_argument("--archetype", required=True, choices=sorted(DEVIL_ARCHETYPES),
                   help="The plan's archetype: build, launch, migrate, hire, buy or process")
    p.set_defaults(func=cmd_devil_plan)

    p = sub.add_parser("devil-premortem",
                       help="It is 12 months later and the plan failed — write the story and its causes (before the challenges)")
    p.add_argument("--failure-story", required=True,
                   help="The concrete failure story, past tense (min 40 chars, no hedging)")
    p.add_argument("--cause", action="append",
                   help="A named cause of the failure, specific enough to check (repeatable, min 1)")
    p.set_defaults(func=cmd_devil_premortem)

    p = sub.add_parser("devil-outside",
                       help="The outside view: reference class + base rate; a bad base rate with no adjustment auto-opens a SERIOUS challenge")
    p.add_argument("--reference-class", required=True,
                   help="Who else has tried something like this (min 10 chars)")
    p.add_argument("--base-rate", type=int, required=True,
                   help="Percent of the reference class that succeeds (0-100)")
    p.add_argument("--adjustment", default="none",
                   help="Why this attempt differs from the class; 'none' means the inside view is unargued")
    p.set_defaults(func=cmd_devil_outside)

    p = sub.add_parser("devil-consequence",
                       help="Second-order effects: the L1 -> L2 -> L3 'and then what?' chain for a top risk")
    p.add_argument("--l1", required=True, help="What the plan's effect causes (min 15 chars)")
    p.add_argument("--l2", required=True, help="What that causes (min 15 chars)")
    p.add_argument("--l3", help="What that causes in turn (optional; min 15 chars if present)")
    p.set_defaults(func=cmd_devil_consequence)

    p = sub.add_parser("qc-pin",
                       help="Pin the question contract: the question, the decision it informs, the consumer, the budget")
    p.add_argument("--question", required=True, help="The question to answer (min 15 chars)")
    p.add_argument("--decision", required=True,
                   help="The decision this answer will inform (min 10 chars) — what the answer is FOR")
    p.add_argument("--consumer", help="Who reads the answer, and in what form")
    p.add_argument("--budget", help="Time/token/effort budget for answering")
    p.add_argument("--decided", action="append",
                   help="Already decided — not open for debate (repeatable)")
    p.add_argument("--open", action="append",
                   help="Genuinely open sub-questions (repeatable)")
    p.add_argument("--force", action="store_true", help="Replace an existing contract (wipes assumptions)")
    p.set_defaults(func=cmd_qc_pin)

    p = sub.add_parser("qc-check",
                       help="The gate: is the contract complete enough to answer? READY or NEEDS_INPUT with what to ask")
    p.set_defaults(func=cmd_qc_check)

    p = sub.add_parser("qc-assume",
                       help="Record a stated assumption where the question was ambiguous — stated in the answer's caveat")
    p.add_argument("--assumption", action="append",
                   help="The interpretation chosen (repeatable, min 10 chars each)")
    p.set_defaults(func=cmd_qc_assume)

    p = sub.add_parser("journal-log",
                       help="Log a decision with its falsifiable prediction, confidence and review date")
    p.add_argument("--decision", required=True,
                   help="What was chosen (min 15 chars)")
    p.add_argument("--prediction", required=True,
                   help="The falsifiable prediction reality can grade (min 15 chars)")
    p.add_argument("--confidence", type=int, required=True,
                   help="Confidence the prediction hits: 0-100")
    p.add_argument("--review-by", required=True,
                   help="When to resolve this entry: YYYY-MM-DD")
    p.add_argument("--mind-changer",
                   help="What observation would change your mind before the review date")
    p.add_argument("--context", help="One line of context for the future reader")
    p.set_defaults(func=cmd_journal_log)

    p = sub.add_parser("journal-resolve", help="Resolve an entry against reality: HIT, MISS or PARTIAL, plus the lesson")
    p.add_argument("--id", required=True, help="Journal entry id (e.g. J1)")
    p.add_argument("--outcome", required=True, choices=JOURNAL_OUTCOMES)
    p.add_argument("--lesson", required=True,
                   help="What you would do differently (min 15 chars)")
    p.set_defaults(func=cmd_journal_resolve)

    p = sub.add_parser("journal-report",
                       help="Calibration report: hit rate vs claimed confidence per band, overdue entries")
    p.set_defaults(func=cmd_journal_report)

    p = sub.add_parser("playbook-list", help="List the pre-composed skill chains: decide, investigate, build, launch, debug")
    p.set_defaults(func=cmd_playbook_list)

    p = sub.add_parser("playbook-show", help="Render a playbook: ordered steps, what each skill contributes, the gate before the next step")
    p.add_argument("--name", required=True, choices=sorted(PLAYBOOKS),
                   help="The playbook to render: decide, investigate, build, launch or debug")
    p.set_defaults(func=cmd_playbook_show)

    p = sub.add_parser("load-skills",
                       help="Route a prompt to the skills it needs and emit their loading brief")
    p.add_argument("--prompt", help="The user's request text (TR or EN) to route")
    p.add_argument("--skill", help="Skip routing: load this skill's brief directly")
    p.add_argument("--max", type=int, default=3, help="Max skills to return (default 3)")
    p.add_argument("--list", action="store_true", help="List all routes with their triggers")
    p.add_argument("--compact", action="store_true",
                   help="Emit a one-line-per-skill brief (token-efficient routing pass)")
    p.add_argument("--core", action="store_true",
                   help="Run-from-this-card brief: skill + 3-step core loop + first command "
                        "+ stop rule, zero file reading (quickest path for simple asks)")
    p.set_defaults(func=cmd_load_skills)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        # OK/PASS exit 0. WARN (doctor's informational findings) also exits 0:
        # only FAIL conditions and structured errors are nonzero.
        return 0 if result.get("status") in {"OK", "PASS", "WARN"} else 2
    except WorkbenchError as exc:
        err_payload = {
            "status": "ERROR",
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
        }
        sys.stderr.write(json.dumps(err_payload, indent=2, ensure_ascii=False) + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
