"""Baselines 2 & 3: Coordinate Random Forest and Support Vector Machine.

Classifies ASL alphabet signs directly from flattened 42-dimensional
normalized landmark coordinates.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import numpy as np

def build_random_forest(n_estimators=100, max_depth=15, seed=42):
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=seed,
        n_jobs=-1
    )

def build_svm(C=1.0, kernel="rbf", seed=42):
    return SVC(
        C=C,
        kernel=kernel,
        probability=True,
        random_state=seed
    )
