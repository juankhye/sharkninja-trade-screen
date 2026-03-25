"""
Fetch SharkNinja patent filings from Google Patents.
Queries assignee "SharkNinja" OR "JS Global Lifestyle".
"""
import json
import urllib.request
import ssl
from datetime import datetime


def fetch(existing_data=None):
    """Fetch patent filing data. Returns dict."""
    results = existing_data.get("patents", {}) if existing_data else {}

    ctx = ssl.create_default_context()
    headers = {"User-Agent": "Mozilla/5.0"}

    queries = ["SharkNinja", "JS Global Lifestyle"]
    patents = []

    for assignee in queries:
        try:
            url = f"https://patents.google.com/xhr/query?url=assignee%3D{assignee.replace(' ', '+')}&num=20&type=PATENT"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            if "results" in data and "cluster" in data["results"]:
                for cluster in data["results"]["cluster"]:
                    for result in cluster.get("result", []):
                        patent = result.get("patent", {})
                        patents.append({
                            "id": patent.get("publication_number", ""),
                            "title": patent.get("title", ""),
                            "date": patent.get("filing_date", ""),
                            "assignee": assignee,
                        })

            print(f"  [OK] Patents for '{assignee}': {len(patents)} found")
        except Exception as e:
            print(f"  [FAIL] Patents '{assignee}': {e}")

    results["filings"] = patents
    results["total_count"] = len(patents)
    results["fetched_at"] = datetime.now().isoformat()

    return results
