"""
jaccard_similarity.py — Theme-level Jaccard similarity across LLM coding runs.

Computes pairwise Jaccard similarity between the sets of major themes produced
by the LLM across multiple runs on the calibration samples, as described in
PROMPT_DESIGN.md Section 5.

Jaccard(A, B) = |A ∩ B| / |A ∪ B|

A value ≥ 0.80 indicates that the major theme vocabulary is stable across runs.

Usage
-----
Supply each run's themes as comma-separated strings (one --run per run):

    python jaccard_similarity.py \\
        --run "Interpolation Preferred,Concatenation Familiarity,Context Dependent,No Preference" \\
        --run "Interpolation Preferred,Concatenation Familiarity,Context Dependent,Both Equal" \\
        --run "Interpolation Preferred,Concatenation Familiarity,Context Dependent,No Preference"

Or load themes from CSV files produced by the LLM (one --csv per run file).
Each file needs one row per response with an assigned theme, in a 'Theme'
column (use --col for a different name):

    python jaccard_similarity.py \\
        --csv calibration/run1_output.csv \\
        --csv calibration/run2_output.csv \\
        --csv calibration/run3_output.csv

NOTE: `calibration/Q1_run*_sample.csv` in this repository are the *input*
samples (UID, R-X, ResponseText) that were fed to the model — they do not carry
theme assignments, and the per-run coded outputs were not retained. Passing them
to --csv is an error. To reproduce Check 1 in PROMPT_DESIGN.md you must re-run
the Q1 prompt over each sample, save each run's coded output with a 'Theme'
column, and pass those files here.

Requirements
------------
    Python standard library only (no extra packages needed).
"""

import argparse
import csv
import itertools
from pathlib import Path


def jaccard(a: set, b: set) -> float:
    # Jaccard is undefined for two empty sets. Returning 1.0 here would report
    # perfect stability for runs that contain no themes at all, so this is
    # treated as an error by the caller rather than silently passing.
    if not a and not b:
        raise ValueError("Jaccard is undefined for two empty theme sets.")
    return len(a & b) / len(a | b)


def themes_from_csv(path: Path, col: str = "Theme") -> set[str]:
    """Read the set of distinct theme labels from one run's LLM output file.

    Raises if the file has no such column, rather than returning an empty set —
    an empty set would otherwise flow through to a vacuous stability PASS.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: file is empty.")
        if col not in reader.fieldnames:
            raise ValueError(
                f"{path}: no '{col}' column. Available columns: "
                f"{', '.join(reader.fieldnames)}.\n"
                f"  This script expects a run's *coded output* — one row per "
                f"response with an assigned theme — not the raw response sample. "
                f"Use --col to select a different column name."
            )
        themes = {row[col].strip() for row in reader if (row.get(col) or "").strip()}
    if not themes:
        raise ValueError(f"{path}: column '{col}' contains no theme labels.")
    return themes


def themes_from_string(s: str) -> set[str]:
    return {t.strip() for t in s.split(",") if t.strip()}


def report(run_themes: list[tuple[str, set]]) -> None:
    print("=" * 56)
    print("  Theme-level Jaccard Similarity Across Runs")
    print("=" * 56)

    for label, themes in run_themes:
        print(f"\n  {label} ({len(themes)} themes): {sorted(themes)}")

    print("\n  Pairwise Jaccard similarity:")
    print(f"  {'Pair':<20}  {'Shared':>6}  {'Union':>6}  {'Jaccard':>8}")
    print("  " + "-" * 44)

    scores = []
    for (la, ta), (lb, tb) in itertools.combinations(run_themes, 2):
        j = jaccard(ta, tb)
        scores.append(j)
        print(f"  {la} vs {lb:<10}  {len(ta & tb):>6}  {len(ta | tb):>6}  {j:>8.3f}")

    print()
    print(f"  Min Jaccard : {min(scores):.3f}")
    print(f"  Mean Jaccard: {sum(scores)/len(scores):.3f}")
    print(f"  Max Jaccard : {max(scores):.3f}")

    threshold = 0.80
    stable = all(s >= threshold for s in scores)
    status = "PASS" if stable else "FAIL"
    print(f"\n  Stability check (≥ {threshold}): {status}")
    print("=" * 56)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute Jaccard similarity of LLM themes across calibration runs."
    )
    parser.add_argument(
        "--run", action="append", metavar="THEMES", dest="runs",
        help="Comma-separated theme labels for one run. Repeat for each run.",
    )
    parser.add_argument(
        "--csv", action="append", metavar="FILE", dest="csvs",
        help="CSV file output by the LLM for one run (needs 'Theme' column). Repeat per run.",
    )
    parser.add_argument(
        "--col", default="Theme",
        help="Column name for theme labels in CSV files (default: 'Theme').",
    )
    args = parser.parse_args()

    if not args.runs and not args.csvs:
        parser.error("Provide at least two runs via --run or --csv.")

    try:
        if args.csvs:
            run_themes = [
                (f"Run {i+1}", themes_from_csv(Path(p), args.col))
                for i, p in enumerate(args.csvs)
            ]
        else:
            run_themes = [
                (f"Run {i+1}", themes_from_string(s))
                for i, s in enumerate(args.runs)
            ]
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: {exc}")

    if len(run_themes) < 2:
        parser.error("Need at least two runs to compute pairwise similarity.")

    report(run_themes)


if __name__ == "__main__":
    main()
