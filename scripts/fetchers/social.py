"""
Fetch Reddit mention counts for SharkNinja products.
Uses praw (Reddit API). Requires REDDIT_CLIENT_ID/SECRET env vars.
"""
import os
from datetime import datetime


SUBREDDITS = ["Cooking", "BuyItForLife", "CleaningTips", "HairCare", "VacuumCleaners"]
SEARCH_TERMS = ["SharkNinja", "Ninja Creami", "Shark vacuum", "Ninja air fryer", "Shark FlexStyle", "CryoGlow"]


def fetch(existing_data=None):
    """Fetch Reddit mention data. Returns dict."""
    results = existing_data.get("social", {}) if existing_data else {}

    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("  [SKIP] No Reddit credentials, skipping social data")
        return results

    try:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="SN-TradeScreen/1.0",
        )

        mentions = {}
        for term in SEARCH_TERMS:
            count = 0
            for sub_name in SUBREDDITS:
                try:
                    sub = reddit.subreddit(sub_name)
                    for post in sub.search(term, time_filter="week", limit=50):
                        count += 1
                except Exception:
                    pass
            mentions[term] = count
            print(f"  [OK] Reddit: '{term}' = {count} mentions (7d)")

        results["reddit_mentions"] = mentions
        results["fetched_at"] = datetime.now().isoformat()

    except ImportError:
        print("  [WARN] praw not installed, skipping Reddit data")

    return results
