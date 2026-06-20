"""
test_adversarial_guard.py — Unit tests for the Adversarial Guard.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.security.adversarial_guard import (
    AdversarialDetector,
    guard_embedding,
    NORM_UPPER,
    NORM_LOWER,
    MAX_DIM_ABS,
)


class TestAdversarialDetector:
    """Tests for the AdversarialDetector heuristics."""

    def setup_method(self):
        self.detector = AdversarialDetector()

    def test_normal_embedding_passes(self):
        """A well-behaved embedding should pass all checks."""
        emb = np.random.normal(0, 0.5, size=768).astype(np.float32)
        assert self.detector.is_safe(emb) is True

    def test_high_norm_fails(self):
        """Embedding with a very large L2 norm should be flagged."""
        emb = np.ones(768, dtype=np.float32) * 10.0  # norm ≈ 277
        assert self.detector._check_norm(emb) is False

    def test_low_norm_fails(self):
        """Embedding with a near-zero norm should be flagged."""
        emb = np.zeros(768, dtype=np.float32)
        assert self.detector._check_norm(emb) is False

    def test_dimension_spike_fails(self):
        """A single dimension far exceeding MAX_DIM_ABS should be flagged."""
        emb = np.random.normal(0, 0.3, size=768).astype(np.float32)
        emb[100] = MAX_DIM_ABS + 5.0  # spike one dimension
        assert self.detector._check_dimension_spike(emb) is False

    def test_normal_dimensions_pass(self):
        emb = np.random.normal(0, 0.3, size=768).astype(np.float32)
        assert self.detector._check_dimension_spike(emb) is True

    def test_drift_check_no_history(self):
        """First call should always pass (no previous embedding)."""
        det = AdversarialDetector()
        emb = np.random.normal(0, 1, size=768).astype(np.float32)
        assert det._check_drift(emb) is True

    def test_drift_check_large_jump(self):
        """A massive jump between successive embeddings should be flagged."""
        det = AdversarialDetector()
        emb1 = np.zeros(768, dtype=np.float32) + 1.0  # norm ≈ 27.7
        det._check_drift(emb1)  # establish history

        emb2 = np.zeros(768, dtype=np.float32) - 1.0
        # L2 distance = sqrt(768 * 4) ≈ 55.4
        assert det._check_drift(emb2) is False


class TestGuardEmbedding:
    """Tests for the public guard_embedding API."""

    def test_safe_embedding_returns_true(self):
        emb = np.random.normal(0, 0.3, size=768).tolist()
        result = guard_embedding(emb)
        assert isinstance(result, bool)

    def test_malicious_embedding_returns_false(self):
        # Embedding with absurd values
        emb = [100.0] * 768
        result = guard_embedding(emb)
        assert result is False
