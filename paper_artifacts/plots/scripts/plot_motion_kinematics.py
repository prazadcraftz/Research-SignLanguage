"""Generates Figure 3: Dynamic Trajectory Kinematics & Discriminator Distributions."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from plot_style import apply_paper_style, PALETTE

def plot():
    apply_paper_style()
    raw_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "raw_results", "motion_kinematics_seed_123.json"))
    with open(raw_file) as f:
        data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    # Panel A: 2D Spatial Fingertip Trajectories
    # Synthesize representative trajectories for plotting
    t = np.linspace(0, 1, 45)
    # 1. Still Hand with noise
    still_x = np.random.normal(0, 0.02, size=45)
    still_y = np.random.normal(0, 0.02, size=45)

    # 2. J trajectory: descent then hook left/up
    j_x = np.where(t < 0.6, 0.0, -0.15 * (1.0 - np.cos((t - 0.6) / 0.4 * np.pi)))
    j_y = np.where(t < 0.6, (t / 0.6) * 0.35, 0.35 - 0.12 * np.sin((t - 0.6) / 0.4 * np.pi))

    # 3. Z trajectory: right -> diag down-left -> right
    z_x = np.zeros(45)
    z_y = np.zeros(45)
    for i, ti in enumerate(t):
        if ti < 0.33:
            z_x[i] = (ti / 0.33) * 0.40
            z_y[i] = 0.0
        elif ti < 0.66:
            p = (ti - 0.33) / 0.33
            z_x[i] = (1.0 - p) * 0.40
            z_y[i] = p * 0.30
        else:
            p = (ti - 0.66) / 0.34
            z_x[i] = p * 0.40
            z_y[i] = 0.30

    ax1.plot(still_x, still_y, label="Still Hand (Idle)", color=PALETTE["light_gray"], linestyle=":", linewidth=2)
    ax1.plot(j_x, j_y, label="Letter 'J' (Pinky Hook)", color=PALETTE["blue"], marker="o", markersize=4, markevery=5)
    ax1.plot(z_x, z_y, label="Letter 'Z' (Index Zigzag)", color=PALETTE["orange"], marker="s", markersize=4, markevery=5)
    ax1.invert_yaxis() # Image coordinates grow downwards
    ax1.set_xlabel("Horizontal Displacement $\Delta x$ (hand-widths)")
    ax1.set_ylabel("Vertical Displacement $\Delta y$ (hand-widths)")
    ax1.set_title("(a) Normalized Spatial Trajectories over 1.5s Window")
    ax1.grid(True)
    ax1.legend(loc="lower left", framealpha=0.9)

    # Panel B: Path Length vs Instantaneous Speed Separation
    categories = ["Still (Light)", "Still (Heavy)", "Slow 'J'", "Normal 'J'", "Slow 'Z'", "Normal 'Z'"]
    speeds = [
        data["scenarios"]["still_hand_light_jitter"]["median_speed"],
        data["scenarios"]["still_hand_heavy_jitter"]["median_speed"],
        data["scenarios"]["slow_j_gesture"]["median_speed"],
        data["scenarios"]["normal_j_gesture"]["median_speed"],
        data["scenarios"]["slow_z_gesture"]["median_speed"],
        data["scenarios"]["normal_z_gesture"]["median_speed"]
    ]
    paths = [
        data["scenarios"]["still_hand_light_jitter"]["median_path"],
        data["scenarios"]["still_hand_heavy_jitter"]["median_path"],
        data["scenarios"]["slow_j_gesture"]["median_path"],
        data["scenarios"]["normal_j_gesture"]["median_path"],
        data["scenarios"]["slow_z_gesture"]["median_path"],
        data["scenarios"]["normal_z_gesture"]["median_path"]
    ]

    x_idx = np.arange(len(categories))
    w = 0.35
    ax2.bar(x_idx - w/2, speeds, width=w, label="Speed (hand-widths/s)", color=PALETTE["purple"], alpha=0.85)
    ax2.bar(x_idx + w/2, paths, width=w, label="Path Length (hand-widths)", color=PALETTE["green"], alpha=0.85)

    # Threshold line
    ax2.axhline(0.035, color=PALETTE["purple"], linestyle="--", linewidth=1.5, label="MOVING_THRESHOLD (0.035)")
    ax2.axhline(0.55, color=PALETTE["green"], linestyle="-.", linewidth=1.5, label="MIN_PATH_LENGTH (0.55)")

    ax2.set_xticks(x_idx)
    ax2.set_xticklabels(categories, rotation=25, ha='right')
    ax2.set_ylabel("Kinematic Metric Value")
    ax2.set_title("(b) Speed vs. Path Length Separability")
    ax2.grid(axis='y')
    ax2.legend(loc="upper left", framealpha=0.9, fontsize=8)

    plt.tight_layout()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdf", "fig3_motion_kinematics.pdf")
    png_path = os.path.join(os.path.dirname(__file__), "..", "png", "fig3_motion_kinematics.png")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.savefig(pdf_path, bbox_inches='tight')
    fig.savefig(png_path, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 3 saved to {pdf_path} and {png_path}")

if __name__ == "__main__":
    plot()
