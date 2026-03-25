"""
SharkNinja Trade Screen — Master Data Fetcher
Orchestrates all fetcher modules and writes to data/live-data.json.
Run locally or via GitHub Actions on a schedule.

Usage:
    python scripts/fetch_data.py
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fetchers import stocks, trends, amazon, macro, patents, shipping, social, traffic

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "live-data.json"


def load_existing():
    """Load existing live-data.json as cache for failed fetches."""
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    print("=" * 60)
    print("SharkNinja Trade Screen — Data Fetcher")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    existing = load_existing()
    output = {"updated_at": datetime.now().isoformat()}

    # 1. Stock prices, FX, commodities
    print("\n[1/8] Fetching stock data...")
    try:
        stock_data = stocks.fetch(existing)
        output["stocks"] = stock_data.get("stocks", {})
        output["fx"] = stock_data.get("fx", {})
        output["commodities"] = stock_data.get("commodities", {})
    except Exception as e:
        print(f"  [ERROR] Stocks: {e}")
        output["stocks"] = existing.get("stocks", {})
        output["fx"] = existing.get("fx", {})
        output["commodities"] = existing.get("commodities", {})

    # 2. Google Trends
    print("\n[2/8] Fetching Google Trends...")
    try:
        output["trends"] = trends.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Trends: {e}")
        output["trends"] = existing.get("trends", {})

    # 3. Amazon (Keepa)
    print("\n[3/8] Fetching Amazon data...")
    try:
        output["amazon"] = amazon.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Amazon: {e}")
        output["amazon"] = existing.get("amazon", {})

    # 4. Macro (FRED)
    print("\n[4/8] Fetching macro indicators...")
    try:
        output["macro"] = macro.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Macro: {e}")
        output["macro"] = existing.get("macro", {})

    # 5. Patents
    print("\n[5/8] Fetching patent data...")
    try:
        output["patents"] = patents.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Patents: {e}")
        output["patents"] = existing.get("patents", {})

    # 6. Shipping
    print("\n[6/8] Fetching shipping rates...")
    try:
        output["shipping"] = shipping.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Shipping: {e}")
        output["shipping"] = existing.get("shipping", {})

    # 7. Social (Reddit)
    print("\n[7/8] Fetching social mentions...")
    try:
        output["social"] = social.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Social: {e}")
        output["social"] = existing.get("social", {})

    # 8. Traffic (SimilarWeb)
    print("\n[8/8] Fetching DTC traffic...")
    try:
        output["traffic"] = traffic.fetch(existing)
    except Exception as e:
        print(f"  [ERROR] Traffic: {e}")
        output["traffic"] = existing.get("traffic", {})

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"[DONE] Data written to {OUTPUT_FILE}")
    print(f"  Stocks: {len(output.get('stocks', {}))} symbols")
    print(f"  FX: {len(output.get('fx', {}))} pairs")
    print(f"  Trends: {len(output.get('trends', {}))} terms")
    print(f"  Amazon: {len(output.get('amazon', {}))} ASINs")
    print(f"  Macro: {len(output.get('macro', {}))} series")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
