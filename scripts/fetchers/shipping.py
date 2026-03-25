"""
Fetch container shipping rates (China to US West Coast).
Uses Freightos API free tier or falls back to placeholder.
"""
import json
import os
import urllib.request
import ssl
from datetime import datetime


def fetch(existing_data=None):
    """Fetch shipping rate data. Returns dict."""
    results = existing_data.get("shipping", {}) if existing_data else {}

    # Try Freightos API
    freightos_key = os.environ.get("FREIGHTOS_API_KEY", "")
    if freightos_key:
        try:
            ctx = ssl.create_default_context()
            url = f"https://api.freightos.com/api/v1/rates/fbx/CNSHA.USLAX?api_key={freightos_key}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            if data:
                results["fbx_china_us"] = {
                    "rate": data.get("rate", None),
                    "currency": "USD",
                    "route": "Shanghai to LA",
                    "fetched_at": datetime.now().isoformat(),
                }
                print(f"  [OK] Freightos FBX: ${results['fbx_china_us']['rate']}/FEU")
                return results
        except Exception as e:
            print(f"  [FAIL] Freightos: {e}")

    # Fallback: keep existing or use placeholder
    if "fbx_china_us" not in results:
        results["fbx_china_us"] = {
            "rate": None,
            "currency": "USD",
            "route": "Shanghai to LA",
            "note": "No API key configured. Set FREIGHTOS_API_KEY.",
        }
        print("  [SKIP] No Freightos API key, using placeholder")
    else:
        print("  [INFO] Keeping cached shipping data")

    return results
