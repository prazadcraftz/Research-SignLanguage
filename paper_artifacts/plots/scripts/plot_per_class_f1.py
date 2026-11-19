"""Generates Figure 6: Per-Class F1-Score Breakdown across all 26 Letters."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_main_and_baselines.json"))
    with open(agg_file) as f:
        data = json.load(f)

    f1_means = [x * 100 for x in data["proposed_per_class_f1_mean"]]
    f1_stds = [x * 100 for x in data["proposed_per_class_f1_std"]]
    class_names = [chr(c).upper() for c in range(ord('a'), ord('z') + 1)]

    fig, ax = plt.subplots(figsize=(10, 5.2))

    y_pos = np.arange(len(class_names))
    # Color code bars: green if >95%, orange if <80%, blue otherwise
    colors = []
    for val in f1_means:
        if val >= 95.0:
            colors.append(PALETTE["green"])
        elif val < 80.0:
            colors.append(PALETTE["orange"])
        else:
            colors.append(PALETTE["blue"])

    bars = ax.bar(y_pos, f1_means, yerr=f1_stds, capsize=3, color=colors,
                  edgecolor=PALETTE["dark_gray"], width=0.65, zorder=3)

    ax.axhline(np.mean(f1_means), color=PALETTE["dark_gray"], linestyle="--", linewidth=1.5,
               label=f"Macro-Average F1 ({np.mean(f1_means):.1f}%)")

    ax.set_xticks(y_pos)
    ax.set_xticklabels(class_names, fontsize=9, weight='bold')
    ax.set_ylabel("F1-Score (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Per-Class Recognition F1-Score on Held-Out Test Data (Mean ± Std Across 5 Seeds)")
    ax.grid(axis='y', zorder=0)
    ax.legend(loc="lower right", framealpha=0.9)

    # Annotate class N bottleneck
    n_idx = class_names.index("N")
    ax.annotate("Class 'N' Bottleneck\n(Thumb occlusion / low data)",
                xy=(n_idx, f1_means[n_idx]),
                xytext=(n_idx - 3.5, f1_means[n_idx] - 30),
                arrowprops=dict(facecolor=PALETTE["orange"], shrink=0.08, width=1.5, headwidth=6),
                fontsize=8.5, weight='bold', color=PALETTE["orange"])

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig6_per_class_f1.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig6_per_class_f1.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 6 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
