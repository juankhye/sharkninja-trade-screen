"""
Fetch Google Trends data via pytrends.
Rotates queries across weekdays to avoid rate limiting.
Day 0 (Mon): core brands, Day 1: new products, Day 2: competitors,
Day 3: international, Day 4: retry failures.
"""
import json
import time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "trends"

# Query batches rotated by day-of-week
BATCHES = {
    0: [  # Monday — core brands
        "Shark vacuum", "Ninja air fryer", "Ninja blender", "SharkNinja",
    ],
    1: [  # Tuesday — new products
        "Ninja Creami", "Shark FlexStyle", "Ninja Luxe Cafe", "Shark CryoGlow",
    ],
    2: [  # Wednesday — competitors + more new
        "Dyson vacuum", "KitchenAid", "Breville", "Ninja Detect Pro",
    ],
    3: [  # Thursday — international (geo queries)
        "Ninja", "Shark",  # queried with geo param
    ],
    4: [],  # Friday — retry any cached failures
}


def fetch(existing_data=None):
    """Fetch Google Trends for today's batch. Returns dict."""
    results = existing_data.get("trends", {}) if existing_data else {}

    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("  [WARN] pytrends not installed, skipping trends")
        return results

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dow = datetime.today().weekday()
    batch = BATCHES.get(dow, [])

    if not batch:
        print(f"  [INFO] No trends batch for day {dow}")
        return results

    pytrends = TrendReq(hl='en-US', tz=300)

    if dow == 3:
        # International geo queries
        geos = {"US": "", "UK": "GB", "DE": "DE", "FR": "FR", "JP": "JP", "AU": "AU"}
        for term in batch:
            for geo_name, geo_code in geos.items():
                try:
                    pytrends.build_payload([term], cat=0, timeframe='today 12-m', geo=geo_code)
                    df = pytrends.interest_over_time()
                    if df is not None and not df.empty:
                        key = f"{term}_{geo_name}"
                        results[key] = {
                            "dates": [d.strftime("%Y-%m-%d") for d in df.index],
                            "values": df[term].tolist(),
                        }
                        print(f"  [OK] Trends: {key}")
                    time.sleep(15)
                except Exception as e:
                    print(f"  [FAIL] Trends {term} ({geo_name}): {e}")
                    time.sleep(30)
    else:
        # Standard queries — up to 5 terms per call
        try:
            pytrends.build_payload(batch[:5], cat=0, timeframe='today 12-m', geo='')
            df = pytrends.interest_over_time()
            if df is not None and not df.empty:
                dates = [d.strftime("%Y-%m-%d") for d in df.index]
                for term in batch[:5]:
                    if term in df.columns:
                        results[term] = {
                            "dates": dates,
                            "values": df[term].tolist(),
                        }
                        print(f"  [OK] Trends: {term}")
        except Exception as e:
            print(f"  [FAIL] Trends batch: {e}")

    # Save dated snapshot
    snapshot_file = DATA_DIR / f"trends_{datetime.now().strftime('%Y-%m-%d')}.json"
    try:
        with open(snapshot_file, "w") as f:
            json.dump(results, f, indent=2)
    except Exception:
        pass

    return results
