"""
Fetch stock prices, FX rates, and commodity prices via yfinance.
SN, peers, FX (USD/CNY, EUR/USD, GBP/USD), commodities (Copper, Crude).
"""
import json
from datetime import datetime


SYMBOLS = {
    "SN": "SharkNinja",
    "XLY": "Consumer Discretionary ETF",
    "SPY": "S&P 500 ETF",
    "HELE": "Helen of Troy",
    "IRBT": "iRobot",
    "WHR": "Whirlpool",
    "HG=F": "Copper Futures",
    "CL=F": "Crude Oil WTI",
}

FX_SYMBOLS = {
    "CNY=X": "USD/CNY",
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
}


def fetch(existing_data=None):
    """Fetch stock, FX, and commodity data. Returns dict."""
    results = {"stocks": {}, "fx": {}, "commodities": {}}

    try:
        import yfinance as yf
    except ImportError:
        print("  [WARN] yfinance not installed, skipping stock data")
        return results

    # Stocks and peers
    all_symbols = {**SYMBOLS, **FX_SYMBOLS}
    for sym, name in all_symbols.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="6mo")
            if hist.empty:
                print(f"  [WARN] {sym}: no data returned")
                continue
            closes = hist["Close"].tolist()
            dates = [d.strftime("%Y-%m-%d") for d in hist.index]

            entry = {
                "name": name,
                "price": round(closes[-1], 2) if closes else None,
                "prevClose": round(closes[-2], 2) if len(closes) > 1 else None,
                "closes": [round(c, 2) for c in closes],
                "dates": dates,
            }

            if sym in FX_SYMBOLS:
                results["fx"][sym.replace("=X", "").replace("USD", "USDCNY") if "CNY" in sym else sym] = entry
                # Also store simple FX value
                if "CNY" in sym:
                    results["fx"]["USDCNY"] = round(closes[-1], 4) if closes else None
            elif sym in ("HG=F", "CL=F"):
                results["commodities"][sym] = entry
            else:
                results["stocks"][sym] = entry

            print(f"  [OK] {sym} ({name}): {entry['price']}")
        except Exception as e:
            print(f"  [FAIL] {sym} ({name}): {e}")

    return results
