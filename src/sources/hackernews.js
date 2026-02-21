const SEARCH_TERMS = [
  "AI agent",
  "LLM tool",
  "coding agent",
  "MCP",
  "function calling",
  "tool use LLM",
];

export async function fetchHackerNews() {
  const since = Math.floor((Date.now() - 24 * 60 * 60 * 1000) / 1000);
  const results = [];

  for (const term of SEARCH_TERMS) {
    try {
      const params = new URLSearchParams({
        query: term,
        tags: "story",
        numericFilters: `created_at_i>${since},points>10`,
        hitsPerPage: "25",
      });
      const res = await fetch(
        `https://hn.algolia.com/api/v1/search_by_date?${params}`
      );
      if (!res.ok) continue;
      const data = await res.json();

      for (const hit of data.hits || []) {
        const url =
          hit.url || `https://news.ycombinator.com/item?id=${hit.objectID}`;
        results.push({
          title: hit.title || "Untitled",
          url,
          source: "Hacker News",
          engagement: hit.points || 0,
        });
      }
    } catch {
      // skip failed searches
    }
  }

  const seen = new Set();
  return results
    .filter((r) => {
      if (seen.has(r.url)) return false;
      seen.add(r.url);
      return true;
    })
    .sort((a, b) => b.engagement - a.engagement)
    .slice(0, 20);
}
