"""Master Automated Reproducibility Runner.

Executes all experimental evaluation benchmarks across 5 random seeds,
aggregates raw results, performs statistical significance tests, and generates
all publication figures (vector PDF + 350 DPI PNG) and tables (LaTeX .tex + CSV).
"""

import os
import sys
import time

ARTIFACTS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEEDS = [42, 123, 456, 789, 1024]

def main():
    start_time = time.time()
    print("=" * 72)
    print("STARTING COMPLETE EVALUATION & FIGURE/TABLE GENERATION PIPELINE")
    print(f"Seeds: {SEEDS}")
    print("=" * 72)

    # 1. Domain Shift
    print("\n--- Running Experiment 1: Domain Shift Breakdown ---")
    from evaluations.scripts.eval_domain_shift import run_evaluation as run_ds
    for s in SEEDS:
        run_ds(s)

    # 2. Smoothing
    print("\n--- Running Experiment 2: Landmark Denoising Benchmark ---")
    from evaluations.scripts.eval_smoothing import run_evaluation as run_sm
    for s in SEEDS:
        run_sm(s)

    # 3. Motion Kinematics
    print("\n--- Running Experiment 3: Trajectory Kinematics Benchmark ---")
    from evaluations.scripts.eval_motion_kinematics import run_evaluation as run_mk
    for s in SEEDS:
        run_mk(s, num_trials=50)

    # 4. Confidence Gating
    print("\n--- Running Experiment 4: Confidence Gating & Jitter Stability ---")
    from evaluations.scripts.eval_confidence_gating import run_evaluation as run_cg
    for s in SEEDS:
        run_cg(s)

    # 5. Efficiency Profiling
    print("\n--- Running Experiment 5: Efficiency Profiling ---")
    from evaluations.scripts.eval_efficiency_profiling import run_profiling
    run_profiling(iterations=500)

    # 6. Main and Baselines
    print("\n--- Running Experiment 6: Main Benchmark & Baselines ---")
    from evaluations.scripts.eval_main_and_baselines import run_evaluation as run_mb
    for s in SEEDS:
        run_mb(s)

    # 7. Ablation Rendering
    print("\n--- Running Ablation Study: Skeleton Rendering Properties ---")
    from ablations.ablate_rendering import run_ablation
    for s in SEEDS:
        run_ablation(s)

    # 8. Aggregation
    print("\n--- Aggregating Results across 5 Seeds ---")
    from evaluations.scripts.aggregate_results import aggregate
    aggregate()

    # 9. Statistical Tests
    print("\n--- Computing Statistical Significance Tests ---")
    from analysis.statistical_significance import run_significance_tests
    run_significance_tests()

    # 10. Figures Generation
    print("\n--- Generating All 10 Publication Figures (Vector PDF + PNG) ---")
    sys.path.insert(0, os.path.join(ARTIFACTS_ROOT, "plots", "scripts"))
    import plot_domain_shift
    import plot_smoothing_tradeoff
    import plot_motion_kinematics
    import plot_gating_sensitivity
    import plot_confusion_matrix
    import plot_per_class_f1
    import plot_latency_breakdown
    import plot_baseline_comparison
    import plot_ablation_rendering
    import plot_training_convergence

    plot_domain_shift.plot()
    plot_smoothing_tradeoff.plot()
    plot_motion_kinematics.plot()
    plot_gating_sensitivity.plot()
    plot_confusion_matrix.plot()
    plot_per_class_f1.plot()
    plot_latency_breakdown.plot()
    plot_baseline_comparison.plot()
    plot_ablation_rendering.plot()
    plot_training_convergence.plot()

    # 11. Tables Generation
    print("\n--- Generating All LaTeX (.tex) and CSV Tables ---")
    from tables.generate_tables import generate_all_tables
    generate_all_tables()

    elapsed = time.time() - start_time
    print("\n" + "=" * 72)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.1f} SECONDS!")
    print("All evaluation plots (PDF/PNG) and tables (LaTeX/CSV) are generated.")
    print("=" * 72)

if __name__ == "__main__":
    # Add artifacts root to path
    sys.path.insert(0, ARTIFACTS_ROOT)
    main()
