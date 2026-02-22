import httpx
from datetime import datetime, timedelta, timezone

SEARCH_QUERIES = [
    "AI agent",
    "LLM agent",
    "tool-calling",
    "coding agent",
    "MCP server",
]


def fetch_github():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%d")
    results = []

    for term in SEARCH_QUERIES:
        try:
            q = f"{term} pushed:>{since}"
            res = httpx.get(
                "https://api.github.com/search/repositories",
                params={"q": q, "sort": "stars", "order": "desc", "per_page": "10"},
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "ai-daily-digest",
                },
                timeout=15,
            )
            if res.status_code != 200:
                continue
            data = res.json()

            for repo in data.get("items", []):
                description = repo.get("description") or "No description"
                results.append({
                    "title": f"{repo['full_name']}: {description}",
                    "url": repo["html_url"],
                    "source": "GitHub",
                    "engagement": repo.get("stargazers_count", 0),
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
