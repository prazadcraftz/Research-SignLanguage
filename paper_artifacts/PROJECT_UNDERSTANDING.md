# Project Understanding: Real-Time American Sign Language Fingerspelling via Canonical Skeleton Rendering, Adaptive Denoising, and Spatiotemporal Kinematic Decomposition

**Document Path:** `paper_artifacts/PROJECT_UNDERSTANDING.md`  
**Date:** November 2026  
**Role:** Senior Research Engineer & Scientific Writing Lead  
**Repository Studied:** `MediaPipe-ASL-sign-language-recognition`  

---

## 1. Executive Summary & Plain-Language Problem Statement

### 1.1 The Practical Problem
American Sign Language (ASL) fingerspelling encompasses 26 distinct alphabet gestures ($A$ through $Z$). While human-to-human signing is fluid, automated computer vision recognition faces several persistent real-world failure modes:
1. **Severe Environmental Sensitivity:** Standard end-to-end convolutional neural networks (CNNs) trained directly on raw RGB camera pixels memorize ambient backgrounds, skin tones, clothing, and illumination variations. When tested under novel webcam environments, performance degrades dramatically.
2. **Train-Inference Domain Shift:** In conventional pipelines, training images are often cropped, scaled, and preprocessed differently from live camera video frames. Minor discrepancies—such as color-channel inversion (RGB vs. BGR), non-uniform aspect ratio distortions, or inconsistent hand bounding-box scales—cause catastrophic inference degradation (measured in this repository as dropping from $98.6\%$ to $39.6\%$ accuracy).
3. **Pervasive Data Leakage in Academic Benchmarks:** Many sign language datasets are recorded as continuous video bursts of identical hand poses. Applying naive random train/test splits places near-duplicate frames into both partitions, producing artificially inflated test accuracies (e.g., $97.9\%$–$99.5\%$) that deceive practitioners and fail completely in live deployment.
4. **Static vs. Dynamic Gesture Incompatibility:** While 24 ASL letters are static hand postures, the letters **J** and **Z** are dynamic movements traced over time. A purely static single-frame classifier cannot inherently disambiguate static start/end poses (e.g., distinguishing 'I' from 'J', or 'D' from 'Z'). Furthermore, static handshape ambiguities exist when digits are included (e.g., $0 \equiv O$, $2 \equiv V$, $6 \equiv W$, $9 \equiv F$).
5. **High-Frequency Landmark Jitter vs. Latency:** Extracted vision landmarks suffer from high-frequency sensor noise even when the user holds their hand motionless. Standard low-pass exponential moving average (EMA) smoothing introduces severe phase lag during rapid hand motions, trailing behind real gestures.

### 1.2 The Project's Solution & Goal
This project establishes an open-source, lightweight, deployable ASL fingerspelling system that resolves these challenges through four foundational principles:
- **Hand Structure Isolation via Canonical Rendering:** Rather than classifying raw photos, the pipeline extracts 21 skeletal landmarks using MediaPipe Hands, normalizes them into an aspect-ratio-preserving, centered coordinate frame ($70\%$ canvas fill), and renders a standardized skeletal diagram on a blank canvas using a single deterministic renderer (`render_skeleton()`) shared strictly between training and inference.
- **Leakage-Free Multi-Signer Evaluation:** The pipeline enforces contiguous per-class chunk partitioning to prevent adjacent burst frame contamination and tests generalization by completely holding out an unseen signer/dataset (`danrasband`).
- **Decoupled Spatiotemporal Kinematics for Dynamic Signs:** Static postures ($A$–$Z$ excluding motion) are classified by a lightweight custom 2D-CNN ($308\text{k}$ parameters), while dynamic letters (**J** and **Z**) are resolved by an explicit trajectory kinematic tracker operating on hand-width-normalized raw pixel landmarks across a $1.5\text{-second}$ rolling window.
- **Adaptive Denoising & Kinetic Commit Gating:** An adaptive 1-euro filter eliminates still-hand shimmer ($1.00\text{ px}$ RMS) without incurring motion lag ($4\text{ ms}$ at $2000\text{ px/s}$). A temporal stability commit gate (confidence floor $0.50$, commit confidence $0.75$, $10$ consecutive frames) ensures robust, flicker-free on-screen typing at full CPU speed.

---

## 2. Core Method & End-to-End Pipeline

### 2.1 Pipeline Architecture Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                    LIVE INPUT OR RAW DATASET                                       |
|  - Offline Training: Raw photo datasets (asl-alphabet, asl-dataset, danrasband)                    |
|  - Online Inference: 30 FPS RGB Webcam video frame (OpenCV capture)                                |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
| STAGE 1: HAND LANDMARK DETECTION (MediaPipe Hands)                                                 |
|  - Model Complexity: 1, Max Hands: 1, Min Detection Confidence: 0.3 (offline) / 0.5 (live)         |
|  - Output: 21 3D hand landmarks in frame-normalized coordinates (x in [0,1], y in [0,1])           |
|  - Conversion: landmarks_to_pixels() restores true aspect ratio in physical pixel units            |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
+------------------------------------------------+ +-------------------------------------------------+
| STAGE 2A: ADAPTIVE DENOISING (smoothing.py)    | | STAGE 2B: TRAJECTORY KINEMATICS (motion.py)     |
| (Online Live Inference Only)                   | | (Dynamic Letters 'J' & 'Z')                     |
|  - Vectorized 1-Euro Filter across 21 joints   | |  - Normalized by hand size: extent.max()        |
|  - D_CUTOFF = 1.0 Hz (derivative smoothing)    | |  - Rolling FIFO buffer: 45 frames (~1.5s)       |
|  - Adaptive Cutoff: fc = 0.8 + 0.02 * |speed|  | |  - Moving average smoothing (kernel = 5)       |
|  - Damps jitter at rest; zero lag at speed     | |  - Metrics: path length, descent, hook, reversals|
|                                                | |  - Classifies J (pinky) & Z (index)             |
|                                                | |  - Gating: is_moving() suppresses false commits |
+-----------------------+------------------------+ +-----------------------+-------------------------+
                        |                                                  |
                        v                                                  |
+-----------------------------------------------------------------------+  |
| STAGE 3: CANONICAL BOUNDING-BOX NORMALIZATION (preprocessing.py)       |  |
|  - Extent: extent = hi - lo; box_size = max(extent) / 0.70 (HAND_FILL)|  |
|  - Aspect ratio preserved by applying isotropic box_size              |  |
|  - Origin centering: origin = centre - box_size / 2.0                 |  |
|  - Output: norm_points in [0, 1] relative canvas coordinates          |  |
+-----------------------------------------------------------------------+  |
                        |                                                  |
                        v                                                  |
+-----------------------------------------------------------------------+  |
| STAGE 4: DETERMINISTIC SKELETON RENDERING (preprocessing.py)          |  |
|  - Canvas Size: 192x192 px canvas (rendered in RGB uint8)             |  |
|  - Joint drawing: 21 joints, radius scaled, MediaPipe standard colors |  |
|  - Bone drawing: 21 connections, anti-aliased cv2.LINE_AA lines       |  |
|  - Downsampling: cv2.INTER_AREA to 96x96x3 (MODEL_INPUT_SIZE)         |  |
|  - Augmentation (Train only): Landmark-space rotation (+-15 deg),     |  |
|    scaling (0.9-1.1), translation (+-0.05), jitter N(0, 0.005), mirror |  |
+-----------------------------------------------------------------------+  |
                        |                                                  |
                        v                                                  |
+-----------------------------------------------------------------------+  |
| STAGE 5: STATIC NEURAL CLASSIFIER (train_model.py / asl_cnn_model.onnx) |
|  - Input: (1, 96, 96, 3) float32 in [0, 255]                         |  |
|  - Rescaling(1/255) -> 3x Double-Conv Blocks [32, 64, 128] + BN + ReLU|  |
|  - MaxPool2D(2x2) + Dropout(0.25) per block                            |  |
|  - GlobalAveragePooling2D (GAP) -> Dense(128) + BN + ReLU + Drop(0.5)  |  |
|  - Dense(26, logits)                                                  |  |
|  - Instrumented Taps: 'conv1_relu' (96x96x32) & 'dense_features' (128) |  |
|  - CPU Inference Engine: ONNX Runtime                                 |  |
+-----------------------------------------------------------------------+  |
                        |                                                  |
                        v                                                  |
+-----------------------------------------------------------------------+  |
| STAGE 6: TEMPORAL POST-PROCESSING & HCI COMMIT GATE (realtime_translator)|
|  - Softmax activation -> 26-class probability distribution            |  |
|  - Rolling temporal probability averaging over last 8 frames          |  |
|  - Kinematic Override: MotionTracker checks J / Z dynamics <----------+  |
|  - Confidence Floor Gating: confidence >= 0.50 (else 'uncertain')     |
|  - Commit Gating: confidence >= 0.75 for 10 consecutive frames        |
|  - Anti-Duplicate Suppression: requires explicit motion or 'r' key    |
|  - Word Buffer Assembly: character append, backspace, clear           |
+-----------------------------------------------------------------------+
```

---

## 3. Dataset Characteristics & Ingestion Protocol

The system utilizes three independent open datasets available on Kaggle:

| Dataset Identifier | Primary Source / Author | Role in Framework | Total Raw Images | Detected Hands | Detection Rate | Native License |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`alphabet`** | Akash Nagaraj (`grassknoted/asl-alphabet`) | Base training corpus (single signer, uniform background) | 78,000 | 64,765 | 83.0% | GPL-2.0 |
| **`ayuraj`** | Ayush Thakur (`ayuraj/asl-dataset`) | Signer diversity in training (multiple individuals) | 1,815 | 1,742 | 96.0% | CC0-1.0 |
| **`danrasband`** | Dan Rasband (`danrasband/asl-alphabet-test`) | Completely held-out unseen test set (novel subject/lighting) | 780 | 765 | 98.1% | CC0-1.0 |
| **Total** | — | — | **80,595** | **67,272** | **83.5%** | Mixed |

### 3.1 Preprocessing & Storage (`prepare_dataset.py`)
- **Border Padding:** A 25% black border (`pad_ratio = 0.25`) is prepended before MediaPipe hand extraction. This prevents palm detector failures caused by hands tightly abutting image boundaries.
- **Landmark Extraction:** Extracts 21 hand landmarks using `mediapipe.python.solutions.hands.Hands` (`static_image_mode=True`, `max_num_hands=1`, `model_complexity=1`, `min_detection_confidence=0.3`).
- **Aspect-Ratio Preservation:** Raw landmark coordinates normalized by frame width and height are converted to isotropic pixel coordinates (`landmarks_to_pixels`) prior to canonical box normalization.
- **Storage Footprint:** Stored as compressed NumPy arrays (`landmarks.npz`, ~20 MB) containing `points` ($N, 21, 2$), `labels` ($N$), `datasets` ($N$), and source `paths`. This reduces disk I/O from 80,000 file reads to single-pass RAM ingestion.

### 3.2 Splitting Strategy & Data Leakage Prevention
- **Contiguous Per-Class Slicing:** Frame sequences within the same directory share temporal and postural correlation. Random $80/20$ splits leak near-duplicate frames into both training and validation sets. The framework sorts filenames via natural alphanumeric ordering (`natural_key`) and extracts validation data as a single contiguous terminal chunk per class ($20\%$).
- **Strict Out-of-Distribution Test Set:** `danrasband` (765 samples across 26 letters) is excluded entirely from model fitting, acting as an honest out-of-domain benchmark.
- **Data Partitions:**
  - **Train Split:** 53,207 samples
  - **Validation Split:** 13,300 samples
  - **Held-Out Test Split:** 765 samples

---

## 4. Model Architecture & Hyperparameters

### 4.1 Neural Network Topology (`train_model.py`)
The classifier is an efficient, fully-convolutional backbone terminating in global pooling and a dense projection head:

```
Input: (Batch, 96, 96, 3) RGB uint8 (internally rescaled to [0, 1] via Rescaling(1./255))
│
├── ConvBlock 1:
│   ├── Conv2D(32 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU [Tap: 'conv1_relu']
│   ├── Conv2D(32 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU
│   └── MaxPooling2D(2x2) -> Dropout(0.25)
│
├── ConvBlock 2:
│   ├── Conv2D(64 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU
│   ├── Conv2D(64 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU
│   └── MaxPooling2D(2x2) -> Dropout(0.25)
│
├── ConvBlock 3:
│   ├── Conv2D(128 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU
│   ├── Conv2D(128 filters, 3x3, padding="same", use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU
│   └── MaxPooling2D(2x2) -> Dropout(0.25)
│
├── GlobalAveragePooling2D()  [Reduces feature map to 128-D vector, eliminating 90% head params]
├── Dense(128, use_bias=False) -> BatchNorm(momentum=0.9) -> ReLU [Tap: 'dense_features']
├── Dropout(0.50)
└── Dense(26, dtype="float32", name="logits")
```
- **Total Trainable Parameters:** 308,602 (~1.2 MB ONNX footprint).

### 4.2 Training Hyperparameters
- **Optimizer:** Adam ($\alpha = 10^{-3}$, $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-7}$).
- **Loss Function:** Sparse Categorical Crossentropy (`from_logits=True`).
- **Class Balancing:** Inverse frequency weighting: $w_c = \frac{N_{\text{total}}}{C \cdot N_c}$.
- **Batch Size:** 128.
- **Maximum Epochs:** 40 (with `EarlyStopping` on `val_accuracy`, patience = 8, restoring best weights; `ReduceLROnPlateau` on `val_loss`, factor = 0.5, patience = 4).
- **Critical Fix - BatchNorm Momentum:** Pinned to **0.90** instead of Keras default 0.99. Momentum 0.99 requires thousands of iterations to calibrate moving mean/variance; on smaller runs, statistics drift, causing multi-layer normalizations to collapse into a single degenerate class.

### 4.3 Landmark-Space Data Augmentation
Augmentations occur exclusively on the $(21, 2)$ landmark coordinate vectors before skeleton rendering:
- **Horizontal Reflection:** Mirroring with $p = 0.5$ (inverts x-coordinates $x' = 1 - x$). Because ASL fingerspelling preserves joint semantics regardless of hand handedness (left vs. right), mirrored poses are biologically valid.
- **In-Plane Rotation:** $\theta \sim \mathcal{U}(-15^\circ, +15^\circ)$ about center $(0.5, 0.5)$.
- **Isotropic Scale Scaling:** $s \sim \mathcal{U}(0.9, 1.1)$.
- **Global Translation:** $\Delta x, \Delta y \sim \mathcal{U}(-0.05, +0.05)$.
- **Gaussian Landmark Jitter:** $\epsilon \sim \mathcal{N}(0, 0.005)$ per joint coordinate.
- **Bounding Box Clamp:** If scaling causes landmarks to exceed $[0, 1]$, the skeleton is shifted rigidly back into view without warping inter-joint distances.

---

## 5. Existing Empirical Results & Baseline Checkpoints

From existing training runs, evaluation scripts (`evaluate.py`), and handoff documentation:

### 5.1 Recognition Performance
- **Validation Accuracy (Contiguous Split, Same Signers):** **96.8%**
- **Held-Out Test Accuracy (Unseen Signer `danrasband`):** **93.7%**
- **Generalization Gap:** **3.1 percentage points** (indicating strong domain transfer without memorization).

### 5.2 Confidence Gating & Stability Metrics
- **Commit Gate Coverage ($\text{Confidence} \ge 0.75$):** $94.6\%$ of frames clear the threshold.
- **Precision at Commit Gate:** $96.7\%$ of committed predictions are correct.
- **Jitter Invariance (Perturbation Survival):**
  - Predictions unchanged across 8 random perturbations when baseline prediction is correct: **99.0%**
  - Predictions unchanged when baseline prediction is incorrect: **85.7%** (confusions remain localized to genuinely ambiguous handshapes).

### 5.3 Filter Denoising Benchmarks (`smoothing.py`)
Evaluated on simulated 30 FPS video with $2\text{ px}$ detection noise:

| Metric | Fixed-Alpha EMA ($\alpha = 0.35$) | Adaptive 1-Euro Filter | Relative Advantage |
| :--- | :---: | :---: | :---: |
| **Still-Hand Shimmer (RMS)** | 1.29 px | **1.00 px** | $22.5\%$ reduction in idle jitter |
| **Dynamic Lag at $300\text{ px/s}$** | 19 px / 62 ms | **5 px / 17 ms** | $73.7\%$ lower latency |
| **Dynamic Lag at $2000\text{ px/s}$** | 124 px / 62 ms | **7 px / 4 ms** | $94.3\%$ lower latency |
| **Effective Smoothing Factor $\alpha$** | Constant $0.35$ | $0.14$ (rest) $\rightarrow$ $0.89$ ($2000\text{ px/s}$) | Dynamically tuned per joint |

### 5.4 Export Verification & Numerical Parity
- Evaluated via `export_onnx.py` over 200 rendered skeleton test samples:
  - Maximum absolute discrepancy between Keras GPU/CPU and ONNX Runtime CPU: **$1.14 \times 10^{-5}$** (well below the $10^{-4}$ tolerance threshold).

---

## 6. What is Novel vs. Borrowed / Prior Work

### Novel Contributions (Paper Value Drivers)
1. **The Single-Source-of-Truth Shared Renderer Paradigm:**
   Proving empirically that cross-modal domain shift between training data and inference cameras can be resolved by enforcing an identical rendering engine (`render_skeleton()`) across both pipelines. Demonstrating that subtle bugs (RGB/BGR mismatch, non-isotropic bounding box squashing, and inconsistent hand fill) cause a 59-point drop ($98.6\% \rightarrow 39.6\%$).
2. **Leakage-Free Benchmark Formulation:**
   Exposing the pervasive flaw of random partitioning on frame-burst sign language datasets, providing an honest contiguous chunking protocol, and validating cross-signer domain transfer on a held-out test set.
3. **Hybrid Kinematic-Static ASL Decomposition:**
   Decoupling static fingerspelling ($A$–$Z$) from dynamic temporal gestures ($J$ and $Z$) through rule-based trajectory kinematics operating on hand-size-normalized coordinates. This bypasses the need for high-complexity 3D-CNNs or video transformer backbones while achieving robust real-time performance.
4. **Latency-Informed Denoising & Kinetic Commit Gating:**
   Demonstrating the synergistic coupling of per-landmark 1-euro filtering and consecutive-frame kinetic gating, simultaneously solving idle prediction flicker and fast signing latency.
5. **Lightweight Explainable Edge Architecture:**
   Deploying an ultra-compact $308\text{k}$-parameter CNN with ONNX Runtime CPU execution and integrated activation taps (`conv1_relu` and `dense_features`) powering an intuitive real-time single-window interface.

### Standard / Borrowed Elements
- MediaPipe Hands 21-landmark tracking module (Lugaresi et al., 2019; Zhang et al., 2020).
- 1-Euro Filter mathematical formulation (Casiez, Roussel, & Vogel, CHI 2012).
- Standard 2D convolutional, batch normalization, max-pooling, and dropout primitives.
- Public Kaggle datasets: `grassknoted/asl-alphabet`, `ayuraj/asl-dataset`, `danrasband/asl-alphabet-test`.

---

## 7. Gaps, Missing Experiments & Scientific Open Questions

To elevate this project into a top-tier research manuscript (e.g., IEEE Transactions / IEEE Access / ACM IMWUT / Springer), several empirical and ablation gaps must be addressed:

### 7.1 Gaps in Current Repo
1. **Absence of Baseline Comparisons:**
   - *Baseline 1: Direct RGB CNN.* What happens if a CNN trains directly on raw RGB images? How severely does performance degrade when tested on an unseen signer or varying backgrounds?
   - *Baseline 2: Direct Coordinate MLP / Random Forest / SVM.* Does spatial 2D convolution on rendered skeletons outperform a direct $(21 \times 2 = 42)$-dimensional vector classifier (e.g., a 3-layer MLP on raw landmarks)?
   - *Baseline 3: Unsmoothed / Fixed EMA Smoothing.* Direct empirical quantification of live typing error rate with raw landmarks vs. fixed EMA vs. 1-euro filter.
2. **Ablation Studies:**
   - *Renderer Properties:* Effect of skeleton stroke thickness, canvas resolution ($48 \times 48$, $96 \times 96$, $192 \times 192$), and joint color-coding (does MediaPipe multi-color drawing provide distinct chromatic cues to the CNN, or is grayscale skeleton equivalent?).
   - *Augmentation Components:* Ablating individual landmark perturbations (rotation, scale, jitter, and horizontal mirroring).
   - *BatchNorm Momentum:* Quantitative ablation demonstrating the failure mode of $\text{momentum} = 0.99$ vs. $\text{momentum} = 0.90$.
   - *Commit Gate Parameters:* Sensitivity curves for `COMMIT_CONFIDENCE` ($0.50$–$0.95$) and `COMMIT_FRAMES` ($3$–$20$) on accuracy vs. typing throughput.
3. **Statistical Rigor:**
   - The reported results reflect a single training checkpoint. Standard scientific protocol requires at least **5 independent runs with distinct random seeds**, reporting mean $\pm$ standard deviation and 95% confidence intervals, alongside statistical significance testing (paired $t$-test or Wilcoxon signed-rank test).
4. **Computational Efficiency Profiling:**
   - Formal wall-clock timing breakdowns across pipeline stages (MediaPipe capture/detection, 1-euro filtering, normalization, skeleton rendering, ONNX inference, and UI compositing), measuring latency (ms), frame rate (FPS), CPU utilization, and FLOPs.
5. **Detailed Error Analysis:**
   - Per-class precision, recall, and F1-score across all 26 letters.
   - Comprehensive confusion matrix analysis, highlighting the persistent structural ambiguity of fist-based signs (M, N, S, T) and the data scarcity bottleneck of class 'N'.

---

## 8. Open Questions for the User

Before executing Phase 1 and Phase 2, we clarify the following operational and empirical constraints:

1. **Dataset Availability for Retraining & Baselines:**
   - `landmarks.npz` and the raw Kaggle datasets are currently not present in the workspace directory (only `asl_cnn_model.onnx`, evaluation scripts, and docs are checked in).
   - *Question for User:* Do you have `landmarks.npz` stored elsewhere on your machine, or do you have Kaggle API credentials / raw image folders that we can link? Alternatively, should our evaluation and ablation scripts operate primarily on the existing trained ONNX model and generated synthetic/perturbed benchmark distributions, or do you want us to download/prepare the datasets for retraining?
2. **Target Publication Venue / Format:**
   - Which template or target venue do you prefer for `paper/main.tex`? (e.g., IEEE Conference 2-column `\documentclass[conference]{IEEEtran}`, ACM Primary Article Template, NeurIPS/ICML, or Springer LNCS)?
3. **Hardware / Compute Allocation:**
   - Training on Windows is CPU-only (TensorFlow dropped native GPU support post-2.10). A full 40-epoch retrain of the CNN on CPU across 5 seeds takes noticeable compute. Are you comfortable with targeted smaller-epoch runs / synthetic benchmark verification, or do you have a Linux/GPU environment or specific compute limits?

---

*Phase 0 is complete. Upon review and clarification of the open questions, we will immediately produce `paper_artifacts/PLAN.md` (Phase 1).*
