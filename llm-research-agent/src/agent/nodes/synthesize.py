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

    # Format documents
    context = ""
    for idx, doc in enumerate(docs, 1):
        context += f"[{idx}] Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}\n\n"

    prompt = f"""You're a helpful research assistant.

Given the question and the documents below, return a JSON object with:
- "answer": a short factual answer under 80 words, using citation markers like [1], [2]
- "citations": an array of objects with "id", "title", and "url"

Only return valid JSON. Do NOT include backticks or markdown.

Question: {question}

Context:
{context}

Format:
{{
  "answer": "...",
  "citations": [
    {{
      "id": 3,
      "title": "...",
      "url": "..."
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    raw = response.text.strip() if hasattr(response, "text") else str(response)
    print("📤 Raw Gemini response:", raw)

    try:
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        raw = raw.strip("`\n ")

        json_start = raw.find("{")
        result = json.loads(raw[json_start:])
        original_answer = result.get("answer", "")
        raw_citations = result.get("citations", [])

        # --- Normalize citation IDs ---
        # Extract [x], [x, y], etc. from answer
        matches = re.findall(r"\[(.*?)\]", original_answer)
        used_ids = set()
        for match in matches:
            for part in re.split(r"[,\s]+", match):
                if part.strip().isdigit():
                    used_ids.add(int(part.strip()))
        used_ids = sorted(used_ids)

        # Remap original ID → local [1, 2, 3]
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

        # Create final compact citation list
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
