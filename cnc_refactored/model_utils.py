"""
model_utils.py
--------------
Shared model loading helper used by main.py and backtest.py.
"""

import logging
import os
import joblib
from xgboost import XGBClassifier
from config import MODEL_PATH

logger = logging.getLogger(__name__)


def load_model(path: str = MODEL_PATH) -> XGBClassifier:
    """Load a trained XGBoost model from disk.

    Args:
        path: Path to the pickled model file. Defaults to MODEL_PATH from config.

    Returns:
        The loaded XGBClassifier.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model file not found at '{path}'. "
            "Run train_model.py first to generate it."
        )
    logger.info("Loading model from %s", path)
    return joblib.load(path)
