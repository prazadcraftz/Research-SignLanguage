"""Aggregates per-seed evaluation results into publication summary tables.

Calculates:
  - Mean across seeds
  - Standard Deviation (std)
  - 95% Confidence Intervals (CI_95) using Student-t distribution (df = 4, t = 2.776)
"""

import json
import os
import glob
import numpy as np

def compute_ci95(values):
    vals = np.array(values, dtype=float)
    n = len(vals)
    if n <= 1:
        return 0.0
    # Student t multiplier for df = 4 at 95% two-sided is 2.776
    t_val = 2.776 if n == 5 else 1.96
    return float(t_val * np.std(vals, ddof=1) / np.sqrt(n))

def aggregate():
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "raw_results"))
    agg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aggregated"))
    os.makedirs(agg_dir, exist_ok=True)

    # 1. Domain Shift
    ds_files = glob.glob(os.path.join(raw_dir, "domain_shift_seed_*.json"))
    if ds_files:
        cond_data = {}
        for f in ds_files:
            with open(f) as fp:
                d = json.load(fp)
            for cond, vals in d["conditions"].items():
                cond_data.setdefault(cond, []).append(vals["accuracy"])

        ds_agg = {
            "experiment": "EXP-DOMAIN-SHIFT",
            "num_seeds": len(ds_files),
            "summary": {}
        }
        for cond, accs in cond_data.items():
            ds_agg["summary"][cond] = {
                "mean": float(np.mean(accs)),
                "std": float(np.std(accs, ddof=1)) if len(accs) > 1 else 0.0,
                "ci95": compute_ci95(accs),
                "values": accs
            }
        with open(os.path.join(agg_dir, "aggregated_domain_shift.json"), "w") as fp:
            json.dump(ds_agg, fp, indent=2)
        print("Aggregated Domain Shift results.")

    # 2. Smoothing
    sm_files = glob.glob(os.path.join(raw_dir, "smoothing_seed_*.json"))
    if sm_files:
        shimmer_acc = {}
        lag_acc = {}
        speeds = None
        noise_levels = None
        for f in sm_files:
            with open(f) as fp:
                d = json.load(fp)
            speeds = d["speeds_px_s"]
            noise_levels = d["noise_levels_px"]
            for filt, vals in d["shimmer_rms"].items():
                shimmer_acc.setdefault(filt, []).append(vals)
            for filt, vals in d["motion_lag_ms"].items():
                lag_acc.setdefault(filt, []).append(vals)

        sm_agg = {
            "experiment": "EXP-DENOISING-SMOOTHING",
            "speeds_px_s": speeds,
            "noise_levels_px": noise_levels,
            "shimmer_rms": {},
            "motion_lag_ms": {}
        }
        for filt, mat in shimmer_acc.items():
            mat = np.array(mat) # (seeds, noise_levels)
            sm_agg["shimmer_rms"][filt] = {
                "mean": [float(x) for x in np.mean(mat, axis=0)],
                "std": [float(x) for x in np.std(mat, axis=0, ddof=1)]
            }
        for filt, mat in lag_acc.items():
            mat = np.array(mat) # (seeds, speeds)
            sm_agg["motion_lag_ms"][filt] = {
                "mean": [float(x) for x in np.mean(mat, axis=0)],
                "std": [float(x) for x in np.std(mat, axis=0, ddof=1)]
            }
        with open(os.path.join(agg_dir, "aggregated_smoothing.json"), "w") as fp:
            json.dump(sm_agg, fp, indent=2)
        print("Aggregated Smoothing results.")

    # 3. Main and Baselines
    mb_files = glob.glob(os.path.join(raw_dir, "main_and_baselines_seed_*.json"))
    if mb_files:
        model_accs = {}
        model_f1s = {}
        model_precs = {}
        model_recs = {}
        per_class_f1s = []
        conf_matrices = []

        for f in mb_files:
            with open(f) as fp:
                d = json.load(fp)
            for m_name, m_data in d["models"].items():
                model_accs.setdefault(m_name, []).append(m_data["accuracy"])
                model_f1s.setdefault(m_name, []).append(m_data["macro_f1"])
                model_precs.setdefault(m_name, []).append(m_data["macro_precision"])
                model_recs.setdefault(m_name, []).append(m_data["macro_recall"])

            if "Proposed_Canonical_CNN" in d["models"]:
                per_class_f1s.append(d["models"]["Proposed_Canonical_CNN"]["per_class_f1"])
                conf_matrices.append(d["models"]["Proposed_Canonical_CNN"]["confusion_matrix"])

        mb_agg = {
            "experiment": "EXP-MAIN-AND-BASELINES",
            "num_seeds": len(mb_files),
            "models": {}
        }
        for m_name in model_accs.keys():
            mb_agg["models"][m_name] = {
                "accuracy_mean": float(np.mean(model_accs[m_name])),
                "accuracy_std": float(np.std(model_accs[m_name], ddof=1)),
                "accuracy_ci95": compute_ci95(model_accs[m_name]),
                "f1_mean": float(np.mean(model_f1s[m_name])),
                "f1_std": float(np.std(model_f1s[m_name], ddof=1)),
                "f1_ci95": compute_ci95(model_f1s[m_name]),
                "precision_mean": float(np.mean(model_precs[m_name])),
                "precision_std": float(np.std(model_precs[m_name], ddof=1)),
                "recall_mean": float(np.mean(model_recs[m_name])),
                "recall_std": float(np.std(model_recs[m_name], ddof=1))
            }

        if per_class_f1s:
            pcf1_arr = np.array(per_class_f1s)
            mb_agg["proposed_per_class_f1_mean"] = [float(x) for x in np.mean(pcf1_arr, axis=0)]
            mb_agg["proposed_per_class_f1_std"] = [float(x) for x in np.std(pcf1_arr, axis=0, ddof=1)]

        if conf_matrices:
            cm_mean = np.mean(np.array(conf_matrices), axis=0)
            mb_agg["proposed_confusion_matrix_mean"] = cm_mean.tolist()

        with open(os.path.join(agg_dir, "aggregated_main_and_baselines.json"), "w") as fp:
            json.dump(mb_agg, fp, indent=2)
        print("Aggregated Main and Baselines results.")

    # 4. Confidence Gating
    cg_files = glob.glob(os.path.join(raw_dir, "confidence_gating_seed_*.json"))
    if cg_files:
        th_sweeps = []
        frame_sweeps = []
        stab_corr = []
        stab_wrong = []
        for f in cg_files:
            with open(f) as fp:
                d = json.load(fp)
            th_sweeps.append(d["threshold_sweep"])
            frame_sweeps.append(d["commit_frame_sweep"])
            stab_corr.append(d["stability"]["agreement_when_baseline_correct"])
            stab_wrong.append(d["stability"]["agreement_when_baseline_wrong"])

        # Average over threshold sweep
        num_th = len(th_sweeps[0])
        agg_th = []
        for i in range(num_th):
            th_val = th_sweeps[0][i]["threshold"]
            covs = [s[i]["coverage"] for s in th_sweeps]
            precs = [s[i]["precision"] for s in th_sweeps]
            wrongs = [s[i]["wrong_commits"] for s in th_sweeps]
            agg_th.append({
                "threshold": th_val,
                "coverage_mean": float(np.mean(covs)),
                "coverage_std": float(np.std(covs, ddof=1)),
                "precision_mean": float(np.mean(precs)),
                "precision_std": float(np.std(precs, ddof=1)),
                "wrong_commits_mean": float(np.mean(wrongs))
            })

        cg_agg = {
            "experiment": "EXP-CONFIDENCE-GATING",
            "threshold_sweep_aggregated": agg_th,
            "stability": {
                "agreement_when_correct_mean": float(np.mean(stab_corr)),
                "agreement_when_correct_std": float(np.std(stab_corr, ddof=1)),
                "agreement_when_wrong_mean": float(np.mean(stab_wrong)),
                "agreement_when_wrong_std": float(np.std(stab_wrong, ddof=1))
            }
        }
        with open(os.path.join(agg_dir, "aggregated_confidence_gating.json"), "w") as fp:
            json.dump(cg_agg, fp, indent=2)
        print("Aggregated Confidence Gating results.")

    # 5. Ablation Rendering
    abl_files = glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "ablations", "ablation_rendering_seed_*.json"))
    if abl_files:
        abl_data = {}
        for f in abl_files:
            with open(f) as fp:
                d = json.load(fp)
            for var, vals in d["variants"].items():
                abl_data.setdefault(var, []).append(vals["accuracy"])

        abl_agg = {
            "experiment": "ABLATION-RENDERING",
            "variants": {}
        }
        for var, accs in abl_data.items():
            abl_agg["variants"][var] = {
                "mean": float(np.mean(accs)),
                "std": float(np.std(accs, ddof=1)),
                "ci95": compute_ci95(accs)
            }
        with open(os.path.join(agg_dir, "aggregated_ablation_rendering.json"), "w") as fp:
            json.dump(abl_agg, fp, indent=2)
        print("Aggregated Ablation Rendering results.")

if __name__ == "__main__":
    aggregate()
