# Task Design Documentation

## Overview

This document describes the methodology used to design, generate, and validate the 16 programming comprehension tasks used in the experiment. It is provided in response to reviewer requests for transparency about how the experimental stimuli were produced.

The authoritative task definitions are in `questions.json`. The script `generator.py` reads that file and produces `generated_experiment.html`, a standalone document showing all tasks with their correct answers — intended for replication and audit. The live experiment delivered the same tasks through the Flask application (`app.py`) using the static template `templates/experiment.html`.

---

## 1. Design Philosophy

The tasks were designed to measure *comprehension* of string expressions, not programming skill. Each task presents a short code expression and asks the participant to identify its correct string output from four options.

Two design principles guided task construction:

**Language neutrality.** Because the study recruited participants with diverse language backgrounds (Python, Java, C++, etc.), all tasks use a language-neutral pseudo-syntax rather than any specific language's syntax. This prevents prior language familiarity from confounding the comparison between interpolation and concatenation. The pseudo-syntax rules are defined formally in Section 2 below.

**Ecological validity.** Tasks draw from domains that arise naturally in everyday programming: name/address formatting, score reporting, file path construction, URL building, and symbolic mathematical expressions. This grounds the stimuli in recognizable contexts while keeping the code short enough for rapid comprehension.

---

## 2. Pseudo-Syntax Evaluation Rules

The experiment uses two operators:

| Symbol | Meaning             |
|--------|---------------------|
| `+`    | String concatenation |
| `{x}`  | Interpolate the value of `x` into the surrounding string |

The following rules define how expressions are evaluated to produce the correct output. These rules are intentionally simpler than any real language to minimize confounds from language-specific knowledge.

### Rule 1 — Concatenation with `+`
Adjacent string segments joined by `+` are placed directly next to each other with no separator added.

> `"Hello, " + name` → `Hello, Daniel` (given `name = "Daniel"`)

### Rule 2 — Interpolation with `{}`
A placeholder `{x}` is replaced by the current value of variable `x`. The surrounding string is otherwise reproduced as written.

> `"Hello, {name}!"` → `Hello, Daniel!` (given `name = "Daniel"`)

### Rule 3 — Parentheses are preserved in output
When a parenthesized subexpression appears inside a concatenation or interpolation expression, the output **retains the parentheses** as grouping markers. Parenthesized groups are not arithmetically collapsed.

> `a + (b + c)` → the output includes `(...)` around the grouped portion

This rule distinguishes the pseudo-syntax from real language semantics. In Python, `"x" + ("y" + "z")` equals `"xyz"` and the parentheses do not appear in the output. In the pseudo-syntax used here, the parentheses are structural and appear in the output.

*Rationale:* Rule 3 allows tasks to test whether participants correctly track grouped subexpressions, adding a meaningful complexity dimension without requiring knowledge of operator precedence in any particular language.

### Rule 4 — Numeric literals are not arithmetically evaluated
Numeric tokens in a concatenation or interpolation expression are treated as literal display values, not as numbers to be computed.

> `"World, " + 1 + 2 + 3` → `World, 123`  
> `(1 + 1 + 1 + 1)` → `(1111)` (parentheses preserved per Rule 3; values juxtaposed per Rule 1)

This differs from Python, where `str(1) + str(1+1+1+1)` would yield `"14"`.

### Rule 5 — Variable declarations are visible but irrelevant variables may be included
Some tasks declare variables that are not referenced in the expression (e.g., Tasks 13 and 14 declare `a` and `b` which do not appear in the expression). These serve as distractors to increase working memory load, consistent with complexity manipulation goals.

### Rule 6 — Nested interpolation markers are valid in the pseudo-syntax
In tasks where `{}` markers appear nested (Task 8), the outer `{}` triggers interpolation and the inner `()` marks a group whose contents are also substituted. This construct does not compile in Python or most languages, but is intentional in the pseudo-syntax to test comprehension of nested grouping structure without language-specific runtime constraints.

---

## 3. Task Generation Process

Tasks were developed manually through an iterative process:

1. **Domain selection.** We identified five real-world domains where string construction commonly occurs: (1) name/address formatting, (2) score/metric reporting, (3) file path construction, (4) URL building, and (5) symbolic/mathematical expressions. Each domain contributed two task pairs (one concatenation, one interpolation), yielding the 16-task instrument.

2. **Expression drafting.** For each domain, we wrote a canonical string expression at the target complexity level. Paired tasks (e.g., Tasks 3 and 4) cover the same domain and same variables, differing only in whether `+` or `{}` is used, so that any comprehension difference is attributable to syntax rather than content.

3. **Distractor construction.** Three distractor options were written for each task. Distractors follow a taxonomy of common comprehension errors:
   - *Order errors*: variables or segments appear in a different order than the expression
   - *Substitution errors*: wrong variables are resolved or variable names appear instead of values
   - *Structural errors*: grouping parentheses are omitted, collapsed, or misplaced
   - *Partial errors*: one segment is omitted from an otherwise correct output

4. **Pilot testing.** Tasks were piloted by the first author across approximately 100 repeated trials (N-of-1 design) to calibrate difficulty, verify timing, and confirm test-retest reliability before the main data collection.

5. **Authoring the instrument.** The finalized tasks were encoded in `questions.json` (the authoritative source) and embedded in `templates/experiment.html` for delivery through the Flask application.

---

## 4. Complexity Level Definitions

Complexity is defined by the number of distinct variables or literal tokens embedded in the string expression:

| Level | Label     | Description                                      | Example tasks |
|-------|-----------|--------------------------------------------------|---------------|
| L-1   | Low       | Two embedded variables or literal values          | 1, 2          |
| L-2   | Moderate  | Three embedded variables or literal values        | 3, 4, 5, 13, 14 |
| L-3   | High      | Four embedded variables or literal values         | 9, 10, 15, 16 |
| L-4   | Very High | More than four embedded variables or literal values | 7, 8, 11, 12 |

---

## 5. Task Ordering and Randomization

All 16 tasks were presented in a **fixed order** to all participants (Tasks 1–16 as numbered). Tasks alternate between Concatenation (odd-numbered tasks in the first half) and Interpolation (even-numbered) to minimize order effects. The fixed order was chosen over full randomization to ensure comparability of within-subject timing data across participants.

The session was preceded by four practice tasks (visible in `templates/pre-tasks.html`) that familiarized participants with the interface and response format. Practice task data were not included in analysis.

---

## 6. Known Issues and Clarifications

### 6.1 Tasks 7 and 8 — Pseudo-syntax clarification

**Reviewer concern (Reviewer 3):** Task 7's correct answer was reported as `"World, 1234513"` under Python semantics, and Task 8's nested interpolation markers were flagged as non-compilable in Python.

**Clarification:** Both tasks are correct under the pseudo-syntax rules defined in this document. Specifically:

- **Task 7** (`"World, " + 1 + 2 + 3 + (1 + 1 + 1 + 1) + ("5" + (6 + 7))`): Under Rule 4 (no arithmetic evaluation) and Rule 3 (parentheses preserved), the output is `"World, 123(1111)("5"(67))"`, which is option 4. Under Python semantics, the output would be `"World, 1234513"`, but the experiment does not use Python semantics.

- **Task 8** (`"{1} {2} {3} {({9} {9} {9} {1})} World { ({"5"} {(67)} )}"` ): Under Rule 6 (nested markers valid in pseudo-syntax) and Rule 3 (parentheses preserved), the output is `"1 2 3 (9 9 9 1) World ("5" (67) )"`, which is option 1.

---

## 7. Files in This Directory

| File | Purpose |
|------|---------|
| `questions.json` | Authoritative task definitions — source of truth for all 16 tasks |
| `generator.py` | Reads `questions.json`; produces `generated_experiment.html` and a summary table |
| `generated_experiment.html` | Standalone document of all tasks with correct answers shown — for reviewers and replicators |
| `templates/experiment.html` | Jinja2 template used in the live Flask application; tasks are embedded statically |
| `app.py` | Flask application that served the experiment to participants |
| `randomize.py` | Early prototype for option randomization; not used in the final experiment |
