"""Ablation Study 1: Skeleton Rendering Properties Script.

Evaluates:
  1. Input Canvas Resolution: 48x48 vs 96x96 (Default) vs 192x192.
  2. Finger Chromatic Encoding: MediaPipe 6-color standard vs Monochrome Grayscale.
  3. Stroke Thickness: Half-width vs Standard vs Double-width.
"""

import argparse
import json
import os
import sys
import time
import cv2
import numpy as np
import onnxruntime as ort

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "MediaPipe-ASL-sign-language-recognition"))
sys.path.insert(0, REPO_ROOT)
import preprocessing as pp

def run_ablation(seed, out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(__file__)

    templates_path = os.path.join(os.path.dirname(__file__), "..", "evaluations", "canonical_templates.npz")
    templates_data = np.load(templates_path)
    base_points = templates_data["points"]
    class_names = [str(c) for c in templates_data["class_names"]]

    model_path = os.path.join(REPO_ROOT, "asl_cnn_model.onnx")
    sess = ort.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name

    rng = np.random.default_rng(seed)

    # Generate benchmark hands
    test_points = []
    test_labels = []
    for cls_idx in range(len(class_names)):
        pts = base_points[cls_idx]
        for _ in range(35):
            aug = pp.augment_landmarks(pts, rng, mirror=True)
            test_points.append(aug)
            test_labels.append(cls_idx)
    test_points = np.array(test_points)
    test_labels = np.array(test_labels)

    variants = [
        "Default (96x96, Color, Standard Stroke)",
        "Resolution: 48x48 (Upscaled to 96x96)",
        "Resolution: 192x192 (Downsampled to 96x96)",
        "Monochrome Grayscale Skeleton",
        "Thin Stroke Weight",
        "Thick Stroke Weight"
    ]

    results = {
        "experiment": "ABLATION-RENDERING",
        "seed": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "variants": {}
    }

    for var in variants:
        rendered = []
        for p in test_points:
            if "48x48" in var:
                skel_small = pp.render_skeleton(p, size=48)
                img = cv2.resize(skel_small, (96, 96), interpolation=cv2.INTER_LINEAR)
            elif "192x192" in var:
                img = pp.render_skeleton(p, size=96, canvas_size=192)
            elif "Monochrome" in var:
                skel = pp.render_skeleton(p, size=96)
                gray = cv2.cvtColor(skel, cv2.COLOR_RGB2GRAY)
                img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            elif "Thin" in var:
                # Sized with lower canvas scale
                img = pp.render_skeleton(p, size=96, canvas_size=128)
            elif "Thick" in var:
                img = pp.render_skeleton(p, size=96, canvas_size=256)
            else:
                img = pp.render_skeleton(p, size=96)

            rendered.append(img.astype(np.float32))

        rendered = np.array(rendered)
        logits = sess.run([sess.get_outputs()[0].name], {input_name: rendered})[0]
        preds = np.argmax(logits, axis=1)
        acc = float(np.mean(preds == test_labels))
        results["variants"][var] = {
            "accuracy": acc,
            "correct": int(np.sum(preds == test_labels)),
            "total": len(test_labels)
        }
        print(f"  [Ablation {seed}] {var:<45}: {acc:.2%}")

    out_file = os.path.join(out_dir, f"ablation_rendering_seed_{seed}.json")
    with open(out_file, "w") as fp:
        json.dump(results, fp, indent=2)
    print(f"Saved ablation results to {out_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    run_ablation(args.seed)
