# Spanish Lemma-Based Frequency Bands

This repository accompanies the manuscript:

**Evaluating Frequency-Based Lexical Stratification in Spanish: A Corpus-Based Validation Framework**

Prepared for resubmission to *Poznań Studies in Contemporary Linguistics*.

## Overview

This repository contains the data, Python scripts, and statistical outputs used to construct and validate lemma-based frequency bands for Spanish.

Lemma frequencies were derived from the Spanish SUBTLEX-ESP corpus. Morphological paradigm sizes were obtained independently from the Spanish AnCora treebank, annotated within the Universal Dependencies framework.

The study evaluates the relationship between lexical frequency and morphological paradigm size using both rank-based frequency bands and continuous-frequency statistical analyses.

The continuous-frequency analysis addresses the nonlinear distribution of lexical frequency and avoids assuming that equal-sized rank bands represent equal intervals of actual lexical frequency.

## Dataset

The validation dataset contains **13,871 Spanish lemmas** with matched frequency and morphological paradigm-size measurements.

The dataset is organized into 14 frequency bands:

- Bands 1–13 contain 1,000 lemmas each.
- Band 14 contains 871 lemmas.

Frequency bands represent consecutive intervals of lemma rank rather than equal numerical intervals of lexical frequency.

## Repository Structure

### data/

- `SUBTLEX-ESP.xlsx` — Source lexical frequency data.
- `spanish_lemma_frequency_bands.tsv` — Ranked lemma list containing lemma, frequency, rank, and band assignment.
- `morpgological_paradigm_sizes.tsv` — Lemma-level morphological paradigm-size measurements derived from AnCora.

### scripts/

- `01_build_spanish_lemma_frequency_bands.py` — Constructs lemma-based frequency bands.
- `02_rerun_validation.py` — Reproduces the original band-based statistical validation.
- `03_sanity_check_bands.py` — Performs qualitative inspection of frequency-band assignments.
- `04_continuous_frequency_validation.py` — Performs continuous-frequency correlation, Poisson regression diagnostics, and negative-binomial regression.

### results/

Original validation outputs:

- `morphological_complexity_by_band.tsv` — Descriptive statistics by frequency band.
- `statistical_validation_results.txt` — Original band-based inferential statistics.

Continuous-frequency validation outputs:

- `frequency_distribution_by_band.tsv` — Frequency distributions within each rank band.
- `lemma_frequency_paradigm_validation.tsv` — Matched lemma-level dataset used for continuous validation.
- `continuous_frequency_validation_results.txt` — Statistical output from continuous-frequency validation.

## Statistical Validation

### Band-Based Validation

The original validation evaluates the relationship between frequency-band rank and morphological paradigm size using Spearman rank correlation and the Kruskal–Wallis test.

These analyses are retained for transparency, reproducibility, and comparison with the continuous-frequency results.

### Continuous-Frequency Validation

The revised analysis treats lexical frequency as a continuous variable rather than relying exclusively on discrete frequency bands.

The analyses include:

1. Spearman rank correlation between actual lemma frequency and morphological paradigm size.
2. Log10 transformation of lemma frequency.
3. Poisson regression diagnostics for dispersion.
4. Negative-binomial regression predicting morphological paradigm size from log10 lemma frequency.

### Continuous-Frequency Results

| Statistic | Result |
|---|---|
| Matched lemmas | 13,871 |
| Spearman correlation (ρ) | 0.384707 |
| Poisson deviance / df | 1.095635 |
| Poisson Pearson chi-square / df | 1.552553 |
| Negative-binomial regression coefficient | 0.383164 |
| Standard error | 0.006883 |
| Incidence rate ratio (IRR) | 1.466918 |
| 95% CI for IRR | 1.447262–1.486841 |
| Statistical significance | p < .001 |

The negative-binomial regression estimates a **46.69% increase in expected morphological paradigm size for each tenfold increase in lemma frequency**.

The results support a positive association between lexical frequency and morphological paradigm size while avoiding the assumption that equal-sized frequency bands correspond to equal intervals of raw frequency.

## Reproducibility

The continuous-frequency analysis was successfully executed using Python 3.11.

Required Python libraries:

- pandas
- NumPy
- SciPy
- statsmodels

Install the required packages:

```bash
py -3.11 -m pip install pandas numpy scipy statsmodels
```

From the repository root, run:

```bash
py -3.11 scripts/04_continuous_frequency_validation.py
```

The script reads the frequency and morphological paradigm-size datasets from `data/` and writes the following outputs to `results/`:

- `frequency_distribution_by_band.tsv`
- `lemma_frequency_paradigm_validation.tsv`
- `continuous_frequency_validation_results.txt`

The original band-based validation scripts and outputs remain available for reproducibility.

## Data and Code Availability

The processed datasets, analysis scripts, and statistical results are available at:

https://github.com/drmattpettus/spanish-lemma-frequency-bands

The previously archived version is available through Zenodo:

https://doi.org/10.5281/zenodo.18625674

The updated repository will be archived as a revised Zenodo version incorporating the continuous-frequency validation.

## Citation

Pettus, M. R. (2026). *Spanish lemma-based frequency bands with morphological validation* [Data set and analysis code]. GitHub.

https://github.com/drmattpettus/spanish-lemma-frequency-bands

Previous Zenodo archive:

https://doi.org/10.5281/zenodo.18625674

## License

This repository is distributed under the MIT License. See the `LICENSE` file for details.
