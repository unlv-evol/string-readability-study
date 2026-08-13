"""
apply_errata.py — Apply documented errata to the published dataset.

The files in data/processed/ are published exactly as recorded by the experiment
platform and are never modified in place. This script applies the corrections
documented in ERRATA.md and writes a corrected copy, so that both the collected
and the corrected results can be reproduced.

Erratum E-1 (Task 6 answer key)
-------------------------------
The live instrument scored Task 6 against option 4; the correct answer is
option 3. All 315 Task 6 rows carry CorrectAnswer = 4. This script rewrites
those to 3 and recomputes correctness.

Duration is unaffected by this erratum, so duration-based analyses (ANOVA,
Tukey-Kramer, box plots) give identical results before and after.

Erratum E-2 (duplicate session)
-------------------------------
UID ab9dba9b submitted two complete 16-task sessions (32 rows). Pass
--dedupe-sessions to keep only the first session for that participant.

Usage
-----
    python apply_errata.py                    # report impact, write corrected copy
    python apply_errata.py --report-only      # report impact, write nothing
    python apply_errata.py --dedupe-sessions  # also apply E-2
    python apply_errata.py --out PATH         # choose output path

Requirements
------------
    pip install pandas
"""

import argparse
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parents[3]
DATA_PATH = REPO_ROOT / "data" / "processed" / "merged_quant.csv"
DEFAULT_OUT = REPO_ROOT / "data" / "processed" / "merged_quant_corrected.csv"

# Erratum E-1: TaskID -> corrected CorrectAnswer
ANSWER_KEY_CORRECTIONS = {6: 3}

# Erratum E-2: participant with a duplicated session
DUPLICATE_SESSION_UID = "ab9dba9b"


def accuracy_table(df: pd.DataFrame) -> dict:
    correct = (df.UserAnswer == df.CorrectAnswer).astype(int)
    by_cat = df.assign(c=correct).groupby("Category").c.mean()
    return {
        "overall": correct.mean(),
        "by_category": by_cat.to_dict(),
    }


def apply_answer_key(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for task_id, correct_option in ANSWER_KEY_CORRECTIONS.items():
        df.loc[df.TaskID == task_id, "CorrectAnswer"] = correct_option
    df["IsCorrect"] = (df.UserAnswer == df.CorrectAnswer).astype(int)
    return df


def dedupe_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the first session for participants who submitted twice."""
    counts = df.groupby("UID").size()
    duplicated = counts[counts > 16].index
    if len(duplicated) == 0:
        return df

    keep = []
    for uid, group in df.groupby("UID", sort=False):
        if uid in duplicated:
            first_source = group.source_file.iloc[0]
            keep.append(group[group.source_file == first_source])
        else:
            keep.append(group)
    return pd.concat(keep).sort_index()


def report(before: pd.DataFrame, after: pd.DataFrame) -> None:
    b, a = accuracy_table(before), accuracy_table(after)

    print("=" * 58)
    print("  String Interpolation Study — Errata Impact")
    print("=" * 58)

    for task_id, correct_option in ANSWER_KEY_CORRECTIONS.items():
        t = before[before.TaskID == task_id]
        shipped = t.CorrectAnswer.iloc[0]
        print(f"\n  E-1: Task {task_id} answer key {shipped} -> {correct_option}")
        print(f"       Responses affected: {len(t):,}")
        print(f"       Scored incorrect but actually correct: "
              f"{int((t.UserAnswer == correct_option).sum()):,}")
        print(f"       Scored correct but actually incorrect: "
              f"{int((t.UserAnswer == shipped).sum()):,}")

    print(f"\n  Accuracy            {'As shipped':>12}  {'Corrected':>12}")
    print("  " + "-" * 42)
    print(f"  {'Overall':<18} {b['overall']:>11.2%}  {a['overall']:>12.2%}")
    for cat in sorted(b["by_category"]):
        print(f"  {cat:<18} {b['by_category'][cat]:>11.2%}"
              f"  {a['by_category'][cat]:>12.2%}")

    if b["by_category"]:
        rank_before = max(b["by_category"], key=b["by_category"].get)
        rank_after = max(a["by_category"], key=a["by_category"].get)
        if rank_before != rank_after:
            print(f"\n  NOTE: the more accurate condition changes from "
                  f"{rank_before} to {rank_after}.")
            print("        Correctness claims must use the corrected scoring.")

    print("\n  Duration is unaffected by E-1; duration-based analyses")
    print("  (ANOVA, Tukey-Kramer, box plots) are unchanged.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply documented errata and write a corrected dataset copy."
    )
    parser.add_argument("--data", type=Path, default=DATA_PATH,
                        help="Path to merged_quant.csv")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Where to write the corrected copy")
    parser.add_argument("--report-only", action="store_true",
                        help="Print the impact report without writing a file")
    parser.add_argument("--dedupe-sessions", action="store_true",
                        help="Also apply E-2 (drop the duplicated second session)")
    args = parser.parse_args()

    original = pd.read_csv(args.data)
    corrected = apply_answer_key(original)

    report(original, corrected)

    if args.dedupe_sessions:
        before_rows = len(corrected)
        corrected = dedupe_sessions(corrected)
        print(f"\n  E-2: dropped {before_rows - len(corrected)} duplicate-session rows "
              f"({DUPLICATE_SESSION_UID})")
        print(f"       Rows: {before_rows:,} -> {len(corrected):,}   "
              f"UIDs: {corrected.UID.nunique():,}")

    if not args.report_only:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        corrected.to_csv(args.out, index=False)
        print(f"\n  Wrote corrected copy: {args.out}")
        print("  (data/processed/merged_quant.csv is unchanged)")

    print("\n" + "=" * 58)


if __name__ == "__main__":
    main()
