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

# Redis setup
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    db=0,
    decode_responses=True
)
CACHE_PREFIX = "llm_cache:"
CACHE_LIMIT = 50

# Ambil pertanyaan dari argumen CLI atau default
question = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"
normalized_question = question.strip().lower()
cache_key = CACHE_PREFIX + normalized_question

async def main():
    # Step 0: Cek Redis Cache
    cached = redis_client.get(cache_key)
    if cached:
        print("\n💾 Loaded from Redis cache:\n")
        print(cached)
        return

    # Step 1: generate queries
    queries = generate_queries(question)
    print("\n🧩 Generated Queries:")
    for q in queries:
        print("-", q)

    # Step 2: run web search
    search_tool = WebSearchTool()
    docs = await search_tool.run(queries)
    print("\n🔍 Search Results:")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.title}\n   {doc.snippet}\n   {doc.url}\n")

    # Step 3: reflect
    print("\n🪞 Calling reflect()...")
    reflection = reflect(question, docs)
    print("\n🪞 Reflect Result:")
    print(reflection)

    if reflection["need_more"]:
        print("\n🔁 Not enough info. Consider running new queries:")
        for q in reflection["new_queries"]:
            print("-", q)
        output = {
            "status": "need_more_info",
            "new_queries": reflection["new_queries"]
        }
    else:
        # Step 4: synthesize
        print("\n🧠 Synthesizing final answer...")
        result = synthesize(question, docs)

        # Assign sequential citation IDs
        for idx, citation in enumerate(result["citations"]):
            citation["id"] = idx + 1

        # Extract citation numbers from answer
        used_citation_ids = list(map(int, re.findall(r"\[(\d+)\]", result["answer"])))

        # Create mapping from old ID to new sequential ID
        old_to_new_id = {old_id: new_id for new_id, old_id in enumerate(used_citation_ids, 1)}

        # Update citation metadata with new IDs
        for citation in result["citations"]:
            citation["id"] = old_to_new_id.get(citation.get("id"), citation.get("id"))

        # Replace citation references in the answer text
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

    # Output final JSON
    output_json = json.dumps(output, indent=2)
    print("\n📦 Final JSON Output:")
    print(output_json)

    # Save to Redis with TTL and trim cache size
    redis_client.set(cache_key, output_json, ex=86400)
    all_keys = redis_client.keys(f"{CACHE_PREFIX}*")
    if len(all_keys) > CACHE_LIMIT:
        for key in sorted(all_keys)[:-CACHE_LIMIT]:
            redis_client.delete(key)

# Run the pipeline
asyncio.run(main())
