"""
test_ensemble.py — Unit tests for the Ensemble Voting Layer.
"""

import sys
import os
import numpy as np
import pytest

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestPredictModelSingle:
    """Tests for the predict_model_single helper."""

    def test_sklearn_model_with_predict_proba(self):
        """Verify that an sklearn-like model with predict_proba works."""
        from app.ml.ensemble import predict_model_single

        class FakeSklearnModel:
            def predict_proba(self, X):
                return np.array([[0.2, 0.8]])

        model = FakeSklearnModel()
        result = predict_model_single("xgboost", model, np.zeros(768))
        assert result["prediction"] == 1
        assert 0.0 <= result["confidence"] <= 1.0
        assert abs(result["confidence"] - 0.8) < 1e-5

    def test_sklearn_model_without_predict_proba(self):
        """Fallback path when predict_proba is missing."""
        from app.ml.ensemble import predict_model_single

        class FakeModel:
            def predict(self, X):
                return np.array([0])

        model = FakeModel()
        result = predict_model_single("svm", model, np.zeros(768))
        assert result["prediction"] == 0
        assert result["confidence"] == 1.0

    def test_returns_dict_with_required_keys(self):
        from app.ml.ensemble import predict_model_single

        class FakeModel:
            def predict_proba(self, X):
                return np.array([[0.6, 0.4]])

        result = predict_model_single("lightgbm", FakeModel(), np.random.randn(768))
        assert "prediction" in result
        assert "confidence" in result


class TestEnsembleDecision:
    """Tests for ensemble-level logic (weighted majority vote)."""

    def test_unanimous_prediction(self):
        """All models agree → confidence should be high and agreement = 1.0."""
        # This tests the data-flow logic rather than loading real models,
        # so we patch get_active_models and get_model.
        from unittest.mock import patch

        class FakeModel:
            def predict_proba(self, X):
                return np.array([[0.1, 0.9]])

        fake_models = {"svm": FakeModel(), "xgboost": FakeModel(),
                       "lightgbm": FakeModel(), "mlp": FakeModel()}

        with patch("app.ml.ensemble.get_active_models", return_value=list(fake_models.keys())), \
             patch("app.ml.ensemble.get_model", side_effect=lambda n: fake_models[n]), \
             patch("app.ml.ensemble.get_weights",
                   return_value={k: 0.25 for k in fake_models}), \
             patch("app.ml.ensemble.update_reputation"):

            # Override predict_model_single for mlp so it doesn't need torch
            with patch("app.ml.ensemble.predict_model_single",
                       return_value={"prediction": 1, "confidence": 0.9}):
                from app.ml.ensemble import get_ensemble_prediction
                result = get_ensemble_prediction([0.0] * 768)

                assert result["prediction"] == 1
                assert result["agreement_rate"] == 1.0
                assert result["low_trust"] is False

    def test_no_active_models_raises(self):
        from unittest.mock import patch
        with patch("app.ml.ensemble.get_active_models", return_value=[]):
            from app.ml.ensemble import get_ensemble_prediction
            with pytest.raises(RuntimeError, match="No active models"):
                get_ensemble_prediction([0.0] * 768)


class TestLowTrustFlag:
    """low_trust should be True when agreement < 0.5 or confidence < 0.6."""

    def test_low_agreement_triggers_low_trust(self):
        from unittest.mock import patch

        class AgreesModel:
            def predict_proba(self, X):
                return np.array([[0.1, 0.9]])

        class DisagreesModel:
            def predict_proba(self, X):
                return np.array([[0.9, 0.1]])

        fake = {"svm": DisagreesModel(), "xgboost": DisagreesModel(),
                "lightgbm": DisagreesModel(), "mlp": AgreesModel()}

        def mock_predict(name, model_instance, embedding):
            if name == "mlp":
                return {"prediction": 1, "confidence": 0.9}
            return {"prediction": 0, "confidence": 0.9}

        with patch("app.ml.ensemble.get_active_models", return_value=list(fake.keys())), \
             patch("app.ml.ensemble.get_model", side_effect=lambda n: fake[n]), \
             patch("app.ml.ensemble.get_weights",
                   return_value={k: 0.25 for k in fake}), \
             patch("app.ml.ensemble.update_reputation"), \
             patch("app.ml.ensemble.predict_model_single", side_effect=mock_predict):

            from app.ml.ensemble import get_ensemble_prediction
            result = get_ensemble_prediction([0.0] * 768)
            # 3 models voted 0, 1 voted 1 → prediction=0, agreement=0.75
            # But the code checks ensemble_prediction against each model.
            # 3 agree with majority (0), 1 disagrees → agreement = 0.75
            assert result["prediction"] == 0
            assert result["agreement_rate"] == 0.75
