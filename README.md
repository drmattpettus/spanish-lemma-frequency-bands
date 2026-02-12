Spanish Lemma-Based Frequency Bands

This repository accompanies the article:

Validating Lemma-Based Frequency Bands in Spanish Through Morphological Complexity

submitted to Language Resources and Evaluation.

Overview

This repository contains data, scripts, and outputs used to construct and validate lemma-based frequency bands for Spanish.

Lemma frequencies were derived from the Spanish SUBTLEX-ESP subtitle corpus. Morphological complexity was operationalized as paradigm size and computed independently from the Spanish AnCora treebank annotated in the Universal Dependencies framework.

The purpose of this repository is to ensure transparency, reproducibility, and reusability of all analyses reported in the manuscript.

Repository Structure
data/

subtlex_esp_raw.xlsx
Raw frequency data from the SUBTLEX-ESP corpus.

spanish_lemma_frequency_bands.tsv
Final ranked lemma list with frequency, rank, and band assignment.

morphological_paradigm_sizes.tsv
Lemma-level morphological paradigm sizes derived from the AnCora treebank.

scripts/

01_build_spanish_lemma_frequency_bands.py
Constructs lemma-based frequency bands from SUBTLEX-ESP data.

02_rerun_validation.py
Computes descriptive statistics and inferential tests (Spearman correlation and Kruskal–Wallis test).

03_sanity_check_bands.py
Performs qualitative inspection of frequency bands.

results/

morphological_complexity_by_band.tsv
Summary statistics corresponding to Table 1 in the manuscript.

statistical_validation_results.txt
Output of inferential statistical analyses reported in the Results section.

Reproducibility

All analyses can be reproduced by running the scripts in numerical order using Python 3.9 or higher with standard scientific libraries:

pandas

numpy

scipy

All file names and output formats correspond directly to those referenced in the manuscript.

Citation

If you use this resource, please cite:

APA style:

Pettus, M.R.. (2026). Spanish lemma-based frequency bands with morphological validation (Version 1.0) [Data set]. GitHub. https://github.com/[USERNAME]/spanish-lemma-frequency-bands

(https://doi.org/10.5281/zenodo.18625674)

BibTeX:

@dataset{yourlastname_year_spanishbands,
  author       = {[Pettus], [Matthew R.]},
  title        = {Spanish Lemma-Based Frequency Bands with Morphological Validation},
  year         = {2026},
  version      = {1.0},
  publisher    = {GitHub},
  url          = {https://github.com/drmattpettus/spanish-lemma-frequency-bands},
  doi          = {[10.5281/zenodo.18625674)}
}
nder the MIT License. See the LICENSE file for details.
