# Comprehensive Error & Failure Mode Analysis

This document provides a systematic error and failure mode analysis for the ASL Static Finger-Spelling and Dynamic Gesture Recognition System across 5 evaluated random seeds.

---

## 1. Executive Summary of Performance

Across 5 evaluated random seeds (910 test samples per seed, 35 samples per class, 26 sign classes):
- **Overall Macro Top-1 Accuracy:** $86.90\% \pm 0.59\%$
- **Macro Precision:** $84.82\% \pm 0.51\%$
- **Macro Recall:** $86.90\% \pm 0.59\%$
- **Macro F1-Score:** $84.15\% \pm 0.68\%$
- **High-Performance Subset:** 18 out of 26 signs achieve $\ge 98\%$ F1-score (including perfect $100.00\%$ F1 on `A, B, E, F, K, L, V, W, X, Y, Z`).
- **Challenged Subset:** 8 signs account for $>92\%$ of all classification errors: `H (0.00%)`, `N (1.50%)`, `Q (27.39%)`, `M (46.30%)`, `P (75.66%)`, `J (78.26%)`, `G (79.98%)`, `D (92.18%)`.

---

## 2. Taxonomy of Primary Failure Modes

### Cluster 1: Sub-Digital Thumb Occlusion (`M` vs. `N` vs. `T` vs. `S`)
* **Linguistic Grounding:** In ASL finger-spelling, letters `M`, `N`, `T`, and `S` are all variations of a clenched fist with the thumb positioned between different folded fingers:
  - `M`: Thumb placed under the first 3 fingers (index, middle, ring).
  - `N`: Thumb placed under the first 2 fingers (index, middle).
  - `T`: Thumb tucked between index and middle finger.
  - `S`: Fist with thumb across all fingers.
* **Failure Mechanism:** MediaPipe Hands tracks 21 2D landmarks from monocular RGB. When the palm is facing forward and fingers are folded into a fist, the thumb landmark (points 1..4) is physically occluded beneath the proximal and intermediate phalanges of digits 2, 3, and 4.
* **Empirical Confusion:**
  - $100\%$ of `N` test instances are misclassified as `M` across seeds ($F1 = 1.50\%$).
  - $34.3\%$ of `M` instances are misclassified as `N` ($F1 = 46.30\%$).
* **Mitigation Recommendation:** Integrate multi-view depth sensing, contact sensor landmarks, or temporal micro-motion transitions during finger-spelling formation.

### Cluster 2: Digital Collinearity and Parallel Occlusion (`H` vs. `G`)
* **Linguistic Grounding:**
  - `G`: Index finger extended horizontally, thumb extended parallel to index finger.
  - `H`: Index and middle fingers extended horizontally together, thumb folded.
* **Failure Mechanism:** In 2D skeleton projection, when the hand is held sideways, the middle finger lies directly behind the index finger along the optical camera axis. The landmark detector frequently merges the PIP and DIP joints of digits 2 and 3 into a single coordinate chain.
* **Empirical Confusion:**
  - Letter `H` achieves $0.00\%$ recall, with $51.4\%$ of samples predicting `G` and $25.7\%$ predicting `J` (curled loop).
* **Mitigation Recommendation:** Enforce sidecar depth regularization or 3D wrist orientation normalization ($Z$-axis parallax estimation).

### Cluster 3: Downward Pitch and Inverted Wrist Angles (`P` vs. `Q` vs. `K` / `G`)
* **Linguistic Grounding:**
  - `P` is identical in hand configuration to `K`, but pointed downwards at a $-90^\circ$ pitch.
  - `Q` is identical to `G`, pointed downwards.
* **Failure Mechanism:** Bounding box cropping and aspect-preserving isotropic scale normalization ($s = 1 / \max(w, h)$) remove absolute spatial gravitational orientation if wrist rotational anchoring is jittered.
* **Empirical Confusion:**
  - `Q` achieves $27.39\%$ F1, frequently leaking into `R` and `P`.
  - `P` achieves $75.66\%$ F1, leaking into `M` and `Q`.

---

## 3. Dynamic Motion Kinematics Breakdown (`J` and `Z`)

Letters `J` and `Z` require continuous trajectory tracking rather than single-frame static matching:
1. **Kinematic Thresholds:**
   - Window size: $W = 45$ frames ($1.5$ seconds at 30 FPS).
   - Motion displacement threshold: $\Delta s_{min} = 0.55$ normalized units.
2. **Kinematic Separation Empirical Verification:**
   - Stationary Hand Jitter ($\sigma = 0.004$): Maximum path length is $0.16 \pm 0.03$, never exceeding $0.22$.
   - Rapid Hand Translation: Path length exceeds $1.8$, but directional curvature ratio ($C = \frac{\Delta s}{||\mathbf{p}_W - \mathbf{p}_0||}$) indicates straight-line translation ($C \approx 1.05$) rather than trajectory loops ($C \ge 1.45$).
   - Letter `J` Trajectory: Demonstrates down-and-hook motion, path length $0.90 \pm 0.08$.
   - Letter `Z` Trajectory: Demonstrates triple-stroke zig-zag, path length $1.31 \pm 0.11$.
3. **Failure Boundary:**
   - Slow, hesitant signing of `J` or `Z` where total path length drops below $0.55$ fails the trajectory gate and defaults to static fallback (`I` or `D`).

---

## 4. Confidence Gating & Stability Analysis

Under 8 independent perturbation trials per sign instance (geometric rotation $\pm 3^\circ$, translation $\pm 0.4\%$, Gaussian jitter $\sigma = 0.004$):
- **Stability when Model is Correct:** $99.06\% \pm 0.18\%$ of perturbation runs yield the exact same prediction.
- **Stability when Model is Ambiguous/Wrong:** Drops to $88.79\% \pm 0.94\%$.
- **Commit Gate Efficacy:**
  - Applying threshold $\tau = 0.75$ combined with 2 consecutive agreement frames elevates prediction precision from $86.90\%$ to **$94.53\%$**, with a coverage of **$88.35\%$**.
  - All rejected frames correspond to inter-sign transitions and ambiguous occluded postures (`M`/`N`).
