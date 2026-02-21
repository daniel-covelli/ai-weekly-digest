const SEARCH_TERMS = [
  "AI agent",
  "tool calling",
  "coding agent",
  "MCP server",
  "function calling",
];

export async function fetchTwitter() {
  const apiKey = process.env.SOCIALDATA_API_KEY;
  if (!apiKey) {
    console.warn("SOCIALDATA_API_KEY not set, skipping Twitter");
    return [];
  }

  const results = [];

  for (const term of SEARCH_TERMS) {
    try {
      const query = `${term} min_faves:50`;
      const params = new URLSearchParams({
        query,
        type: "Latest",
      });
      const res = await fetch(
        `https://api.socialdata.tools/twitter/search?${params}`,
        { headers: { Authorization: `Bearer ${apiKey}` } }
      );
      if (!res.ok) continue;
      const data = await res.json();

      for (const tweet of data.tweets || []) {
        const likes = tweet.favorite_count || 0;
        const retweets = tweet.retweet_count || 0;
        const engagement = likes + retweets;

        const createdAt = new Date(tweet.created_at);
        if (Date.now() - createdAt.getTime() > 24 * 60 * 60 * 1000) continue;

        const username = tweet.user?.screen_name || "unknown";
        const url = `https://x.com/${username}/status/${tweet.id_str}`;
        const text = tweet.full_text || tweet.text || "";
        const title =
          text.length > 140 ? text.slice(0, 140) + "..." : text;

        results.push({ title, url, source: "Twitter", engagement });
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
