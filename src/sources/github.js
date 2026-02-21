const SEARCH_QUERIES = [
  "AI agent",
  "LLM agent",
  "tool-calling",
  "coding agent",
  "MCP server",
];

export async function fetchGitHub() {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000)
    .toISOString()
    .split("T")[0];
  const results = [];

  for (const term of SEARCH_QUERIES) {
    try {
      const q = encodeURIComponent(`${term} pushed:>${since}`);
      const res = await fetch(
        `https://api.github.com/search/repositories?q=${q}&sort=stars&order=desc&per_page=10`,
        {
          headers: {
            Accept: "application/vnd.github+json",
            "User-Agent": "ai-daily-digest",
          },
        }
      );
      if (!res.ok) continue;
      const data = await res.json();

      for (const repo of data.items || []) {
        results.push({
          title: `${repo.full_name}: ${repo.description || "No description"}`,
          url: repo.html_url,
          source: "GitHub",
          engagement: repo.stargazers_count || 0,
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
