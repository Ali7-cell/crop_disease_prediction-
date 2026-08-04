"""
ML Model Loader — loads all pkl files once at application startup
and caches them in memory. Models are never reloaded per-request.

Usage:
    from app.utils.model_loader import ml_models

    pipeline = ml_models["crop_pipeline"]
    encoder  = ml_models["crop_label_encoder"]
"""

import os
import logging

import joblib

logger = logging.getLogger("agrilux.model_loader")

# Global in-memory cache for loaded models
ml_models: dict = {}

# Path to the models directory (relative to project root)
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


def load_models() -> None:
    """
    Load all ML models from disk into memory.
    Called once at application startup via the lifespan handler.
    """
    model_files = {
        "crop_pipeline": "crop_pipeline.pkl",
        "crop_label_encoder": "crop_label_encoder.pkl",
        "fertilizer_pipeline": "fertilizer_pipeline.pkl",
        "fertilizer_label_encoder": "fertilizer_label_encoder.pkl",
        "yield_pipeline": "yield_pipeline.pkl",
    }

    for key, filename in model_files.items():
        filepath = os.path.join(MODELS_DIR, filename)
        logger.info("Loading model: %s from %s", key, filepath)

        if not os.path.exists(filepath):
            logger.error("Model file not found: %s", filepath)
            raise FileNotFoundError(
                f"Required model file not found: {filepath}. "
                "Ensure all .pkl files are in app/models/"
            )

        ml_models[key] = joblib.load(filepath)
        logger.info("✓ Loaded %s successfully", key)

    logger.info("All %d models loaded into memory", len(ml_models))
