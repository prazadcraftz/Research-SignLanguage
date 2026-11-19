"""Experiment 2: Landmark Denoising Benchmark Script.

Evaluates:
  1. Still-Hand Shimmer (RMS in pixels) over 5 seconds at 30 FPS across
     detection noise levels (0.5 to 5.0 px).
  2. Dynamic Tracking Lag (pixels and milliseconds) across hand velocities
     (50 to 2000 px/s).
  3. Effective alpha curves: 1-Euro adaptive alpha vs Fixed EMA.
"""

import argparse
import json
import os
import sys
import time
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "MediaPipe-ASL-sign-language-recognition"))
sys.path.insert(0, REPO_ROOT)
import smoothing

def simulate_still_hand(filter_fn, noise_sigma, num_frames=150, fps=30.0, rng=None):
    dt = 1.0 / fps
    true_pos = np.array([[200.0, 200.0]], dtype=np.float32) # Hand center in px
    filter_fn.reset()

    filtered_positions = []
    t = 0.0
    for _ in range(num_frames):
        noisy_pos = true_pos + rng.normal(0, noise_sigma, size=true_pos.shape).astype(np.float32)
        out = filter_fn(noisy_pos, timestamp=t)
        filtered_positions.append(out[0])
        t += dt

    # Discard first 15 frames for warmup
    filtered_positions = np.array(filtered_positions[15:])
    diff = filtered_positions - true_pos[0]
    rms = float(np.sqrt(np.mean(diff ** 2)))
    return rms

def simulate_motion_lag(filter_fn, speed_px_s, duration=1.0, fps=30.0, noise_sigma=1.0, rng=None):
    dt = 1.0 / fps
    num_frames = int(duration * fps)
    start_pos = np.array([[100.0, 100.0]], dtype=np.float32)
    velocity = np.array([[speed_px_s, 0.0]], dtype=np.float32)

    filter_fn.reset()
    true_path = []
    filtered_path = []
    t = 0.0

    for i in range(num_frames):
        true_p = start_pos + velocity * t
        noisy_p = true_p + rng.normal(0, noise_sigma, size=true_p.shape).astype(np.float32)
        out = filter_fn(noisy_p, timestamp=t)
        true_path.append(true_p[0])
        filtered_path.append(out[0])
        t += dt

    # Look at steady-state lag during motion (second half)
    half = num_frames // 2
    true_arr = np.array(true_path[half:])
    filt_arr = np.array(filtered_path[half:])

    # Lag in pixels
    lag_px = float(np.mean(np.linalg.norm(true_arr - filt_arr, axis=1)))
    # Lag in time (ms) = lag_px / speed * 1000
    lag_ms = float((lag_px / speed_px_s) * 1000.0) if speed_px_s > 0 else 0.0
    return lag_px, lag_ms

class FixedAlphaFilter:
    def __init__(self, alpha):
        self.alpha = float(alpha)
        self.reset()
    def reset(self):
        self.prev = None
    def __call__(self, x, timestamp=None):
        if self.prev is None:
            self.prev = np.array(x, copy=True)
            return self.prev.copy()
        out = self.alpha * x + (1.0 - self.alpha) * self.prev
        self.prev = out.copy()
        return out

class RawFilter:
    def reset(self): pass
    def __call__(self, x, timestamp=None): return np.array(x, copy=True)

def run_evaluation(seed, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "raw_results")
    os.makedirs(out_dir, exist_ok=True)

    rng = np.random.default_rng(seed)

    filters = {
        "Raw (No Filter)": RawFilter(),
        "Fixed-EMA (alpha=0.20)": FixedAlphaFilter(0.20),
        "Fixed-EMA (alpha=0.35)": FixedAlphaFilter(0.35),
        "Fixed-EMA (alpha=0.50)": FixedAlphaFilter(0.50),
        "1-Euro Adaptive Filter": smoothing.OneEuroFilter(min_cutoff=0.8, beta=0.02, d_cutoff=1.0)
    }

    noise_levels = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    speeds = [50, 100, 200, 300, 500, 750, 1000, 1500, 2000]

    results = {
        "experiment": "EXP-DENOISING-SMOOTHING",
        "seed": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "noise_levels_px": noise_levels,
        "speeds_px_s": speeds,
        "shimmer_rms": {},
        "motion_lag_ms": {},
        "motion_lag_px": {},
        "effective_alpha": {}
    }

    # 1. Shimmer RMS across noise levels
    for name, f in filters.items():
        results["shimmer_rms"][name] = []
        for nl in noise_levels:
            rms = simulate_still_hand(f, nl, num_frames=150, rng=rng)
            results["shimmer_rms"][name].append(rms)

    # 2. Dynamic lag across speeds
    for name, f in filters.items():
        results["motion_lag_ms"][name] = []
        results["motion_lag_px"][name] = []
        for spd in speeds:
            lag_px, lag_ms = simulate_motion_lag(f, spd, duration=1.0, rng=rng)
            results["motion_lag_px"][name].append(lag_px)
            results["motion_lag_ms"][name].append(lag_ms)

    # 3. Effective alpha across speeds
    oe = smoothing.OneEuroFilter(min_cutoff=0.8, beta=0.02, d_cutoff=1.0)
    results["effective_alpha"]["1-Euro Adaptive Filter"] = [float(oe.effective_alpha(s)) for s in speeds]
    results["effective_alpha"]["Fixed-EMA (alpha=0.35)"] = [0.35 for _ in speeds]

    out_file = os.path.join(out_dir, f"smoothing_seed_{seed}.json")
    with open(out_file, "w") as fp:
        json.dump(results, fp, indent=2)
    print(f"Saved smoothing benchmark to {out_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    run_evaluation(args.seed)
