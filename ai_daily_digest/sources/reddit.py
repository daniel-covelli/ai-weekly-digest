import httpx
from datetime import datetime, timedelta, timezone

SUBREDDITS = ["LocalLLaMA", "MachineLearning", "artificial"]
SEARCH_TERMS = ["AI agent", "tool calling", "coding agent", "MCP", "LLM agent"]


def fetch_reddit():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000
    results = []

    for sub in SUBREDDITS:
        for term in SEARCH_TERMS:
            try:
                params = {
                    "q": term,
                    "restrict_sr": "on",
                    "sort": "relevance",
                    "t": "day",
                }
                res = httpx.get(
                    f"https://www.reddit.com/r/{sub}/search.json",
                    params=params,
                    headers={"User-Agent": "ai-daily-digest/1.0"},
                    timeout=15,
                )
                if res.status_code != 200:
                    continue
                data = res.json()

                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    created_at = (post.get("created_utc", 0)) * 1000
                    if created_at < since:
                        continue
                    if post.get("score", 0) < 5:
                        continue

                    results.append({
                        "title": post.get("title", "Untitled"),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "source": f"Reddit r/{sub}",
                        "engagement": post.get("score", 0),
                    })
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
