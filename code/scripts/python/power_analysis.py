"""
power_analysis.py — Sample size and power analysis for the String Interpolation Study.

This script documents the assumptions behind the a priori sample-size estimate
reported in Section 2.4 of the paper, and reports the achieved power given the
effect sizes observed in the final sample.

Study design
------------
  Within-subjects repeated-measures experiment.
  Primary comparison: two conditions (Concatenation vs. Interpolation).
  Secondary comparison: seven academic-level groups (college year).
  N = 314 participants; 16 tasks each.

A priori reasoning (Section 2.4)
---------------------------------
No prior empirical study on string interpolation vs. concatenation existed,
so the expected effect size could not be estimated from the literature.
Following standard practice in human-subjects program-comprehension research,
we assumed a small-to-medium effect size and used a conservative target to:
  (a) remain adequately powered if the true effect is small (d ≈ 0.20);
  (b) support subgroup analyses (e.g., by college year) which require larger
      samples than the primary two-condition comparison.

A paired t-test is the appropriate unit for the primary two-condition within-
subjects comparison (Concatenation vs. Interpolation). Required sample sizes
for the primary comparison under three effect-size assumptions are shown below.
The target of ≈ 280 corresponds to the conservative small effect (d = 0.20),
providing a comfortable buffer above the minimum and allowing precision for
secondary analyses. Recruitment exceeded this target, yielding n = 314.

Usage
-----
    python power_analysis.py

Requirements
------------
    pip install statsmodels
"""

import math
from statsmodels.stats.power import TTestPower

# ── Study constants ────────────────────────────────────────────────────────────
ALPHA = 0.05
TARGET_POWER = 0.80
N_ACTUAL = 314

# Observed F-statistic for the primary within-subjects factor (task category)
# from the repeated-measures ANOVA reported in the paper:
#   F(1, 5026) = 92.35, p < .001, η²G = .018
F_PRIMARY = 92.35

# For a 2-level within-subjects factor, F = t², so t = √F,
# and Cohen's d_z (the paired effect size) = t / √N.
D_Z_OBSERVED = math.sqrt(F_PRIMARY) / math.sqrt(N_ACTUAL)


def required_n(d: float, alpha: float = ALPHA, power: float = TARGET_POWER) -> int:
    """Return the minimum n for a two-tailed paired t-test."""
    analysis = TTestPower()
    n = analysis.solve_power(
        effect_size=d, alpha=alpha, power=power, alternative="two-sided"
    )
    return math.ceil(n)


def achieved_power(d: float, n: int, alpha: float = ALPHA) -> float:
    """Return achieved power for a two-tailed paired t-test."""
    analysis = TTestPower()
    return analysis.solve_power(
        effect_size=d, nobs=n, alpha=alpha, alternative="two-sided"
    )


def separator(char: str = "-", width: int = 58) -> None:
    print(char * width)


def main() -> None:
    print("=" * 58)
    print("  String Interpolation Study — Power Analysis")
    print("=" * 58)

    # ── A priori analysis ──────────────────────────────────────────────────────
    print("\n[1] A Priori Sample-Size Estimation")
    separator()
    print(f"  Design:        Within-subjects, 2 conditions (paired)")
    print(f"  Test:          Two-tailed paired t-test")
    print(f"  Alpha (α):     {ALPHA}")
    print(f"  Target power:  {TARGET_POWER}")
    print()

    scenarios = [
        ("Small",        "d = 0.20", 0.20),
        ("Small-medium", "d = 0.30", 0.30),
        ("Medium",       "d = 0.50", 0.50),
    ]

    print(f"  {'Assumption':<14}  {'Effect size':<14}  {'Required n':>10}")
    separator(" ", 0)
    print(f"  {'':<14}  {'':<14}  {'----------':>10}")
    for label, desc, d in scenarios:
        n = required_n(d)
        print(f"  {label:<14}  {desc:<14}  {n:>10}")

    print()
    print("  The conservative small-effect scenario (d = 0.20, n ≈ 199)")
    print("  was used as the basis for the ≈ 280 participant target.")
    print("  The additional headroom above 199 accounts for anticipated")
    print("  attrition and supports secondary subgroup analyses")
    print("  (e.g., by college year, which involves 7 groups).")
    print(f"\n  Actual enrollment: {N_ACTUAL} participants.")

    # ── Post-hoc achieved power ────────────────────────────────────────────────
    print("\n[2] Achieved Power (post-hoc, based on observed results)")
    separator()
    print(f"  Observed F(1, 5026) = {F_PRIMARY} for task category")
    print(f"  Derived Cohen's d_z = √F / √N = {D_Z_OBSERVED:.3f}  (medium effect)")
    print()

    ap = achieved_power(D_Z_OBSERVED, N_ACTUAL)
    print(f"  {'Effect size':<22}  {'n':>6}  {'Achieved power':>15}")
    separator(" ", 0)
    print(f"  {'':<22}  {'------':>6}  {'---------------':>15}")
    print(f"  {'Observed (d_z = ' + f'{D_Z_OBSERVED:.3f})':<22}  {N_ACTUAL:>6}  {ap:>15.4f}")

    # Show power at other plausible d values for reference
    for label, d in [("Small (d = 0.20)", 0.20), ("Medium (d = 0.50)", 0.50)]:
        p = achieved_power(d, N_ACTUAL)
        print(f"  {label:<22}  {N_ACTUAL:>6}  {p:>15.4f}")

    print()
    print("  With n = 314 and the observed medium effect (d_z ≈ 0.54),")
    print("  the study is effectively at ceiling power for the primary")
    print("  two-condition comparison.")

    # ── Reference ─────────────────────────────────────────────────────────────
    print("\n[3] Reference")
    separator()
    print("  Cohen, J. (1988). Statistical Power Analysis for the")
    print("  Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.")
    print()
    print("  Statsmodels: Seabold & Perktold (2010). Statsmodels:")
    print("  Econometric and statistical modeling with Python.")
    print("  Proceedings of the 9th Python in Science Conference.")
    print("=" * 58)


if __name__ == "__main__":
    main()
