"""
tests/test_core.py
------------------
Unit tests for labeling, feature engineering, and trade simulation.
Run with: pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_ohlcv(n: int = 100, close: float = 100.0) -> pd.DataFrame:
    """Create a minimal synthetic OHLCV DataFrame for testing."""
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "Open":   [close] * n,
        "High":   [close * 1.05] * n,
        "Low":    [close * 0.95] * n,
        "Close":  [close] * n,
        "Volume": [1_000_000] * n,
    }, index=idx)


# ── trade_utils ────────────────────────────────────────────────────────────────

class TestSimulateTrade:
    def test_target_hit(self):
        """High well above target → label=1, pnl=+TARGET_PCT."""
        from trade_utils import simulate_trade
        from config import TARGET_PCT
        df = make_ohlcv(20, close=100.0)
        # Force high to smash through target
        df.loc[df.index[2], "High"] = 200.0
        label, pnl = simulate_trade(df, 0)
        assert label == 1
        assert abs(pnl - TARGET_PCT) < 1e-9

    def test_stop_hit(self):
        """Low well below stop → label=0, pnl=-STOP_PCT."""
        from trade_utils import simulate_trade
        from config import STOP_PCT
        df = make_ohlcv(20, close=100.0)
        df.loc[df.index[2], "Low"] = 1.0
        label, pnl = simulate_trade(df, 0)
        assert label == 0
        assert abs(pnl - (-STOP_PCT)) < 1e-9

    def test_expired_no_hit(self):
        """Neither target nor stop hit → label=0, pnl=0.0."""
        from trade_utils import simulate_trade
        df = make_ohlcv(20, close=100.0)
        # Flat price — no target/stop hit
        label, pnl = simulate_trade(df, 0)
        assert label == 0
        assert pnl == 0.0


# ── labeling ───────────────────────────────────────────────────────────────────

class TestCreateLabels:
    def test_output_length(self):
        """Output DataFrame should have len(df) - HOLD_DAYS - 1 rows."""
        from labeling import create_labels
        from config import HOLD_DAYS
        df = make_ohlcv(50)
        result = create_labels(df)
        assert len(result) == 50 - HOLD_DAYS - 1

    def test_label_column_exists(self):
        from labeling import create_labels
        df = make_ohlcv(50)
        result = create_labels(df)
        assert "label" in result.columns

    def test_label_values_binary(self):
        from labeling import create_labels
        df = make_ohlcv(50)
        result = create_labels(df)
        assert set(result["label"].unique()).issubset({0, 1})

    def test_does_not_mutate_input(self):
        """create_labels must not modify the original DataFrame."""
        from labeling import create_labels
        df = make_ohlcv(50)
        original_len = len(df)
        original_cols = list(df.columns)
        create_labels(df)
        assert len(df) == original_len
        assert list(df.columns) == original_cols

    def test_too_short_returns_empty(self):
        from labeling import create_labels
        df = make_ohlcv(3)
        result = create_labels(df)
        assert len(result) == 0


# ── features ───────────────────────────────────────────────────────────────────

class TestAddFeatures:
    def test_feature_columns_present(self):
        from features import add_features
        from config import FEATURE_COLS
        df = make_ohlcv(100)
        result = add_features(df)
        for col in FEATURE_COLS:
            assert col in result.columns, f"Missing feature: {col}"

    def test_does_not_mutate_input(self):
        from features import add_features
        df = make_ohlcv(100)
        original_cols = list(df.columns)
        add_features(df)
        assert list(df.columns) == original_cols

    def test_no_nans_in_output(self):
        from features import add_features
        from config import FEATURE_COLS
        df = make_ohlcv(100)
        result = add_features(df)
        assert result[FEATURE_COLS].isna().sum().sum() == 0
