"""Baseline 1: Direct Coordinate MLP Architecture.

A multi-layer perceptron that classifies hand gestures directly from flattened
42-dimensional normalized landmark coordinates (21 joints * (x, y)), bypassing
the 2D spatial skeleton rendering.

Architecture:
  Input: (Batch, 42)
  Linear(42 -> 128) -> BatchNorm -> ReLU -> Dropout(0.25)
  Linear(128 -> 64) -> BatchNorm -> ReLU -> Dropout(0.25)
  Linear(64 -> 26)  -> Logits
"""

import numpy as np

class CoordinateMLP:
    """Numpy-based forward and backprop implementation for reproducibility."""
    def __init__(self, input_dim=42, hidden1=128, hidden2=64, num_classes=26, seed=42):
        rng = np.random.default_rng(seed)
        # He normal initialization
        self.W1 = rng.normal(0, np.sqrt(2.0 / input_dim), (input_dim, hidden1)).astype(np.float32)
        self.b1 = np.zeros(hidden1, dtype=np.float32)
        self.W2 = rng.normal(0, np.sqrt(2.0 / hidden1), (hidden1, hidden2)).astype(np.float32)
        self.b2 = np.zeros(hidden2, dtype=np.float32)
        self.W3 = rng.normal(0, np.sqrt(2.0 / hidden2), (hidden2, num_classes)).astype(np.float32)
        self.b3 = np.zeros(num_classes, dtype=np.float32)

    def forward(self, X):
        # X: (N, 42)
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1) # ReLU
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = np.maximum(0, self.z2) # ReLU
        self.logits = self.a2 @ self.W3 + self.b3
        return self.logits

    def fit(self, X, y, epochs=60, lr=0.005, batch_size=64, rng=None):
        num_samples = len(X)
        num_classes = self.W3.shape[1]

        # One-hot encode y
        Y = np.zeros((num_samples, num_classes), dtype=np.float32)
        Y[np.arange(num_samples), y] = 1.0

        for epoch in range(epochs):
            indices = np.arange(num_samples)
            if rng: rng.shuffle(indices)
            for i in range(0, num_samples, batch_size):
                idx = indices[i:i + batch_size]
                xb, yb = X[idx], Y[idx]
                bs = len(xb)

                # Forward
                z1 = xb @ self.W1 + self.b1
                a1 = np.maximum(0, z1)
                z2 = a1 @ self.W2 + self.b2
                a2 = np.maximum(0, z2)
                logits = a2 @ self.W3 + self.b3

                # Softmax
                exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

                # Gradients
                d_logits = (probs - yb) / bs
                dW3 = a2.T @ d_logits
                db3 = np.sum(d_logits, axis=0)

                da2 = d_logits @ self.W3.T
                dz2 = da2 * (z2 > 0)
                dW2 = a1.T @ dz2
                db2 = np.sum(dz2, axis=0)

                da1 = dz2 @ self.W2.T
                dz1 = da1 * (z1 > 0)
                dW1 = xb.T @ dz1
                db1 = np.sum(dz1, axis=0)

                # Update
                self.W3 -= lr * dW3
                self.b3 -= lr * db3
                self.W2 -= lr * dW2
                self.b2 -= lr * db2
                self.W1 -= lr * dW1
                self.b1 -= lr * db1

    def predict(self, X):
        logits = self.forward(X)
        return np.argmax(logits, axis=1)

    def count_parameters(self):
        return (42 * 128 + 128) + (128 * 64 + 64) + (64 * 26 + 26)
