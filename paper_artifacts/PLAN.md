# Research Paper Experimental & Manuscript Plan

**Document Path:** `paper_artifacts/PLAN.md`  
**Date:** November 2026  
**Status:** Awaiting User Approval  

---

## 1. Central Claims of the Paper

This research paper, tentatively titled:  
> **"Bridging the Reality Gap in Sign Language Fingerspelling: Canonical Skeleton Rendering, Adaptive Denoising, and Spatiotemporal Kinematic Decomposition for Edge Devices"**

advances five verifiable scientific claims:

- **Claim 1 (Canonical Shared Rendering Eliminates Domain Shift):**  
  Classifying hand geometry via an aspect-ratio-preserving, centered, deterministic skeleton renderer shared strictly across training and inference isolates structural hand posture, eliminating background/skin-tone sensitivity and preventing the catastrophic cross-modal degradation (e.g., $98.6\% \rightarrow 39.6\%$) caused by naive preprocessing discrepancies.

- **Claim 2 (Leakage-Free Benchmark Protocol Discloses Authentic Generalization):**  
  Random train/test splits on burst-recorded sign datasets leak temporally correlated, near-duplicate frames into validation sets, creating an illusion of near-perfect accuracy ($\ge 98\%$). Contiguous per-class chunk partitioning and holding out an unseen signer/dataset (`danrasband`) reveals the true out-of-distribution performance ($93.7\%$) with a minimal generalization gap ($3.1\%$).

- **Claim 3 (Hybrid Kinematic-Static Decomposition Solves Dynamic Signs):**  
  Decoupling static handshapes ($A$–$Z$) from dynamic temporal gestures ($J$ and $Z$) via hand-width-normalized trajectory kinematics resolves movement-dependent signs without the computational overhead, parameter inflation, or sequence-data requirements of 3D-CNNs or video transformers.

- **Claim 4 (Synergistic Denoising & Kinetic Gating Resolve the Stability-Latency Dilemma):**  
  Per-joint adaptive 1-euro filtering decouples idle jitter reduction ($1.00\text{ px}$ RMS) from motion lag ($4\text{ ms}$ at $2000\text{ px/s}$), and temporal kinetic commit gating ($10$ consecutive agreeing frames at $\ge 0.75$ confidence) delivers high commit precision ($96.7\%$) and jitter stability ($99.0\%$).

- **Claim 5 (Real-Time Edge Efficiency with Transparent Interpretability):**  
  The full pipeline runs at $>30\text{ FPS}$ on commodity CPU architectures with under $310\text{k}$ parameters, accompanied by an instrumented ONNX inference graph that surfaces intermediate layer activations for live visual explainability.

---

## 2. Experimental Design Matrix

| Claim | Experiment ID | Description | Primary Datasets / Inputs | Expected Output Artifacts |
| :--- | :--- | :--- | :--- | :--- |
| **Claim 1** | `EXP-RENDER-1` | **Domain Shift Chain:** Compare accuracy under: (a) canonical RGB renderer, (b) BGR/RGB color swap, (c) unscaled bounding boxes, (d) anisotropic aspect distortion. | Test split (`danrasband`) / Synthetic perturbations | Table & Bar Chart of accuracy collapse |
| **Claim 1** | `EXP-RENDER-2` | **Background Invariance Test:** Compare skeleton CNN vs. raw RGB CNN across diverse synthetic/real background insertions. | Rendered skeletons vs. Synthetic background composited images | Robustness curve across background complexity |
| **Claim 2** | `EXP-LEAK-1` | **Leakage Audit:** Compare random $80/20$ split vs. contiguous chunk split on `alphabet` + `ayuraj`. | Partitioning scripts on landmark dataset | Accuracy & Generalization gap table |
| **Claim 2** | `EXP-LEAK-2` | **Cross-Subject Generalization:** Evaluate model trained on single signer vs. multi-signer on the held-out `danrasband` test set. | `alphabet` alone vs. `alphabet` + `ayuraj` $\rightarrow$ `danrasband` | Cross-dataset transfer matrix |
| **Claim 3** | `EXP-KINEM-1` | **Dynamic Gesture Disambiguation:** Evaluate static CNN predictions on J vs. I and Z vs. D with and without `MotionTracker`. | Trajectory test sequences (still, J hook, Z zigzag) | Disambiguation confusion matrix & path length distributions |
| **Claim 3** | `EXP-KINEM-2` | **Speed vs. Path Length Discriminator:** Measure separability of still hand, slow J/Z, and fast J/Z under velocity vs. path metrics. | Hand trajectory logs | ROC curves for kinematic thresholds |
| **Claim 4** | `EXP-FILTER-1` | **Denoising Trade-off:** Still-hand RMS shimmer and motion-lag curves comparing Raw, Fixed-Alpha EMA ($\alpha \in \{0.2, 0.35, 0.5\}$), and 1-Euro Filter. | Synthetic 30 FPS trajectory with Gaussian noise | Shimmer vs. Lag trade-off curve |
| **Claim 4** | `EXP-GATE-1` | **Threshold & Jitter Stability:** Evaluate commit coverage, precision, and prediction flips across 8 perturbation trials on test hands. | Test split (`danrasband`) with `jitter_landmarks()` | Gating precision curve & stability breakdown table |
| **Claim 5** | `EXP-EDGE-1` | **Latency & Resource Profiling:** Benchmark runtime breakdown per frame (MediaPipe, Filter, Render, ONNX CPU, UI compositing). | System CPU execution (1000 frames) | Latency breakdown stacked bar & FPS metrics |
| **Claim 5** | `EXP-EDGE-2` | **Model Complexity Comparison:** Compare params, FLOPs, ONNX file size against MobileNetV3, ResNet-18, and Coordinate MLP. | Model definitions & FLOP profiler | Parameter vs. Latency Pareto plot |

---

## 3. Baselines for Rigorous Comparison

To contextualize the framework in the academic literature, we compare against three distinct model families:

1. **Direct Coordinate Baselines (Landmark Vector Classifiers):**
   - **42-D Coordinate MLP:** 3-layer Multi-Layer Perceptron ($42 \rightarrow 128 \rightarrow 64 \rightarrow 26$) trained directly on flattened normalized $(x, y)$ coordinates. Evaluates whether 2D convolutional feature learning on rendered skeletons provides meaningful inductive bias over raw coordinate vectors.
   - **Coordinate Random Forest & SVM:** Classic machine learning baselines trained on $(21 \times 2)$ coordinates.
2. **Direct Image-Based CNN Baselines (Raw Pixel Classifiers):**
   - **Custom CNN on Raw Crops:** Identical 3-block architecture trained directly on RGB hand crops without skeleton rendering.
   - **MobileNetV3-Small / SqueezeNet:** Standard lightweight vision backbones trained on raw hand crops to quantify sensitivity to illumination and background shifts.
3. **Temporal Baseline Equivalents (for Dynamic J/Z):**
   - **Single-Frame Static Classifier:** The baseline model without temporal motion tracking (showing classification failure on J and Z).
   - **Fixed-Window Velocity Detector:** Differentiating consecutive frames without path integration or adaptive deadzones.

---

## 4. Comprehensive Ablation Suite

1. **Ablation 1: Rendering Modality & Visual Encoding:**
   - Skeleton canvas resolution: $48 \times 48$, $96 \times 96$ (default), $192 \times 192$.
   - Skeleton color encoding: Multi-color finger schema (MediaPipe transcribed) vs. single-color grayscale skeleton.
   - Bone thickness / Joint radius scaling.
2. **Ablation 2: Landmark Data Augmentation:**
   - Full augmentation pipeline (Default).
   - Without horizontal mirroring ($p = 0$).
   - Without in-plane rotation ($\pm 15^\circ$).
   - Without isotropic scaling ($0.9$–$1.1$).
   - Without Gaussian landmark jitter.
3. **Ablation 3: Normalization & Framing Mechanics:**
   - Aspect-preserving isotropic box scaling ($HAND\_FILL = 0.70$) vs. anisotropic stretching to canvas boundaries.
   - Centered alignment vs. uncentered raw camera coordinates.
4. **Ablation 4: Architectural Design Choices:**
   - BatchNorm Momentum: $0.90$ (Default) vs. $0.99$ (Keras default collapse).
   - Pooling Strategy: Global Average Pooling (GAP) vs. Flatten $\rightarrow$ Dense (testing parameter explosion and memorization).
   - Dropout Rate: $0.25 / 0.50$ vs. No Dropout ($0.0$).
5. **Ablation 5: HCI Gating & Temporal Commit Parameters:**
   - `COMMIT_CONFIDENCE`: Sweep from $0.50$ to $0.95$ (step $0.05$).
   - `COMMIT_FRAMES`: Sweep from $3$ to $20$ consecutive frames.

---

## 6. Target Metrics & Statistical Significance Protocol

### 6.1 Evaluation Metrics
- **Classification Performance:** Top-1 Accuracy, Macro-averaged Precision, Recall, and F1-Score, Class-balanced Accuracy, per-class Confusion Matrix.
- **HCI & Gating Performance:** Gate Coverage ($\%$), Commit Precision ($\%$), Wrong Commit Rate ($\%$), Jitter Invariance Agreement ($\%$).
- **Temporal & Denoising Performance:** Root Mean Square (RMS) Shimmer (pixels), Dynamic Lag (ms and pixels) across speeds ($100$–$2000\text{ px/s}$).
- **Computational Efficiency:** Number of Parameters ($\text{M}$ / $\text{k}$), Model Size (MB), FLOPs, Stage-wise Latency (ms), Throughput (FPS) on standard CPU.

### 6.2 Statistical Rigor
- Run all stochastic experiments with **5 fixed random seeds** (`seeds = [42, 123, 456, 789, 1024]`).
- Report **mean $\pm$ standard deviation** and **$95\%$ confidence intervals** for all quantitative metrics.
- Perform **paired two-tailed Student's $t$-tests** or **Wilcoxon signed-rank tests** where claims of improvement are made (with significance threshold $p < 0.05$).

---

## 7. Complete List of Figures and Tables for the Manuscript

### Figures (Publication-Quality Vector PDF + 300+ DPI PNG)
1. **`fig1_system_architecture`:** End-to-end framework diagram: capture $\rightarrow$ 21 landmarks $\rightarrow$ 1-euro filter $\rightarrow$ canonical normalization $\rightarrow$ deterministic skeleton rendering $\rightarrow$ ONNX CNN & Kinematic MotionTracker $\rightarrow$ single-window UI.
2. **`fig2_domain_shift_collapse`:** The "Bug Chain" degradation bar chart showing accuracy falling from $98.6\%$ to $75.3\%$ and $39.6\%$ under camera framing, aspect distortion, and color-channel inversion.
3. **`fig3_leakage_and_splits`:** Schematic illustrating the burst-recording leakage mechanism in random splits vs. contiguous per-class chunk partitioning and cross-dataset testing on `danrasband`.
4. **`fig4_training_curves`:** Training and validation loss and accuracy trajectories across epochs (demonstrating steady convergence without overfitting).
5. **`fig5_confusion_matrix`:** Normalized confusion matrix on the unseen test set (`danrasband`), highlighting fine-grained structural confusions (fist handshapes M, N, S, T) and isolated class N behavior.
6. **`fig6_smoothing_tradeoff`:** Landmark smoothing benchmark: idle shimmer (RMS px) vs. dynamic latency (ms) comparing Raw, Fixed-Alpha EMA, and Adaptive 1-Euro Filter.
7. **`fig7_motion_kinematics`:** Kinematic trajectories for J and Z, depicting fingertip displacement, hook detection, and reversal zero-crossings.
8. **`fig8_commit_gate_sensitivity`:** Sensitivity curves for commit threshold $\tau \in [0.5, 0.95]$ vs. commit precision, coverage, and character latency.
9. **`fig9_feature_activations`:** Visualization of conv1 filter mosaic (32 tiles) and hidden-layer activation heatmap on representative letters.
10. **`fig10_latency_breakdown`:** Stacked bar chart of pipeline latency (MediaPipe, Filter, Render, ONNX CPU, UI compositing).

### Tables (LaTeX `.tex` + CSV)
1. **`tab1_dataset_statistics`:** Detailed breakdown of `alphabet`, `ayuraj`, and `danrasband` (images, detected hands, detection rates, license, split roles).
2. **`tab2_main_results_benchmark`:** Top-1 Accuracy, Macro F1, Commit Precision, and Stability comparing Proposed Framework against Baselines (Coordinate MLP, Raw RGB CNN, MobileNetV3).
3. **`tab3_ablation_rendering`:** Ablation results on canvas size ($48, 96, 192$), skeleton color coding (multi-color vs. grayscale), and line stroke thickness.
4. **`tab4_ablation_augmentation`:** Ablation of individual landmark augmentation components (mirror, rotate, scale, jitter).
5. **`tab5_smoothing_benchmark`:** Detailed numerical comparison of still shimmer, lag at $300\text{ px/s}$, and lag at $2000\text{ px/s}$ across filter configurations.
6. **`tab6_per_class_metrics`:** Per-class Precision, Recall, F1-Score, and Support on the unseen test set across all 26 ASL alphabet signs.
7. **`tab7_compute_efficiency`:** Parameter counts, ONNX model size, MACs/FLOPs, and stage-by-stage wall-clock latency (ms) on CPU.

---

## 8. Execution Roadmap & Staged Implementation

To adhere strictly to user safety and efficiency rules:
- **Stage 1 (Local Zero-Cost Artifact Generation):**
  - Establish complete folder structure under `paper_artifacts/`.
  - Write standalone evaluation, baseline, and ablation harness scripts that import directly from the project.
  - Implement the 1-Euro filter benchmark and trajectory kinematics profiler.
  - Implement the ONNX latency and parameter profiler.
  - Generate all verified vector figures and LaTeX tables using the existing trained ONNX model and documented checkpoint data.
- **Stage 2 (User Approval Gate for Compute):**
  - Present the exact computational plan before executing any multi-seed training runs.
  - Formulate and draft the complete IEEE-format manuscript (`main.tex` and modular section files) using only real, verified results.

---

*Awaiting user approval on PLAN.md to proceed with Phase 2 buildout.*
