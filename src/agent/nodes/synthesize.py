import os
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

    # Build citation context with [1], [2], ...
    context = ""
    for idx, doc in enumerate(docs, 1):
        context += f"[{idx}] Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}\n\n"

    prompt = f"""You're a helpful research assistant.

Here is the question: {question}

And here are the search results:
{context}

Please provide a clear, concise, beginner-friendly answer to the question above,
synthesizing the most relevant and useful information. 
Use Markdown-style numeric citations like [1], [2] referring to the sources.
Keep the answer under 80 words.
Only output the answer sentence, no explanation or prefix.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    answer = response.text.strip() if hasattr(response, "text") else str(response)
    print("📤 Raw Answer from Gemini:", answer)

    # Extract all citation numbers, e.g. from [1], [4, 5], [6, 8, 11, 12, 21, 22]
    matches = re.findall(r"\[(.*?)\]", answer)
    used_ids = set()
    for match in matches:
        for part in re.split(r"[,\s]+", match):
            part = part.strip()
            if part.isdigit():
                used_ids.add(int(part))
    used_ids = sorted(used_ids)
    print("🔢 Used citation IDs in answer:", used_ids)

    # Mapping old_id → new_id [1], [2], ...
    id_mapping = {old: new for new, old in enumerate(used_ids, 1)}
    print("📑 ID mapping (old → new):", id_mapping)

    # Replace citations in answer text using mapping
    def replace_citations(text: str, id_mapping: dict[int, int]) -> str:
        def repl(match):
            ids = match.group(1)
            new_ids = []
            for part in re.split(r"[,\s]+", ids):
                if part.strip().isdigit():
                    old_id = int(part.strip())
                    if old_id in id_mapping:
                        new_ids.append(str(id_mapping[old_id]))
            return f"[{', '.join(new_ids)}]"
        return re.sub(r"\[(.*?)\]", repl, text)

    updated_answer = replace_citations(answer, id_mapping)

    # Build citation map
    citation_map = []
    for old_id in used_ids:
        if 1 <= old_id <= len(docs):
            doc = docs[old_id - 1]
            citation_map.append({
                "id": id_mapping[old_id],
                "title": doc.title,
                "url": doc.url
            })
        else:
            print(f"⚠️ Skipping invalid citation [{old_id}] (docs length = {len(docs)})")

    print("📚 Final citation map:", citation_map)

    return {
        "status": "complete",
        "answer": updated_answer,
        "citations": citation_map
    }
