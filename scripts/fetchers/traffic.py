"""
Fetch SimilarWeb traffic estimates for sharkninja.com.
Scrapes free tier data. Falls back to cached on failure.
"""
import json
import urllib.request
import ssl
from datetime import datetime


def fetch(existing_data=None):
    """Fetch DTC traffic data. Returns dict."""
    results = existing_data.get("traffic", {}) if existing_data else {}

    try:
        ctx = ssl.create_default_context()
        url = "https://data.similarweb.com/api/v1/data?domain=sharkninja.com"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data:
            results["sharkninja_com"] = {
                "total_visits": data.get("EstimatedMonthlyVisits", {}),
                "bounce_rate": data.get("BounceRate", None),
                "pages_per_visit": data.get("PagesPerVisit", None),
                "avg_duration": data.get("TimeOnSite", None),
                "fetched_at": datetime.now().isoformat(),
            }
            print(f"  [OK] SimilarWeb: sharkninja.com traffic data fetched")
            return results

    except Exception as e:
        print(f"  [FAIL] SimilarWeb: {e}")

    if "sharkninja_com" not in results:
        results["sharkninja_com"] = {"note": "SimilarWeb scrape failed. May require paid API."}
        print("  [SKIP] SimilarWeb unavailable, using placeholder")

    return results
