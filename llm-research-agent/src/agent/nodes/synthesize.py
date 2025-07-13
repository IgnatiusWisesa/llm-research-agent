import os
import json
import re
from typing import List
from dotenv import load_dotenv
from google import genai
from agent.types.document import Document

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def synthesize(question: str, docs: List[Document]) -> dict:
    print(">>> synthesize() called")
    print(">>> Question:", question)
    print(">>> Number of docs:", len(docs))

    # Step 1: Format documents into context
    context = ""
    for idx, doc in enumerate(docs, 1):
        context += f"[{idx}] Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}\n\n"

    # Step 2: Prompt with stronger instruction
    prompt = f"""You're a helpful research assistant.

Given the question and the documents below, return a JSON object with:
- "answer": a short factual answer under 80 words, using citation markers like [1], [2]
- "citations": an array of objects with "id", "title", and "url"

Only return valid JSON. Do NOT include backticks or markdown.
Do NOT say "Not enough information" or similar.
Do your best to write a helpful answer even if information is partial.

Question: {question}

Context:
{context}

Format:
{{
  "answer": "...",
  "citations": [
    {{
      "id": 1,
      "title": "...",
      "url": "..."
    }}
  ]
}}
"""

    # Step 3: Get Gemini response
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    raw = response.text.strip() if hasattr(response, "text") else str(response)
    print("📤 Raw Gemini response:", raw)

    try:
        # Step 4: Clean and parse JSON
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip("`\n ")
        json_start = raw.find("{")
        result = json.loads(raw[json_start:])

        original_answer = result.get("answer", "")
        raw_citations = result.get("citations", [])

        # Step 5: Extract citation IDs from [1], [2, 3], etc.
        matches = re.findall(r"\[(.*?)\]", original_answer)
        used_ids = set()
        for match in matches:
            for part in re.split(r"[,\s]+", match):
                if part.strip().isdigit():
                    used_ids.add(int(part.strip()))
        used_ids = sorted(used_ids)

        # Step 6: Map old → new compact IDs
        id_mapping = {old_id: new_id for new_id, old_id in enumerate(used_ids, 1)}

        def replace_citations(text: str, id_mapping: dict[int, int]) -> str:
            def repl(match):
                ids = match.group(1)
                new_ids = []
                for part in re.split(r"[,\s]+", ids):
                    if part.strip().isdigit():
                        old = int(part.strip())
                        if old in id_mapping:
                            new_ids.append(str(id_mapping[old]))
                return f"[{', '.join(new_ids)}]"
            return re.sub(r"\[(.*?)\]", repl, text)

        updated_answer = replace_citations(original_answer, id_mapping)

        # Step 7: Build final citation map
        final_citations = []
        for old_id in used_ids:
            for c in raw_citations:
                if c["id"] == old_id:
                    final_citations.append({
                        "id": id_mapping[old_id],
                        "title": c["title"],
                        "url": c["url"]
                    })
                    break

        # Step 8: Optional fallback — check if answer is vague
        if not updated_answer or "not enough" in updated_answer.lower() or len(updated_answer.split()) < 4:
            print("⚠️ Gemini returned insufficient answer.")
            return {
                "status": "incomplete",
                "answer": updated_answer,
                "citations": final_citations
            }

        return {
            "status": "complete",
            "answer": updated_answer,
            "citations": final_citations
        }

    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        return {
            "status": "incomplete",
            "answer": raw,
            "citations": []
        }
