import { fetchBluesky } from "./sources/bluesky.js";
import { fetchTwitter } from "./sources/twitter.js";
import { fetchHackerNews } from "./sources/hackernews.js";
import { fetchGitHub } from "./sources/github.js";
import { fetchReddit } from "./sources/reddit.js";
import { fetchArxiv } from "./sources/arxiv.js";
import { summarize } from "./summarize.js";
import { sendEmail } from "./email.js";

const sources = [
  { name: "Bluesky", fn: fetchBluesky },
  { name: "Twitter", fn: fetchTwitter },
  { name: "Hacker News", fn: fetchHackerNews },
  { name: "GitHub", fn: fetchGitHub },
  { name: "Reddit", fn: fetchReddit },
  { name: "arxiv", fn: fetchArxiv },
];

async function main() {
  console.log("Fetching from all sources...");

  const results = await Promise.allSettled(
    sources.map(async ({ name, fn }) => {
      const items = await fn();
      console.log(`  ${name}: ${items.length} items`);
      return items;
    })
  );

  const allItems = results.flatMap((r, i) => {
    if (r.status === "fulfilled") return r.value;
    console.warn(`  ${sources[i].name} failed:`, r.reason?.message);
    return [];
  });

  console.log(`Total items: ${allItems.length}`);

  if (allItems.length === 0) {
    console.log("No items found, skipping digest.");
    return;
  }

  console.log("Summarizing with Claude...");
  const digest = await summarize(allItems);

  console.log("Sending email...");
  await sendEmail(digest);

  console.log("Done! Digest sent.");
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
