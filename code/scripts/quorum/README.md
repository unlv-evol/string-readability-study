# Quorum Statistical Analyses

The inferential statistics reported in the paper (one-way ANOVA, Tukey–Kramer
multiple comparisons, Bonferroni correction, correlation, linear regression) and
the duration box plots were produced with the
[Quorum](https://quorumlanguage.com/) statistics libraries.

## Requirements

- **Quorum Studio 5.5.0** or later — https://quorumlanguage.com/download.html

Quorum is a separate toolchain from the Python analyses in `code/scripts/python/`
and `code/notebooks/`. If you only need the Python results, you can skip this
directory.

## Running

1. Open `Project/Project.qp` in Quorum Studio.
2. Set the file you want to run as the main file (right-click the file in
   `SourceCode/` → *Set as Main*), or edit the `"Main"` key in `Project.qp`.
3. Run the project. Output is printed to the Quorum Studio console.

Scripts resolve their input **relative to the project root** (this directory),
so they must be run from the project rather than from `SourceCode/`.

## Input data

`data/merged_quant.csv` is a verbatim copy of
[`data/processed/merged_quant.csv`](../../../data/processed/merged_quant.csv) at
the repository root. It is duplicated here because Quorum Studio resolves
`frame:Load(...)` paths relative to the project directory. If you regenerate the
processed dataset, refresh this copy:

```bash
cp data/processed/merged_quant.csv code/scripts/quorum/data/merged_quant.csv
```

## Scripts

| File | Analysis | Reported in |
|---|---|---|
| `OneWayAnovaComplexityDuration.quorum` | One-way ANOVA of task duration by complexity | Results |
| `TukeyKramer.quorum` | Tukey–Kramer pairwise comparisons of duration by college year | [`results/Tukey–Kramer-Multiple-Comparsion-Results.txt`](../../../results/) |
| `BonferroniCorrection.quorum` | Bonferroni-corrected pairwise comparisons | Results |
| `CorrelationCorrectnessTest.quorum` | Correlation involving task correctness | Results |
| `LinearRegressionCorrectness.quorum` | Linear regression on correctness | Results |
| `BoxPlotTaskGroup.quorum` | Duration by task group | `results/figures/Fig-TaskGroup-Duration.svg` |
| `BoxPlotTaskLevelCOYDuration.quorum` | Duration by task level and college year | `results/figures/Fig-TaskLevels-Duration.svg` |
| `BoxplotTaskCatDurationOverall.quorum` | Duration by task category, overall | `results/figures/Fig-concatation-interpolation-general.svg` |
| `BoxplotTaskCatDurationEach.quorum` | Duration by task category, per level | Results |
| `BoxplotTaskDurationCollegeYr.quorum` | Duration by college year | `results/figures/BoxPlotCollegeYear.svg` |

## Known gap: `TaskGroup`

`BoxplotTaskCatDurationEach.quorum` selects a factor named `TaskGroup`:

```quorum
frame:AddSelectedFactors("TaskGroup,Category")
```

**No `TaskGroup` column exists in `merged_quant.csv`.** The available columns are
`UID, Gender, Age, YearInCollege, Education, State, Major, JobExperience,
TaskID, Complexity, Category, CorrectAnswer, UserAnswer, Duration, source_file`.

This script therefore cannot run against the published dataset as-is, and
`results/figures/Fig-TaskGroup-Duration.svg` cannot be regenerated from it. The
grouping was evidently derived during analysis but the derivation was not
preserved in the processed data or in this repository.

If you are replicating this figure, define `TaskGroup` explicitly and add it to
the dataset before running the script. All other scripts in this directory run
against the published data unmodified.

## Note on correctness analyses

`CorrelationCorrectnessTest.quorum` and `LinearRegressionCorrectness.quorum` use
the `CorrectAnswer` column as collected, which contains the Task 6 answer-key
error described in [`ERRATA.md`](../../../ERRATA.md) (erratum E-1). Duration-based
analyses in this directory are unaffected. See `ERRATA.md` before interpreting
correctness results.
