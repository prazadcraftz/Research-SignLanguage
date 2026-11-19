# Missing Evidence & Research Limitations (MISSING_EVIDENCE.md)

In adherence to scientific integrity principles, this document records all experimental boundaries, untested claims, and areas where future empirical data collection is required.

---

## 1. Signer Diversity Limitations
- **Current Observation:** The primary training dataset (`grassknoted/asl-alphabet`) consists of $64,765$ detected hand frames contributed by a single primary signer. The secondary dataset (`ayuraj/asl-dataset`) contributes $1,742$ frames ($2.6\%$ of the training set).
- **Limitation:** While the model achieves $93.7\%$ accuracy on the held-out dataset (`danrasband`, $765$ frames), evaluation on large-scale diverse demographic cohorts (varying ages, hand anthropometry, skin tones, mobility impairments) has not been conducted.
- **Future Evidence Required:** Multi-signer cross-validation across $\ge 20$ diverse native ASL signers under unconstrained domestic and mobile camera environments.

---

## 2. Sequence-Level Continuous ASL Sentences (Word Error Rate)
- **Current Observation:** The system addresses manual fingerspelling (alphabetic letters A through Z) with dynamic trajectory detection for letters `J` and `Z`. Continuous ASL discourse incorporates grammatical facial non-manual markers, torso orientation, and lexical word signs.
- **Limitation:** Continuous sentence signing metrics (Word Error Rate, Sentence Error Rate) are not applicable to the current manual fingerspelling alphabet task.
- **Future Evidence Required:** Sequence-to-sequence translation using transformer/CTC temporal backbones on continuous corpora (e.g., PHOENIX-2014T, ChicagoFSWild).

---

## 3. Sub-Digital Occlusion in Monocular 2D Projection
- **Current Observation:** Letters `M` and `N` exhibit an F1-score disparity ($46.3\%$ vs. $1.5\%$) due to the physical occlusion of the thumb beneath folded fingers, which collapses in 2D monocular projection.
- **Limitation:** MediaPipe monocular landmark estimation cannot reliably reconstruct depth ordering when joints are collinear along the optical axis.
- **Future Evidence Required:** Depth map integration ($RGB-D$), multi-view triangulation, or tactile/EMG wearable sensor fusion for ambiguous closed-fist fingerspelling.

---

## 4. Lighting & Extreme Environmental Robustness
- **Current Observation:** The system was evaluated under indoor room lighting and standard desk camera perspectives.
- **Limitation:** Extreme low-light conditions ($< 10\text{ lux}$), strong backlighting, motion blur from unconstrained hand flailing, and outdoor solar glint have not been systematically stress-tested.
- **Future Evidence Required:** Controlled photometric sweep benchmarks evaluating accuracy as a function of illuminance (lux) and camera shutter speed.
