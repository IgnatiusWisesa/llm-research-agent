import os
import sys
import asyncio
import json
import re
import redis

from agent.nodes.generate_queries import generate_queries
from agent.nodes.reflect import reflect
from agent.nodes.synthesize import synthesize
from agent.tools.websearch import WebSearchTool

# === Redis setup ===
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    db=0,
    decode_responses=True
)
CACHE_PREFIX = "llm_cache:"
CACHE_LIMIT = 50

# === Accept user question from CLI argument, or use a default fallback ===
question = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"
normalized_question = question.strip().lower()
cache_key = CACHE_PREFIX + normalized_question

async def main():
    # === Step 0: Check if answer already exists in Redis cache ===
    cached = redis_client.get(cache_key)
    if cached:
        print("\n💾 Loaded from Redis cache:\n")
        print(cached)
        return

    # === Step 1: Generate search queries using Gemini ===
    queries = generate_queries(question)
    print("\n🧩 Generated Queries:")
    for q in queries:
        print("-", q)

    # === Step 2: Search the web using Google Custom Search API ===
    search_tool = WebSearchTool()
    docs = await search_tool.run(queries)
    print("\n🔍 Search Results:")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.title}\n   {doc.snippet}\n   {doc.url}\n")

    # === Step 3: Reflect to see if current results are enough to answer ===
    print("\n🪞 Calling reflect()...")
    reflection = reflect(question, docs)
    print("\n🪞 Reflect Result:")
    print(reflection)

    if reflection["need_more"]:
        # Not enough info yet → return additional queries
        print("\n🔁 Not enough info. Consider running new queries:")
        for q in reflection["new_queries"]:
            print("-", q)
        output = {
            "status": "need_more_info",
            "new_queries": reflection["new_queries"]
        }
    else:
        # === Step 4: Synthesize final answer from retrieved documents ===
        print("\n🧠 Synthesizing final answer...")
        result = synthesize(question, docs)

        # Step 4.1: Assign new sequential citation IDs (1, 2, 3, ...)
        for idx, citation in enumerate(result["citations"]):
            citation["id"] = idx + 1

        # Step 4.2: Extract citation numbers from the original synthesized text
        used_citation_ids = list(map(int, re.findall(r"\[(\d+)\]", result["answer"])))

        # Step 4.3: Build a mapping from old to new citation IDs
        old_to_new_id = {old_id: new_id for new_id, old_id in enumerate(used_citation_ids, 1)}

        # Step 4.4: Update the citation metadata to reflect new IDs
        for citation in result["citations"]:
            citation["id"] = old_to_new_id.get(citation.get("id"), citation.get("id"))

        # Step 4.5: Replace old citation numbers in the final answer with new ones
        def replace_citation_ids(match):
            old_id = int(match.group(1))
            return f"[{old_to_new_id.get(old_id, old_id)}]"

        final_answer = re.sub(r"\[(\d+)\]", replace_citation_ids, result["answer"])

        print("\n✅ Synthesized Answer:\n")
        print(final_answer)

        output = {
            "status": "complete",
            "answer": final_answer,
            "citations": result["citations"]
        }

    # === Step 5: Output result in JSON format ===
    output_json = json.dumps(output, indent=2)
    print("\n📦 Final JSON Output:")
    print(output_json)

    # === Step 6: Save result to Redis for caching (TTL: 1 day) ===
    redis_client.set(cache_key, output_json, ex=86400)

    # Clean up older keys if cache exceeds limit
    all_keys = redis_client.keys(f"{CACHE_PREFIX}*")
    if len(all_keys) > CACHE_LIMIT:
        for key in sorted(all_keys)[:-CACHE_LIMIT]:
            redis_client.delete(key)

# === Kick off the async pipeline ===
asyncio.run(main())
