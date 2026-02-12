import pandas as pd

bands = pd.read_csv(
    "spanish_lemma_frequency_bands.tsv",
    sep="\t"
)

print("Top 20 lemmas in Band 1:")
print(
    bands[bands["band_id"] == 1]
    .head(20)[["lemma", "frequency"]]
)

print("\nTop 20 lemmas in Band 5:")
print(
    bands[bands["band_id"] == 5]
    .head(20)[["lemma", "frequency"]]
)

print("\nTop 20 lemmas in Band 10:")
print(
    bands[bands["band_id"] == 10]
    .head(20)[["lemma", "frequency"]]
)

print("\nBottom 20 lemmas (last band):")
print(
    bands[bands["band_id"] == bands["band_id"].max()]
    .tail(20)[["lemma", "frequency"]]
)
