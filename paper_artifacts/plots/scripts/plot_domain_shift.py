"""Generates Figure 1: Domain Shift Breakdown ("Bug Chain") Degradation Bar Chart."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_domain_shift.json"))
    with open(agg_file) as f:
        data = json.load(f)["summary"]

    conditions = [
        "1. Canonical Shared Renderer",
        "2. Framing Mismatch (29%-76% fill)",
        "3. Aspect Squashed (4:3 camera stretch)",
        "4. Channel Inverted (BGR vs RGB)",
        "5. Cumulative Combined Shift"
    ]
    labels = [
        "Canonical\nRenderer",
        "+ Framing\nMismatch",
        "+ Aspect Ratio\nSquashing",
        "+ Color Order\nInversion",
        "Cumulative\nCombined"
    ]

    means = [data[c]["mean"] * 100 for c in conditions]
    stds = [data[c]["std"] * 100 for c in conditions]
    ci95 = [data[c]["ci95"] * 100 for c in conditions]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    colors = [PALETTE["green"], PALETTE["blue"], PALETTE["purple"], PALETTE["orange"], "#D9534F"]

    bars = ax.bar(labels, means, yerr=ci95, capsize=4, color=colors, edgecolor=PALETTE["dark_gray"], width=0.55, zorder=3)

    ax.set_ylabel("Inference Accuracy (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Inference Degradation under Domain Shift Violations (Mean ± 95% CI)")
    ax.grid(axis='y', zorder=0)

    # Annotate values and drops
    baseline_acc = means[0]
    for i, bar in enumerate(bars):
        h = bar.get_height()
        drop_str = f"(-{baseline_acc - h:.1f}%)" if i > 0 else "(Baseline)"
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 2.5,
                f"{h:.1f}%\n{drop_str}", ha='center', va='bottom', fontsize=8.5, weight='bold')

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig1_domain_shift.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig1_domain_shift.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 1 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
