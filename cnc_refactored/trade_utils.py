"""
trade_utils.py
--------------
Shared trade simulation logic used by both labeling.py and backtest.py.
Extracted to eliminate copy-paste duplication.
"""

import logging
import pandas as pd
from config import TARGET_PCT, STOP_PCT, HOLD_DAYS

logger = logging.getLogger(__name__)


def simulate_trade(df: pd.DataFrame, i: int) -> tuple[int, float]:
    """Simulate a single trade starting at bar index i.

    Enters at next bar's Open, then checks each subsequent bar for a
    target hit (+TARGET_PCT) or stop hit (-STOP_PCT) within HOLD_DAYS.

    Args:
        df: OHLCV DataFrame with at least HOLD_DAYS bars after index i.
        i:  Index of the signal bar. Entry is at bar i+1 Open.

    Returns:
        A tuple of (label, pnl) where:
          - label is 1 if target was hit, 0 otherwise.
          - pnl is +TARGET_PCT, -STOP_PCT, or 0.0 (held to expiry).
    """
    entry  = df["Open"].iloc[i + 1]
    target = entry * (1 + TARGET_PCT)
    stop   = entry * (1 - STOP_PCT)

    for j in range(1, HOLD_DAYS + 1):
        high = df["High"].iloc[i + j]
        low  = df["Low"].iloc[i + j]

        if low <= stop:
            return 0, -STOP_PCT

        if high >= target:
            return 1, TARGET_PCT

    return 0, 0.0
