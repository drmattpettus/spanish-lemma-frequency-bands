
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.api as sm


# ==========================================
# 1. LOCATE PROJECT FOLDERS
# ==========================================

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

RESULTS.mkdir(parents=True, exist_ok=True)

bands_file = DATA / "spanish_lemma_frequency_bands.tsv"
paradigms_file = DATA / "morpgological_paradigm_sizes.tsv"


# ==========================================
# 2. LOAD DATA
# ==========================================

print("Loading datasets...")

bands = pd.read_csv(bands_file, sep="\t")
paradigms = pd.read_csv(paradigms_file, sep="\t")

print("Frequency records:", len(bands))
print("Paradigm records:", len(paradigms))


# ==========================================
# 3. MERGE DATA
# ==========================================

merged = pd.merge(
    bands,
    paradigms,
    on="lemma",
    how="inner",
    validate="one_to_one"
)

merged["frequency"] = pd.to_numeric(
    merged["frequency"],
    errors="coerce"
)

merged["paradigm_size"] = pd.to_numeric(
    merged["paradigm_size"],
    errors="coerce"
)

merged = merged.dropna(
    subset=["frequency", "paradigm_size"]
)

merged = merged[
    (merged["frequency"] > 0) &
    (merged["paradigm_size"] > 0)
].copy()

print("Matched lemmas:", len(merged))

if len(merged) != len(bands):
    raise ValueError("Some frequency lemmas were not matched.")


# ==========================================
# 4. FREQUENCY SUMMARY BY BAND
# ==========================================

summary = (
    merged.groupby("band_id")["frequency"]
    .agg(["count", "min", "median", "max"])
    .reset_index()
)

summary.columns = [
    "band_id",
    "n",
    "minimum_frequency",
    "median_frequency",
    "maximum_frequency"
]

summary.to_csv(
    RESULTS / "frequency_distribution_by_band.tsv",
    sep="\t",
    index=False
)

print()
print("Frequency distribution by band:")
print(summary.to_string(index=False))


# ==========================================
# 5. SPEARMAN CORRELATION
# ==========================================

rho, spearman_p = spearmanr(
    merged["frequency"],
    merged["paradigm_size"]
)

print()
print("Continuous Spearman correlation:")
print("rho =", round(rho, 6))
print("p =", spearman_p)


# ==========================================
# 6. LOG10 FREQUENCY
# ==========================================

merged["log10_frequency"] = np.log10(
    merged["frequency"]
)

X = sm.add_constant(
    merged[["log10_frequency"]]
)

y = merged["paradigm_size"]


# ==========================================
# 7. POISSON MODEL DIAGNOSTICS
# ==========================================

poisson = sm.GLM(
    y,
    X,
    family=sm.families.Poisson()
).fit()

deviance_ratio = (
    poisson.deviance / poisson.df_resid
)

pearson_ratio = (
    poisson.pearson_chi2 / poisson.df_resid
)

print()
print("Poisson diagnostics:")
print("Deviance / df =", round(deviance_ratio, 6))
print("Pearson / df =", round(pearson_ratio, 6))


# ==========================================
# 8. NEGATIVE BINOMIAL REGRESSION
# ==========================================

nb = sm.NegativeBinomial(
    y,
    X
).fit(disp=False)

if not nb.mle_retvals.get("converged", False):
    raise RuntimeError("Regression did not converge.")

coefficient = nb.params["log10_frequency"]
standard_error = nb.bse["log10_frequency"]
regression_p = nb.pvalues["log10_frequency"]

ci = nb.conf_int().loc["log10_frequency"]

ci_low = ci.iloc[0]
ci_high = ci.iloc[1]

irr = np.exp(coefficient)
irr_low = np.exp(ci_low)
irr_high = np.exp(ci_high)

percentage_change = (irr - 1) * 100

print()
print("Negative binomial regression:")
print("Coefficient =", round(coefficient, 6))
print("Standard error =", round(standard_error, 6))
print("p =", regression_p)
print("IRR =", round(irr, 6))
print("IRR CI lower =", round(irr_low, 6))
print("IRR CI upper =", round(irr_high, 6))
print("Percent change =", round(percentage_change, 2))


# ==========================================
# 9. SAVE MERGED DATA
# ==========================================

merged.to_csv(
    RESULTS / "lemma_frequency_paradigm_validation.tsv",
    sep="\t",
    index=False
)


# ==========================================
# 10. SAVE STATISTICAL RESULTS
# ==========================================

output_file = (
    RESULTS / "continuous_frequency_validation_results.txt"
)

with open(output_file, "w", encoding="utf-8") as f:

    f.write("CONTINUOUS FREQUENCY VALIDATION\n")
    f.write("===============================\n\n")

    f.write("N = " + str(len(merged)) + "\n\n")

    f.write("Spearman correlation\n")
    f.write("rho = " + str(rho) + "\n")
    f.write("p = " + str(spearman_p) + "\n\n")

    f.write("Poisson diagnostics\n")
    f.write("Deviance ratio = " + str(deviance_ratio) + "\n")
    f.write("Pearson ratio = " + str(pearson_ratio) + "\n\n")

    f.write("Negative binomial regression\n")
    f.write("Coefficient = " + str(coefficient) + "\n")
    f.write("Standard error = " + str(standard_error) + "\n")
    f.write("p = " + str(regression_p) + "\n")
    f.write("IRR = " + str(irr) + "\n")
    f.write("IRR lower CI = " + str(irr_low) + "\n")
    f.write("IRR upper CI = " + str(irr_high) + "\n")
    f.write("Percent change = " + str(percentage_change) + "\n")


# ==========================================
# 11. FINISHED
# ==========================================

print()
print("ANALYSIS COMPLETE")
print("Results saved in:")
print(RESULTS)
