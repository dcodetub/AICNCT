"""
labeling.py
-----------
Generates binary trade labels for supervised learning.
Label = 1 if a long trade hits the target within HOLD_DAYS, else 0.
"""

import logging
import pandas as pd
from trade_utils import simulate_trade
from config import HOLD_DAYS

logger = logging.getLogger(__name__)


def create_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Attach binary trade outcome labels to each bar in the DataFrame.

    For each bar i, simulates a long entry at bar i+1 Open and checks
    whether the target or stop is hit within HOLD_DAYS bars.

    Works on a copy — does NOT mutate the original DataFrame.

    Args:
        df: OHLCV DataFrame (must have Open, High, Low columns).
            Requires at least HOLD_DAYS + 2 rows.

    Returns:
        A copy of df truncated to the labellable range, with a new
        'label' column (int): 1 = target hit, 0 = stop hit or expired.
    """
    df = df.copy()
    n = len(df) - HOLD_DAYS - 1

    if n <= 0:
        logger.warning("create_labels: DataFrame too short to label (%d rows). Returning empty.", len(df))
        return df.iloc[0:0]

    labels = []
    for i in range(n):
        label, _ = simulate_trade(df, i)
        labels.append(label)

    # Explicitly truncate to match label length — documented intentional behaviour
    df = df.iloc[:n].copy()
    df["label"] = labels

    logger.info("create_labels: generated %d labels (%d positive)", n, sum(labels))
    return df
