import os
import httpx
from datetime import datetime, timedelta, timezone

SEARCH_TERMS = [
    "AI agent",
    "tool calling",
    "coding agent",
    "MCP server",
    "function calling",
]


def fetch_twitter():
    api_key = os.environ.get("SOCIALDATA_API_KEY")
    if not api_key:
        print("SOCIALDATA_API_KEY not set, skipping Twitter")
        return []

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    results = []

    for term in SEARCH_TERMS:
        try:
            query = f"{term} min_faves:50"
            params = {"query": query, "type": "Latest"}
            res = httpx.get(
                "https://api.socialdata.tools/twitter/search",
                params=params,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            if res.status_code != 200:
                continue
            data = res.json()

            for tweet in data.get("tweets", []):
                likes = tweet.get("favorite_count", 0)
                retweets = tweet.get("retweet_count", 0)
                engagement = likes + retweets

                created_at = datetime.strptime(
                    tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"
                )
                if created_at < since:
                    continue

                username = tweet.get("user", {}).get("screen_name", "unknown")
                url = f"https://x.com/{username}/status/{tweet.get('id_str', '')}"
                text = tweet.get("full_text") or tweet.get("text", "")
                title = text[:140] + "..." if len(text) > 140 else text

                results.append(
                    {"title": title, "url": url, "source": "Twitter", "engagement": engagement}
                )
        except Exception:
            continue

    seen = set()
    deduped = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    deduped.sort(key=lambda r: r["engagement"], reverse=True)
    return deduped[:20]
