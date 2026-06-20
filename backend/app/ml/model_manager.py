"""
model_manager.py — Self-Healing Model Manager for AttackLayer.

Loads all four models (SVM, XGBoost, LightGBM, MLP) on import,
verifies SHA-256 integrity, and attempts automatic recovery from
a local backup registry if tampering is detected.

Public API
----------
get_model(name)         → return a single model instance (lazy-loads if needed)
get_active_models()     → list of model names that pass integrity
load_all_models()       → dict {name: model_instance}
reload_models_if_needed() → periodic health check
SimpleMLP               → re-exported so benchmark_models.py can import it
"""

import os
import logging
import torch
import joblib
from typing import Dict, Optional

from app.security.model_integrity import verify_model, generate_model_hashes

logger = logging.getLogger(__name__)

# ── paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
# Local backup folder for self-healing; could be swapped for a remote URL
REGISTRY_DIR = os.path.join(BASE_DIR, "model_registry")

ALL_MODEL_NAMES = ["svm", "xgboost", "lightgbm", "mlp"]


# ── SimpleMLP definition (must match train_mlp.py) ──────────────────────
class SimpleMLP(torch.nn.Module):
    """Lightweight binary classifier matching the architecture in train_mlp.py."""

    def __init__(self, input_dim: int = 768, hidden_dim: int = 128, dropout_rate: float = 0.3):
        super().__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(hidden_dim),
            torch.nn.Dropout(dropout_rate),
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(hidden_dim // 2),
            torch.nn.Dropout(dropout_rate),
            torch.nn.Linear(hidden_dim // 2, 2),
        )

    def forward(self, x):
        return self.network(x)


# ── Internal model cache ────────────────────────────────────────────────
_model_cache: Dict[str, object] = {}


# ── Loaders ─────────────────────────────────────────────────────────────
def _load_single_model(model_name: str):
    """Deserialize one model from disk and return the instance."""
    if model_name == "mlp":
        # MLP is saved as a state_dict (.pth)
        pth_path = os.path.join(MODELS_DIR, "mlp.pth")
        pt_path = os.path.join(MODELS_DIR, "mlp.pt")
        path = pth_path if os.path.exists(pth_path) else pt_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"MLP model file not found at {pth_path} or {pt_path}")
        state = torch.load(path, map_location="cpu")
        # Infer input dim from the first Linear layer weight
        first_weight = next(iter(state.values()))
        input_dim = first_weight.shape[1]
        model = SimpleMLP(input_dim=input_dim)
        model.load_state_dict(state)
        model.eval()
        return model
    else:
        pkl_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
        if not os.path.exists(pkl_path):
            raise FileNotFoundError(f"Model file not found: {pkl_path}")
        return joblib.load(pkl_path)


def _try_restore_from_backup(model_name: str):
    """Copy the backup model over the primary and reload."""
    ext = "pth" if model_name == "mlp" else "pkl"
    backup_path = os.path.join(REGISTRY_DIR, f"{model_name}.{ext}")
    if not os.path.exists(backup_path):
        raise FileNotFoundError(
            f"No backup found for {model_name} in {REGISTRY_DIR}"
        )
    os.makedirs(MODELS_DIR, exist_ok=True)
    dest_path = os.path.join(MODELS_DIR, f"{model_name}.{ext}")
    with open(backup_path, "rb") as src, open(dest_path, "wb") as dst:
        dst.write(src.read())
    logger.info("Restored %s from registry backup.", model_name)
    # After restore, regenerate hashes so future checks pass
    generate_model_hashes()
    return _load_single_model(model_name)


# ── Public API ──────────────────────────────────────────────────────────
def get_model(name: str) -> Optional[object]:
    """Return a model instance by name. Loads from cache or disk.

    If the model fails the integrity check and a backup exists in the
    registry, the manager will attempt automatic recovery.
    """
    if name in _model_cache:
        return _model_cache[name]

    try:
        if not verify_model(name):
            logger.warning("Integrity check FAILED for %s — attempting recovery.", name)
            model = _try_restore_from_backup(name)
        else:
            model = _load_single_model(name)
        _model_cache[name] = model
        return model
    except Exception as e:
        logger.error("Failed to load model %s: %s", name, e)
        return None


def get_active_models() -> list:
    """Return names of models that are currently loadable and healthy."""
    active = []
    for name in ALL_MODEL_NAMES:
        try:
            if verify_model(name):
                active.append(name)
            else:
                logger.warning("Model %s failed integrity check — excluded.", name)
        except Exception:
            continue
    return active


def load_all_models(active_models: list = None) -> Dict[str, object]:
    """Load (and cache) all requested models, verifying integrity first."""
    if active_models is None:
        active_models = list(ALL_MODEL_NAMES)
    models = {}
    for name in active_models:
        m = get_model(name)
        if m is not None:
            models[name] = m
    return models


def reload_models_if_needed():
    """Periodic health-check: reload any models that have gone bad."""
    healthy = get_active_models()
    unhealthy = set(ALL_MODEL_NAMES) - set(healthy)
    if unhealthy:
        logger.info("Unhealthy models detected: %s. Attempting recovery.", unhealthy)
        for name in unhealthy:
            try:
                _try_restore_from_backup(name)
            except Exception as e:
                logger.error("Recovery of %s failed: %s", name, e)
    else:
        logger.debug("All models passed integrity checks.")


def clear_cache():
    """Wipe the in-memory cache (useful for testing)."""
    _model_cache.clear()
