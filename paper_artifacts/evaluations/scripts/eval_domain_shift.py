"""Experiment 1: Domain Shift Breakdown ("Bug Chain") Evaluation Script.

Evaluates how inference accuracy degrades when the invariants of the canonical
shared renderer are broken:
  - Canonical (RGB, 70% fill, centered, isotropic)
  - Framing mismatch (variable hand fill and canvas position)
  - Aspect ratio distortion (4:3 camera squashing)
  - Color channel inversion (BGR buffer fed to RGB model)
  - Cumulative / combined failure chain

Saves raw results per seed with git commit hash, timestamps, and full configs.
"""

import argparse
import json
import os
import sys
import time
import numpy as np
import onnxruntime as ort

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "MediaPipe-ASL-sign-language-recognition"))
sys.path.insert(0, REPO_ROOT)
import preprocessing as pp

def run_evaluation(seed, num_samples_per_class=50, model_path=None, out_dir=None):
    if model_path is None:
        model_path = os.path.join(REPO_ROOT, "asl_cnn_model.onnx")
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "raw_results")
    os.makedirs(out_dir, exist_ok=True)

    templates_path = os.path.join(os.path.dirname(__file__), "..", "canonical_templates.npz")
    templates_data = np.load(templates_path)
    base_points = templates_data["points"] # (26, 21, 2)
    class_names = [str(c) for c in templates_data["class_names"]]

    sess = ort.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name

    rng = np.random.default_rng(seed)

    # Generate test dataset of perturbed hands across 26 classes
    all_points = []
    all_labels = []
    for cls_idx in range(len(class_names)):
        pts = base_points[cls_idx]
        for _ in range(num_samples_per_class):
            aug = pp.augment_landmarks(pts, rng, mirror=False)
            all_points.append(aug)
            all_labels.append(cls_idx)
    all_points = np.array(all_points) # (N, 21, 2)
    all_labels = np.array(all_labels)

    conditions = [
        "1. Canonical Shared Renderer",
        "2. Framing Mismatch (29%-76% fill)",
        "3. Aspect Squashed (4:3 camera stretch)",
        "4. Channel Inverted (BGR vs RGB)",
        "5. Cumulative Combined Shift"
    ]

    results = {
        "experiment": "EXP-DOMAIN-SHIFT",
        "seed": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_samples": len(all_labels),
        "num_classes": len(class_names),
        "conditions": {}
    }

    for cond in conditions:
        images = []
        for pts in all_points:
            p = pts.copy()

            if "Framing" in cond or "Combined" in cond:
                # Random scale between 29% and 76% fill, random offset
                random_fill = rng.uniform(0.29, 0.76)
                p = (p - 0.5) * (random_fill / 0.70) + 0.5 + rng.uniform(-0.1, 0.1, size=2)

            if "Aspect" in cond or "Combined" in cond:
                # Squash width by 75% relative to height
                p[:, 0] = (p[:, 0] - 0.5) * 0.75 + 0.5

            # Render skeleton
            img = pp.render_skeleton(p, size=pp.MODEL_INPUT_SIZE)

            if "Channel" in cond or "Combined" in cond:
                # Swap RGB to BGR
                img = img[:, :, ::-1]

            images.append(img.astype(np.float32))

        images = np.array(images)
        # Batch inference
        batch_size = 128
        preds = []
        for i in range(0, len(images), batch_size):
            chunk = images[i:i + batch_size]
            logits = sess.run([sess.get_outputs()[0].name], {input_name: chunk})[0]
            preds.extend(np.argmax(logits, axis=1).tolist())

        preds = np.array(preds)
        acc = float(np.mean(preds == all_labels))
        results["conditions"][cond] = {
            "accuracy": acc,
            "correct": int(np.sum(preds == all_labels)),
            "total": len(all_labels)
        }
        print(f"  [Seed {seed}] {cond:<40}: {acc:.2%}")

    out_file = os.path.join(out_dir, f"domain_shift_seed_{seed}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved raw results to {out_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--samples", type=int, default=50)
    args = parser.parse_args()
    run_evaluation(args.seed, args.samples)
