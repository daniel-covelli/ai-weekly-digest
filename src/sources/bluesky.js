const SEARCH_TERMS = [
  "AI agent",
  "tool calling",
  "coding agent",
  "MCP server",
  "function calling LLM",
];

export async function fetchBluesky() {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const results = [];

  for (const term of SEARCH_TERMS) {
    try {
      const params = new URLSearchParams({
        q: term,
        since,
        sort: "top",
        limit: "25",
      });
      const res = await fetch(
        `https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?${params}`
      );
      if (!res.ok) continue;
      const data = await res.json();

      for (const post of data.posts || []) {
        const likes = post.likeCount || 0;
        const reposts = post.repostCount || 0;
        const engagement = likes + reposts;
        if (engagement < 5) continue;

        const handle = post.author?.handle || "unknown";
        const rkey = post.uri?.split("/").pop();
        const url = `https://bsky.app/profile/${handle}/post/${rkey}`;
        const text = post.record?.text || "";
        const title =
          text.length > 140 ? text.slice(0, 140) + "..." : text;

        results.push({ title, url, source: "Bluesky", engagement });
      }
    } catch {
      // skip failed searches
    }
  }

  // Deduplicate by URL and sort by engagement
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
