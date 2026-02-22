"""
main.py
-------
Generates live buy signals for all stocks in STOCK_LIST using the
trained XGBoost model.
"""

import logging
from data_utils import fetch_data
from features import add_features
from model_utils import load_model
from config import STOCK_LIST, FEATURE_COLS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SIGNAL_THRESHOLD = 0.65


def generate_signals() -> None:
    """Load the trained model and print buy signals for the latest bar of each stock."""
    model = load_model()

    for stock in STOCK_LIST:
        df = fetch_data(stock)
        if df is None:
            logger.warning("Skipping %s — no data.", stock)
            continue

        df = add_features(df)
        latest = df.iloc[-1:]
        prob = model.predict_proba(latest[FEATURE_COLS])[:, 1][0]

        if prob >= SIGNAL_THRESHOLD:
            logger.info("BUY SIGNAL : %s | Probability: %.2f", stock, prob)
        else:
            logger.info("No trade   : %s | Probability: %.2f", stock, prob)


if __name__ == "__main__":
    generate_signals()
