"""
Fetch Amazon BSR, pricing, and review data via Keepa API.
Requires KEEPA_API_KEY env var. Gracefully skips if unavailable.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests

KEEPA_KEY = os.environ.get("KEEPA_API_KEY", "")

TRACKED_ASINS = {
    "US": {
        "Ninja Air Fryer AF101": "B07FDJMC9Q",
        "Ninja Creami NC501": "B0B7R8HN93",
        "Shark Navigator NV356E": "B01IAEEVBA",
        "Shark FlexStyle HD430": "B0CD9625KH",
        "Ninja Woodfire OG701": "B0BXBTXKZ4",
    },
    "UK": {
        "Ninja Air Fryer AF100UK": "B089TQFKGX",
    },
}

DOMAIN_MAP = {"US": 1, "UK": 2, "DE": 3, "FR": 4, "JP": 5, "AU": 9}


def fetch(existing_data=None):
    """Fetch Keepa data for tracked ASINs. Returns dict."""
    results = existing_data.get("amazon", {}) if existing_data else {}

    if not KEEPA_KEY:
        print("  [SKIP] No KEEPA_API_KEY set, skipping Amazon data")
        return results

    for market, asins in TRACKED_ASINS.items():
        domain = DOMAIN_MAP.get(market, 1)
        for name, asin in asins.items():
            try:
                resp = requests.get(
                    f"https://api.keepa.com/product?key={KEEPA_KEY}&domain={domain}&asin={asin}&stats=90",
                    timeout=15,
                )
                data = resp.json()
                if data.get("products"):
                    product = data["products"][0]
                    stats = product.get("stats", {})
                    csv_data = product.get("csv", [])

                    entry = {
                        "name": name,
                        "asin": asin,
                        "market": market,
                        "current_price": stats.get("current", [None])[0],
                        "avg30": stats.get("avg30", [None])[0],
                        "avg90": stats.get("avg90", [None])[0],
                        "bsr_current": stats.get("salesRankCurrent", {}).get("ABIS_KITCHEN", None),
                        "review_count": stats.get("reviewCount", None),
                        "fetched_at": datetime.now().isoformat(),
                    }

                    # Convert Keepa price format (cents) to dollars
                    for key in ["current_price", "avg30", "avg90"]:
                        if entry[key] and entry[key] > 0:
                            entry[key] = round(entry[key] / 100, 2)

                    results[f"{market}_{asin}"] = entry
                    print(f"  [OK] Keepa: {name} ({market})")

                time.sleep(2)
            except Exception as e:
                print(f"  [FAIL] Keepa {name} ({market}): {e}")

    return results
