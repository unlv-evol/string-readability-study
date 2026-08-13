"""
outlier_analysis.py — Outlier identification for the String Interpolation Study.

Applies the standard IQR criterion to task completion times (Duration):
  Lower fence: Q1 - 1.5 * IQR
  Upper fence: Q3 + 1.5 * IQR

Observations outside these bounds are flagged as outliers. Consistent with
Section 2.12 of the paper, flagged observations are NOT removed — they are
retained in all analyses to preserve natural variability in human-performance
data. This script documents and reports outliers for transparency.

Usage
-----
    python outlier_analysis.py
    python outlier_analysis.py --data path/to/merged_quant.csv
    python outlier_analysis.py --by-task   # report outliers broken down by task

Requirements
------------
    pip install pandas
"""

import argparse
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parents[3] / "data" / "processed" / "merged_quant.csv"


def iqr_bounds(series: pd.Series) -> tuple[float, float]:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def flag_outliers(df: pd.DataFrame, col: str = "Duration") -> pd.DataFrame:
    lower, upper = iqr_bounds(df[col])
    df = df.copy()
    df["is_outlier"] = (df[col] < lower) | (df[col] > upper)
    df["lower_fence"] = lower
    df["upper_fence"] = upper
    return df


def print_overall(df: pd.DataFrame) -> None:
    total = len(df)
    n_outliers = df["is_outlier"].sum()
    pct = 100 * n_outliers / total
    lower = df["lower_fence"].iloc[0]
    upper = df["upper_fence"].iloc[0]

    print("=" * 58)
    print("  String Interpolation Study — Outlier Analysis")
    print("=" * 58)
    print(f"\n  Column examined : Duration (seconds)")
    print(f"  Total observations: {total:,}")
    print()
    print(f"  Q1              : {df['Duration'].quantile(0.25):.3f} s")
    print(f"  Q3              : {df['Duration'].quantile(0.75):.3f} s")
    print(f"  IQR             : {df['Duration'].quantile(0.75) - df['Duration'].quantile(0.25):.3f} s")
    print(f"  Lower fence     : {lower:.3f} s  (Q1 - 1.5 × IQR)")
    print(f"  Upper fence     : {upper:.3f} s  (Q3 + 1.5 × IQR)")
    print()
    print(f"  Outliers flagged: {n_outliers:,} ({pct:.1f}% of observations)")
    print(f"  Retained in analyses: YES (see Section 2.12)")


def print_by_task(df: pd.DataFrame) -> None:
    print("\n--- Outliers by Task ---")
    print(f"  {'TaskID':<8}  {'Category':<15}  {'Complexity':<12}"
          f"  {'N obs':>6}  {'N outliers':>10}  {'% outliers':>10}")
    print("  " + "-" * 70)

    for task_id, group in df.groupby("TaskID"):
        g = flag_outliers(group)
        n = len(g)
        n_out = g["is_outlier"].sum()
        cat = group["Category"].iloc[0]
        cplx = group["Complexity"].iloc[0]
        print(f"  {task_id:<8}  {cat:<15}  {cplx:<12}"
              f"  {n:>6}  {n_out:>10}  {100*n_out/n:>9.1f}%")


def print_by_category(df: pd.DataFrame) -> None:
    print("\n--- Outliers by Task Category ---")
    for cat, group in df.groupby("Category"):
        g = flag_outliers(group)
        n_out = g["is_outlier"].sum()
        pct = 100 * n_out / len(g)
        lower, upper = g["lower_fence"].iloc[0], g["upper_fence"].iloc[0]
        print(f"\n  {cat}")
        print(f"    Fences  : [{lower:.3f}, {upper:.3f}] s")
        print(f"    Outliers: {n_out} / {len(g)} ({pct:.1f}%)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report IQR-based outliers in task completion time."
    )
    parser.add_argument("--data", type=Path, default=DATA_PATH,
                        help="Path to merged_quant.csv")
    parser.add_argument("--by-task", action="store_true",
                        help="Also report outlier counts broken down by task")
    parser.add_argument("--by-category", action="store_true",
                        help="Also report outlier counts broken down by task category")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    df = flag_outliers(df)

    print_overall(df)

    if args.by_task:
        print_by_task(df)

    if args.by_category:
        print_by_category(df)

    print("\n" + "=" * 58)


if __name__ == "__main__":
    main()
