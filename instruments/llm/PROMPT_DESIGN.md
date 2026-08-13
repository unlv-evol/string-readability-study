# LLM-Assisted Qualitative Analysis — Prompt Design

## Overview

This document describes the design of the prompts used to support the qualitative
analysis of open-ended post-survey responses, as reported in Section 2.14 of the
paper. It is provided to address reviewer requests for transparency about prompt
engineering practices, iteration history, and robustness checks.

The five prompt files are in `prompts/`. The five final codebooks produced by the
LLM and refined by human researchers are in `codebooks/`.

---

## 1. Model and Settings

| Property | Value |
|----------|-------|
| Model | ChatGPT (GPT-5.0) |
| Interface | ChatGPT web interface (chat.openai.com) |
| Temperature | Default (1.0) |
| Context window | Full prompt + CSV data uploaded per session |
| Sessions | One session per open-ended question (5 total) |

The default temperature was used throughout. No system-level fine-tuning or
retrieval augmentation was applied. The model was given the full participant
response CSV for the relevant question in each session.

---

## 2. Prompt Structure and Rationale

All five prompts follow the same structural template:

```
ROLE / PERSONA
OBJECTIVE
INPUTS (provided)
METHOD (must follow)
OUTPUT FORMAT (CSV)
ADDITIONAL OUTPUT (Structured Codebook Summary)
```

Each section serves a specific purpose:

**ROLE / PERSONA** — Instructs the model to adopt the perspective of a
qualitative researcher applying the Framework Method. This was found during
piloting to improve consistency of code granularity and reduce overly generic
labels. Without the persona, early drafts produced codes at the wrong level of
abstraction (either too broad, e.g., "positive sentiment," or too narrow,
e.g., individual participant paraphrases).

**OBJECTIVE** — Anchors the model to the specific survey question and states
the analytical goal (inductive open coding, not sentiment analysis or
summarization). The verbatim question text is included to prevent the model from
inferring a different question from the response data alone.

**INPUTS** — Specifies the data format (CSV with a `ResponseText` column) and
provides study context. The context sentence establishes that responses come
from developers comparing two syntactic constructs, which reduces hallucinated
codes unrelated to the study (e.g., codes about unrelated programming topics
that appeared in early iterations without this context).

**METHOD (must follow)** — The five-step method corresponds directly to the
Framework Method stages used in the paper: open coding → labeling → decision
rules → illustrative quotes → comparative reference. Enumerating the steps as
a numbered list with explicit must-follow language was found to reduce
step-skipping compared to prose instructions.

The key constraints embedded in the method:
- *Non-overlapping codes (≤4 words)*: limits verbosity and forces precision
- *Decision rules (when to use / when not to use)*: the most important
  constraint for human validation; without it, early iterations produced codes
  whose boundaries were ambiguous and difficult to apply consistently
- *Verbatim quote with respondent ID*: grounds each code in the data and
  makes it auditable; early iterations sometimes produced paraphrased quotes
  that could not be traced back to the source

**OUTPUT FORMAT (CSV)** — Explicit column specification prevents format drift
across the five questions and makes the output directly importable for the
case-by-code matrix.

**ADDITIONAL OUTPUT (Codebook Summary)** — Requests a structured summary table
alongside the per-response coding. This table became the primary artifact
reviewed by human coders during the validation phase (Section 4 below).

---

## 3. Variation Across Questions

The five prompts share the structure above but differ in:

| Element | Varies how |
|---------|------------|
| Objective | Reworded for each question's focus (readability, debugging, preference, learning, suggestions) |
| Open coding focus | Adjusted to surface relevant constructs (e.g., Q4 focuses on familiarity and learning; Q5 focuses on actionable design improvements) |
| Example theme labels | Tailored to expected response patterns to anchor the model's vocabulary |
| Comparative reference instruction | Q5 (suggestions) includes a note about whether improvements target interpolation, concatenation, or both, since responses often addressed both constructs |

---

## 4. Iteration History

The prompts were developed iteratively using Q1 responses as the calibration
question. Three failure modes were identified and addressed through targeted
prompt revisions; the full error log with examples is in `error_log.md`.

| Failure mode | Prompt element added |
|---|---|
| Overly broad codes with no sub-themes | Five-step METHOD with explicit sub-theme requirement |
| Hallucinated or paraphrased quotes | Verbatim quote + respondent ID requirement (METHOD step 4) |
| Inconsistent label length | ≤4-word label constraint (METHOD step 2) |

The five prompt files in `prompts/` represent the final versions applied to the
full dataset.

---

## 5. Robustness Checks

Two robustness checks were performed after the prompts were finalised.

**Check 1 — Stability across runs (calibration samples).** The final Q1 prompt
was run on three independently drawn stratified 20% samples of Q1 responses
(`calibration/Q1_run1_sample.csv`, `run2_sample.csv`, `run3_sample.csv`).
Theme-level Jaccard similarity was computed across all three pairwise
combinations using `jaccard_similarity.py`. A threshold of ≥ 0.80 was used
to define acceptable stability.

> **Reproducibility note.** The `calibration/Q1_run*_sample.csv` files shipped
> here are the *input* samples (`UID`, `R-X`, `ResponseText`) that were fed to
> the model. The per-run coded outputs — the theme assigned to each response in
> each run — were not retained, so this check cannot be recomputed from the
> repository alone. To reproduce it, re-run the Q1 prompt over each of the three
> samples, save each run's output with a `Theme` column, and pass those files to
> `jaccard_similarity.py --csv`. Passing the input samples directly is rejected
> by the script rather than silently reporting perfect agreement.

**Check 2 — Sensitivity to role/persona wording.** The Q1 prompt was re-run
with two paraphrased versions of the ROLE/PERSONA block
(`prompts/persona_paraphrase_v1.txt`, `prompts/persona_paraphrase_v2.txt`)
on the Run 1 calibration sample. Major themes were compared manually; no
change in the set of major themes was observed across the three persona
formulations.

---

## 6. Known LLM Errors and Corrections

Three recurring error types were identified during human review and corrected
before the codebook was applied at scale:

| Error type | Description | Correction |
|------------|-------------|------------|
| Overgeneralization | A single broad code (e.g., "Positive Interpolation Sentiment") applied to responses with distinct underlying reasons | Split into two or more specific sub-themes with narrower decision rules |
| Hallucinated labels | A code label appeared in the codebook summary with no supporting quote from any actual response | Removed; human researchers confirmed absence in data |
| Omitted context | The model coded a response without accounting for the specific syntax construct being referenced, producing an ambiguous code | Human analyst re-coded with explicit construct reference added |

All corrections were documented in coding memos maintained by the research
team. The final validated codebook supersedes the LLM draft in all cases where
conflicts were identified.

---

## 7. Human Validation Process

The LLM draft codes were treated as a starting point, not a final output.
The validation procedure followed the Framework Method (Section 2.14 of
the paper):

1. Both researchers independently reviewed the LLM codebook summary for each
   question and flagged ambiguous, overlapping, or unsupported codes.
2. Each researcher independently applied the draft codebook to a stratified
   30% subset of responses (stratified by response length quartile to ensure
   coverage of short, medium, and long responses).
3. Disagreements were resolved through structured discussion until convergence.
   Cohen's Kappa was not computed; agreement was verified through convergence
   on shared definitions rather than statistical coefficient, consistent with
   interpretive qualitative practice.
4. The codebook was refined based on disagreements: overlapping categories
   were merged, ambiguous labels were split, and decision rules were sharpened.
5. The refined codebook was applied to all remaining responses, with LLM draft
   annotations re-examined under the updated definitions.

---

## 8. Files in This Directory

| File | Description |
|------|-------------|
| `prompts/q1_prompt.txt` | Final prompt — Q1 (readability reflection) |
| `prompts/q2_prompt.txt` | Final prompt — Q2 (comprehension and debugging) |
| `prompts/q3_prompt.txt` | Final prompt — Q3 (preference rationale) |
| `prompts/q4_prompt.txt` | Final prompt — Q4 (learning curve) |
| `prompts/q5_prompt.txt` | Final prompt — Q5 (suggestions for improvement) |
| `prompts/persona_paraphrase_v1.txt` | Paraphrased role/persona block — robustness check version 1 |
| `prompts/persona_paraphrase_v2.txt` | Paraphrased role/persona block — robustness check version 2 |
| `calibration/Q1_run1_sample.csv` | Stratified 20% sample of Q1 responses — run 1 |
| `calibration/Q1_run2_sample.csv` | Stratified 20% sample of Q1 responses — run 2 |
| `calibration/Q1_run3_sample.csv` | Stratified 20% sample of Q1 responses — run 3 |
| `error_log.md` | Three failure modes identified during iteration, with examples and prompt fixes |
| `jaccard_similarity.py` | Script to compute theme-level Jaccard similarity across runs |
| `codebooks/Q1_readability_codebook.csv` | Validated codebook — Q1 |
| `codebooks/Q2_comprehension_debugging_codebook.csv` | Validated codebook — Q2 |
| `codebooks/Q3_preference_codebook.csv` | Validated codebook — Q3 |
| `codebooks/Q4_familiarity_codebook.csv` | Validated codebook — Q4 |
| `codebooks/Q5_improvement_codebook.csv` | Validated codebook — Q5 |
