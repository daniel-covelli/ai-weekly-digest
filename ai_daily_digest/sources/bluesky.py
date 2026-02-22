import os
import httpx
from datetime import datetime, timedelta, timezone
from atproto import Client
from dotenv import load_dotenv

load_dotenv()

SEARCH_TERMS = [
    "AI agent",
    "tool calling",
    "coding agent",
    "MCP server",
    "function calling LLM",
]

BSKY_API = "https://bsky.social/xrpc"

client = Client()
IDENTIFIER = os.getenv("BSKY_IDENTIFIER")
PASSWORD = os.getenv("BSKY_APP_PASSWORD")
client.login(IDENTIFIER, PASSWORD)


def fetch_bluesky():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    results = []

    for term in SEARCH_TERMS:
        try:
            params = {"q": term, "since": since, "sort": "top", "limit": 25}
            res = client.app.bsky.feed.search_posts(params)

            for post in res.posts:
                likes = post.like_count
                reposts = post.repost_count
                engagement = likes + reposts
                if engagement < 5:
                    continue

                handle = post.author.handle
                rkey = post.uri.split("/")[-1]
                url = f"https://bsky.app/profile/{handle}/post/{rkey}"
                text = post.record.text
                title = text[:1000] + "..." if len(text) > 1000 else text

                results.append(
                    {"title": title, "url": url, "source": "Bluesky", "engagement": engagement}
                )
        except Exception as err:
            print(err)
            continue

    seen = set()
    deduped = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    deduped.sort(key=lambda r: r["engagement"], reverse=True)
    return deduped[:20]

if __name__ == "__main__":
    fetch_bluesky()
