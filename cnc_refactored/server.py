"""
server.py
---------
Local Flask server that powers the CNC AI Trading System browser dashboard.
Started automatically by launch.bat — do not run directly unless debugging.
"""

import logging
import os
import sys
import threading
import webbrowser
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import STOCK_LIST, FEATURE_COLS, MODEL_PATH
from data_utils import fetch_data
from features import add_features
from labeling import create_labels
from model_utils import load_model
from trade_utils import simulate_trade

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "gui"))
CORS(app)

SIGNAL_THRESHOLD = 0.65


# ── API routes ─────────────────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    model_ready = os.path.exists(os.path.join(BASE_DIR, MODEL_PATH))
    return jsonify({"status": "ok", "model_ready": model_ready})


@app.route("/api/train", methods=["POST"])
def train():
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "train_model.py")],
            capture_output=True, text=True, cwd=BASE_DIR
        )
        if result.returncode != 0:
            return jsonify({"success": False, "error": result.stderr[-2000:]}), 500
        return jsonify({"success": True, "output": result.stdout[-2000:]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/signals")
def signals():
    try:
        model = load_model(os.path.join(BASE_DIR, MODEL_PATH))
        results = []
        for stock in STOCK_LIST:
            df = fetch_data(stock)
            if df is None:
                results.append({"symbol": stock, "error": "No data"})
                continue
            df = add_features(df)
            latest = df.iloc[-1:]
            prob = float(model.predict_proba(latest[FEATURE_COLS])[:, 1][0])
            results.append({
                "symbol": stock,
                "probability": round(prob, 4),
                "signal": "BUY" if prob >= SIGNAL_THRESHOLD else "HOLD",
                "rsi": round(float(latest["rsi"].iloc[0]), 2),
                "atr_pct": round(float(latest["atr_pct"].iloc[0]) * 100, 3),
                "vol_ratio": round(float(latest["vol_ratio"].iloc[0]), 2),
            })
        return jsonify({"success": True, "signals": results})
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.exception("signals error")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/backtest")
def backtest():
    try:
        model = load_model(os.path.join(BASE_DIR, MODEL_PATH))
        total_return = 0.0
        trades = 0
        wins = 0
        per_stock = []

        for stock in STOCK_LIST:
            df = fetch_data(stock)
            if df is None:
                continue
            df = add_features(df)
            df = create_labels(df)
            probs = model.predict_proba(df[FEATURE_COLS])[:, 1]

            s_trades, s_wins, s_return = 0, 0, 0.0
            for i in range(len(df) - 6):
                if probs[i] >= SIGNAL_THRESHOLD:
                    label, pnl = simulate_trade(df, i)
                    s_trades += 1
                    s_return += pnl
                    if label == 1:
                        s_wins += 1

            trades += s_trades
            wins += s_wins
            total_return += s_return
            per_stock.append({
                "symbol": stock,
                "trades": s_trades,
                "wins": s_wins,
                "win_rate": round(s_wins / s_trades * 100, 1) if s_trades else 0,
                "total_return": round(s_return * 100, 2),
            })

        return jsonify({
            "success": True,
            "summary": {
                "trades": trades,
                "wins": wins,
                "win_rate": round(wins / trades * 100, 1) if trades else 0,
                "total_return": round(total_return * 100, 2),
            },
            "per_stock": per_stock,
        })
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.exception("backtest error")
        return jsonify({"success": False, "error": str(e)}), 500


# ── Serve GUI ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "gui"), "index.html")


# ── Launch ─────────────────────────────────────────────────────────────────────



if __name__ == "__main__":
    logger.info("Starting CNC AI Trading System dashboard at http://localhost:5000")
    # Browser is opened by LAUNCH.bat after server is ready
    app.run(host="127.0.0.1", port=5000, debug=False)
