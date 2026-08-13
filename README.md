# String Readability Study — Replication Package
**Empirical Investigation to Understand the Impact of String Interpolation on Program Readability and Comprehension**

This repository contains all materials required to reproduce the quantitative and qualitative analyses reported in the study. The research investigates how **string interpolation** and **string concatenation** affect program readability, comprehension, and debugging efficiency among developers with prior programming experience.
It includes datasets, analysis scripts, survey instruments, qualitative prompts, and replication instructions.

<!-- > **⚠️ Read [`ERRATA.md`](ERRATA.md) before using the data.** It documents an
> answer-key error affecting all correctness analyses (erratum E-1) and several
> smaller data issues. Duration-based analyses are unaffected. -->

---

## Overview
The study combines **quantitative task-based experiments** and **qualitative thematic analysis** to examine developer reasoning and performance differences when reading or debugging string expressions.

- **Participants:** 314
- **Design:** Mixed-method study with randomized task presentation
- **Tasks:** 16 programming questions comparing string concatenation and interpolation (four complexity levels)
- **Post-survey:** Five open-ended questions exploring readability, debugging, learning curve, preference, and improvement suggestions
- **Goal:** To empirically determine how syntactic style, familiarity, and code complexity influence readability and comprehension.

---

## Repository Structure
```
string-readability-study/
├── README.md                        # Main documentation
├── ERRATA.md                        # Known data and instrument defects — read first
├── LICENSE                          # Code/data license
├── CITATION.cff                     # Citation metadata (for Zenodo DOI)
│
├── data/
│   ├── raw/                         # Original anonymized responses, one file per session
│   │   ├── quant/                   #   315 task-response files
│   │   └── qual/                    #   315 post-survey files
│   └── processed/                   # Merged datasets used by all analyses
│       ├── merged_quant.csv         #   5,040 rows (314 participants × 16 tasks)
│       ├── merged_qual.csv          #   315 post-survey responses
│       └── merged_qual_deduplicate_clean.csv   # manually cleaned, 304 responses
│
├── code/
│   ├── requirements.txt             # Dependencies for the analyses
│   ├── scripts/
│   │   ├── python/                  # Sample size, outliers, data provenance, errata
│   │   └── quorum/                  # Inferential statistics + duration plots (see its README)
│   └── notebooks/                   # Qualitative theme figures
│
├── instruments/
│   ├── survey-app/                  # Web-based experiment platform (Flask)
│   │   └── TASK_DESIGN.md           #   Task construction and pseudo-syntax rules
│   └── llm/                         # LLM-assisted qualitative coding
│       ├── PROMPT_DESIGN.md         #   Prompt development and robustness checks
│       ├── codebooks/               #   Validated codebooks (Q1–Q5)
│       ├── prompts/                 #   Standardized prompts (Q1–Q5)
│       ├── calibration/             #   Stability-check input samples
│       └── error_log.md             #   LLM error types and corrections
│
└── results/
    ├── figures/                     # Figures reported in the paper
    ├── csv_xlsx/                    # Coded qualitative data (Q1–Q5)
    └── Tukey–Kramer-Multiple-Comparsion-Results.txt
```

---

## Setup and Environment

### Prerequisites
- **Python** ≥ 3.10 and **pip** ≥ 23.0 — for the experiment platform and the Python analyses
- **Quorum Studio** ≥ 5.5.0 — only for the inferential statistics in `code/scripts/quorum/` ([download](https://quorumlanguage.com/download.html))
- **Git**; **Docker** (optional)

Set up a virtual environment for the Python components:

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python3 -m virtualenv venv
venv\Scripts\activate
```

---

## Reproducing the Analyses

Install the analysis dependencies:

```bash
pip install -r code/requirements.txt
```

### 1. Data provenance — rebuild `data/processed/` from `data/raw/`

```bash
python code/scripts/python/build_processed_data.py --check   # verify, write nothing
python code/scripts/python/build_processed_data.py           # rebuild
```

`--check` confirms that the published merged datasets are reproducible from the
raw session files, and reports the UID corruption documented as erratum E-5.

### 2. Sample size and power

```bash
python code/scripts/python/power_analysis.py
```

### 3. Outliers

```bash
python code/scripts/python/outlier_analysis.py
python code/scripts/python/outlier_analysis.py --by-task --by-category
```

Outliers are reported for transparency and **retained** in all analyses.

### 4. Errata impact

```bash
python code/scripts/python/apply_errata.py
```

Reports how the Task 6 answer-key error affects reported accuracy and writes a
corrected copy of the dataset. The published files are never modified.

### 5. Inferential statistics and duration plots (Quorum)

ANOVA, Tukey–Kramer, Bonferroni, correlation, linear regression, and the
duration box plots are implemented in Quorum. See
[`code/scripts/quorum/README.md`](code/scripts/quorum/README.md) for how to run
them and for one known gap (`BoxplotTaskCatDurationEach.quorum`).

### 6. Qualitative theme figures

```bash
jupyter notebook code/notebooks/1.0_quant_plots.ipynb
```

Regenerates the five theme bar charts into `results/figures/` as PNG and PDF.
The counts are the **human-adjudicated** theme assignments — the `Human Reviewer`
columns of the spreadsheets in `results/csv_xlsx/`, which differ from the
LLM-assigned `Theme` columns by design.

---

## Running the Experiment Platform

The Flask application in `instruments/survey-app/` is the instrument used to
collect the data.

### Running locally

```bash
cd instruments/survey-app
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` (or `http://127.0.0.1:5000`) to reach the consent
page.

> **macOS:** port 5000 is used by the AirPlay Receiver by default. Either
> disable it under *System Settings → General → AirDrop & Handoff*, or run
> `PORT=5050 python app.py` and use `http://localhost:5050`.

**Where responses go.** By default each participant's responses are written as
CSV files to `data/responses/` — one `<uid>_response.csv` for the 16 tasks and
one `<uid>_post_survey_response.csv` for the open-ended answers. These use the
same schema as `data/raw/`, so they can be merged with
`build_processed_data.py`.

No credentials or configuration are required. Copy `.env.example` to `.env` only
if you want to change the port, the output directory, or the storage backend.

The original study uploaded responses to a private S3 bucket
(`RESPONSE_STORAGE=s3`); those buckets are not accessible to replications, so
local storage is the default.

### Running with Docker

```bash
cd instruments/survey-app
docker compose up -d
```

The platform will be available on port 5000, and responses are written to
`data/responses/` on the host.

---

## Qualitative Coding and Codebook

- [`instruments/llm/PROMPT_DESIGN.md`](instruments/llm/PROMPT_DESIGN.md) — prompt development, calibration, and robustness checks
- `instruments/llm/prompts/` — standardized LLM prompts for Q1–Q5
- `instruments/llm/codebooks/` — validated codebooks
- `instruments/llm/error_log.md` — recurring LLM error types and their corrections
- `results/csv_xlsx/` and `results/figures/` — coded data and figures

Coding followed the **Framework Method** with human validation of all
model-assisted outputs. The `Human Reviewer` columns in `results/csv_xlsx/`
carry the adjudicated themes reported in the paper.

---

## Summary of Key Results
- Interpolation improved readability and reduced comprehension time.
- Familiarity influenced preferences, but interpolation's advantages were consistent across levels.
- Tooling, syntax, and formatting were key readability factors.

---

## Issues
If you encounter any problem reproducing this experiment, please check
[`ERRATA.md`](ERRATA.md) first, then contact the corresponding author.

---

## License
- **Code:** MIT License
- **Data:** Creative Commons Attribution 4.0 International (CC BY 4.0)
