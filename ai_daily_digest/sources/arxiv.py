import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

SEARCH_TERMS = [
    "AI agent",
    "tool calling",
    "LLM agent",
    "function calling",
    "code generation agent",
]

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_arxiv():
    since = datetime.now(timezone.utc) - timedelta(hours=48)  # 48h for arxiv lag
    results = []

    for term in SEARCH_TERMS:
        try:
            query = f'cat:cs.AI AND all:"{term}"'
            params = {
                "search_query": query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": "15",
            }
            res = httpx.get(
                "https://export.arxiv.org/api/query",
                params=params,
                timeout=15,
            )
            if res.status_code != 200:
                continue

            root = ET.fromstring(res.text)

            for entry in root.findall(f"{ATOM_NS}entry"):
                title_el = entry.find(f"{ATOM_NS}title")
                id_el = entry.find(f"{ATOM_NS}id")
                published_el = entry.find(f"{ATOM_NS}published")

                if title_el is None or id_el is None:
                    continue

                url = (id_el.text or "").strip()
                if "arxiv.org/abs/" not in url:
                    continue

                if published_el is not None and published_el.text:
                    published = datetime.fromisoformat(
                        published_el.text.strip().replace("Z", "+00:00")
                    )
                    if published < since:
                        continue

                title = " ".join((title_el.text or "").split())

                results.append({
                    "title": title,
                    "url": url,
                    "source": "arxiv",
                    "engagement": 0,
                })
        except Exception:
            continue

    seen = set()
    deduped = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    return deduped
