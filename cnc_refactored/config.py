import os

# ── Date ranges ────────────────────────────────────────────────────────────────
START_DATE = "2019-01-01"
END_DATE   = "2024-12-31"

TRAIN_END  = "2022-12-31"
TEST_END   = "2023-12-31"

# ── Trade parameters ───────────────────────────────────────────────────────────
TARGET_PCT = 0.03
STOP_PCT   = 0.02
HOLD_DAYS  = 5

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_PATH = "xgb_model.pkl"

# ── Universe ───────────────────────────────────────────────────────────────────
STOCK_LIST = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "TCS.NS",
]

# ── Feature columns (single source of truth — used by train, backtest, main) ──
FEATURE_COLS = [
    "close_ema20_ratio",
    "ema20_ema50_diff",
    "atr_pct",
    "rsi",
    "vol_ratio",
]
