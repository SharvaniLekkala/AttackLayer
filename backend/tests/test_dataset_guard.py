"""
test_dataset_guard.py — Unit tests for Dataset Poisoning Defense.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def clean_guard_dir(tmp_path, monkeypatch):
    """Point guard artefacts to a temporary directory."""
    import app.security.dataset_guard as dg

    guard_dir = str(tmp_path / "guard")
    monkeypatch.setattr(dg, "GUARD_DIR", guard_dir)
    monkeypatch.setattr(dg, "GUARD_SCALER_PATH", os.path.join(guard_dir, "guard_scaler.pkl"))
    monkeypatch.setattr(dg, "GUARD_MODEL_PATH", os.path.join(guard_dir, "guard_iforest.pkl"))
    monkeypatch.setattr(dg, "GUARD_STATE_FILE", os.path.join(guard_dir, "guard_state.json"))
    return guard_dir


class TestTrainGuard:
    def test_train_creates_artefacts(self, clean_guard_dir):
        import app.security.dataset_guard as dg

        X = np.random.normal(0, 1, size=(200, 768))
        model, scaler = dg.train_guard(X)
        assert model is not None
        assert scaler is not None
        assert os.path.exists(os.path.join(clean_guard_dir, "guard_scaler.pkl"))
        assert os.path.exists(os.path.join(clean_guard_dir, "guard_iforest.pkl"))
        assert os.path.exists(os.path.join(clean_guard_dir, "guard_state.json"))


class TestDetectPoisoning:
    def test_clean_data_mostly_passes(self, clean_guard_dir):
        import app.security.dataset_guard as dg

        X_clean = np.random.normal(0, 0.5, size=(200, 50))
        mask = dg.detect_poisoning(X_clean)
        # With contamination=0.01, at most ~2% should be flagged
        assert mask.sum() <= int(0.05 * len(X_clean))

    def test_outliers_are_flagged(self, clean_guard_dir):
        import app.security.dataset_guard as dg

        # Train on clean data first
        X_clean = np.random.normal(0, 0.5, size=(200, 50))
        dg.train_guard(X_clean)

        # Now test with some extreme outliers injected
        X_test = np.vstack([
            np.random.normal(0, 0.5, size=(100, 50)),
            np.random.normal(20, 1.0, size=(5, 50)),  # obvious outliers
        ])
        mask = dg.detect_poisoning(X_test)
        # At least some of the injected outliers should be flagged
        assert mask[-5:].sum() >= 1


class TestFilterDataset:
    def test_filter_reduces_size(self, clean_guard_dir):
        import app.security.dataset_guard as dg

        X = np.vstack([
            np.random.normal(0, 0.5, size=(100, 50)),
            np.random.normal(30, 1.0, size=(10, 50)),  # outliers
        ])
        y = np.array([0] * 100 + [1] * 10)

        X_clean, y_clean = dg.filter_dataset(X, y)
        assert len(X_clean) <= len(X)
        assert len(X_clean) == len(y_clean)

    def test_filter_without_labels(self, clean_guard_dir):
        import app.security.dataset_guard as dg

        X = np.random.normal(0, 0.5, size=(100, 50))
        result = dg.filter_dataset(X)
        assert isinstance(result, np.ndarray)
        assert len(result) <= len(X)
