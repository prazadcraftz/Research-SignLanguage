# Research Paper Artifacts: ASL Recognition Evaluation, Benchmarks, Plots & Tables

This folder contains the complete, self-contained empirical evaluation framework, baseline models, ablation experiments, publication-quality figures, and LaTeX tables for the research paper:

> **"Bridging the Reality Gap in Sign Language Fingerspelling: Canonical Skeleton Rendering, Adaptive Denoising, and Spatiotemporal Kinematic Decomposition for Edge Devices"**

All evaluations are conducted with strict scientific rigor:
- **5 fixed random seeds** (`[42, 123, 456, 789, 1024]`), reporting mean $\pm$ standard deviation and 95% confidence intervals.
- **Leakage-free protocol**: Contiguous per-class chunk partitioning and out-of-domain cross-signer testing (`danrasband`).
- **No fabricated numbers**: All figures and tables are generated programmatically from immutable raw JSON runs stored in `evaluations/raw_results/`.
- **Publication standards**: All figures are provided simultaneously as vector PDFs (with embedded fonts) and high-resolution 350 DPI PNG previews using a colorblind-safe palette (Okabe-Ito / Wong). All tables are generated as both publication LaTeX (`.tex`) with `booktabs` and machine-readable `.csv`.

---

## 1. Directory Structure

```
paper_artifacts/
├── PROJECT_UNDERSTANDING.md   # Comprehensive project analysis, architecture & dataset study
├── PLAN.md                    # Research claims, experimental matrix, baselines & ablations
├── README.md                  # This file: step-by-step reproduction instructions
├── environment/
│   ├── hardware_info.json     # OS, CPU, RAM, and exact library versions
│   ├── requirements.txt       # Pinned dependencies
│   └── seeds.json             # Pinned experimental random seeds [42, 123, 456, 789, 1024]
├── configs/                   # One JSON configuration file per experiment
├── evaluations/
│   ├── canonical_templates.npz # Extracted (26, 21, 2) baseline hand landmarks
│   ├── scripts/               # Standalone evaluation scripts
│   ├── raw_results/           # Immutable per-seed JSON result files
│   ├── aggregated/            # Mean, std, and 95% CIs across seeds
│   └── logs/                  # Execution logs
├── baselines/                 # Baseline implementations (Coordinate MLP, Random Forest, SVM)
├── ablations/                 # Ablation scripts & results (Rendering properties, etc.)
├── analysis/
│   ├── statistical_significance.py # Paired t-tests, Wilcoxon signed-rank tests, Cohen's d
│   └── statistical_tests.json      # Output statistical significance metrics
├── plots/
│   ├── scripts/               # Matplotlib reproduction scripts per figure
│   ├── pdf/                   # Vector PDF figures (TrueType fonts embedded)
│   └── png/                   # 350+ DPI preview PNG figures
├── tables/                    # LaTeX (.tex) and CSV (.csv) versions of all tables
└── reproducibility/
    ├── reproducibility_checklist.md # Standard ML reproducibility checklist
    ├── model_card.md          # Formal model card for asl_cnn_model.onnx
    ├── data_card.md           # Dataset provenance, detection rates & splits
    └── run_all_evaluations.py # Master one-click automated runner
```

---

## 2. Quick Reproduction (One-Click)

To reproduce the entire benchmark suite, all 10 figures, and all 7 tables in a single run:

```bash
python paper_artifacts/reproducibility/run_all_evaluations.py
```

This master runner will sequentially execute:
1. Domain Shift Failure Chain (`eval_domain_shift.py` across 5 seeds)
2. Landmark Denoising Benchmark (`eval_smoothing.py` across 5 seeds)
3. Spatiotemporal Trajectory Kinematics (`eval_motion_kinematics.py` across 5 seeds)
4. Confidence Gating Sensitivity & Jitter Stability (`eval_confidence_gating.py` across 5 seeds)
5. Computational Efficiency & Latency Profiling (`eval_efficiency_profiling.py`)
6. Main Benchmark vs. Vector Baselines (`eval_main_and_baselines.py` across 5 seeds)
7. Rendering Properties Ablation (`ablate_rendering.py` across 5 seeds)
8. Cross-seed aggregation (`aggregate_results.py`)
9. Paired $t$-test and Wilcoxon statistical significance testing (`statistical_significance.py`)
10. Vector PDF and 350 DPI PNG plot generation (`plots/scripts/*.py`)
11. LaTeX (`.tex`) and CSV table generation (`tables/generate_tables.py`)

---

## 3. Step-by-Step Individual Experiment Reproduction

Each experiment can also be executed independently:

### A. Domain Shift Breakdown ("Bug Chain")
Evaluates accuracy degradation under scale/framing mismatches, aspect ratio squashing, and color channel inversion:
```bash
python paper_artifacts/evaluations/scripts/eval_domain_shift.py --seed 123
python paper_artifacts/plots/scripts/plot_domain_shift.py
```
- Output: `plots/pdf/fig1_domain_shift.pdf` and `tables/tab2_domain_shift.tex`

### B. Landmark Denoising (1-Euro vs. Fixed EMA vs. Raw)
Measures still-hand shimmer RMS across noise levels and dynamic tracking latency across speeds:
```bash
python paper_artifacts/evaluations/scripts/eval_smoothing.py --seed 123
python paper_artifacts/plots/scripts/plot_smoothing_tradeoff.py
```
- Output: `plots/pdf/fig2_smoothing_tradeoff.pdf` and `tables/tab3_smoothing_benchmark.tex`

### C. Kinetic Motion Detection for J and Z
Evaluates trajectory discrimination and path length vs. speed separability:
```bash
python paper_artifacts/evaluations/scripts/eval_motion_kinematics.py --seed 123
python paper_artifacts/plots/scripts/plot_motion_kinematics.py
```
- Output: `plots/pdf/fig3_motion_kinematics.pdf`

### D. Confidence Gating & Jitter Stability
Sweeps confidence threshold $\tau \in [0.4, 0.95]$ and evaluates prediction invariance across 8 perturbation trials:
```bash
python paper_artifacts/evaluations/scripts/eval_confidence_gating.py --seed 123
python paper_artifacts/plots/scripts/plot_gating_sensitivity.py
```
- Output: `plots/pdf/fig4_gating_sensitivity.pdf`

### E. Main Benchmark vs. Baselines
Compares Proposed Canonical CNN against 42-D Coordinate MLP, Random Forest, and SVM across 5 seeds:
```bash
python paper_artifacts/evaluations/scripts/eval_main_and_baselines.py --seed 123
python paper_artifacts/plots/scripts/plot_baseline_comparison.py
python paper_artifacts/plots/scripts/plot_confusion_matrix.py
python paper_artifacts/plots/scripts/plot_per_class_f1.py
```
- Output: `plots/pdf/fig5_confusion_matrix.pdf`, `plots/pdf/fig6_per_class_f1.pdf`, `plots/pdf/fig8_baseline_comparison.pdf`, and `tables/tab1_main_results.tex`

### F. Computational Efficiency & Latency Breakdown
Profiles per-stage wall-clock latency (ms), parameter count, FLOPs, and FPS on CPU:
```bash
python paper_artifacts/evaluations/scripts/eval_efficiency_profiling.py
python paper_artifacts/plots/scripts/plot_latency_breakdown.py
```
- Output: `plots/pdf/fig7_latency_breakdown.pdf` and `tables/tab5_efficiency_profiling.tex`

### G. Rendering Ablations
Evaluates input resolution ($48, 96, 192$), chromatic encoding, and stroke thickness:
```bash
python paper_artifacts/ablations/ablate_rendering.py --seed 123
python paper_artifacts/plots/scripts/plot_ablation_rendering.py
```
- Output: `plots/pdf/fig9_ablation_rendering.pdf`

---

## 4. Key Empirical Findings Summary (Averaged across 5 Random Seeds)

| Evaluation Experiment | Proposed System | Baseline / Old Pipeline | Statistical Significance & Finding |
| :--- | :---: | :---: | :--- |
| **Domain Shift Robustness** | **86.77% ± 0.39%** (Canonical) | **35.11% ± 0.51%** (Combined Shift) | Enforcing a single shared renderer prevents a **51.66% accuracy collapse**. |
| **Landmark Denoising (Still Shimmer)** | **0.70 ± 0.04 px** RMS | 1.99 ± 0.07 px (Raw) / 1.20 px (EMA 0.5) | 1-Euro reduces idle shimmer by **64.8%** vs raw input at zero drag. |
| **Landmark Denoising (Lag @ 2000 px/s)** | **3.6 ± 0.1 ms** (7.2 px) | 131.8 ± 0.1 ms (EMA 0.20) | 1-Euro eliminates **97.3%** of dynamic motion latency. |
| **Top-1 Test Accuracy (vs. Vector MLP)** | **86.90% ± 0.59%** (CNN) | 63.89% ± 5.86% (Coordinate MLP) | Significant improvement: **+23.01%** ($t = 8.22$, $p = 1.195 \times 10^{-3}$, Cohen's $d = 3.68$). |
| **Commit Gate Precision** | **94.53%** (at $\tau = 0.75$) | 86.90% (Ungated raw output) | Elevates precision by **+7.63%** while maintaining 88.35% coverage. |
| **Jitter Stability (Correct Predictions)** | **99.06% ± 0.18%** Invariance | 88.79% ± 0.94% (Ambiguous/wrong signs) | Prediction flips are concentrated on ambiguous signs, not scattered randomly. |
| **Single-Window UI Latency** | **18.1 ms** Compositing | Separate Windows ($>45$ ms) | Single-window OpenCV composition cuts inter-window IPC overhead. |
| **CNN Inference Latency (CPU)** | **3.78 ms** (p50) / 11.6 ms (mean) | Real-time requirement ($<33.3$ ms) | Model uses only 308k params (1.18 MB ONNX), executing at 86+ FPS isolated. |
