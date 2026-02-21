const SUBREDDITS = ["LocalLLaMA", "MachineLearning", "artificial"];
const SEARCH_TERMS = ["AI agent", "tool calling", "coding agent", "MCP", "LLM agent"];

export async function fetchReddit() {
  const since = Date.now() - 24 * 60 * 60 * 1000;
  const results = [];

  for (const sub of SUBREDDITS) {
    for (const term of SEARCH_TERMS) {
      try {
        const params = new URLSearchParams({
          q: term,
          restrict_sr: "on",
          sort: "relevance",
          t: "day",
        });
        const res = await fetch(
          `https://www.reddit.com/r/${sub}/search.json?${params}`,
          {
            headers: {
              "User-Agent": "ai-daily-digest/1.0",
            },
          }
        );
        if (!res.ok) continue;
        const data = await res.json();

        for (const child of data?.data?.children || []) {
          const post = child.data;
          const createdAt = (post.created_utc || 0) * 1000;
          if (createdAt < since) continue;
          if ((post.score || 0) < 5) continue;

          results.push({
            title: post.title || "Untitled",
            url: `https://reddit.com${post.permalink}`,
            source: `Reddit r/${sub}`,
            engagement: post.score || 0,
          });
        }
      } catch {
        // skip failed searches
      }
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
