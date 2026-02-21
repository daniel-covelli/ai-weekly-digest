const SEARCH_TERMS = [
  "AI agent",
  "tool calling",
  "LLM agent",
  "function calling",
  "code generation agent",
];

export async function fetchArxiv() {
  const results = [];

  for (const term of SEARCH_TERMS) {
    try {
      const query = encodeURIComponent(
        `cat:cs.AI AND all:"${term}"`
      );
      const params = new URLSearchParams({
        search_query: query,
        sortBy: "submittedDate",
        sortOrder: "descending",
        max_results: "15",
      });
      const res = await fetch(
        `https://export.arxiv.org/api/query?${params}`
      );
      if (!res.ok) continue;
      const xml = await res.text();

      // Simple XML parsing for Atom feed entries
      const entries = xml.split("<entry>").slice(1);
      const since = Date.now() - 48 * 60 * 60 * 1000; // 48h for arxiv lag

      for (const entry of entries) {
        const titleMatch = entry.match(/<title>([\s\S]*?)<\/title>/);
        const linkMatch = entry.match(
          /<id>(https?:\/\/arxiv\.org\/abs\/[\w.]+)<\/id>/
        );
        const publishedMatch = entry.match(
          /<published>([\s\S]*?)<\/published>/
        );

        if (!titleMatch || !linkMatch) continue;

        const published = publishedMatch
          ? new Date(publishedMatch[1].trim()).getTime()
          : 0;
        if (published < since) continue;

        const title = titleMatch[1].trim().replace(/\s+/g, " ");
        const url = linkMatch[1].trim();

        results.push({
          title,
          url,
          source: "arxiv",
          engagement: 0,
        });
      }
    } catch {
      // skip failed searches
    }
  }

  const seen = new Set();
  return results.filter((r) => {
    if (seen.has(r.url)) return false;
    seen.add(r.url);
    return true;
  });
}
