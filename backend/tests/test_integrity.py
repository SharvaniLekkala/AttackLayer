"""
test_integrity.py — Unit tests for Model Integrity verification.
"""

import sys
import os
import json
import tempfile
import hashlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_models_dir(tmp_path):
    """Create a temporary models directory with fake model files."""
    models_dir = tmp_path / "ml" / "models"
    models_dir.mkdir(parents=True)

    # Create fake model files
    for name in ["svm.pkl", "xgboost.pkl", "lightgbm.pkl", "mlp.pth"]:
        fake_content = f"fake-model-content-{name}".encode()
        (models_dir / name).write_bytes(fake_content)

    return models_dir


class TestHashGeneration:
    """Tests for SHA-256 hash computation."""

    def test_calculate_sha256_known(self, tmp_path):
        """Verify hash matches Python's hashlib on the same content."""
        from app.security.model_integrity import calculate_sha256

        test_file = tmp_path / "test.bin"
        content = b"hello world test content"
        test_file.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()
        actual = calculate_sha256(str(test_file))
        assert actual == expected

    def test_calculate_sha256_missing_file(self):
        from app.security.model_integrity import calculate_sha256
        result = calculate_sha256("/nonexistent/path/to/model.pkl")
        assert result == ""

    def test_generate_model_hashes_creates_file(self, monkeypatch, temp_models_dir):
        """generate_model_hashes should create model_hashes.json."""
        import app.security.model_integrity as mi

        # Monkey-patch the MODELS_DIR and HASHES_FILE
        monkeypatch.setattr(mi, "MODELS_DIR", str(temp_models_dir))
        monkeypatch.setattr(mi, "HASHES_FILE", str(temp_models_dir / "model_hashes.json"))

        hashes = mi.generate_model_hashes()
        assert len(hashes) == 4
        assert os.path.exists(str(temp_models_dir / "model_hashes.json"))

        for name in ["svm", "xgboost", "lightgbm", "mlp"]:
            assert name in hashes
            assert len(hashes[name]) == 64  # SHA-256 hex length


class TestVerification:
    """Tests for verify_model()."""

    def test_verify_valid_model(self, monkeypatch, temp_models_dir):
        import app.security.model_integrity as mi

        monkeypatch.setattr(mi, "MODELS_DIR", str(temp_models_dir))
        monkeypatch.setattr(mi, "HASHES_FILE", str(temp_models_dir / "model_hashes.json"))

        # Generate hashes first
        mi.generate_model_hashes()

        # All models should pass
        for name in ["svm", "xgboost", "lightgbm", "mlp"]:
            assert mi.verify_model(name) is True

    def test_verify_tampered_model(self, monkeypatch, temp_models_dir):
        import app.security.model_integrity as mi

        monkeypatch.setattr(mi, "MODELS_DIR", str(temp_models_dir))
        monkeypatch.setattr(mi, "HASHES_FILE", str(temp_models_dir / "model_hashes.json"))

        # Generate hashes, then tamper with a file
        mi.generate_model_hashes()
        (temp_models_dir / "svm.pkl").write_bytes(b"TAMPERED CONTENT")

        assert mi.verify_model("svm") is False
        # Others should still pass
        assert mi.verify_model("xgboost") is True

    def test_get_compromised_models(self, monkeypatch, temp_models_dir):
        import app.security.model_integrity as mi

        monkeypatch.setattr(mi, "MODELS_DIR", str(temp_models_dir))
        monkeypatch.setattr(mi, "HASHES_FILE", str(temp_models_dir / "model_hashes.json"))

        mi.generate_model_hashes()
        (temp_models_dir / "lightgbm.pkl").write_bytes(b"TAMPERED")
        (temp_models_dir / "mlp.pth").write_bytes(b"TAMPERED")

        compromised = mi.get_compromised_models()
        assert "lightgbm" in compromised
        assert "mlp" in compromised
        assert "svm" not in compromised
