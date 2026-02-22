import anthropic


def summarize(items):
    if not items:
        return "No relevant AI agent developments found in the last 24 hours."

    item_list = "\n".join(
        f"{i + 1}. [{item['source']}] {item['title']}\n   URL: {item['url']}\n   Engagement: {item['engagement']}"
        for i, item in enumerate(items)
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""You are an AI newsletter editor. Below are items from the last 24 hours related to AI agents, tool calling, coding agents, and related topics. Create a concise daily digest.

Instructions:
- Deduplicate items that refer to the same thing
- Categorize into these sections: **Frameworks & Tools**, **Research & Papers**, **Industry News**, **Notable Discussions**
- Each item should be a bullet point with a markdown link and 1-sentence summary
- Skip any section that has no items
- Start with a "Top Story" callout highlighting the single most significant development
- Keep the total output under 800 words
- Use markdown formatting

Items:
{item_list}""",
            },
        ],
    )

    return message.content[0].text
