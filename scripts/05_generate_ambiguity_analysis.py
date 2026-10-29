
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kruskal
import statsmodels.api as sm


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

if SCRIPT_DIR.name.lower() == "scripts":
    ROOT = SCRIPT_DIR.parent
else:
    ROOT = SCRIPT_DIR

DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

BAND_SIZE = 1000
VALID_WORD = r"[a-záéíóúüñ]+"

SEARCH_DIRS = [
    DATA_DIR,
    ROOT,
    SCRIPT_DIR,
    ROOT / "raw",
    ROOT / "source",
]


def find_file(filename):
    """Find an input file in common project directories."""

    for folder in SEARCH_DIRS:
        candidate = folder / filename
        if candidate.is_file():
            return candidate

    stem = Path(filename).stem
    suffix = Path(filename).suffix

    for folder in SEARCH_DIRS:
        for number in range(1, 10):
            candidate = folder / f"{stem}({number}){suffix}"

            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        f"Cannot find {filename}. "
        f"Place the file in {DATA_DIR}"
    )


# ============================================================
# STEP 1: READ ANCORA WORD-FORM / LEMMA MAPPINGS
# ============================================================

print("STEP 1: Reading AnCora files...")

pairs = set()

for split in ("train", "dev", "test"):

    filename = f"es_ancora-ud-{split}.conllu"
    path = find_file(filename)

    with path.open(encoding="utf-8") as stream:

        for line in stream:

            if line.startswith("#"):
                continue

            columns = line.rstrip("\n").split("\t")

            if len(columns) < 3:
                continue

            # Exclude multiword tokens and empty nodes.
            if not columns[0].isdigit():
                continue

            wordform = columns[1].lower().strip()
            lemma = columns[2].lower().strip()

            pairs.add((wordform, lemma))


lexicon = pd.DataFrame(
    sorted(pairs),
    columns=["wordform", "lemma"]
)

lexicon = lexicon[
    lexicon["wordform"].str.fullmatch(
        VALID_WORD, na=False
    )
    & lexicon["lemma"].str.fullmatch(
        VALID_WORD, na=False
    )
].copy()

lexicon["candidate_count"] = (
    lexicon.groupby("wordform")["lemma"]
    .transform("nunique")
)

print(f"Unique valid mappings: {len(lexicon):,}")


# ============================================================
# STEP 2: READ SUBTLEX-ESP
# ============================================================

print("STEP 2: Reading SUBTLEX-ESP...")

subtlex_path = find_file("SUBTLEX-ESP.xlsx")

raw = pd.read_excel(subtlex_path)

blocks = []

for index, column in enumerate(raw.columns[:-1]):

    if str(column).strip().startswith("Word"):

        block = raw.iloc[:, [index, index + 1]].copy()

        block.columns = [
            "wordform",
            "frequency"
        ]

        blocks.append(block)


if not blocks:
    raise ValueError(
        "No Word/Frequency column pairs were found "
        "in SUBTLEX-ESP.xlsx."
    )


subtlex = pd.concat(
    blocks,
    ignore_index=True
)

subtlex["wordform"] = (
    subtlex["wordform"]
    .astype(str)
    .str.lower()
    .str.strip()
)

subtlex["frequency"] = pd.to_numeric(
    subtlex["frequency"],
    errors="coerce"
)

subtlex = subtlex.dropna(
    subset=["frequency"]
)

subtlex = subtlex[
    (subtlex["frequency"] > 0)
    & subtlex["wordform"].str.fullmatch(
        VALID_WORD,
        na=False
    )
].copy()

print(f"SUBTLEX rows: {len(subtlex):,}")


# ============================================================
# STEP 3: RECONSTRUCT FREQUENCY ALLOCATIONS
# ============================================================

print("STEP 3: Reconstructing frequencies...")

matched = subtlex.merge(
    lexicon,
    on="wordform",
    how="inner"
)

# Original method:
# Full frequency is assigned to every candidate lemma.

original_rebuilt = (
    matched.groupby("lemma")["frequency"]
    .sum()
)

# Sensitivity method:
# Divide each wordform frequency equally among
# all distinct candidate lemmas.

matched["equal_share"] = (
    matched["frequency"]
    / matched["candidate_count"]
)

equal_rebuilt = (
    matched.groupby("lemma")["equal_share"]
    .sum()
)

ambiguous_count = (
    matched.loc[
        matched["candidate_count"] > 1,
        "wordform"
    ]
    .nunique()
)

print(
    f"Ambiguous matched word forms: "
    f"{ambiguous_count:,}"
)


# ============================================================
# STEP 4: VERIFY ORIGINAL FREQUENCY DATA
# ============================================================

print("STEP 4: Checking original frequencies...")

original_path = find_file(
    "spanish_lemma_frequency_bands.tsv"
)

original = pd.read_csv(
    original_path,
    sep="\t"
)

required_columns = {
    "lemma",
    "frequency",
    "rank",
    "band_id"
}

missing_columns = (
    required_columns - set(original.columns)
)

if missing_columns:
    raise ValueError(
        "Original band file is missing columns: "
        + ", ".join(sorted(missing_columns))
    )

original["lemma"] = (
    original["lemma"]
    .astype(str)
    .str.lower()
    .str.strip()
)

if original["lemma"].duplicated().any():
    raise ValueError(
        "Duplicate lemmas in original band file."
    )

reference = (
    original.set_index("lemma")["frequency"]
)

rebuilt = original_rebuilt.reindex(
    reference.index
)

if rebuilt.isna().any():
    raise ValueError(
        "Some original lemmas could not be reconstructed."
    )

reference_values = reference.to_numpy(dtype=float)
rebuilt_values = rebuilt.to_numpy(dtype=float)

if not np.allclose(
    reference_values,
    rebuilt_values,
    rtol=0,
    atol=1e-6
):

    maximum_difference = np.max(
        np.abs(reference_values - rebuilt_values)
    )

    raise ValueError(
        "Reconstructed frequencies do not match "
        "the original dataset. "
        f"Maximum difference: {maximum_difference}"
    )

print("PASS: Original frequencies match.")


# ============================================================
# STEP 5: CREATE LEMMA-LEVEL COMPARISON DATASET
# ============================================================

print("STEP 5: Creating comparison dataset...")

comparison = original[
    ["lemma", "frequency", "rank", "band_id"]
].copy()

comparison["fractional_frequency"] = (
    comparison["lemma"].map(equal_rebuilt)
)

if comparison["fractional_frequency"].isna().any():
    raise ValueError(
        "Missing equal-allocation frequency values."
    )

comparison = comparison.sort_values(
    ["fractional_frequency", "rank"],
    ascending=[False, True],
    kind="stable"
).reset_index(drop=True)

comparison["fractional_rank"] = (
    np.arange(1, len(comparison) + 1)
)

comparison["fractional_band"] = (
    (comparison["fractional_rank"] - 1)
    // BAND_SIZE
) + 1

comparison["rank_shift"] = (
    comparison["fractional_rank"]
    - comparison["rank"]
)

comparison["band_changed"] = (
    comparison["band_id"]
    != comparison["fractional_band"]
)

comparison = comparison.sort_values(
    "rank"
).reset_index(drop=True)

comparison_path = (
    RESULTS_DIR
    / "ambiguity_impact_lemma_comparison.tsv"
)

comparison.to_csv(
    comparison_path,
    sep="\t",
    index=False
)

print(f"Saved: {comparison_path}")


# ============================================================
# STEP 6: LOAD MORPHOLOGICAL PARADIGM SIZES
# ============================================================

print("STEP 6: Loading paradigm sizes...")

paradigm_path = None

possible_names = [
    "morpgological_paradigm_sizes.tsv",
    "morphological_paradigm_sizes.tsv",
    "lemma_paradigm_sizes.txt"
]

for filename in possible_names:

    try:
        paradigm_path = find_file(filename)
        break

    except FileNotFoundError:
        continue


if paradigm_path is None:
    raise FileNotFoundError(
        "Cannot find the morphological paradigm-size file."
    )


if paradigm_path.suffix.lower() == ".txt":

    paradigms = pd.read_csv(
        paradigm_path,
        sep="\t",
        header=None,
        names=["lemma", "paradigm_size"]
    )

else:

    paradigms = pd.read_csv(
        paradigm_path,
        sep="\t"
    )


required_paradigm_columns = {
    "lemma",
    "paradigm_size"
}

if not required_paradigm_columns.issubset(
    paradigms.columns
):
    raise ValueError(
        "Paradigm file must contain columns named "
        "'lemma' and 'paradigm_size'."
    )


paradigms["lemma"] = (
    paradigms["lemma"]
    .astype(str)
    .str.lower()
    .str.strip()
)

paradigms["paradigm_size"] = pd.to_numeric(
    paradigms["paradigm_size"],
    errors="raise"
)

if paradigms["lemma"].duplicated().any():
    raise ValueError(
        "Duplicate lemmas in paradigm-size data."
    )


analysis = comparison.merge(
    paradigms[["lemma", "paradigm_size"]],
    on="lemma",
    how="inner",
    validate="one_to_one"
)

if len(analysis) != len(comparison):
    raise ValueError(
        "Some lemmas are missing paradigm-size values. "
        f"Expected {len(comparison):,}, "
        f"found {len(analysis):,}."
    )

if (
    analysis["paradigm_size"].isna().any()
    or (analysis["paradigm_size"] <= 0).any()
):
    raise ValueError(
        "Paradigm sizes must be positive and nonmissing."
    )

print(
    f"Paradigm observations: {len(analysis):,}"
)


# ============================================================
# STEP 7: RUN SENSITIVITY ANALYSIS
# ============================================================

print("STEP 7: Running statistical analyses...")

changed = int(
    analysis["band_changed"].sum()
)

percentage = (
    100 * changed / len(analysis)
)

lines = [
    "AMBIGUITY SENSITIVITY ANALYSIS",
    "=" * 50,
    f"Lemmas analyzed: {len(analysis):,}",
    f"Ambiguous matched forms: {ambiguous_count:,}",
    f"Band changes: {changed:,} ({percentage:.2f}%)"
]


analyses = [
    (
        "ORIGINAL",
        "frequency",
        "band_id"
    ),
    (
        "EQUAL ALLOCATION",
        "fractional_frequency",
        "fractional_band"
    )
]


for label, frequency_column, band_column in analyses:

    frequencies = analysis[
        frequency_column
    ].astype(float)

    paradigm_sizes = analysis[
        "paradigm_size"
    ].astype(float)

    if (frequencies <= 0).any():
        raise ValueError(
            f"Nonpositive frequencies in {label}."
        )

    # Continuous-frequency Spearman correlation
    rho, p_value = spearmanr(
        frequencies,
        paradigm_sizes
    )

    # Band-level Spearman correlation
    band_rho, band_p = spearmanr(
        analysis[band_column],
        paradigm_sizes
    )

    # Kruskal-Wallis test
    groups = [
        group["paradigm_size"].to_numpy()
        for _, group in analysis.groupby(band_column)
    ]

    H, kw_p = kruskal(*groups)

    # Negative-binomial regression
    log_frequency = np.log10(
        frequencies
    )

    X = pd.DataFrame(
        {
            "const": np.ones(len(analysis)),
            "log10_frequency": log_frequency.to_numpy()
        }
    )

    X.index = analysis.index

    model = sm.NegativeBinomial(
        paradigm_sizes,
        X
    )

    fit = model.fit(
        disp=False,
        maxiter=500
    )

    if not fit.mle_retvals.get("converged", False):
        raise RuntimeError(
            f"Negative-binomial model did not converge: "
            f"{label}"
        )

    coefficient = float(
        fit.params["log10_frequency"]
    )

    irr = float(
        np.exp(coefficient)
    )

    confidence_interval = np.exp(
        fit.conf_int()
        .loc["log10_frequency"]
        .to_numpy()
    )

    lines.extend([
        "",
        label,
        "-" * 50,
        f"Continuous Spearman rho: {rho:.6f}",
        f"Continuous Spearman p: {p_value:.6e}",
        f"Band Spearman rho: {band_rho:.6f}",
        f"Band Spearman p: {band_p:.6e}",
        f"Kruskal-Wallis H: {H:.6f}",
        f"Kruskal-Wallis p: {kw_p:.6e}",
        f"Negative-binomial coefficient: {coefficient:.6f}",
        f"IRR: {irr:.6f}",
        (
            "95% CI: "
            f"[{confidence_interval[0]:.6f}, "
            f"{confidence_interval[1]:.6f}]"
        )
    ])


# ============================================================
# STEP 8: SAVE STATISTICAL RESULTS
# ============================================================

print("STEP 8: Saving results...")

results_path = (
    RESULTS_DIR
    / "ambiguity_sensitivity_validation_results.txt"
)

results_path.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print()
print("\n".join(lines))
print()
print("=" * 50)
print("SUCCESS: Analysis completed.")
print("=" * 50)

print("\nFiles created:")

print(comparison_path)
print(results_path)
