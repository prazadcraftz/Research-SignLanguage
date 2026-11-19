# Comprehensive Project Facts & Repository Audit: ASL Recognition System

This document constitutes the official, single-source-of-truth factual reference for the University Project Report. Every statement, parameter, dimension, metric, and finding recorded below is strictly verified against source code files, checkpoints, and execution logs in the repository.

---

## 1. Project Identification & Team Metadata

| Field | Repository Ground Truth / University Submission Details | Source File & Line |
| :--- | :--- | :--- |
| **Project Title** | Real-Time American Sign Language Fingerspelling and Gesture Recognition Using MediaPipe Hand Landmarks and Deep Convolutional Neural Networks | User prompt & `README.md` |
| **Short / Working Title** | Edge-ASL: Vision-Based Real-Time Fingerspelling Recognition | `README.md` L1–L10 |
| **Candidate 1** | Kesavarapu Nikhil Nowshan (UID: 23BAI71439) | User metadata |
| **Candidate 2** | Dasari Bhanu Prasad (UID: 23BAI70391) | User metadata |
| **Candidate 3** | Sanyam Singla (UID: 23BAI70220) | User metadata |
| **Degree Program** | Bachelor of Engineering in Computer Science and Engineering (Specialization: Artificial Intelligence and Machine Learning) | User metadata |
| **Department** | Department of Computer Science and Engineering, Apex Institute of Technology | `Project_Report.pdf` p. 1 |
| **University** | Chandigarh University, Gharuan, Mohali – 140413, Punjab, India | `Project_Report.pdf` p. 1 |
| **Supervisor** | Dr. Preeti Khera, Assistant Professor, Department of CSE / AIT-CSE | `Project_Report.pdf` p. 2, 3 |
| **Head of Department** | Dr. Suresh Kaswan, Head of Department, Department of CSE / AIT-CSE | `Project_Report.pdf` p. 2 |
| **Repository URL** | `https://github.com/itsbhanuprasad/MediaPipe-ASL-sign-language-recognition` (Local: `d:\SignLanguage\MediaPipe-ASL-sign-language-recognition`) | `README.md`, local git |

---

## 2. Task Definition & Scope

- **Sign Language Modality:** American Sign Language (ASL) manual alphabet fingerspelling and dynamic motion gestures.
- **Vocabulary & Classes:** 26 English alphabetical classes: `A` through `Z` (`class_names.txt`, `prepare_dataset.py` line 33: `DEFAULT_CLASSES = [chr(c) for c in range(ord('a'), ord('z') + 1)]`).
- **Decomposition of Task:**
  - **Static Alphabet (24 signs):** Letters `A`–`I` and `K`–`Y` are static manual postures classified on single-frame rendered skeleton images by a custom deep Convolutional Neural Network (`asl_cnn`).
  - **Dynamic Letters (2 signs):** Letters `J` and `Z` inherently require continuous motion tracking. They are detected using spatiotemporal trajectory kinematics over a sliding window (`motion.py` lines 1–60) combined with initial/terminal handshape gating (`J_SHAPES = {"i", "j"}`, `Z_SHAPES = {"d", "z"}`).
- **Operational Scope:** Real-time monocular RGB camera input on edge hardware (CPU execution); no specialized depth sensors, datagloves, or physiological wearables required (`README.md` L12–L25).

---

## 3. Data Pipeline & Preprocessing Specifications

All preprocessing operations are consolidated into a single module (`preprocessing.py`) to eliminate train-inference domain discrepancy.

| Parameter / Step | Exact Specification | Implementation Detail & Source File/Line |
| :--- | :--- | :--- |
| **Input Source** | Monocular RGB webcam stream / static photograph | `realtime_translator.py` L26–L30, `prepare_dataset.py` L58 |
| **Hand Detector** | Google MediaPipe Hands (`mp.solutions.hands.Hands`) | `model_complexity=1`, `max_num_hands=1`, `min_detection_confidence=0.3` (`prepare_dataset.py` L42–L47, `preprocessing.py` L50) |
| **Raw Landmarks** | 21 3D hand joints $(x, y, z)$ | Normalized $[0, 1]$ by image width and height (`preprocessing.py` L45, L87–L96) |
| **Pixel Reconstruction** | $(x \cdot W, y \cdot H)$ in real Euclidean pixels | `landmarks_to_pixels()` (`preprocessing.py` L87–L96) |
| **Aspect Ratio Normalization** | Isotropic bounding box expansion preserving aspect ratio | Single `box_size = extent.max() / HAND_FILL` applied to both axes (`preprocessing.py` L99–L120) |
| **Hand Canvas Fill** | $70\%$ (`HAND_FILL = 0.70`) | Centers hand at $(0.5, 0.5)$ and scales to exactly $70\%$ canvas span (`preprocessing.py` L41) |
| **Canvas Drawing Size** | $192 \times 192$ px (`CANVAS_SIZE = 192`) | Intermediate drawing canvas to prevent thin line aliasing (`preprocessing.py` L36) |
| **Final Input Size** | $96 \times 96 \times 3$ RGB (`MODEL_INPUT_SIZE = 96`) | Resized from 192 using `cv2.INTER_AREA` downsampling (`preprocessing.py` L43, L150–L153) |
| **Chromatic Styling** | MediaPipe 6-color coding (transcribed byte-for-byte) | Red (wrist/MCP), Peach (thumb), Purple (index), Yellow (middle), Green (ring), Blue (pinky) (`preprocessing.py` L58–L80) |
| **Color Order** | Pure RGB (converted to BGR only for `cv2.imshow`) | `render_skeleton()` returns RGB uint8 (`preprocessing.py` L122–L128) |
| **Landmark Augmentation** | Landmark-space perturbation (preserves stroke weight & palette) | `augment_landmarks()` (`preprocessing.py` L156–L195):<br>• Left-hand mirror ($p=0.5$)<br>• In-plane rotation: $\pm 15.0^\circ$<br>• Isotropic scaling: $\times [0.9, 1.1]$<br>• Translation: $\pm 0.05$ canvas units<br>• Gaussian joint jitter: $\mathcal{N}(0, 0.005^2)$<br>• Boundary containment clamping |

---

## 4. Landmark Denoising & Motion Kinematics

### 4.1. Adaptive 1-Euro Denoising Filter (`smoothing.py`)
To resolve resting-hand jitter without adding motion drag during fast signing:
- **Filter Formulation:**
  $$\text{cutoff} = f_c = f_{c,\min} + \beta \cdot \|\dot{x}\|$$
  $$\alpha = \frac{1}{1 + \frac{\tau}{\Delta t}}, \quad \text{where } \tau = \frac{1}{2\pi f_c}$$
- **Hyperparameters:**
  - $f_{c,\min} = 0.8\text{ Hz}$ (`MIN_CUTOFF = 0.8`, `smoothing.py` L38): baseline cutoff frequency for motionless hands.
  - $\beta = 0.02\text{ Hz/(px/s)}$ (`BETA = 0.02`, `smoothing.py` L43): velocity adaptation coefficient.
  - $f_{c,d} = 1.0\text{ Hz}$ (`D_CUTOFF = 1.0`, `smoothing.py` L48): derivative low-pass filter cutoff.
  - Clock guards: $\Delta t \in [10^{-3}, 1.0]\text{ s}$ (`smoothing.py` L55–L56).

### 4.2. Trajectory Kinematics for Dynamic Signs `J` and `Z` (`motion.py`)
- **Tracking Reference:** Raw pixel landmarks divided by instantaneous hand span ($s = \max(w, h)$), rendering measurements scale-invariant in units of "hand-widths" without centering away translation (`motion.py` L85–L93).
- **Buffer Parameters:**
  - Sliding history: $W = 45$ frames ($\sim 1.5\text{ s}$ at 30 FPS, `HISTORY_FRAMES = 45`, `motion.py` L41).
  - Trajectory smoothing: 5-frame moving average (`SMOOTHING = 5`, `motion.py` L58).
  - Motion gate threshold: $\Delta s_{\min} = 0.55$ hand-widths (`MIN_PATH_LENGTH = 0.55`, `motion.py` L42).
  - Static commit suppression threshold: $v_{\text{moving}} = 0.035$ hand-widths/frame (`MOVING_THRESHOLD = 0.035`, `motion.py` L51).
- **Kinematic Rule Constraints:**
  - **Sign `J`:** Handshape gate in `{"i", "j"}`; downward vertical drop $\Delta y \ge 0.20$ (`J_MIN_DESCENT = 0.20`) followed by horizontal hook curl $\Delta x \ge 0.12$ (`J_MIN_HOOK = 0.12`).
  - **Sign `Z`:** Handshape gate in `{"d", "z"}`; index finger travel $\ge 0.30$ hand-widths (`Z_MIN_HORIZONTAL = 0.30`) with at least 2 horizontal direction reversals (`Z_MIN_REVERSALS = 2`, `motion.py` L54).

---

## 5. Model Architecture & Training Implementation

The static classifier is a custom deep convolutional neural network (`asl_cnn`, implemented in `train_model.py` L145–L174):

### 5.1. Layer-by-Layer Architectural Breakdown
1. **Input Stage:** Input tensor shape $(96, 96, 3)$ with `Rescaling(1.0 / 255)`.
2. **Convolutional Block 1:**
   - $\text{Conv2D}(32, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}(\text{name}=\text{"conv1\_relu"})$
   - $\text{Conv2D}(32, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}()$
   - $\text{MaxPooling2D}(2 \times 2, \text{stride}=2) \implies (48, 48, 32)$
   - $\text{Dropout}(0.25)$
3. **Convolutional Block 2:**
   - $\text{Conv2D}(64, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}()$
   - $\text{Conv2D}(64, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}()$
   - $\text{MaxPooling2D}(2 \times 2, \text{stride}=2) \implies (24, 24, 64)$
   - $\text{Dropout}(0.25)$
4. **Convolutional Block 3:**
   - $\text{Conv2D}(128, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}()$
   - $\text{Conv2D}(128, 3 \times 3, \text{padding}=\text{"same"}, \text{use\_bias}=\text{False})$
   - $\text{BatchNormalization}(\text{momentum}=0.90)$
   - $\text{ReLU}()$
   - $\text{MaxPooling2D}(2 \times 2, \text{stride}=2) \implies (12, 12, 128)$
   - $\text{Dropout}(0.25)$
5. **Classifier Head:**
   - $\text{GlobalAveragePooling2D}() \implies 128\text{-dimensional vector}$
   - $\text{Dense}(128, \text{use\_bias}=\text{False}) \to \text{BatchNormalization}(\text{momentum}=0.90) \to \text{ReLU}(\text{name}=\text{"dense\_features"}) \to \text{Dropout}(0.50)$
   - $\text{Dense}(26, \text{dtype}=\text{"float32"}, \text{name}=\text{"logits"})$
- **Total Parameters:** $308,602$ trainable parameters (Zero non-trainable parameters after conversion). Model disk size: $1.18\text{ MB}$ ONNX (`asl_cnn_model.onnx`).

### 5.2. Hyperparameters & Optimization Protocol
- **Optimizer:** Adam ($\eta = 10^{-3}$, $\beta_1 = 0.9$, $\beta_2 = 0.999$, `train_model.py` L247).
- **Loss Function:** Sparse Categorical Cross-Entropy from logits (`from_logits=True`, `train_model.py` L248).
- **Batch Size:** $128$ (`train_model.py` L208).
- **Epochs:** $40$ planned, with Early Stopping patience = 8 epochs (`train_model.py` L259).
- **Learning Rate Schedule:** `ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4)` (`train_model.py` L261).
- **Class Imbalance Mitigation:** Inverse-frequency class weighting ($w_i = \frac{N}{C \cdot n_i}$, `train_model.py` L254–L256).
- **BatchNorm Momentum:** $0.90$ (`BN_MOMENTUM = 0.9`, `train_model.py` L142).
- **Training Infrastructure:** Linux (Arch/CachyOS), Python 3.12, NVIDIA GeForce RTX 3050 Laptop GPU (6 GB VRAM), CUDA 12, cuDNN 9 (`HANDOFF.md` L42–L68).

---

## 6. Datasets & Split Strategy

The repository constructs a unified landmark archive (`landmarks.npz`, $20\text{ MB}$) from three distinct public ASL photo collections:

| Dataset Name | Source / Author | Raw Images | MediaPipe Detected | Detection Yield | Primary Role in Split |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **ASL Alphabet** | `grassknoted/asl-alphabet` | $78,000$ | $64,765$ | $83.0\%$ | Training ($80\%$) & Validation ($20\%$) |
| **ASL Dataset** | `ayuraj/asl-dataset` | $1,815$ | $1,742$ | $96.0\%$ | Multi-signer Training ($80\%$) & Validation ($20\%$) |
| **ASL Alphabet Test** | `danrasband/asl-alphabet-test` | $780$ | $765$ | $98.1\%$ | **Out-of-Domain Held-Out Test Set** (100% unseen) |
| **Combined** | — | $\mathbf{80,595}$ | $\mathbf{67,272}$ | $\mathbf{83.5\%}$ | — |

### Split Strategy & Data Leakage Prevention
- **Contiguous Block Partitioning:** Splits are performed on contiguous chunks sorted by natural file key per class (`train_model.py` L79–L114). Random frame shuffling is strictly prohibited before splitting to prevent adjacent video-frame duplicates from bleeding into validation.
- **Unseen Subject Generalization:** The `danrasband` dataset ($765$ frames) is withheld in its entirety during training and validation. It functions as an honest benchmark for real-world unseen-signer evaluation.

---

## 7. Inference Pipeline, Post-Processing & UI

- **Execution Engine:** ONNX Runtime (`asl_cnn_model.onnx`, single-thread CPU execution).
- **Temporal Probability Smoothing:** 8-frame rolling average over output softmax probability distributions (`SMOOTHING_WINDOW = 8`, `realtime_translator.py` L50).
- **Two-Stage Confidence Gating:**
  - Uncertainty floor: $P_{\text{max}} < 0.50$ (`CONFIDENCE_FLOOR = 0.50`, `realtime_translator.py` L47) renders the prediction uncertain.
  - Commit threshold: $P_{\text{max}} \ge 0.75$ (`COMMIT_CONFIDENCE = 0.75`, `realtime_translator.py` L48) required for letter registration.
  - Temporal stability requirement: Must sustain commitment confidence for $10$ consecutive frames (`COMMIT_FRAMES = 10`, `realtime_translator.py` L49) while hand is stationary ($v \le 0.035$).
- **User Interface (`ui.py`):**
  - High-performance single-window OpenCV composition ($1100 \times 696$ px).
  - Main camera feed ($800 \times 600$) with hand tracking focus rectangle.
  - Right-hand diagnostics rail ($300$ px): live $96 \times 96$ skeleton render, top-3 class confidence progress bars, and word spelling buffer.
  - Interactive popup windows: Conv1 filter activation mosaic ($32$ filters) and Dense-128 hidden layer neuron heatmap (`realtime_translator.py` L37–L40).
  - Visual colorblind-safe dark mode theme (#0d0d0d canvas, #1a1a19 panels, #ffffff/#0ca30c/#fab219 accents).

---

## 8. Summary of Empirical Results

### 8.1. Retrained Repository Model Metrics (`HANDOFF.md` L20–L30)
- Validation Accuracy (contiguous split): **$96.8\%$**
- Out-of-Domain Test Accuracy (unseen signer `danrasband`): **$93.7\%$**
- Generalization Gap: **$3.1\%$**
- Commitment Gate Performance: Coverage = **$94.6\%$**, Precision at Gate = **$96.7\%$**
- Jitter Stability Agreement: **$99.0\%$** on correct predictions, **$85.7\%$** on uncertain/ambiguous predictions.
- Keras-to-ONNX Parity Error: **$1.14 \times 10^{-5}$** max absolute error.

### 8.2. Rigorous 5-Seed Statistical Benchmark Suite (`paper_artifacts/evaluations/aggregated/`)
Across seeds `[42, 123, 456, 789, 1024]`:
- **Model Comparison:**
  - Proposed Canonical Skeleton CNN: Accuracy **$86.90\% \pm 0.59\%$**, Macro F1 **$84.15\% \pm 0.68\%$**
  - 42-D Coordinate MLP Baseline: Accuracy **$63.89\% \pm 5.86\%$**, Macro F1 **$61.14\% \pm 6.81\%$**
  - Statistical Significance: Paired $t$-test $t = 8.218$, $p = 1.195 \times 10^{-3}$, Cohen's $d = 3.68$ (Statistically significant improvement over coordinate MLP).
- **Domain Shift Decomposition:**
  - Canonical Shared Renderer: $86.77\% \pm 0.39\%$
  - + Framing Mismatch (arbitrary fill $29\%-76\%$): $71.95\% \pm 0.64\%$
  - + BGR vs. RGB Color Inversion: $59.25\% \pm 0.46\%$
  - Cumulative Compound Shift: **$35.11\% \pm 0.51\%$** (A severe $51.66\%$ performance collapse).
- **Landmark Denoising:**
  - Raw Hand Jitter: $1.99 \pm 0.07\text{ px}$ shimmer, $0.6\text{ ms}$ lag.
  - Fixed EMA ($\alpha = 0.20$): $0.62 \pm 0.03\text{ px}$ shimmer, **$131.8 \pm 0.1\text{ ms}$ lag**.
  - **Proposed 1-Euro Filter:** **$0.70 \pm 0.04\text{ px}$ shimmer**, **$3.6 \pm 0.1\text{ ms}$ lag** (Eliminates $97.3\%$ of tracking latency).
- **Computational Latency Breakdown (Single-Thread x86_64 CPU):**
  - MediaPipe Hands Detection: $19.43 \pm 8.08\text{ ms}$
  - 1-Euro Adaptive Filter: $0.22 \pm 0.52\text{ ms}$
  - Bounding Box Normalization: $0.14 \pm 0.72\text{ ms}$
  - Skeleton Rendering: $0.89 \pm 1.82\text{ ms}$
  - ONNX CNN Forward Pass: $11.61 \pm 19.37\text{ ms}$ ($3.78\text{ ms}$ median)
  - UI Compositing: $18.10 \pm 20.92\text{ ms}$
  - **Total Pipeline Execution:** $51.14\text{ ms}$ ($\sim 19.6\text{ FPS}$ end-to-end; standalone CNN operates at $>86\text{ FPS}$).
