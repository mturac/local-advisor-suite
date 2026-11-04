# Host Compatibility Matrix (Codex, Claude Code, ZCode, Cursor, OpenCode, AGENTS.md)

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
