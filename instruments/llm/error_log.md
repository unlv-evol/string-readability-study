# LLM Coding Error Log

This log documents the three recurring failure modes identified during prompt
development (Q1 calibration phase) and the targeted prompt revision that
addressed each one. It supports the iteration history described in
`PROMPT_DESIGN.md` Section 4.

---

## Failure Mode 1 — Overly Broad Codes

**Description:** The model produced high-level theme labels with no sub-themes,
collapsing distinct participant reasoning patterns into a single undifferentiated
category.

**Example observed:**
- Code assigned: `Interpolation Preferred`
- Responses with very different reasoning (visual clarity vs. fewer keystrokes
  vs. familiarity with Python f-strings) were all grouped under this single label.

**Impact:** The codebook could not distinguish between meaningfully different
participant positions, reducing analytical resolution.

**Prompt revision:** Added the five-step METHOD section requiring explicit
sub-theme labels (≤4 words each) alongside each theme, and introduced the
non-overlapping constraint.

---

## Failure Mode 2 — Hallucinated Quotes

**Description:** The model generated illustrative quotes that were paraphrases
or fabrications rather than verbatim excerpts from the response data. These
quotes could not be traced back to any actual participant response.

**Example observed:**
- Attributed quote: *"Interpolation just feels more natural to me"* (R-47)
- Actual R-47 response: *"I think concatenation is what I am used to, so it
  feels easier even if it takes more typing."*
- The quote was fabricated and attributed to the wrong respondent.

**Impact:** The codebook could not be audited against the source data,
undermining credibility and traceability.

**Prompt revision:** Added the explicit requirement in METHOD step 4:
*"Include one verbatim quote (≤30 words) from the response, tagged with the
respondent ID (e.g., R-142)."* Also added the INPUTS context sentence to
anchor the model more firmly to the provided data.

---

## Failure Mode 3 — Inconsistent Label-Length Enforcement

**Description:** Without an explicit constraint, the model produced sub-theme
labels of highly variable length — some single words ("Clarity"), others full
sentences ("Participant finds interpolation reduces the number of operators
needed to construct a string"). Long labels were not reusable across responses
and made the codebook unwieldy for human application.

**Example observed:**
- Sub-theme: `Interpolation reduces syntactic overhead and operator clutter`
  (8 words, not portable)
- Desired form: `Reduced Operator Clutter` (3 words)

**Impact:** The codebook lacked a consistent vocabulary, making inter-coder
application unreliable.

**Prompt revision:** Added the ≤4-word label constraint explicitly to the
METHOD section: *"Assign non-overlapping Theme and Sub-theme labels (≤4 words
each)."*

---

## Summary

| # | Failure mode | Prompt element added | Section |
|---|-------------|----------------------|---------|
| 1 | Overly broad codes | Five-step METHOD with sub-theme requirement | METHOD |
| 2 | Hallucinated quotes | Verbatim quote + respondent ID requirement | METHOD step 4 |
| 3 | Inconsistent label length | ≤4-word label constraint | METHOD step 2 |
