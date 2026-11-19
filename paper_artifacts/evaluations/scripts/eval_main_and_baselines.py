"""Experiment 6: Main Benchmark & Baseline Evaluation Across 5 Seeds.

Evaluates:
  1. Proposed Canonical Skeleton CNN (ONNX checkpoint)
  2. Baseline 1: Coordinate MLP (3-layer, 42-D input)
  3. Baseline 2: Coordinate Random Forest (100 trees)
  4. Baseline 3: Coordinate Support Vector Machine (RBF kernel)

Measures:
  - Top-1 Accuracy
  - Macro Precision, Macro Recall, Macro F1
  - Per-class precision, recall, F1 across all 26 signs
  - Full 26x26 confusion matrix
  - Commit Gate Coverage and Precision
  - Jitter Stability (8 perturbation trials)

Saves individual seed JSON files in raw_results/.
"""

import argparse
import json
import os
import sys
import time
import numpy as np
import onnxruntime as ort
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "MediaPipe-ASL-sign-language-recognition"))
BASELINES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "baselines"))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, BASELINES_DIR)

import preprocessing as pp
from coordinate_mlp import CoordinateMLP
from coordinate_rf_svm import build_random_forest, build_svm

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

def generate_partitioned_dataset(base_points, class_names, num_train_per_class=60, num_test_per_class=35, rng=None):
    # Generates a clean train / test split with realistic geometric augmentation
    X_train_pts, y_train = [], []
    X_test_pts, y_test = [], []

    for cls_idx in range(len(class_names)):
        pts = base_points[cls_idx]
        # Train partition
        for _ in range(num_train_per_class):
            aug = pp.augment_landmarks(pts, rng, mirror=True)
            X_train_pts.append(aug)
            y_train.append(cls_idx)
        # Test partition (distinct perturbations)
        for _ in range(num_test_per_class):
            aug = pp.augment_landmarks(pts, rng, mirror=True)
            X_test_pts.append(aug)
            y_test.append(cls_idx)

    return (np.array(X_train_pts), np.array(y_train),
            np.array(X_test_pts), np.array(y_test))

def run_evaluation(seed, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "raw_results")
    os.makedirs(out_dir, exist_ok=True)

    templates_path = os.path.join(os.path.dirname(__file__), "..", "canonical_templates.npz")
    templates_data = np.load(templates_path)
    base_points = templates_data["points"] # (26, 21, 2)
    class_names = [str(c) for c in templates_data["class_names"]]

    rng = np.random.default_rng(seed)

    X_train_pts, y_train, X_test_pts, y_test = generate_partitioned_dataset(
        base_points, class_names, num_train_per_class=80, num_test_per_class=35, rng=rng
    )

    # Flatten coordinates for vector baselines: (N, 42)
    X_train_vec = X_train_pts.reshape(len(X_train_pts), -1)
    X_test_vec = X_test_pts.reshape(len(X_test_pts), -1)

    # Render 96x96 RGB skeletons for Proposed CNN
    X_test_rendered = np.stack([pp.render_skeleton(p, size=pp.MODEL_INPUT_SIZE) for p in X_test_pts]).astype(np.float32)

    results = {
        "experiment": "EXP-MAIN-AND-BASELINES",
        "seed": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "class_names": class_names,
        "models": {}
    }

    # 1. Proposed Canonical Skeleton CNN
    model_path = os.path.join(REPO_ROOT, "asl_cnn_model.onnx")
    sess = ort.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name
    cnn_logits = sess.run([sess.get_outputs()[0].name], {input_name: X_test_rendered})[0]
    cnn_probs = softmax(cnn_logits)
    cnn_preds = np.argmax(cnn_probs, axis=1)

    p, r, f1, s = precision_recall_fscore_support(y_test, cnn_preds, average=None, zero_division=0)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, cnn_preds, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, cnn_preds)

    # Gating and Stability
    commit_mask = cnn_probs.max(axis=1) >= 0.75
    commit_prec = float(np.mean(cnn_preds[commit_mask] == y_test[commit_mask])) if np.any(commit_mask) else 1.0
    commit_cov = float(np.mean(commit_mask))

    # Jitter stability (8 trials)
    stability_trials = 8
    agreements = np.zeros(len(X_test_pts), dtype=int)
    for _ in range(stability_trials):
        j_pts = np.stack([jitter_landmarks(pt, rng) for pt in X_test_pts])
        j_rend = np.stack([pp.render_skeleton(pt, size=pp.MODEL_INPUT_SIZE) for pt in j_pts]).astype(np.float32)
        j_preds = sess.run([sess.get_outputs()[0].name], {input_name: j_rend})[0].argmax(axis=1)
        agreements += (j_preds == cnn_preds)
    stab_correct = float(np.mean((agreements / stability_trials)[cnn_preds == y_test]))
    stab_wrong = float(np.mean((agreements / stability_trials)[cnn_preds != y_test])) if np.any(cnn_preds != y_test) else 0.0

    results["models"]["Proposed_Canonical_CNN"] = {
        "accuracy": float(np.mean(cnn_preds == y_test)),
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "commit_precision": commit_prec,
        "commit_coverage": commit_cov,
        "stability_when_correct": stab_correct,
        "stability_when_wrong": stab_wrong,
        "parameters": 308602,
        "per_class_f1": [float(x) for x in f1],
        "per_class_precision": [float(x) for x in p],
        "per_class_recall": [float(x) for x in r],
        "confusion_matrix": cm.tolist()
    }
    print(f"  [Seed {seed}] Proposed CNN: Acc = {results['models']['Proposed_Canonical_CNN']['accuracy']:.2%} | F1 = {macro_f1:.2%}")

    # 2. Baseline 1: Coordinate MLP
    mlp = CoordinateMLP(input_dim=42, hidden1=128, hidden2=64, num_classes=26, seed=seed)
    mlp.fit(X_train_vec, y_train, epochs=80, lr=0.005, batch_size=64, rng=rng)
    mlp_preds = mlp.predict(X_test_vec)
    mlp_p, mlp_r, mlp_f1, _ = precision_recall_fscore_support(y_test, mlp_preds, average="macro", zero_division=0)
    results["models"]["Coordinate_MLP"] = {
        "accuracy": float(np.mean(mlp_preds == y_test)),
        "macro_precision": float(mlp_p),
        "macro_recall": float(mlp_r),
        "macro_f1": float(mlp_f1),
        "parameters": mlp.count_parameters()
    }
    print(f"  [Seed {seed}] Coordinate MLP: Acc = {results['models']['Coordinate_MLP']['accuracy']:.2%} | F1 = {mlp_f1:.2%}")

    # 3. Baseline 2: Random Forest
    rf = build_random_forest(n_estimators=100, max_depth=15, seed=seed)
    rf.fit(X_train_vec, y_train)
    rf_preds = rf.predict(X_test_vec)
    rf_p, rf_r, rf_f1, _ = precision_recall_fscore_support(y_test, rf_preds, average="macro", zero_division=0)
    results["models"]["Coordinate_Random_Forest"] = {
        "accuracy": float(np.mean(rf_preds == y_test)),
        "macro_precision": float(rf_p),
        "macro_recall": float(rf_r),
        "macro_f1": float(rf_f1)
    }
    print(f"  [Seed {seed}] Random Forest: Acc = {results['models']['Coordinate_Random_Forest']['accuracy']:.2%} | F1 = {rf_f1:.2%}")

    # 4. Baseline 3: Support Vector Machine (RBF)
    svm = build_svm(C=2.0, kernel="rbf", seed=seed)
    svm.fit(X_train_vec, y_train)
    svm_preds = svm.predict(X_test_vec)
    svm_p, svm_r, svm_f1, _ = precision_recall_fscore_support(y_test, svm_preds, average="macro", zero_division=0)
    results["models"]["Coordinate_SVM"] = {
        "accuracy": float(np.mean(svm_preds == y_test)),
        "macro_precision": float(svm_p),
        "macro_recall": float(svm_r),
        "macro_f1": float(svm_f1)
    }
    print(f"  [Seed {seed}] Coordinate SVM: Acc = {results['models']['Coordinate_SVM']['accuracy']:.2%} | F1 = {svm_f1:.2%}")

    out_file = os.path.join(out_dir, f"main_and_baselines_seed_{seed}.json")
    with open(out_file, "w") as fp:
        json.dump(results, fp, indent=2)
    print(f"Saved main and baselines results to {out_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    run_evaluation(args.seed)
