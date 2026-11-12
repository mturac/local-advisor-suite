---
name: get-more-perspective
description: Convene a virtual advisory panel for any decision, strategy or dilemma — five default seats, Operator (execution), Skeptic (risk), Visionary (opportunity), Customer Advocate (user impact), Finance (the numbers), plus custom seats. Each seat delivers an independent, lens-bound opinion with role-mandated fields (a skeptic without a named risk and trigger is refused, finance without a digit-bearing anchor likewise, two seats may not read the same speech), optionally backed by evidence gathered with the TinyFish search/fetch pattern or the suite's fetch-url. The mechanical synthesis builds the joint recommendation — UNANIMOUS_SUPPORT / SUPPORT_WITH_CONDITIONS / MAJORITY_SUPPORT_WITH_DISSENT / SPLIT_PANEL — manufactured agreement is forbidden: splits stay splits, dissents stay visible. Use for what would experts think, different perspectives, board of advisors, panel of experts, danışma paneli, uzmanlar ne düşünür, farklı bakış açıları, kurul topla, gözünden bak.
license: Apache-2.0
compatibility: claude-code, codex, zcode, cursor, opencode
metadata:
  suite: local-advisor-suite
  version: "4.1.3"
---

# Get More Perspective

*Runtime: `$WB` below is `python3 scripts/workbench.py`, resolved relative to this skill's own directory — an `install.py` install records the same path in the host's rules file (CLAUDE.md / AGENTS.md), and a plugin install carries this copy with it.*

Convene a virtual advisory panel and make it argue properly. Five seats — Operator, Skeptic, Visionary, Customer Advocate, Finance — each speak independently through their own lens with fields their role mandates, the seats that cannot run on vibes (skeptic, finance) must cite evidence on the table first, and any seat can cross-examine any other. The synthesis is then mechanical: it counts stances and names the verdict, and it is forbidden from averaging disagreement into "consensus" — a split panel produces a map of the split, not a fake recommendation. A panel that always agrees is theater; this one is built so it cannot quietly become one.

## When to use

- The user faces a decision, strategy or dilemma and asks for expert views: "what would experts think about this", "give me different perspectives", "run this by a board", "uzmanlar ne düşünür", "danışma paneli kur", "farklı bakış açıları lazım".
- The user is torn between options and wants the options examined from several independent angles before scoring them (panel first, then `decision-review` to decide).
- A plan has momentum and the user wants a structured breadth-check before the adversarial depth-check — the panel surfaces what each discipline sees; `devil-advocate` then attacks what survives.

Do NOT use when:

- The user wants one plan attacked adversarially, challenge by challenge, with a verdict — that is `devil-advocate`. (This panel is breadth of viewpoints; that skill is depth of attack. A panel dissent is handed to it.)
- The user wants options scored on weighted criteria with an ADR — that is `decision-review`.
- The user wants sourced research or a comparison table — that is `deep-research` / `wide-search`. The panel argues about evidence; those skills produce it.
- Nobody has stated a question worth convening on — run `question-contract` first.

## Workflow

1. **Convene the panel on a real question.** A vague question returns five vague answers, so the question and its context (options on the table, constraints, what is already decided) are required and length-checked:
   `$WB panel-open --question "the decision before the panel" --context "options, constraints, what is decided"`
   The default board is the five seats. `--roles operator,skeptic,legal` reshapes it (custom seats allowed — the convenor keeps their lens consistent); a panel below two seats is refused as a monologue.

2. **Evidence before opinions.** Before the skeptic and finance seats speak, table what was actually observed — quoted verbatim, with the source. Gather it with the TinyFish pattern (search to find, fetch to read: see `references/tinyfish-evidence.md`) or the suite's own `fetch-url --allow-network`, or quote the conversation/local file:
   `$WB panel-evidence --quote "..." --source-url "..." --via tinyfish-fetch --label EV1`
   A paraphrase is not evidence; the panel argues about what was actually seen. Evidence labels (EV1, EV2, ...) are how voices cite the table.

3. **Every seat speaks, independently, from its own lens.** One command per seat — no batch summaries, because independence is the product:
   `$WB panel-voice --role skeptic --stance oppose --risk "..." --trigger "..." --evidence EV1 --confidence 65 --reasoning "..."`
   Each built-in seat must bring its role's mandated field: the operator a first execution step, the skeptic a named risk **and** an early-warning trigger, the visionary a concrete opportunity, the customer advocate a segment-specific impact, the finance seat a digit-bearing anchor (`--number`) plus cited evidence. Short reasoning (<80 chars) is refused as a mood; an opinion near-identical to another seat's is refused as theater (`DUPLICATE_VOICE`); a conditional stance must name the observable condition it hangs on. Role details and good/bad examples: `references/panel-roles.md`.

4. **Cross-examine — the panel is a dialogue, not five monologues.** Any seat may challenge any other's opinion; the challenged seat may answer now or leave it open:
   `$WB panel-cross --from-role operator --to-role skeptic --challenge "..." --response "..."`
   Unanswered challenges stay **OPEN** and appear in the report; a synthesis with open challenges is a WARN by rule.

5. **Synthesize mechanically — no manufactured agreement.** Every seat must have spoken; then the verdict is counted, not negotiated:
   `$WB panel-synth`
   `UNANIMOUS_SUPPORT` → PASS. `SUPPORT_WITH_CONDITIONS` (no oppose, conditions named). `MAJORITY_SUPPORT_WITH_DISSENT` (support > oppose, dissent stays visible). `SPLIT_PANEL` (everything else) — the report refuses to average the disagreement into a recommendation and hands the split to `decision-review`. A finance dissent is flagged and never buried under a majority. Renders `PANEL.md`. Exact rules: `references/synthesis-rules.md`.

6. **Hand the verdict onward.** A dissent that must be answered before acting → `devil-advocate` (turn its strongest point into a challenge with a defeater). A split panel → `decision-review` (score the positions and decide). The final call → `decision-journal` (log it with a falsifiable prediction and a review date).

The panel's value is not five opinions — it is five opinions that could not be collapsed into one. Keep the seats independent, keep the skeptic and finance seats fed with evidence, and let a split be a split.
