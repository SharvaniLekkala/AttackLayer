"""
dataset_guard.py — Dataset Poisoning Defense for AttackLayer.

Uses IsolationForest + StandardScaler to detect and filter poisoned
or anomalous training samples before they reach the model-training
pipeline.

Public API
----------
train_guard(X)              → fit guard on known-clean data
detect_poisoning(X)         → boolean mask (True = suspicious)
filter_dataset(X, y=None)   → return cleaned X (and y)
"""

import os
import json
import logging
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Persist trained guard artefacts alongside the data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARD_DIR = os.path.join(BASE_DIR, "data", "guard")
GUARD_SCALER_PATH = os.path.join(GUARD_DIR, "guard_scaler.pkl")
GUARD_MODEL_PATH = os.path.join(GUARD_DIR, "guard_iforest.pkl")
GUARD_STATE_FILE = os.path.join(GUARD_DIR, "guard_state.json")


def _ensure_dir():
    os.makedirs(GUARD_DIR, exist_ok=True)


def _load_state() -> dict:
    if os.path.exists(GUARD_STATE_FILE):
        try:
            with open(GUARD_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"trained": False}


def _save_state(state: dict):
    _ensure_dir()
    with open(GUARD_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Public API ──────────────────────────────────────────────────────────
def train_guard(X: np.ndarray, contamination: float = 0.01):
    """Fit an IsolationForest on *known-clean* data.

    Persists the scaler and model to disk so subsequent calls to
    ``detect_poisoning`` and ``filter_dataset`` can reuse them without
    retraining.
    """
    _ensure_dir()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    # Persist using joblib (much more reliable than JSON for sklearn objects)
    joblib.dump(scaler, GUARD_SCALER_PATH)
    joblib.dump(model, GUARD_MODEL_PATH)
    _save_state({"trained": True, "n_samples": int(X.shape[0])})

    logger.info(
        "Dataset guard trained on %d samples (contamination=%.3f).",
        X.shape[0],
        contamination,
    )
    return model, scaler


def _load_guard():
    """Load persisted scaler + IsolationForest, or return None."""
    state = _load_state()
    if not state.get("trained"):
        return None, None
    try:
        scaler = joblib.load(GUARD_SCALER_PATH)
        model = joblib.load(GUARD_MODEL_PATH)
        return model, scaler
    except Exception as e:
        logger.warning("Failed to reload guard artefacts: %s", e)
        return None, None


def detect_poisoning(X: np.ndarray) -> np.ndarray:
    """Return a boolean mask where ``True`` = suspicious/poisoned sample.

    If the guard has not been trained yet, it will train on the supplied
    data first (treating it as mostly clean with 1 % contamination).
    """
    model, scaler = _load_guard()
    if model is None or scaler is None:
        logger.info("Guard not trained yet — training on supplied data.")
        model, scaler = train_guard(X)

    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)  # -1 = outlier, 1 = inlier
    return preds == -1


def filter_dataset(X: np.ndarray, y: np.ndarray = None):
    """Remove poisoned/outlier samples from X (and y if provided)."""
    mask = detect_poisoning(X)
    n_removed = int(np.sum(mask))
    logger.info("Dataset guard removed %d / %d suspicious samples.", n_removed, X.shape[0])

    clean_X = X[~mask]
    if y is None:
        return clean_X
    return clean_X, y[~mask]
