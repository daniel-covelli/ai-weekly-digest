import httpx
from datetime import datetime, timedelta, timezone

SEARCH_TERMS = [
    "AI agent",
    "LLM tool",
    "coding agent",
    "MCP",
    "function calling",
    "tool use LLM",
]


def fetch_hackernews():
    since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    results = []

    for term in SEARCH_TERMS:
        try:
            params = {
                "query": term,
                "tags": "story",
                "numericFilters": f"created_at_i>{since},points>10",
                "hitsPerPage": "25",
            }
            res = httpx.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params=params,
                timeout=15,
            )
            if res.status_code != 200:
                continue
            data = res.json()

            for hit in data.get("hits", []):
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                results.append({
                    "title": hit.get("title", "Untitled"),
                    "url": url,
                    "source": "Hacker News",
                    "engagement": hit.get("points", 0),
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
