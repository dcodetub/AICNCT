"""
train_model.py
--------------
Trains an XGBoost classifier to predict whether a long trade will hit
its target within HOLD_DAYS. Saves the trained model to MODEL_PATH.
"""

import logging
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from data_utils import fetch_data
from features import add_features
from labeling import create_labels
from config import STOCK_LIST, TRAIN_END, TEST_END, MODEL_PATH, FEATURE_COLS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def process_stock(stock: str) -> pd.DataFrame | None:
    """Fetch, engineer features, and label data for a single stock.

    Args:
        stock: Ticker symbol.

    Returns:
        Processed DataFrame with feature columns and 'label', or None on failure.
    """
    df = fetch_data(stock)
    if df is None:
        return None
    df = add_features(df)
    df = create_labels(df)
    df["symbol"] = stock
    return df


def prepare_data() -> pd.DataFrame:
    """Fetch and process all stocks, returning a combined DataFrame.

    Returns:
        Concatenated DataFrame across all stocks in STOCK_LIST.

    Raises:
        ValueError: If no valid data could be loaded for any stock.
    """
    all_data = []
    for stock in STOCK_LIST:
        df = process_stock(stock)
        if df is not None:
            all_data.append(df)
        else:
            logger.warning("Skipping %s — could not load data.", stock)

    if not all_data:
        raise ValueError("No data loaded for any stock. Check STOCK_LIST and network.")

    return pd.concat(all_data)


def train() -> None:
    """Train the XGBoost model on TRAIN_END data, evaluate on TEST_END, and save."""
    df = prepare_data()

    train_df = df[df.index <= TRAIN_END]
    test_df  = df[(df.index > TRAIN_END) & (df.index <= TEST_END)]

    X_train, y_train = train_df[FEATURE_COLS], train_df["label"]
    X_test,  y_test  = test_df[FEATURE_COLS],  test_df["label"]

    logger.info("Training on %d samples, evaluating on %d samples.", len(X_train), len(X_test))

    model = XGBClassifier(
        max_depth=4,
        learning_rate=0.05,
        n_estimators=300,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        # Note: use_label_encoder removed — deprecated and removed in recent XGBoost versions
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    joblib.dump(model, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)


if __name__ == "__main__":
    train()
