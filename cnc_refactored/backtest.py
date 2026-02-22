"""
backtest.py
-----------
Simulates the trading strategy on historical data using a trained model.
Reports trade count, win rate, and total return.
"""

import logging
import pandas as pd
from data_utils import fetch_data
from features import add_features
from labeling import create_labels
from trade_utils import simulate_trade
from model_utils import load_model
from config import STOCK_LIST, FEATURE_COLS, TARGET_PCT, STOP_PCT, HOLD_DAYS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SIGNAL_THRESHOLD = 0.65


def backtest() -> None:
    """Run a historical backtest across all stocks in STOCK_LIST.

    For each bar where the model predicts probability >= SIGNAL_THRESHOLD,
    simulates a trade and accumulates P&L. Prints a summary at the end.
    """
    model = load_model()

    total_return = 0.0
    trades = 0
    wins = 0

    for stock in STOCK_LIST:
        df = fetch_data(stock)
        if df is None:
            logger.warning("Skipping %s — no data.", stock)
            continue

        df = add_features(df)
        df = create_labels(df)

        probs = model.predict_proba(df[FEATURE_COLS])[:, 1]

        for i in range(len(df) - HOLD_DAYS - 1):
            if probs[i] >= SIGNAL_THRESHOLD:
                label, pnl = simulate_trade(df, i)
                trades += 1
                total_return += pnl
                if label == 1:
                    wins += 1

    win_rate = wins / trades if trades > 0 else 0.0
    logger.info("─── Backtest Results ───────────────────────────")
    logger.info("Trades      : %d", trades)
    logger.info("Win Rate    : %.2f%%", win_rate * 100)
    logger.info("Total Return: %.2f%%", total_return * 100)


if __name__ == "__main__":
    backtest()
