"""Generates Figure 2: Landmark Denoising Benchmark (Shimmer vs Latency)."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    agg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "aggregated", "aggregated_smoothing.json"))
    with open(agg_file) as f:
        data = json.load(f)

    noise_levels = data["noise_levels_px"]
    speeds = data["speeds_px_s"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    filter_styles = {
        "Raw (No Filter)": {"color": PALETTE["light_gray"], "ls": ":", "marker": "x"},
        "Fixed-EMA (alpha=0.50)": {"color": PALETTE["yellow"], "ls": "--", "marker": "s"},
        "Fixed-EMA (alpha=0.35)": {"color": PALETTE["orange"], "ls": "--", "marker": "^"},
        "Fixed-EMA (alpha=0.20)": {"color": PALETTE["purple"], "ls": "--", "marker": "d"},
        "1-Euro Adaptive Filter": {"color": PALETTE["green"], "ls": "-", "marker": "o"}
    }

    # Panel A: Still-Hand Shimmer vs Noise
    for filt, style in filter_styles.items():
        if filt in data["shimmer_rms"]:
            means = data["shimmer_rms"][filt]["mean"]
            stds = data["shimmer_rms"][filt]["std"]
            ax1.plot(noise_levels, means, label=filt, color=style["color"],
                     linestyle=style["ls"], marker=style["marker"])

    ax1.set_xlabel("MediaPipe Detection Noise $\sigma$ (pixels)")
    ax1.set_ylabel("Still-Hand Shimmer RMS (pixels)")
    ax1.set_title("(a) Idle Landmark Shimmer vs. Sensor Noise")
    ax1.grid(True)
    ax1.legend(loc="upper left", framealpha=0.9)

    # Panel B: Dynamic Lag vs Speed
    for filt, style in filter_styles.items():
        if filt in data["motion_lag_ms"]:
            means = data["motion_lag_ms"][filt]["mean"]
            ax2.plot(speeds, means, label=filt, color=style["color"],
                     linestyle=style["ls"], marker=style["marker"])

    ax2.set_xlabel("Hand Movement Speed (pixels / second)")
    ax2.set_ylabel("Dynamic Tracking Lag (milliseconds)")
    ax2.set_title("(b) Dynamic Latency vs. Gesture Velocity")
    ax2.grid(True)
    ax2.legend(loc="upper right", framealpha=0.9)

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig2_smoothing_tradeoff.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig2_smoothing_tradeoff.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 2 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
