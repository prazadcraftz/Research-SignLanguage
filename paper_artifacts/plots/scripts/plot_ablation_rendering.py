"""Generates Figure 9: Ablation Study on Skeleton Rendering Properties."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_ablation_rendering.json"))
    with open(agg_file) as f:
        data = json.load(f)["variants"]

    variants = [
        ("Default (96x96, Color, Standard Stroke)", "Proposed Canonical\n(96x96, Color)"),
        ("Resolution: 48x48 (Upscaled to 96x96)", "Resolution:\n48x48 (Low)"),
        ("Resolution: 192x192 (Downsampled to 96x96)", "Resolution:\n192x192 (High)"),
        ("Monochrome Grayscale Skeleton", "Monochrome\n(No Color)"),
        ("Thin Stroke Weight", "Thin\nStroke"),
        ("Thick Stroke Weight", "Thick\nStroke")
    ]

    labels = [clean for key, clean in variants if key in data]
    means = [data[key]["mean"] * 100 for key, clean in variants if key in data]
    cis = [data[key]["ci95"] * 100 for key, clean in variants if key in data]

    fig, ax = plt.subplots(figsize=(8.5, 4.4))

    colors = [PALETTE["green"], PALETTE["blue"], PALETTE["cyan"], PALETTE["orange"], PALETTE["purple"], PALETTE["yellow"]]

    bars = ax.bar(labels, means, yerr=cis, capsize=4, color=colors[:len(labels)],
                  edgecolor=PALETTE["dark_gray"], width=0.55, zorder=3)

    ax.set_ylabel("Inference Accuracy (%)")
    ax.set_ylim(60, 102)
    ax.set_title("Ablation of Rendering Resolution, Chromatic Encoding, and Stroke Thickness")
    ax.grid(axis='y', zorder=0)

    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2.0, m + 1.2,
                f"{m:.1f}%", ha='center', fontsize=8.5, weight='bold')

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig9_ablation_rendering.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig9_ablation_rendering.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 9 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
