import re
import json
import os
import redis
from agent.nodes.generate_queries import generate_queries
from agent.nodes.reflect import reflect
from agent.nodes.synthesize import synthesize
from agent.tools.websearch import WebSearchTool
from opentelemetry import trace
from agent.utils.metrics import TOOL_CALL_COUNT, TOOL_LATENCY

tracer = trace.get_tracer(__name__)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    db=0,
    decode_responses=True
)

CACHE_PREFIX = "llm_cache:"
CACHE_LIMIT = 50
MAX_REFLECTION_ROUNDS = 2

async def run_pipeline(question: str) -> dict:
    with tracer.start_as_current_span("run_pipeline"):
        normalized_question = question.strip().lower()
        cache_key = CACHE_PREFIX + normalized_question

        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        with tracer.start_as_current_span("generate_queries"):
            TOOL_CALL_COUNT.labels("generate_queries").inc()
            queries = generate_queries(question)

        with tracer.start_as_current_span("initial_web_search"):
            TOOL_CALL_COUNT.labels("web_search").inc()
            with TOOL_LATENCY.labels("web_search").time():
                search_tool = WebSearchTool()
                docs = await search_tool.run(queries)

        rounds = 0
        while rounds < MAX_REFLECTION_ROUNDS:
            with tracer.start_as_current_span(f"reflect_round_{rounds+1}"):
                TOOL_CALL_COUNT.labels("reflect").inc()
                reflection = reflect(question, docs)

            if not reflection.get("need_more") or not reflection.get("new_queries"):
                break

            print(f"🔄 Reflection round {rounds+1}: need more info, expanding...")

            with tracer.start_as_current_span(f"web_search_round_{rounds+1}"):
                TOOL_CALL_COUNT.labels("web_search").inc()
                with TOOL_LATENCY.labels("web_search").time():
                    extra_docs = await search_tool.run(reflection["new_queries"])
                    docs += extra_docs
            rounds += 1

        with tracer.start_as_current_span("synthesize"):
            TOOL_CALL_COUNT.labels("synthesize").inc()
            result = synthesize(question, docs)

        # Normalize citations
        matches = re.findall(r"\[(.*?)\]", result["answer"])
        used_ids = set()
        for m in matches:
            for part in re.split(r"[,\s]+", m):
                if part.isdigit():
                    used_ids.add(int(part))
        used_ids = sorted(used_ids)
        id_map = {old: new for new, old in enumerate(used_ids, 1)}

        def replace(match):
            parts = match.group(1)
            new_parts = []
            for p in re.split(r"[,\s]+", parts):
                if p.isdigit():
                    new_parts.append(str(id_map.get(int(p), p)))
            return f"[{', '.join(new_parts)}]"

        final_answer = re.sub(r"\[(.*?)\]", replace, result["answer"])

        final_citations = []
        for citation in result["citations"]:
            old_id = citation["id"]
            if old_id in id_map:
                final_citations.append({
                    "id": id_map[old_id],
                    "title": citation["title"],
                    "url": citation["url"]
                })

        output = {
            "status": "complete",
            "answer": final_answer,
            "citations": final_citations
        }

        redis_client.set(cache_key, json.dumps(output), ex=86400)

        all_keys = redis_client.keys(f"{CACHE_PREFIX}*")
        if len(all_keys) > CACHE_LIMIT:
            for key in sorted(all_keys)[:-CACHE_LIMIT]:
                redis_client.delete(key)

        return output

