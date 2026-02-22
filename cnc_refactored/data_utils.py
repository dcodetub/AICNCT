"""
data_utils.py
-------------
Fetches OHLCV price data from Yahoo Finance.
"""

import logging
import pandas as pd
import yfinance as yf
from config import START_DATE, END_DATE

logger = logging.getLogger(__name__)


def fetch_data(symbol: str) -> pd.DataFrame | None:
    """Download historical OHLCV data for a symbol via yfinance.

    Args:
        symbol: Ticker symbol (e.g. 'RELIANCE.NS').

    Returns:
        A cleaned DataFrame indexed by date, or None if the download
        fails or returns no data.
    """
    try:
        df = yf.download(symbol, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)
    except Exception as e:
        logger.error("Failed to download data for %s: %s", symbol, e)
        return None

    if df.empty:
        logger.warning("No data returned for symbol '%s'. Skipping.", symbol)
        return None

    df.dropna(inplace=True)

    if len(df) == 0:
        logger.warning("All rows dropped after NaN removal for '%s'. Skipping.", symbol)
        return None

    logger.info("Fetched %d rows for %s", len(df), symbol)
    return df
