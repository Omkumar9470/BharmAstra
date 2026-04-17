"""
BharmAstra — services/fundamental.py
Fundamental analysis engine for delivery/positional trading.
Pulls data via yfinance, scores on a 0–10 scale.
NaN-safe throughout (compatible with main.py SafeJSONResponse).
"""

import yfinance as yf
import math
from typing import Optional

# ---------------------------------------------------------------------------
# Sector PE benchmarks (NSE/BSE context, approximate)
# Used to judge whether a stock's PE is cheap/expensive relative to peers.
# ---------------------------------------------------------------------------
SECTOR_PE = {
    "Technology":           28.0,
    "Financial Services":   18.0,
    "Consumer Cyclical":    35.0,
    "Consumer Defensive":   40.0,
    "Healthcare":           30.0,
    "Energy":               12.0,
    "Basic Materials":      15.0,
    "Industrials":          25.0,
    "Utilities":            20.0,
    "Communication Services": 22.0,
    "Real Estate":          35.0,
    "Unknown":              25.0,   # fallback
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe(val, fallback=None):
    """Return val if it's a real finite number, else fallback."""
    if val is None:
        return fallback
    try:
        if math.isnan(val) or math.isinf(val):
            return fallback
    except TypeError:
        pass
    return val


def _pct(new_val, old_val) -> Optional[float]:
    """YoY percentage change, returns None if inputs are invalid."""
    n = _safe(new_val)
    o = _safe(old_val)
    if n is None or o is None or o == 0:
        return None
    return ((n - o) / abs(o)) * 100


# ---------------------------------------------------------------------------
# Sub-scorers  (each returns a score 0–10 and a human-readable note)
# ---------------------------------------------------------------------------

def _score_pe(pe: Optional[float], sector: str) -> tuple[float, str]:
    benchmark = SECTOR_PE.get(sector, SECTOR_PE["Unknown"])
    if pe is None:
        return 5.0, "PE not available — neutral score"
    if pe <= 0:
        return 3.0, f"Negative PE ({pe:.1f}) — loss-making or distorted"
    ratio = pe / benchmark
    if ratio <= 0.6:
        score, note = 10.0, f"PE {pe:.1f} is very cheap vs sector avg {benchmark:.1f}"
    elif ratio <= 0.85:
        score, note = 8.0, f"PE {pe:.1f} is below sector avg {benchmark:.1f} — attractive"
    elif ratio <= 1.10:
        score, note = 6.0, f"PE {pe:.1f} is near sector avg {benchmark:.1f} — fairly valued"
    elif ratio <= 1.40:
        score, note = 4.0, f"PE {pe:.1f} is above sector avg {benchmark:.1f} — slightly expensive"
    else:
        score, note = 2.0, f"PE {pe:.1f} is expensive vs sector avg {benchmark:.1f}"
    return score, note


def _score_revenue_growth(growth_pct: Optional[float]) -> tuple[float, str]:
    if growth_pct is None:
        return 5.0, "Revenue growth not available — neutral score"
    if growth_pct >= 25:
        return 10.0, f"Revenue grew strongly at {growth_pct:.1f}% YoY"
    elif growth_pct >= 15:
        return 8.0, f"Revenue grew well at {growth_pct:.1f}% YoY"
    elif growth_pct >= 8:
        return 6.5, f"Revenue grew moderately at {growth_pct:.1f}% YoY"
    elif growth_pct >= 0:
        return 5.0, f"Revenue growth was marginal at {growth_pct:.1f}% YoY"
    elif growth_pct >= -10:
        return 3.0, f"Revenue declined {growth_pct:.1f}% YoY — caution"
    else:
        return 1.0, f"Revenue fell sharply {growth_pct:.1f}% YoY — bearish"


def _score_profit_growth(growth_pct: Optional[float]) -> tuple[float, str]:
    if growth_pct is None:
        return 5.0, "Net profit growth not available — neutral score"
    if growth_pct >= 30:
        return 10.0, f"Net profit surged {growth_pct:.1f}% YoY"
    elif growth_pct >= 20:
        return 8.5, f"Strong net profit growth of {growth_pct:.1f}% YoY"
    elif growth_pct >= 10:
        return 7.0, f"Decent net profit growth of {growth_pct:.1f}% YoY"
    elif growth_pct >= 0:
        return 5.0, f"Marginal profit growth of {growth_pct:.1f}% YoY"
    elif growth_pct >= -15:
        return 3.0, f"Profit declined {growth_pct:.1f}% YoY"
    else:
        return 1.0, f"Profit fell sharply {growth_pct:.1f}% YoY — bearish"


def _score_debt_equity(de: Optional[float]) -> tuple[float, str]:
    if de is None:
        return 5.5, "Debt-to-Equity not available — neutral score"
    if de < 0:
        return 5.0, f"Negative D/E ({de:.2f}) — unusual, check balance sheet"
    if de <= 0.3:
        return 10.0, f"Very low debt (D/E={de:.2f}) — strong balance sheet"
    elif de <= 0.7:
        return 8.0, f"Low debt (D/E={de:.2f}) — healthy leverage"
    elif de <= 1.2:
        return 6.0, f"Moderate debt (D/E={de:.2f}) — acceptable"
    elif de <= 2.0:
        return 4.0, f"High debt (D/E={de:.2f}) — elevated risk"
    else:
        return 2.0, f"Very high debt (D/E={de:.2f}) — significant risk"


def _score_promoter_holding(holding_pct: Optional[float], change_pct: Optional[float]) -> tuple[float, str]:
    """
    holding_pct  : e.g. 52.3 means promoters hold 52.3% of shares
    change_pct   : change from previous quarter (positive = increasing)
    """
    if holding_pct is None:
        return 5.0, "Promoter holding not available — neutral score"

    if holding_pct >= 60:
        base = 9.0
        level = "high"
    elif holding_pct >= 45:
        base = 7.5
        level = "healthy"
    elif holding_pct >= 30:
        base = 6.0
        level = "moderate"
    else:
        base = 4.0
        level = "low"

    note = f"Promoter holding {holding_pct:.1f}% ({level})"

    # Bonus/penalty for direction of change
    if change_pct is not None:
        if change_pct > 0:
            base = min(10.0, base + 0.75)
            note += f", increasing +{change_pct:.2f}% — bullish signal"
        elif change_pct < -1:
            base = max(0.0, base - 1.5)
            note += f", decreasing {change_pct:.2f}% — bearish signal"

    return base, note


def _score_roe(roe_pct: Optional[float]) -> tuple[float, str]:
    if roe_pct is None:
        return 5.0, "ROE not available — neutral score"
    if roe_pct >= 25:
        return 10.0, f"Excellent ROE of {roe_pct:.1f}%"
    elif roe_pct >= 18:
        return 8.5, f"Strong ROE of {roe_pct:.1f}%"
    elif roe_pct >= 12:
        return 7.0, f"Good ROE of {roe_pct:.1f}% (above 12% threshold)"
    elif roe_pct >= 8:
        return 5.5, f"Average ROE of {roe_pct:.1f}%"
    elif roe_pct >= 0:
        return 3.5, f"Weak ROE of {roe_pct:.1f}%"
    else:
        return 1.5, f"Negative ROE of {roe_pct:.1f}% — loss-making"


def _score_roce(roce_pct: Optional[float]) -> tuple[float, str]:
    if roce_pct is None:
        return 5.0, "ROCE not available — neutral score"
    if roce_pct >= 25:
        return 10.0, f"Excellent ROCE of {roce_pct:.1f}%"
    elif roce_pct >= 18:
        return 8.0, f"Strong ROCE of {roce_pct:.1f}%"
    elif roce_pct >= 12:
        return 6.5, f"Decent ROCE of {roce_pct:.1f}%"
    elif roce_pct >= 0:
        return 4.0, f"Low ROCE of {roce_pct:.1f}%"
    else:
        return 2.0, f"Negative ROCE of {roce_pct:.1f}% — capital not being used efficiently"


def _score_current_ratio(cr: Optional[float]) -> tuple[float, str]:
    if cr is None:
        return 5.0, "Current ratio not available — neutral score"
    if cr >= 2.5:
        return 9.0, f"Strong liquidity (current ratio={cr:.2f})"
    elif cr >= 1.5:
        return 8.0, f"Good liquidity (current ratio={cr:.2f})"
    elif cr >= 1.0:
        return 6.0, f"Adequate liquidity (current ratio={cr:.2f})"
    elif cr >= 0.7:
        return 4.0, f"Tight liquidity (current ratio={cr:.2f}) — monitor"
    else:
        return 2.0, f"Poor liquidity (current ratio={cr:.2f}) — risk of cash crunch"


def _score_operating_cashflow(ocf: Optional[float], net_income: Optional[float]) -> tuple[float, str]:
    """Score based on OCF positivity and OCF vs net income (earnings quality)."""
    if ocf is None:
        return 5.0, "Operating cash flow not available — neutral score"
    if ocf > 0:
        base = 7.0
        note = f"Positive operating cash flow (₹{ocf/1e7:.1f}Cr)"
        # Check earnings quality: OCF should ideally exceed net income
        ni = _safe(net_income)
        if ni and ni > 0:
            ratio = ocf / ni
            if ratio >= 1.2:
                base = 10.0
                note += " — high quality earnings (OCF > Net Income)"
            elif ratio >= 0.8:
                base = 8.0
                note += " — good earnings quality"
            else:
                base = 6.5
                note += " — earnings quality could be better"
    else:
        base = 2.0
        note = f"Negative operating cash flow (₹{ocf/1e7:.1f}Cr) — cash burn risk"
    return base, note


# ---------------------------------------------------------------------------
# Data fetcher
# ---------------------------------------------------------------------------

def _fetch_fundamentals(ticker: str) -> dict:
    """
    Fetch all raw fundamental data from yfinance.
    Returns a dict of raw values (may include None for missing fields).
    """
    stock = yf.Ticker(ticker)
    info = stock.info or {}

    # --- Income statement (annual) ---
    try:
        fin = stock.financials  # columns = fiscal years, newest first
        revenue_current = _safe(fin.loc["Total Revenue"].iloc[0]) if "Total Revenue" in fin.index else None
        revenue_prev    = _safe(fin.loc["Total Revenue"].iloc[1]) if "Total Revenue" in fin.index and len(fin.columns) > 1 else None
        net_income_current = _safe(fin.loc["Net Income"].iloc[0]) if "Net Income" in fin.index else None
        net_income_prev    = _safe(fin.loc["Net Income"].iloc[1]) if "Net Income" in fin.index and len(fin.columns) > 1 else None
    except Exception:
        revenue_current = revenue_prev = net_income_current = net_income_prev = None

    # --- Balance sheet ---
    try:
        bs = stock.balance_sheet
        total_debt = _safe(bs.loc["Total Debt"].iloc[0]) if "Total Debt" in bs.index else None
        stockholder_equity = _safe(bs.loc["Stockholders Equity"].iloc[0]) if "Stockholders Equity" in bs.index else None
        current_assets = _safe(bs.loc["Current Assets"].iloc[0]) if "Current Assets" in bs.index else None
        current_liab   = _safe(bs.loc["Current Liabilities"].iloc[0]) if "Current Liabilities" in bs.index else None
        total_assets   = _safe(bs.loc["Total Assets"].iloc[0]) if "Total Assets" in bs.index else None
    except Exception:
        total_debt = stockholder_equity = current_assets = current_liab = total_assets = None

    # --- Cash flow ---
    try:
        cf = stock.cashflow
        operating_cf = _safe(cf.loc["Operating Cash Flow"].iloc[0]) if "Operating Cash Flow" in cf.index else None
    except Exception:
        operating_cf = None

    # --- Derived metrics ---
    debt_to_equity = None
    if total_debt is not None and stockholder_equity and stockholder_equity != 0:
        debt_to_equity = total_debt / stockholder_equity

    current_ratio = None
    if current_assets is not None and current_liab and current_liab != 0:
        current_ratio = current_assets / current_liab

    # ROE = Net Income / Stockholders Equity
    roe_pct = None
    if net_income_current is not None and stockholder_equity and stockholder_equity != 0:
        roe_pct = (net_income_current / stockholder_equity) * 100

    # ROCE = EBIT / Capital Employed  (Capital Employed = Total Assets − Current Liabilities)
    roce_pct = None
    try:
        fin_local = stock.financials
        if "EBIT" in fin_local.index:
            ebit = _safe(fin_local.loc["EBIT"].iloc[0])
        else:
            # Approximate: Operating Income
            ebit = _safe(fin_local.loc["Operating Income"].iloc[0]) if "Operating Income" in fin_local.index else None
        if ebit is not None and total_assets is not None and current_liab is not None:
            capital_employed = total_assets - current_liab
            if capital_employed != 0:
                roce_pct = (ebit / capital_employed) * 100
    except Exception:
        pass

    # Revenue and profit growth
    revenue_growth = _pct(revenue_current, revenue_prev)
    profit_growth  = _pct(net_income_current, net_income_prev)

    # PE from info dict (yfinance provides trailingPE)
    pe = _safe(info.get("trailingPE"))

    # Promoter holding — yfinance doesn't expose this directly for Indian stocks.
    # majorHoldersBreakdown or institutionsFloatPercentHeld are the closest proxies.
    # We'll use heldPercentInsiders as a rough proxy and note the limitation.
    promoter_holding = None
    promoter_change  = None
    held_insiders = _safe(info.get("heldPercentInsiders"))
    if held_insiders is not None:
        promoter_holding = held_insiders * 100  # convert to %

    sector = info.get("sector", "Unknown")

    return {
        "sector": sector,
        "pe": pe,
        "revenue_current": revenue_current,
        "revenue_prev": revenue_prev,
        "revenue_growth_pct": revenue_growth,
        "net_income_current": net_income_current,
        "net_income_prev": net_income_prev,
        "profit_growth_pct": profit_growth,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "roe_pct": roe_pct,
        "roce_pct": roce_pct,
        "operating_cf": operating_cf,
        "promoter_holding_pct": promoter_holding,
        "promoter_change_pct": promoter_change,
        "market_cap": _safe(info.get("marketCap")),
        "book_value": _safe(info.get("bookValue")),
        "price_to_book": _safe(info.get("priceToBook")),
        "dividend_yield": _safe(info.get("dividendYield")),
        "beta": _safe(info.get("beta")),
    }


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def get_fundamental_score(ticker: str) -> dict:
    """
    Entry point called by the router.

    Returns a dict compatible with SafeJSONResponse (no NaN/Inf):
    {
        "fundamental_score": float,        # 0–10
        "fundamental_score_normalized": float, # –1 to +1 (for scoring combo)
        "breakdown": { metric: score },
        "insights": [ str, ... ],
        "raw": { ... }                     # raw fetched values
    }
    """
    try:
        raw = _fetch_fundamentals(ticker)
    except Exception as e:
        return _error_response(f"Failed to fetch fundamentals: {e}")

    sector = raw.get("sector", "Unknown")

    # --- Score each metric ---
    pe_score,       pe_note       = _score_pe(raw["pe"], sector)
    rev_score,      rev_note      = _score_revenue_growth(raw["revenue_growth_pct"])
    prof_score,     prof_note     = _score_profit_growth(raw["profit_growth_pct"])
    de_score,       de_note       = _score_debt_equity(raw["debt_to_equity"])
    promo_score,    promo_note    = _score_promoter_holding(raw["promoter_holding_pct"], raw["promoter_change_pct"])
    roe_score,      roe_note      = _score_roe(raw["roe_pct"])
    roce_score,     roce_note     = _score_roce(raw["roce_pct"])
    cr_score,       cr_note       = _score_current_ratio(raw["current_ratio"])
    ocf_score,      ocf_note      = _score_operating_cashflow(raw["operating_cf"], raw["net_income_current"])

    # --- Weighted average (weights must sum to 1.0) ---
    # Prioritise profitability quality & growth for delivery trading
    weights = {
        "pe":              0.12,
        "revenue_growth":  0.12,
        "profit_growth":   0.15,
        "debt_equity":     0.13,
        "promoter":        0.10,
        "roe":             0.13,
        "roce":            0.10,
        "current_ratio":   0.08,
        "operating_cf":    0.07,
    }

    scores = {
        "pe":              pe_score,
        "revenue_growth":  rev_score,
        "profit_growth":   prof_score,
        "debt_equity":     de_score,
        "promoter":        promo_score,
        "roe":             roe_score,
        "roce":            roce_score,
        "current_ratio":   cr_score,
        "operating_cf":    ocf_score,
    }

    fundamental_score = sum(scores[k] * weights[k] for k in weights)
    fundamental_score = round(fundamental_score, 2)

    # Normalize to –1 → +1 for combination with technical/sentiment
    # Score of 5.0 = neutral (0.0), 10 = +1.0, 0 = –1.0
    normalized = round((fundamental_score - 5.0) / 5.0, 4)

    # Qualitative label
    if fundamental_score >= 8.0:
        label = "STRONG"
    elif fundamental_score >= 6.5:
        label = "GOOD"
    elif fundamental_score >= 5.0:
        label = "AVERAGE"
    elif fundamental_score >= 3.5:
        label = "WEAK"
    else:
        label = "POOR"

    insights = [
        pe_note, rev_note, prof_note, de_note,
        promo_note, roe_note, roce_note, cr_note, ocf_note
    ]

    # Build safe raw output (replace None-able floats with None for JSON safety)
    safe_raw = {k: (v if not isinstance(v, float) or (not math.isnan(v) and not math.isinf(v)) else None)
                for k, v in raw.items()}

    return {
        "fundamental_score": fundamental_score,
        "fundamental_score_normalized": normalized,
        "fundamental_label": label,
        "breakdown": {k: round(v, 2) for k, v in scores.items()},
        "weights": weights,
        "insights": insights,
        "raw": safe_raw,
    }


def _error_response(msg: str) -> dict:
    return {
        "fundamental_score": 5.0,
        "fundamental_score_normalized": 0.0,
        "fundamental_label": "UNAVAILABLE",
        "breakdown": {},
        "weights": {},
        "insights": [msg],
        "raw": {},
    }