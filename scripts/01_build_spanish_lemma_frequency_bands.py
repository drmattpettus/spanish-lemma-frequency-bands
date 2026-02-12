import pandas as pd

# =====================================================
# CONFIG
# =====================================================

SUBTLEX_PATH = "SUBTLEX-ESP.xlsx"
LEXICON_PATH = "ancora_lexicon.txt"
BAND_SIZE = 1000
BLOCK_WIDTH = 4   # Word | Freq | per million | log

# =====================================================
# STEP 1: LOAD + STACK SUBTLEX
# =====================================================

print("Loading SUBTLEX...")

df = pd.read_excel(SUBTLEX_PATH)

blocks = []

for i, col in enumerate(df.columns):
    colname = str(col).strip()
    if colname.startswith("Word"):
        # frequency column is immediately to the right
        if i + 1 < len(df.columns):
            freq_col = df.columns[i + 1]
            block = df[[col, freq_col]].copy()
            block.columns = ["wordform", "frequency"]
            blocks.append(block)

subtlex_long = pd.concat(blocks, ignore_index=True)

# Normalize
subtlex_long["wordform"] = (
    subtlex_long["wordform"]
    .astype(str)
    .str.lower()
    .str.strip()
)

subtlex_long["frequency"] = pd.to_numeric(
    subtlex_long["frequency"],
    errors="coerce"
)

# Clean
subtlex_long = subtlex_long.dropna()
subtlex_long = subtlex_long[subtlex_long["frequency"] > 0]

# Remove numerals and non-alphabetic forms
subtlex_long = subtlex_long[
    subtlex_long["wordform"].str.match(r"^[a-záéíóúüñ]+$", na=False)
]


print(f"Loaded {len(subtlex_long):,} SUBTLEX wordform-frequency pairs")

# =====================================================
# STEP 2: LOAD ANCORA LEXICON
# =====================================================

print("Loading AnCora lexicon...")

lexicon = pd.read_csv(
    LEXICON_PATH,
    sep="\t",
    names=["wordform", "lemma"],
    dtype=str
)

lexicon["wordform"] = lexicon["wordform"].str.lower().str.strip()
lexicon["lemma"] = lexicon["lemma"].str.lower().str.strip()

print(f"Loaded {len(lexicon):,} AnCora lexicon entries")

# =====================================================
# STEP 3: LEMMATIZE SUBTLEX VIA ANCORA
# =====================================================

print("Lemmatizing SUBTLEX...")

lemmatized = subtlex_long.merge(
    lexicon,
    on="wordform",
    how="inner"
)

# Remove non-alphabetic lemmas (e.g. numerals)
lemmatized = lemmatized[
    lemmatized["lemma"].str.match(r"^[a-záéíóúüñ]+$", na=False)
]

print(f"Lemmatized {len(lemmatized):,} SUBTLEX wordforms")

# =====================================================
# STEP 4: AGGREGATE BY LEMMA
# =====================================================

lemma_freq = (
    lemmatized
    .groupby("lemma", as_index=False)["frequency"]
    .sum()
)

lemma_freq = lemma_freq.sort_values(
    by="frequency",
    ascending=False
).reset_index(drop=True)

print(f"Produced {len(lemma_freq):,} lemmas")

# =====================================================
# STEP 5: ASSIGN FREQUENCY BANDS
# =====================================================

lemma_freq["rank"] = lemma_freq.index + 1
lemma_freq["band_id"] = ((lemma_freq["rank"] - 1) // BAND_SIZE) + 1

print(f"Total bands: {lemma_freq['band_id'].max()}")

# =====================================================
# STEP 6: EXPORT
# =====================================================

OUTPUT_PATH = "spanish_lemma_frequency_bands.tsv"

lemma_freq.to_csv(
    OUTPUT_PATH,
    sep="\t",
    index=False
)

print("DONE!")
print(f"Saved: {OUTPUT_PATH}")
