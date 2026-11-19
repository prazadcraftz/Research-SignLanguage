"""Experiment 4: Confidence Gating & Jitter Stability Script.

Evaluates:
  1. Sensitivity of typing behavior to COMMIT_CONFIDENCE threshold (0.40 to 0.95):
     measures coverage (%), commit precision (%), and wrong commits (%).
  2. Sensitivity to COMMIT_FRAMES window (3 to 20 frames):
     measures latency vs accuracy trade-off.
  3. Jitter Stability: evaluates prediction flip rate under small
     sensor perturbations across 8 trials on test hands.
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

def softmax(logits):
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)

def jitter_landmarks(points, rng, degrees=3.0, shift=0.004, noise=0.004):
    pts = np.asarray(points, dtype=np.float32).copy()
    centre = np.float32([0.5, 0.5])
    angle = np.deg2rad(rng.uniform(-degrees, degrees))
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    pts = (pts - centre) @ np.float32([[cos_a, -sin_a], [sin_a, cos_a]]).T + centre
    pts += rng.uniform(-shift, shift, size=2).astype(np.float32)
    pts += rng.normal(0.0, noise, size=pts.shape).astype(np.float32)
    return pts.astype(np.float32)

def run_evaluation(seed, num_samples_per_class=30, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "raw_results")
    os.makedirs(out_dir, exist_ok=True)

    templates_path = os.path.join(os.path.dirname(__file__), "..", "canonical_templates.npz")
    templates_data = np.load(templates_path)
    base_points = templates_data["points"]
    class_names = [str(c) for c in templates_data["class_names"]]

    model_path = os.path.join(REPO_ROOT, "asl_cnn_model.onnx")
    sess = ort.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name

    rng = np.random.default_rng(seed)

    # 1. Synthesize benchmark hands across classes
    test_points = []
    test_labels = []
    for cls_idx in range(len(class_names)):
        pts = base_points[cls_idx]
        for _ in range(num_samples_per_class):
            aug = pp.augment_landmarks(pts, rng, mirror=True)
            test_points.append(aug)
            test_labels.append(cls_idx)
    test_points = np.array(test_points)
    test_labels = np.array(test_labels)

    # Run ONNX inference on test points
    rendered_batch = np.stack([pp.render_skeleton(p, size=pp.MODEL_INPUT_SIZE) for p in test_points]).astype(np.float32)
    logits = sess.run([sess.get_outputs()[0].name], {input_name: rendered_batch})[0]
    probs = softmax(logits)

    predicted = probs.argmax(axis=1)
    confidence = probs.max(axis=1)
    correct = predicted == test_labels

    thresholds = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    threshold_results = []

    for th in thresholds:
        passing = confidence >= th
        cov = float(np.mean(passing))
        prec = float(np.mean(correct[passing])) if np.any(passing) else 1.0
        wrong_count = int(np.sum(~correct[passing]))
        total_committed = int(np.sum(passing))
        threshold_results.append({
            "threshold": th,
            "coverage": cov,
            "precision": prec,
            "wrong_commits": wrong_count,
            "total_committed": total_committed
        })

    # 2. Jitter Stability across 8 trials
    trials = 8
    agreements = np.zeros(len(test_points), dtype=np.int32)
    for _ in range(trials):
        jittered = np.stack([jitter_landmarks(p, rng) for p in test_points])
        j_rendered = np.stack([pp.render_skeleton(p, size=pp.MODEL_INPUT_SIZE) for p in jittered]).astype(np.float32)
        j_logits = sess.run([sess.get_outputs()[0].name], {input_name: j_rendered})[0]
        j_pred = j_logits.argmax(axis=1)
        agreements += (j_pred == predicted)

    per_sample_agreement = agreements / trials
    rock_solid = float(np.mean(agreements == trials))
    overall_agreement = float(np.mean(per_sample_agreement))
    correct_mask = correct
    wrong_mask = ~correct
    corr_agreement = float(np.mean(per_sample_agreement[correct_mask])) if np.any(correct_mask) else 1.0
    wrong_agreement = float(np.mean(per_sample_agreement[wrong_mask])) if np.any(wrong_mask) else 0.0

    # 3. Commit Frame Latency Simulation (3 to 20 frames)
    commit_windows = [3, 5, 8, 10, 12, 15, 18, 20]
    frame_results = []
    for win in commit_windows:
        # Probability of staying consistent over win frames for correct vs wrong predictions
        # Modeled from jitter agreement
        p_commit_corr = float(corr_agreement ** win)
        p_commit_wrong = float(wrong_agreement ** win)
        frame_results.append({
            "commit_frames": win,
            "p_commit_correct": p_commit_corr,
            "p_commit_wrong": p_commit_wrong,
            "effective_latency_ms": win * (1000.0 / 30.0)
        })

    results = {
        "experiment": "EXP-CONFIDENCE-GATING",
        "seed": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "baseline_accuracy": float(np.mean(correct)),
        "threshold_sweep": threshold_results,
        "commit_frame_sweep": frame_results,
        "stability": {
            "rock_solid_hands_pct": rock_solid,
            "overall_agreement": overall_agreement,
            "agreement_when_baseline_correct": corr_agreement,
            "agreement_when_baseline_wrong": wrong_agreement
        }
    }

    print(f"  [Seed {seed}] Baseline Acc: {results['baseline_accuracy']:.2%} | Stability Correct: {corr_agreement:.1%} | Wrong: {wrong_agreement:.1%}")

    out_file = os.path.join(out_dir, f"confidence_gating_seed_{seed}.json")
    with open(out_file, "w") as fp:
        json.dump(results, fp, indent=2)
    print(f"Saved confidence gating benchmark to {out_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    run_evaluation(args.seed)
