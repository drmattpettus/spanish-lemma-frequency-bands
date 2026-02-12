import pandas as pd
from scipy.stats import spearmanr, kruskal

# =========================================
# LOAD DATA
# =========================================

bands = pd.read_csv(
    "spanish_lemma_frequency_bands.tsv",
    sep="\t"
)

paradigms = pd.read_csv(
    "lemma_paradigm_sizes.txt",
    sep="\t",
    names=["lemma", "paradigm_size"]
)

print(f"Loaded {len(bands):,} frequency-banded lemmas")
print(f"Loaded {len(paradigms):,} paradigm-size entries")

# =========================================
# MERGE
# =========================================

merged = bands.merge(
    paradigms,
    on="lemma",
    how="inner"
)
merged = bands.merge(
    paradigms,
    on="lemma",
    how="inner"
)

merged["paradigm_size"] = pd.to_numeric(
    merged["paradigm_size"],
    errors="coerce"
)

merged = merged.dropna(subset=["paradigm_size"])

print(f"Merged dataset contains {len(merged):,} lemmas")

# =========================================
# DESCRIPTIVE STATISTICS BY BAND
# =========================================

summary = (
    merged
    .groupby("band_id")["paradigm_size"]
    .agg(["count", "mean", "median"])
    .reset_index()
)

print("\nParadigm size by frequency band:")
print(summary)

summary.to_csv(
    "morphological_complexity_by_band.tsv",
    sep="\t",
    index=False
)

# =========================================
# STATISTICAL TESTS
# =========================================

# Spearman correlation (band_id vs paradigm size)
rho, spearman_p = spearmanr(
    merged["band_id"],
    merged["paradigm_size"]
)

# Kruskal–Wallis across bands
groups = [
    group["paradigm_size"].values
    for _, group in merged.groupby("band_id")
]

H, kruskal_p = kruskal(*groups)

print("\nSpearman rank correlation:")
print(f"rho = {rho:.4f}")
print(f"p-value = {spearman_p:.3e}")

print("\nKruskal–Wallis test:")
print(f"H statistic = {H:.4f}")
print(f"p-value = {kruskal_p:.3e}")

# =========================================
# SAVE RESULTS
# =========================================

with open("statistical_validation_results.txt", "w") as f:
    f.write("Spearman rank correlation\n")
    f.write(f"rho\t{rho:.6f}\n")
    f.write(f"p\t{spearman_p:.6e}\n\n")
    f.write("Kruskal-Wallis test\n")
    f.write(f"H\t{H:.6f}\n")
    f.write(f"p\t{kruskal_p:.6e}\n")

print("\nSaved:")
print("- morphological_complexity_by_band.tsv")
print("- statistical_validation_results.txt")
