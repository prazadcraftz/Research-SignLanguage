"""Root entry point for Empirical Evaluations and Benchmark Reproducibility.

Executes the experimental evaluation benchmarks across 5 random seeds
(domain shift breakdown, OneEuroFilter vs EWMA landmark denoising,
dynamic trajectory kinematics for 'J'/'Z', confidence hysteresis stability,
hardware latency/throughput profiling, and baseline comparisons).
Regenerates all publication figures and LaTeX/CSV tables.

Usage:
    python run_evaluations.py
"""

import os
import sys

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(repo_root, "paper_artifacts")
    
    if not os.path.isdir(artifacts_dir):
        sys.stderr.write(f"Error: Directory '{artifacts_dir}' not found.\n")
        sys.exit(1)
        
    os.chdir(artifacts_dir)
    sys.path.insert(0, artifacts_dir)
    
    from reproducibility.run_all_evaluations import main as run_all
    run_all()

if __name__ == "__main__":
    main()
