"""
build_processed_data.py — Rebuild data/processed/ from data/raw/.

Documents and reproduces the provenance of the processed datasets. Each
participant's session was stored as one CSV in data/raw/; this script
concatenates them into the merged datasets used by every downstream analysis.

Steps
-----
1. Read every CSV in data/raw/quant/ and data/raw/qual/, in filename order.
   Filenames embed the upload timestamp, so filename order is chronological.
2. Record the originating filename in a `source_file` column.
3. Assign each qualitative respondent a sequential display ID (`R-1`, `R-2`, …)
   in that same chronological order. These IDs are what the codebooks in
   instruments/llm/codebooks/ refer to.
4. Concatenate and write merged_quant.csv / merged_qual.csv.

The published files in data/processed/ were produced this way. Use --check to
verify that this script still reproduces them exactly before relying on it.

Note: this script does NOT produce merged_qual_deduplicate_clean.csv, which
involved manual review of free-text responses (removal of blank, duplicate, and
unusable answers) and is therefore not scriptable. It is published as-is.

Usage
-----
    python build_processed_data.py --check     # verify against published files
    python build_processed_data.py             # rebuild into data/processed/
    python build_processed_data.py --out DIR   # rebuild into DIR instead

Requirements
------------
    pip install pandas
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parents[3]
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

# Erratum E-5. UIDs are 8-character hex strings from uuid1(). Two of them are
# also valid scientific-notation literals, and the original merge let pandas
# coerce them to floats. This script reads UID as a string so it does not
# reproduce that corruption; --check reports these as expected differences.
KNOWN_UID_CORRUPTIONS = {
    "610081e7": ("6100810000000.0", "6.10081E+12"),
    "30377e60": ("3.0377e+64",),
}


def merge_directory(directory: Path, add_respondent_id: bool = False) -> pd.DataFrame:
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found in {directory}")

    frames = []
    for path in files:
        # dtype={"UID": str} is essential: without it, UIDs such as "610081e7"
        # and "30377e60" are read as floats. See KNOWN_UID_CORRUPTIONS.
        df = pd.read_csv(path, dtype={"UID": str})
        df["source_file"] = path.name
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)

    if add_respondent_id:
        # One row per respondent in the qualitative files, so a running counter
        # over the concatenated frame gives the R-X IDs used in the codebooks.
        uid_position = merged.columns.get_loc("UID")
        merged.insert(uid_position + 1, "R-X", [f"R-{i + 1}" for i in range(len(merged))])

    return merged


def build() -> dict[str, pd.DataFrame]:
    return {
        "merged_quant.csv": merge_directory(RAW_DIR / "quant"),
        "merged_qual.csv": merge_directory(RAW_DIR / "qual", add_respondent_id=True),
    }


def check(built: dict[str, pd.DataFrame]) -> int:
    failures = 0
    for name, rebuilt in built.items():
        published_path = PROCESSED_DIR / name
        if not published_path.exists():
            print(f"  {name}: MISSING published file at {published_path}")
            failures += 1
            continue

        published = pd.read_csv(published_path, dtype={"UID": str})

        # The published files carry the unnamed pandas index column from the
        # original write; normalise it away on both sides before comparing.
        published = published.loc[:, ~published.columns.str.startswith("Unnamed:")]
        rebuilt = rebuilt.loc[:, ~rebuilt.columns.str.startswith("Unnamed:")]

        # Erratum E-5: restore the corrupted UIDs in the published copy so the
        # rest of the comparison is meaningful, and report what was restored.
        restored = []
        for correct, corrupted_forms in KNOWN_UID_CORRUPTIONS.items():
            mask = published["UID"].isin(corrupted_forms)
            if mask.any():
                restored.append((correct, int(mask.sum())))
                published.loc[mask, "UID"] = correct

        if list(published.columns) != list(rebuilt.columns):
            print(f"  {name}: COLUMN MISMATCH")
            print(f"    published: {list(published.columns)}")
            print(f"    rebuilt  : {list(rebuilt.columns)}")
            failures += 1
            continue

        if len(published) != len(rebuilt):
            print(f"  {name}: ROW COUNT {len(published):,} published "
                  f"vs {len(rebuilt):,} rebuilt")
            failures += 1
            continue

        try:
            pd.testing.assert_frame_equal(
                published.reset_index(drop=True),
                rebuilt.reset_index(drop=True),
                check_dtype=False,
            )
        except AssertionError as exc:
            print(f"  {name}: CONTENT MISMATCH")
            print("   ", str(exc).split("\n")[0])
            failures += 1
            continue

        print(f"  {name}: OK — {len(rebuilt):,} rows, "
              f"{rebuilt.columns.size} columns reproduced exactly")
        for correct, n_rows in restored:
            print(f"      note: UID '{correct}' is stored corrupted in "
                  f"{n_rows} published row(s) (erratum E-5); "
                  f"rebuilt output has it correct")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild the processed datasets from the raw response files."
    )
    parser.add_argument("--check", action="store_true",
                        help="Verify the rebuild matches data/processed/ without writing")
    parser.add_argument("--out", type=Path, default=PROCESSED_DIR,
                        help="Directory to write rebuilt files into")
    args = parser.parse_args()

    print("=" * 58)
    print("  String Interpolation Study — Rebuild Processed Data")
    print("=" * 58)

    n_quant = len(list((RAW_DIR / "quant").glob("*.csv")))
    n_qual = len(list((RAW_DIR / "qual").glob("*.csv")))
    print(f"\n  Raw session files: {n_quant} quantitative, {n_qual} qualitative\n")

    built = build()

    if args.check:
        failures = check(built)
        print("\n" + "=" * 58)
        sys.exit(1 if failures else 0)

    args.out.mkdir(parents=True, exist_ok=True)
    for name, df in built.items():
        path = args.out / name
        df.to_csv(path, index=False)
        print(f"  Wrote {path} ({len(df):,} rows)")

    print("\n" + "=" * 58)


if __name__ == "__main__":
    main()
