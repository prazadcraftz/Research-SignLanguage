"""Generates Figure 4: Confidence Gating Sensitivity & Temporal Commit Trade-offs."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_confidence_gating.json"))
    with open(agg_file) as f:
        data = json.load(f)

    th_data = data["threshold_sweep_aggregated"]
    thresholds = [x["threshold"] for x in th_data]
    coverages = [x["coverage_mean"] * 100 for x in th_data]
    precisions = [x["precision_mean"] * 100 for x in th_data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    # Panel A: Coverage vs Precision
    ax1.plot(thresholds, precisions, label="Commit Precision (%)", color=PALETTE["green"], marker="o", linewidth=2)
    ax1.plot(thresholds, coverages, label="Commit Coverage (%)", color=PALETTE["blue"], marker="s", linewidth=2)

    # Highlight operational commit threshold at 0.75
    ax1.axvline(0.75, color=PALETTE["orange"], linestyle="--", linewidth=1.5, label="Operating Point (0.75)")
    ax1.set_xlabel("Confidence Gate Threshold $\\tau$")
    ax1.set_ylabel("Percentage (%)")
    ax1.set_title("(a) Precision vs. Coverage Trade-off Across Thresholds")
    ax1.set_ylim(60, 102)
    ax1.grid(True)
    ax1.legend(loc="lower left", framealpha=0.9)

    # Panel B: Jitter Stability Agreement (Correct vs Wrong Baseline)
    stab = data["stability"]
    categories = ["Baseline Prediction\nCORRECT", "Baseline Prediction\nINCORRECT"]
    means = [stab["agreement_when_correct_mean"] * 100, stab["agreement_when_wrong_mean"] * 100]
    stds = [stab["agreement_when_correct_std"] * 100, stab["agreement_when_wrong_std"] * 100]

    bars = ax2.bar(categories, means, yerr=stds, capsize=5, color=[PALETTE["green"], PALETTE["orange"]],
                   width=0.45, edgecolor=PALETTE["dark_gray"], zorder=3)
    ax2.set_ylabel("Perturbation Agreement (%)")
    ax2.set_ylim(0, 110)
    ax2.set_title("(b) Jitter Invariance over 8 Random Perturbations")
    ax2.grid(axis='y', zorder=0)

    for bar, val in zip(bars, means):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, val + 3.0,
                 f"{val:.1f}%", ha='center', va='bottom', fontsize=9.5, weight='bold')

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig4_gating_sensitivity.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig4_gating_sensitivity.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 4 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
