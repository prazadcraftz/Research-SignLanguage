# Data Card: Multi-Source ASL Fingerspelling Corpus

## 1. Dataset Provenance & Sources

| Dataset Name | Source / Author | Total Images | Detected Samples | Split Assignment | License |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **ASL Alphabet** | Akash Nagaraj (`grassknoted/asl-alphabet`) | 78,000 | 64,765 | Main Training & Validation | GPL-2.0 |
| **ASL Dataset** | Ayush Thakur (`ayuraj/asl-dataset`) | 1,815 | 1,742 | Signer Diversity in Training | CC0-1.0 |
| **ASL Alphabet Test** | Dan Rasband (`danrasband/asl-alphabet-test`) | 780 | 765 | Held-Out Out-of-Domain Test | CC0-1.0 |
| **Total** | — | **80,595** | **67,272** | — | Mixed |

## 2. Preprocessing & Extraction Pipeline
1. **Palm Detection Padding:** A 25% black border (`pad_ratio = 0.25`) is prepended to each image to prevent palm bounding-box clipping on tightly cropped photos.
2. **MediaPipe Landmark Extraction:** 21 landmarks extracted using `mediapipe.python.solutions.hands.Hands(model_complexity=1, min_detection_confidence=0.3)`.
3. **Aspect-Ratio Preservation:** Raw normalized coordinates are transformed to pixel space (`landmarks_to_pixels`) to remove camera aspect distortions.
4. **Canonical Box Normalization:** Hand bounding box extent is calculated; coordinates are scaled by `max(extent) / 0.70` and centered to canvas range $[0, 1]$.
5. **Storage:** Saved as compressed float32 coordinate arrays (`landmarks.npz`, ~20 MB).

## 3. Partitioning & Leakage Mitigation
- **Contiguous per-class chunk partitioning:** Because image datasets are recorded in burst sequences of adjacent video frames, random 80/20 splitting causes catastrophic leakage of near-duplicate frames into validation sets.
- **Protocol:** Images are sorted via natural alphanumeric order (`natural_key`) and the final 20% of each class sequence is carved out as a contiguous block for validation.
- **Unseen Subject Hold-Out:** `danrasband` (a companion dataset recorded by an unseen signer in novel lighting) is completely withheld from training, serving as an honest test set.
- **Sample Distribution:**
  - **Train:** 53,207 samples
  - **Validation:** 13,300 samples
  - **Test (Unseen):** 765 samples
