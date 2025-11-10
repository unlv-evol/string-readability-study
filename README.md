# 📘 String Readability Study — Replication Package
**Empirical Investigation to Understand the Impact of String Interpolation on Program Readability and Comprehension**

This repository contains all materials required to reproduce the quantitative and qualitative analyses reported in the study. The research investigates how **string interpolation** and **string concatenation** affect program readability, comprehension, and debugging efficiency among developers with prior programming experience.  
It includes datasets, analysis scripts, survey instruments, qualitative prompts, and replication instructions.

---

## 🧠 Overview
The study combines **quantitative task-based experiments** and **qualitative thematic analysis** to examine developer reasoning and performance differences when reading or debugging string expressions.

- **Participants:** 314
- **Design:** Mixed-method study with randomized task presentation
- **Tasks:** 16 programming questions comparing string concatenation and interpolation (four complexity levels)
- **Post-survey:** Five open-ended questions exploring readability, debugging, learning curve, preference, and improvement suggestions
- **Goal:** To empirically determine how syntactic style, familiarity, and code complexity influence readability and comprehension.

---

## 📁 Repository Structure
```
string-readability-study/
string-readability-study/
├── README.md                        # Main documentation
├── LICENSE                          # Code/data license
├── CITATION.cff                     # Citation metadata (for Zenodo DOI)
│
├── data/                            # Raw and processed datasets
│   ├── raw/                         # Original anonymized responses
│   ├── processed/                   # Cleaned and structured datasets
│
├── code/                            # Scripts and reproducibility assets
│   ├── scripts/
│   ├── notebooks/                   # Jupyter notebooks for exploratory analysis
│
├── instruments/                     # Study instruments and materials
│   ├── survey-app/                  # Web-based experiment platform (Flask)
│   └── llm/                         # LLM 
│       ├── codebooks                # LLM qualitative codebooks
│       ├── prompts                  # LLM qualitative prompts (RQ1–RQ5)
│
├── results/                         # Output and visualizations
│   ├── figures/
│   ├── csv_xlsx/

```

---

## ⚙️ Setup and Environment

### 🔧 Prerequisites
- **Python** ≥ 3.10  
- **Pip** ≥ 23.0  
- **Git**, **Docker** (optional)

---

## ▶️ Reproduction Instructions
### Tool Setup
To replicate the experiment, you can simply follow the steps below to setup the data gathering tool.
#### Installation and Usage
1. **Running locally**
   - Setup the  by cloning the repository using `git clone` or download the repository.
   - It is a good practice to configure python virtual environment. Use the commands below to setup python virtual environment on `Linux/MacOS` or `Windows OS`. NB: The tool is designed using `Python 3.10` and tested on `Python 3.8` and `Python 3.9`.
   ```
   # For Linux/MacOS

   python3 -m venv venv
   source venv/bin/activate
   ```
   - For `Window OS` user, the easiest approach is to install `virtualenv` by running `pip install virtualenv`. The next step is pretty much similar to above;
   ```
   # For Window OS

   python3 -m virtualenv venv
   venv\Scripts\activate
   ```
   - Install required dependencies using `pip3 install -r requirements.txt`
   - Start the `experiment` by running `python3 app.py`. Ensure that port `5000` is open on your firewell. To interact with the experiment, go to your browser and type `localhost:5000` or `127.0.0.1:5000`.

2. **Running locally with "Docker for Desktop" - Not Yet Fully Tested!!**
   - Download and install `Docker fo Desktop` using the [link](https://www.docker.com/products/docker-desktop/). Once you are all set, run the commands below;
   ```
   git clone <project>
   cd /<project>/instruments/suvery-app
   docker compose up -d
   ```
  - That's all 😎!! the tool will be running on port `5000`. To interact with the experiment, go to your browser and type `localhost:5000`. You should be able to see the consent page of the experiment.
  
**NB: The ouput of the experiment will be stored in the [data](data) folder with the file name `responses.csv`**

---
### Issues 
Incase you encounter any challenge trying to reproduce this experiment, please feel free to report to the corresponding author of the paper.


Results appear in `results/figures/` and `results/csv_xlsx/`.

---

## 🧩 Qualitative Coding and Codebook
The repository includes:
- `instruments/prompts/` — standardized LLM prompts for RQ1–RQ5  
- `data/processed/codebook_final.csv` — validated codebook  
- `results/logs/qual_refinement.md` — coder agreement notes  

Coding followed the **Framework Method** with human validation of all model-assisted outputs.

---

## 📊 Summary of Key Results
- Interpolation improved readability and reduced comprehension time.  
- Familiarity influenced preferences, but interpolation’s advantages were consistent across levels.  
- Tooling, syntax, and formatting were key readability factors.

---

## 🧾 License
- **Code:** MIT License  
- **Data:** Creative Commons Attribution 4.0 International (CC BY 4.0)
