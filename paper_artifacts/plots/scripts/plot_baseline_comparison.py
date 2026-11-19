"""Generates Figure 8: Main Results Comparison against Baseline Architectures."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_main_and_baselines.json"))
    with open(agg_file) as f:
        data = json.load(f)["models"]

    models_order = [
        ("Proposed_Canonical_CNN", "Proposed Canonical CNN\n(Skeleton + ONNX)"),
        ("Coordinate_MLP", "Coordinate MLP\n(3-Layer, 42-D)"),
        ("Coordinate_Random_Forest", "Random Forest\n(100 Trees, 42-D)"),
        ("Coordinate_SVM", "Support Vector Machine\n(RBF Kernel, 42-D)")
    ]

    labels = [clean for key, clean in models_order if key in data]
    acc_means = [data[key]["accuracy_mean"] * 100 for key, clean in models_order if key in data]
    acc_cis = [data[key]["accuracy_ci95"] * 100 for key, clean in models_order if key in data]

    f1_means = [data[key]["f1_mean"] * 100 for key, clean in models_order if key in data]
    f1_cis = [data[key]["f1_ci95"] * 100 for key, clean in models_order if key in data]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))

    x = np.arange(len(labels))
    w = 0.35

    bars1 = ax.bar(x - w/2, acc_means, yerr=acc_cis, capsize=4, width=w,
                   label="Top-1 Accuracy (%)", color=PALETTE["blue"], edgecolor=PALETTE["dark_gray"], zorder=3)
    bars2 = ax.bar(x + w/2, f1_means, yerr=f1_cis, capsize=4, width=w,
                   label="Macro-Average F1 (%)", color=PALETTE["green"], edgecolor=PALETTE["dark_gray"], zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Score (%)")
    ax.set_ylim(60, 105)
    ax.set_title("Performance Comparison Against Alternative Baselines (Mean ± 95% CI Across 5 Seeds)")
    ax.grid(axis='y', zorder=0)
    ax.legend(loc="lower right", framealpha=0.9)

    # Annotate top numbers
    for b1, b2, a, f in zip(bars1, bars2, acc_means, f1_means):
        ax.text(b1.get_x() + b1.get_width() / 2.0, a + 1.2, f"{a:.1f}%", ha='center', fontsize=8.5, weight='bold')
        ax.text(b2.get_x() + b2.get_width() / 2.0, f + 1.2, f"{f:.1f}%", ha='center', fontsize=8.5, weight='bold')

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig8_baseline_comparison.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig8_baseline_comparison.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 8 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
