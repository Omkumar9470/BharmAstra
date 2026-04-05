# services/technical.py
import math
import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from services.stock_data import fetch_ohlcv


def compute_indicators(ticker: str, period: str = "6mo") -> dict:
    raw = fetch_ohlcv(ticker, period=period, interval="1d")
    if "error" in raw:
        return raw

    df = pd.DataFrame(raw["data"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

    df["rsi"]         = RSIIndicator(close=close, window=14).rsi()
    
    macd              = MACD(close=close)
    df["macd"]        = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"]   = macd.macd_diff()

    bb                = BollingerBands(close=close, window=20, window_dev=2)
    df["bb_upper"]    = bb.bollinger_hband()
    df["bb_lower"]    = bb.bollinger_lband()
    df["bb_mid"]      = bb.bollinger_mavg()
    df["bb_pct"]      = bb.bollinger_pband()

    df["ema_20"]      = EMAIndicator(close=close, window=20).ema_indicator()
    df["ema_50"]      = EMAIndicator(close=close, window=50).ema_indicator()
    df["sma_200"]     = SMAIndicator(close=close, window=200).sma_indicator()

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    numeric_cols = df.select_dtypes(include=["float64", "float32"]).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    # Convert to records then sanitize NaN at Python level
    records = df.reset_index(drop=True).to_dict(orient="records")
    
    def sanitize(record):
        return {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in record.items()
        }
    
    records = [sanitize(r) for r in records]

    return {
        "ticker": ticker,
        "indicators": records
    }


def safe(val, default=None):
    """Return default if value is None or NaN."""
    if val is None:
        return default
    try:
        if np.isnan(val):
            return default
    except Exception:
        pass
    return val


def generate_signals(ticker: str, period: str = "6mo") -> dict:
    result = compute_indicators(ticker, period)
    if "error" in result:
        return result

    latest = result["indicators"][-1]
    prev   = result["indicators"][-2] if len(result["indicators"]) > 1 else latest

    signals = []
    score   = 0.0
    total   = 0

    # --- RSI ---
    rsi_val = safe(latest.get("rsi"))
    if rsi_val is not None:
        if rsi_val < 30:
            signals.append({"indicator": "RSI", "signal": "BUY",
                            "reason": f"RSI {rsi_val} is oversold (< 30)", "weight": 1})
            score += 1
        elif rsi_val > 70:
            signals.append({"indicator": "RSI", "signal": "SELL",
                            "reason": f"RSI {rsi_val} is overbought (> 70)", "weight": 1})
            score -= 1
        else:
            signals.append({"indicator": "RSI", "signal": "NEUTRAL",
                            "reason": f"RSI {rsi_val} is in neutral zone (30–70)", "weight": 0})
        total += 1

    # --- MACD ---
    macd_diff      = safe(latest.get("macd_diff"))
    prev_macd_diff = safe(prev.get("macd_diff"))
    if macd_diff is not None and prev_macd_diff is not None:
        if macd_diff > 0 and prev_macd_diff <= 0:
            signals.append({"indicator": "MACD", "signal": "BUY",
                            "reason": "MACD bullish crossover detected", "weight": 1.5})
            score += 1.5
        elif macd_diff < 0 and prev_macd_diff >= 0:
            signals.append({"indicator": "MACD", "signal": "SELL",
                            "reason": "MACD bearish crossover detected", "weight": 1.5})
            score -= 1.5
        elif macd_diff > 0:
            signals.append({"indicator": "MACD", "signal": "BUY",
                            "reason": "MACD histogram is positive", "weight": 0.5})
            score += 0.5
        else:
            signals.append({"indicator": "MACD", "signal": "SELL",
                            "reason": "MACD histogram is negative", "weight": 0.5})
            score -= 0.5
        total += 1.5

    # --- Bollinger Bands ---
    bb_pct = safe(latest.get("bb_pct"))
    close  = safe(latest.get("Close"))
    if bb_pct is not None:
        if bb_pct < 0.05:
            signals.append({"indicator": "Bollinger Bands", "signal": "BUY",
                            "reason": "Price near lower band — potential reversal", "weight": 1})
            score += 1
        elif bb_pct > 0.95:
            signals.append({"indicator": "Bollinger Bands", "signal": "SELL",
                            "reason": "Price near upper band — potential pullback", "weight": 1})
            score -= 1
        else:
            signals.append({"indicator": "Bollinger Bands", "signal": "NEUTRAL",
                            "reason": "Price inside Bollinger Bands", "weight": 0})
        total += 1

    # --- EMA Cross ---
    ema20      = safe(latest.get("ema_20"))
    ema50      = safe(latest.get("ema_50"))
    prev_ema20 = safe(prev.get("ema_20"))
    prev_ema50 = safe(prev.get("ema_50"))
    if all(v is not None for v in [ema20, ema50, prev_ema20, prev_ema50]):
        if ema20 > ema50 and prev_ema20 <= prev_ema50:
            signals.append({"indicator": "EMA Cross", "signal": "BUY",
                            "reason": "EMA 20 crossed above EMA 50 (golden cross)", "weight": 2})
            score += 2
        elif ema20 < ema50 and prev_ema20 >= prev_ema50:
            signals.append({"indicator": "EMA Cross", "signal": "SELL",
                            "reason": "EMA 20 crossed below EMA 50 (death cross)", "weight": 2})
            score -= 2
        elif ema20 > ema50:
            signals.append({"indicator": "EMA Cross", "signal": "BUY",
                            "reason": "EMA 20 is above EMA 50 — uptrend", "weight": 0.5})
            score += 0.5
        else:
            signals.append({"indicator": "EMA Cross", "signal": "SELL",
                            "reason": "EMA 20 is below EMA 50 — downtrend", "weight": 0.5})
            score -= 0.5
        total += 2

    # --- SMA 200 ---
    sma200 = safe(latest.get("sma_200"))
    if sma200 is not None and close is not None:
        if close > sma200:
            signals.append({"indicator": "SMA 200", "signal": "BUY",
                            "reason": "Price above 200 SMA — long-term uptrend", "weight": 1})
            score += 1
        else:
            signals.append({"indicator": "SMA 200", "signal": "SELL",
                            "reason": "Price below 200 SMA — long-term downtrend", "weight": 1})
            score -= 1
        total += 1

    max_possible     = total if total > 0 else 1
    normalized_score = round(score / max_possible, 3)
    normalized_score = max(-1.0, min(1.0, normalized_score))

    if normalized_score >= 0.4:
        bias = "BULLISH"
    elif normalized_score <= -0.4:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    return {
        "ticker": ticker,
        "date": latest.get("date"),
        "close": close,
        "technical_score": normalized_score,
        "bias": bias,
        "signals": signals,
        "latest_indicators": {
            "rsi": rsi_val,
            "macd_diff": macd_diff,
            "bb_pct": bb_pct,
            "ema_20": ema20,
            "ema_50": ema50,
            "sma_200": sma200,
        }
    }