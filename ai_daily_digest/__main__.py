import sys
from concurrent.futures import ThreadPoolExecutor

from ai_daily_digest.sources.bluesky import fetch_bluesky
from ai_daily_digest.sources.twitter import fetch_twitter
from ai_daily_digest.sources.hackernews import fetch_hackernews
from ai_daily_digest.sources.github import fetch_github
from ai_daily_digest.sources.reddit import fetch_reddit
from ai_daily_digest.sources.arxiv import fetch_arxiv
from ai_daily_digest.summarize import summarize
from ai_daily_digest.email_sender import send_email


SOURCES = [
    ("Bluesky", fetch_bluesky),
    ("Twitter", fetch_twitter),
    ("Hacker News", fetch_hackernews),
    ("GitHub", fetch_github),
    ("Reddit", fetch_reddit),
    ("arxiv", fetch_arxiv),
]


def fetch_source(name, fn):
    try:
        items = fn()
        print(f"  {name}: {len(items)} items")
        return items
    except Exception as e:
        print(f"  {name} failed: {e}")
        return []


def main():
    print("Fetching from all sources...")

    all_items = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_source, name, fn): name for name, fn in SOURCES}
        for future in futures:
            all_items.extend(future.result())

    print(f"Total items: {len(all_items)}")

    if not all_items:
        print("No items found, skipping digest.")
        return

    print("Summarizing with Claude...")
    digest = summarize(all_items)

    print("Sending email...")
    send_email(digest)

    print("Done! Digest sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
