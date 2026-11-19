"""Generates Figure 7: Computational Efficiency and Stage-Wise Latency Profiling."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    raw_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "raw_results", "efficiency_profiling.json"))
    with open(raw_file) as f:
        data = json.load(f)

    stages_raw = data["stage_latency"]
    labels_clean = [
        ("mediapipe_detection", "MediaPipe Landmark Extraction"),
        ("one_euro_filter", "1-Euro Adaptive Filter"),
        ("coordinate_normalization", "Coordinate Normalization"),
        ("skeleton_rendering", "Skeleton Rendering (render_skeleton)"),
        ("onnx_inference_cpu", "ONNX Model Inference (CPU)"),
        ("temporal_gating", "Temporal Smoothing & Gating"),
        ("ui_compositing", "UI Compositing (Single-Window)")
    ]

    names = [clean for key, clean in labels_clean if key in stages_raw]
    means = [stages_raw[key]["mean_ms"] for key, clean in labels_clean if key in stages_raw]
    stds = [stages_raw[key]["std_ms"] for key, clean in labels_clean if key in stages_raw]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))

    y_pos = np.arange(len(names))
    colors = [PALETTE["blue"], PALETTE["green"], PALETTE["cyan"], PALETTE["yellow"],
              PALETTE["orange"], PALETTE["purple"], PALETTE["light_gray"]]

    bars = ax.barh(y_pos, means, xerr=stds, capsize=3, color=colors[:len(names)],
                   edgecolor=PALETTE["dark_gray"], height=0.6, zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis() # Top down
    ax.set_xlabel("Execution Time per Frame (milliseconds)")
    total_lat = data["total_end_to_end_latency_ms"]
    fps = data["effective_fps"]
    ax.set_title(f"Stage-by-Stage Latency on Commodity CPU (Total: {total_lat:.1f} ms ~ {fps:.1f} FPS)")
    ax.grid(axis='x', zorder=0)

    # Annotate ms numbers
    for bar, m in zip(bars, means):
        ax.text(m + 0.4, bar.get_y() + bar.get_height() / 2.0,
                f"{m:.2f} ms", va='center', fontsize=8.5, weight='bold')

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig7_latency_breakdown.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig7_latency_breakdown.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 7 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
