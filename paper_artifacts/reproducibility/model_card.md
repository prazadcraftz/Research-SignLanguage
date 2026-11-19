# Model Card: ASL Canonical Skeleton Classifier

## 1. Model Details
- **Model Name:** `asl_cnn_model.onnx`
- **Architecture:** Lightweight Convolutional Neural Network (3 Double-Conv Blocks + GAP + Dense Head)
- **Parameters:** 308,602 trainable parameters (~1.23 MB on disk)
- **Input Specification:** `input_image: (Batch, 96, 96, 3)` float32 representing an anti-aliased RGB hand skeleton centered at 70% canvas fill.
- **Output Specification:**
  - `logits: (Batch, 26)` raw class scores for letters A through Z.
  - `conv1_relu: (Batch, 96, 96, 32)` internal activation tap for conv1 filter mosaic explainability.
  - `dense_features: (Batch, 128)` internal activation tap for 128-neuron dense layer heatmap.
- **Target Hardware:** x86_64 / ARM Commodity CPU (CPUExecutionProvider).
- **Inference Runtime:** ONNX Runtime >= 1.16.

## 2. Intended Use
- **Primary Use Case:** Real-time American Sign Language fingerspelling translation on commodity webcams and edge devices without GPU acceleration.
- **Out-of-Scope Use:** Whole-word dynamic sign language (e.g., continuous sentence signing) without fingerspelling decomposition, non-standard sign languages without retraining.

## 3. Training Details
- **Training Data:** 67,272 skeletal landmark frames extracted from 80,595 raw images across `grassknoted/asl-alphabet` and `ayuraj/asl-dataset`.
- **Optimizer:** Adam (lr=1e-3, beta1=0.9, beta2=0.999).
- **Batch Size:** 128.
- **Epochs:** 40 max (EarlyStopping restored best weights at epoch 12).
- **Loss:** Sparse Categorical Cross-Entropy (from_logits=True) with inverse frequency class weighting.
- **BatchNorm Momentum:** 0.90 (critical fix preventing statistical collapse observed at default 0.99).
- **Augmentation:** Landmark-space in-plane rotation (+-15 deg), isotropic scale (0.9-1.1), translation (+-0.05), Gaussian jitter, horizontal reflection (mirroring).

## 4. Quantitative Performance
- **Validation Accuracy (Same Signers, Contiguous Split):** 96.8%
- **Out-of-Domain Test Accuracy (Unseen Signer `danrasband`):** 93.7%
- **Commit Precision (Confidence >= 0.75):** 96.7%
- **Jitter Invariance (8 Perturbation Trials):** 99.0% agreement for correct predictions.
- **Inference Latency:** 3.12 ms on CPU (~320 FPS standalone model forward pass).

## 5. Limitations & Ethical Considerations
- **Class N Bottleneck:** Class N shares structural fist posture with M, S, and T, and experienced the lowest palm detector detection rate (56.6%), resulting in lower test recall (~54%).
- **Dynamic Signs J & Z:** Frame-by-frame static CNN cannot distinguish movement; dynamic disambiguation requires the accompanying `motion.MotionTracker` kinematics module.
- **Skin Tone and Background:** Because the network classifies rendered skeletal representations rather than raw pixel photographs, it exhibits near-complete invariance to skin tone, lighting, and background variations.
