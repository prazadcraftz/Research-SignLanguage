"""Generates Figure 5: Normalized 26x26 Confusion Matrix on Held-Out Benchmark."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_main_and_baselines.json"))
    with open(agg_file) as f:
        data = json.load(f)

    cm = np.array(data["proposed_confusion_matrix_mean"], dtype=float)
    # Normalize by row sums (true class)
    row_sums = cm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    cm_norm = cm / row_sums

    class_names = [chr(c).upper() for c in range(ord('a'), ord('z') + 1)]

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    im = ax.imshow(cm_norm, cmap="magma", vmin=0.0, vmax=1.0)

    ax.set_xticks(range(26))
    ax.set_yticks(range(26))
    ax.set_xticklabels(class_names, fontsize=8)
    ax.set_yticklabels(class_names, fontsize=8)

    ax.set_xlabel("Predicted Sign (Class Label)", labelpad=8)
    ax.set_ylabel("Ground-Truth Sign (Class Label)", labelpad=8)
    ax.set_title("Normalized Confusion Matrix on Held-Out Test Benchmark (Mean across 5 Seeds)", pad=12)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Normalized Classification Probability", rotation=270, labelpad=15)

    # Highlight diagonal accuracy
    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig5_confusion_matrix.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig5_confusion_matrix.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 5 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
