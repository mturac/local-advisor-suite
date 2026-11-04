# Audit Rules: Issue Taxonomy and the Manual Checklist

## The mechanical checks (what `audit-report` enforces)

### Ledger integrity

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `CLAIM_WITHOUT_SOURCE` | blocking | Claim with no source IDs | Register the source and link the claim |
| `DANGLING_SOURCE_REF` | blocking | Claim referencing an unregistered source ID | Register the missing source or fix the ID |
| `MISSING_OR_WEAK_QUOTE` | blocking | Quote under 10 characters | Re-copy the real sentence |
| `HIGH_CONFIDENCE_UNVERIFIED_QUOTE` | blocking | HIGH claim whose quote never matched the excerpt | Re-verify or downgrade honestly |

### Citations

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `UNREGISTERED_REPORT_URL` | blocking | Inline link to a URL not in the ledger | Open the page, register it, then cite it — or drop the link |
| `GENERIC_OR_RAW_ANCHOR` | blocking | `[source]`, `[here]`, `[link]`, raw-URL anchors | Name the publisher or document |

### Content

| Code | Severity | Trigger | Fix |
|---|---|---|---|
| `UNCITED_NUMERIC_CLAIM` | blocking | Number/date in prose without a citation on that sentence | Cite or remove |
| `UNSUPPORTED_NUMBER` | blocking | Number absent from the cited evidence | Use the source's number, or cite the source that has yours |
| `DATE_AHEAD_OF_EVIDENCE` | blocking | Year newer than any cited source's date | Find newer evidence or write "as of <evidence date>" |
| `UNDATED_EVIDENCE` | warning | Current/dated claim on an undated source | Record `--published-date`, or add "as of <access date>" |
| `STALE_CURRENTNESS_CLAIM` | warning | "currently/latest" with evidence older than the window | Newer source, or qualify with the evidence date |
| `OVERCLAIM_LANGUAGE` | warning | Absolute term without 2+ independent domains AND a primary source | Calibrate the wording or add evidence |
| `SINGLE_SOURCE_RELIANCE` | warning | One domain carries >50% of >=5 citations | Corroborate key claims independently |

Exempt sections (numbers and currentness are not checked there): Method, Scope, Knowledge Gaps, Appendix, Metadata, Verification, Changelog.

## The manual checklist (after the mechanical PASS)

The audit cannot read. These checks need you, line by line:

1. **Context of numbers.** Does the source's number mean what the sentence says it means? Same unit, same population, same timeframe, same metric?
2. **Selection fairness.** Is there a credible disconfirming source class you did not look for? If the answer is "the vendor's blog and the vendor's docs", the section needs independent eyes before "verified".
3. **Reasoning validity.** Do the cited facts actually entail the conclusion, or is there an inference the evidence does not cover? An inference is fine — label it as your inference.
4. **Quote fidelity.** Spot-check quotes in their source context: a verbatim sentence can still be lifted from a paragraph that negates it.
5. **Gaps still gaps.** Confirm nothing in the final edit quietly filled a gap's topic from memory (editors do this without noticing).
6. **The reader's decision.** Would the reader, knowing only what the report shows, reach the report's recommendation? If not, what's missing is the next question to answer.

## Audit etiquette

- Fix the document, not the ledger — unless the ledger is factually wrong, in which case fix the ledger and re-derive everything downstream.
- Do not rephrase merely to dodge a flag: if `UNSUPPORTED_NUMBER` fires, the honest fix is evidence or deletion, not "approximately".
- Keep the audit output with the deliverable trail (`.local-workbench/`); it is the receipt that PASS meant something.
