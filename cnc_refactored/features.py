"""
features.py
-----------
Technical indicator feature engineering for the CNC AI trading system.
"""

import logging
import pandas as pd
import ta

logger = logging.getLogger(__name__)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute technical indicator features and append them to the DataFrame.

    Works on a copy of the input — does NOT mutate the original.

    Args:
        df: OHLCV DataFrame with columns: Open, High, Low, Close, Volume.

    Returns:
        A new DataFrame with additional feature columns:
          - ema20, ema50: exponential moving averages
          - atr: average true range
          - rsi: relative strength index
          - close_ema20_ratio: Close / EMA20 (trend proximity)
          - ema20_ema50_diff: (EMA20 - EMA50) / EMA50 (trend direction)
          - atr_pct: ATR / Close (normalised volatility)
          - vol_ratio: Volume / 10-day rolling mean volume (volume surge)
        Rows with NaN values (from indicator warm-up) are dropped.
    """
    df = df.copy()

    df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["atr"]   = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)
    df["rsi"]   = ta.momentum.rsi(df["Close"], window=14)

    df["close_ema20_ratio"] = df["Close"] / df["ema20"]
    df["ema20_ema50_diff"]  = (df["ema20"] - df["ema50"]) / df["ema50"]
    df["atr_pct"]           = df["atr"] / df["Close"]
    df["vol_ratio"]         = df["Volume"] / df["Volume"].rolling(10).mean()

    before = len(df)
    df.dropna(inplace=True)
    logger.debug("add_features: dropped %d warm-up rows, %d remaining", before - len(df), len(df))

    return df
