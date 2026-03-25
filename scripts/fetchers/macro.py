"""
Fetch macro indicators from FRED API.
UMCSENT (Michigan Consumer Sentiment), EXHOSLUSM495S (Existing Home Sales).
Requires FRED_API_KEY env var.
"""
import os
from datetime import datetime


FRED_KEY = os.environ.get("FRED_API_KEY", "")

SERIES = {
    "UMCSENT": "U. Michigan Consumer Sentiment",
    "EXHOSLUSM495S": "Existing Home Sales (SAAR)",
}


def fetch(existing_data=None):
    """Fetch FRED macro data. Returns dict."""
    results = existing_data.get("macro", {}) if existing_data else {}

    if not FRED_KEY:
        print("  [SKIP] No FRED_API_KEY set, skipping macro data")
        return results

    try:
        from fredapi import Fred
        fred = Fred(api_key=FRED_KEY)

        for series_id, name in SERIES.items():
            try:
                data = fred.get_series(series_id, observation_start="2025-01-01")
                if data is not None and not data.empty:
                    results[series_id] = {
                        "name": name,
                        "dates": [d.strftime("%Y-%m-%d") for d in data.index],
                        "values": [round(v, 2) if v == v else None for v in data.tolist()],
                        "latest": round(data.dropna().iloc[-1], 2) if not data.dropna().empty else None,
                    }
                    print(f"  [OK] FRED: {series_id} ({name}): latest={results[series_id]['latest']}")
            except Exception as e:
                print(f"  [FAIL] FRED {series_id}: {e}")

    except ImportError:
        print("  [WARN] fredapi not installed, skipping macro data")

    return results
