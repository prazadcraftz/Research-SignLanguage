"""Root entry point for the Edge-ASL Real-Time Translator.

Launches the live American Sign Language (ASL) fingerspelling translator with
MediaPipe Hands landmark extraction, ONNX-accelerated CNN inference,
hysteresis confidence smoothing, and kinematic motion tracking for dynamic signs ('J', 'Z').

Usage:
    python run_translator.py
    python run_translator.py --activations     # View convolutional filter activations
    python run_translator.py --debug-motion    # Live trajectory kinematics readout
    python run_translator.py --camera 1        # Specify external camera index
"""

import os
import sys

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(repo_root, "MediaPipe-ASL-sign-language-recognition")
    
    if not os.path.isdir(app_dir):
        sys.stderr.write(f"Error: Module directory '{app_dir}' not found.\n")
        sys.exit(1)
        
    # Switch working directory to ensure model weights, classes, and UI assets resolve cleanly
    os.chdir(app_dir)
    sys.path.insert(0, app_dir)
    
    import realtime_translator
    realtime_translator.main()

if __name__ == "__main__":
    main()
