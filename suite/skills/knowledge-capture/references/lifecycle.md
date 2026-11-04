# Knowledge Lifecycle

## When to capture

Capture at the moment knowledge is **verified**, not at the moment it is discussed:

| Event | Capture? | Entry shape |
|---|---|---|
| A research claim was verified with a quote | Yes | Question = the sub-question; answer = claim + boundaries; source = the ledger source |
| A debug root cause was confirmed and fixed | Yes | Question = "why did X happen?"; answer = mechanism + fix location; source = verification record or criterion |
| A decision was recorded in an ADR | Yes (thin) | Question = "what did we choose and why?"; answer = choice + one-line rationale + ADR path; source = the ADR |
| An assumption was made explicitly | Yes, with `--assumed` | The marker is the point: it makes the debt visible |
| A workaround was applied without understanding | Only as `--assumed` | "Works, unknown why" is honest and searchable |
| Chat speculation never verified | No | Capture when verified, or capture as assumption deliberately |

## Deduplication

The runtime rejects an exact duplicate question (unless `--force`). Near-duplicates are a judgment call:

- **Same question, better answer** → add the new entry, and note in its answer that it supersedes the old one's ID. Deleting history is not possible by design; supersession is.
- **Different scope** (v1 vs. v2 behavior) → separate entries, each naming its scope in the answer.
- **Different question, same answer** → separate entries; retrieval is by question.

## Review cadence

The knowledge base is state, and state rots. Two rhythms:

1. **Per-session**: before ending, `kb-export` and skim the ASSUMPTION entries — anything now verifiable gets re-captured with a source.
2. **Per-milestone** (release, quarter): review entries against the current code; supersede or mark stale ones. An entry contradicting the code is worse than a missing entry, because it is trusted.

## How entries age

- **Sourced entries** age with their source. When the source's truth changes (new version, new policy), the entry is stale regardless of when it was captured.
- **Assumed entries** never age into truth. They age into either verified entries (re-capture with source) or deletion candidates (the assumption was wrong and is now a warning).
- **Tags** age by drift: a rename in the project's vocabulary strands old entries under dead tags. During milestone review, reconcile tags before adding new ones.

## Integration points

- `deep-research` and `web-search` should **search the KB first**; the budget saved is the budget earned.
- `session-handoff` packing should mention the KB's notable additions this session.
- `spec-builder` criteria that encode captured knowledge should cite the entry ID in the criterion's notes — the spec then inherits the evidence trail.
