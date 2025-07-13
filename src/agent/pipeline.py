import re
import json
import os
import redis
from agent.nodes.generate_queries import generate_queries
from agent.nodes.reflect import reflect
from agent.nodes.synthesize import synthesize
from agent.tools.websearch import WebSearchTool

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    db=0,
    decode_responses=True
)
CACHE_PREFIX = "llm_cache:"
CACHE_LIMIT = 50

async def run_pipeline(question: str) -> dict:
    normalized_question = question.strip().lower()
    cache_key = CACHE_PREFIX + normalized_question

    # 1. Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Generate queries
    queries = generate_queries(question)

    # 3. Search web
    search_tool = WebSearchTool()
    docs = await search_tool.run(queries)

    # 4. Reflect
    reflection = reflect(question, docs)

    if reflection["need_more"]:
        output = {
            "status": "need_more_info",
            "new_queries": reflection["new_queries"]
        }
    else:
        result = synthesize(question, docs)

        # Renumber citations to [1], [2], etc.
        for idx, citation in enumerate(result["citations"]):
            citation["id"] = idx + 1

        used_citation_ids = list(map(int, re.findall(r"\[(\d+)\]", result["answer"])))
        old_to_new_id = {old_id: new_id for new_id, old_id in enumerate(used_citation_ids, 1)}

        for citation in result["citations"]:
            citation["id"] = old_to_new_id.get(citation.get("id"), citation.get("id"))

        def replace(match):
            old_id = int(match.group(1))
            return f"[{old_to_new_id.get(old_id, old_id)}]"

        final_answer = re.sub(r"\[(\d+)\]", replace, result["answer"])

        output = {
            "status": "complete",
            "answer": final_answer,
            "citations": result["citations"]
        }

    # 5. Save to Redis
    redis_client.set(cache_key, json.dumps(output), ex=86400)

    # 6. Clean old cache keys
    all_keys = redis_client.keys(f"{CACHE_PREFIX}*")
    if len(all_keys) > CACHE_LIMIT:
        for key in sorted(all_keys)[:-CACHE_LIMIT]:
            redis_client.delete(key)

    return output
