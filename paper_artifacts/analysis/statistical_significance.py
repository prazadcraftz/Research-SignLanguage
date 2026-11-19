"""Statistical Significance Tests between Proposed System and Baselines.

Runs:
  - Paired two-tailed Student's t-test
  - Wilcoxon signed-rank test
  - Cohen's d effect size calculation
Outputs statistical test reports to analysis/statistical_tests.json.
"""

import json
import os
import numpy as np
from scipy import stats

def cohens_d(x, y):
    diff = np.array(x) - np.array(y)
    return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-8))

def run_significance_tests():
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evaluations", "raw_results"))
    import glob
    mb_files = sorted(glob.glob(os.path.join(raw_dir, "main_and_baselines_seed_*.json")))

    if not mb_files:
        print("No raw evaluation files found for significance tests.")
        return

    proposed_accs = []
    mlp_accs = []
    rf_accs = []
    svm_accs = []

    for f in mb_files:
        with open(f) as fp:
            d = json.load(fp)
        proposed_accs.append(d["models"]["Proposed_Canonical_CNN"]["accuracy"])
        proposed_accs.append(d["models"]["Proposed_Canonical_CNN"]["macro_f1"]) # test both
        mlp_accs.append(d["models"]["Coordinate_MLP"]["accuracy"])
        rf_accs.append(d["models"]["Coordinate_Random_Forest"]["accuracy"])
        svm_accs.append(d["models"]["Coordinate_SVM"]["accuracy"])

    # Look specifically at the accuracy arrays per seed:
    seeds_count = len(mb_files)
    prop = [d["models"]["Proposed_Canonical_CNN"]["accuracy"] for d in [json.load(open(f)) for f in mb_files]]
    mlp = [d["models"]["Coordinate_MLP"]["accuracy"] for d in [json.load(open(f)) for f in mb_files]]
    rf = [d["models"]["Coordinate_Random_Forest"]["accuracy"] for d in [json.load(open(f)) for f in mb_files]]
    svm = [d["models"]["Coordinate_SVM"]["accuracy"] for d in [json.load(open(f)) for f in mb_files]]

    tests = {}
    for baseline_name, b_vals in [("Coordinate_MLP", mlp), ("Coordinate_Random_Forest", rf), ("Coordinate_SVM", svm)]:
        t_stat, p_val_t = stats.ttest_rel(prop, b_vals)
        try:
            w_stat, p_val_w = stats.wilcoxon(prop, b_vals)
        except Exception:
            w_stat, p_val_w = 0.0, 1.0

        d_val = cohens_d(prop, b_vals)

        tests[f"Proposed_vs_{baseline_name}"] = {
            "proposed_mean": float(np.mean(prop)),
            "baseline_mean": float(np.mean(b_vals)),
            "mean_difference": float(np.mean(prop) - np.mean(b_vals)),
            "t_statistic": float(t_stat),
            "p_value_paired_t": float(p_val_t),
            "wilcoxon_stat": float(w_stat),
            "p_value_wilcoxon": float(p_val_w),
            "cohens_d": d_val,
            "statistically_significant_p05": bool(p_val_t < 0.05)
        }

    out_file = os.path.join(os.path.dirname(__file__), "statistical_tests.json")
    with open(out_file, "w") as fp:
        json.dump(tests, fp, indent=2)
    print(f"Saved statistical tests to {out_file}")

    print("\n--- Statistical Significance Test Results (alpha = 0.05) ---")
    for comp, res in tests.items():
        sig_str = "SIGNIFICANT (p < 0.05)" if res["statistically_significant_p05"] else "NOT SIGNIFICANT"
        print(f"  {comp:<32}: t = {res['t_statistic']:6.3f}, p = {res['p_value_paired_t']:.4e}, d = {res['cohens_d']:5.2f} [{sig_str}]")

if __name__ == "__main__":
    run_significance_tests()
