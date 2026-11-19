# Reproducibility Checklist

This checklist follows the standard IEEE / ACM / NeurIPS reproducibility criteria for machine learning and computer vision research.

---

## 1. Claims and Hypotheses
- [x] **Clear Claims:** All central claims ($C_1$–$C_5$) are explicitly stated in `paper_artifacts/PLAN.md` and supported by empirical experiments.
- [x] **Error Bars & Variance:** Every quantitative metric is measured across **5 fixed random seeds** (`[42, 123, 456, 789, 1024]`), reporting mean, standard deviation, and 95% confidence intervals.
- [x] **Statistical Significance:** Statistical significance tests (two-tailed paired $t$-test, Wilcoxon signed-rank test, Cohen's $d$) are executed and reported in `paper_artifacts/tables/tab6_statistical_significance.tex` and `.csv`.

---

## 2. Experimental Data & Partitions
- [x] **Dataset Provenance:** All 3 source datasets (`grassknoted/asl-alphabet`, `ayuraj/asl-dataset`, `danrasband/asl-alphabet-test`) are documented with their respective licenses, sizes, and collection contexts in `data_card.md`.
- [x] **Data Leakage Mitigation:** Contiguous per-class chunk partitioning is applied to prevent burst-capture frames from leaking between training and validation sets.
- [x] **Out-of-Distribution Testing:** An entire independent dataset recorded by a different signer (`danrasband`) is held out exclusively for out-of-domain generalization testing.
- [x] **No Fabricated Data:** Raw per-run results are saved with timestamps, seeds, and configurations into `paper_artifacts/evaluations/raw_results/` and are never overwritten.

---

## 3. Computational Assets & Baseline Models
- [x] **Deployed Checkpoint:** The trained model `asl_cnn_model.onnx` is verified with input shape `(1, 96, 96, 3)` and 3 declared output taps (`logits`, `conv1_relu`, `dense_features`).
- [x] **Parity Verification:** Numerical parity between the Keras baseline and ONNX Runtime CPU is verified with a maximum logit discrepancy of $1.14 \times 10^{-5}$ ($< 10^{-4}$).
- [x] **Baselines:** 3 comparative baselines are implemented in `paper_artifacts/baselines/` (42-D Coordinate MLP, Coordinate Random Forest, Coordinate SVM).
- [x] **Ablations:** Major design components are ablated (rendering resolution, chromatic encoding, stroke weight, threshold gating, denoising filters).

---

## 4. Figures and Tables Reproducibility
- [x] **Script-Driven Plotting:** Every figure in `paper_artifacts/plots/pdf/` and `paper_artifacts/plots/png/` is generated programmatically by its corresponding script in `paper_artifacts/plots/scripts/` from raw results.
- [x] **Publication Standards:** Figures are exported as vector PDFs and high-resolution 350 DPI PNGs with colorblind-safe palettes (Okabe-Ito / Wong), labeled axes with units, and font consistency.
- [x] **Dual Table Formats:** All tables are generated simultaneously as publication LaTeX (`.tex`) with `booktabs` and machine-readable `.csv`.
- [x] **One-Click Execution:** The master runner `paper_artifacts/reproducibility/run_all_evaluations.py` reproduces all raw results, aggregations, plots, and tables in a single command.
