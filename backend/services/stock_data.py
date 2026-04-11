# services/stock_data.py
import yfinance as yf
import pandas as pd
from typing import Optional

# Common NSE tickers map (company name → ticker)
TICKER_MAP = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "wipro": "WIPRO.NS",
    "sbi": "SBIN.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "asian paints": "ASIANPAINT.NS",
    "hul": "HINDUNILVR.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "kotak mahindra": "KOTAKBANK.NS",
    "larsen": "LT.NS",
    "l&t": "LT.NS",
    "maruti": "MARUTI.NS",
    "nestle": "NESTLEIND.NS",
    "ongc": "ONGC.NS",
    "power grid": "POWERGRID.NS",
    "sun pharma": "SUNPHARMA.NS",
    "tata motors": "TATAMOTORS.NS",
    "tata steel": "TATASTEEL.NS",
    "tech mahindra": "TECHM.NS",
    "titan": "TITAN.NS",
    "ultracemco": "ULTRACEMCO.NS",
    "upl": "UPL.NS",
    "nifty 50": "^NSEI",
    "nifty": "^NSEI",
    "sensex": "^BSESN",
    "bse": "^BSESN",
}

def resolve_ticker(query: str) -> Optional[str]:
    """Map a company name or raw ticker to yfinance ticker string."""
    q = query.lower().strip()
    
    # Direct map lookup
    if q in TICKER_MAP:
        return TICKER_MAP[q]
    
    # Partial match
    for key, val in TICKER_MAP.items():
        if q in key or key in q:
            return val
    
    # Assume user passed raw ticker — try both NSE and BSE
    upper = query.upper()
    if not upper.endswith(".NS") and not upper.endswith(".BO"):
        return upper + ".NS"  # default to NSE
    return upper


def fetch_ohlcv(ticker: str, period: str = "6mo", interval: str = "1d") -> dict:
    """
    Fetch OHLCV data from yfinance.
    period options: 1mo, 3mo, 6mo, 1y, 2y
    interval options: 1d, 1wk, 1mo
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            return {"error": f"No data found for ticker: {ticker}"}
        
        df.index = df.index.strftime("%Y-%m-%d")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df.round(2)
        
        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "data": df.reset_index().rename(columns={"Date": "date"}).to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_stock_info(ticker: str) -> dict:
    """Fetch basic stock metadata — name, sector, market cap etc."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", None),
            "current_price": info.get("currentPrice", None),
            "52w_high": info.get("fiftyTwoWeekHigh", None),
            "52w_low": info.get("fiftyTwoWeekLow", None),
            "pe_ratio": info.get("trailingPE", None),
            "currency": info.get("currency", "INR"),
        }
    except Exception as e:
        return {"error": str(e)}