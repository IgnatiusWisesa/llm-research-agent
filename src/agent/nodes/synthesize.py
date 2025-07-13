import os
import re
from typing import List
from dotenv import load_dotenv
from google import genai
from agent.types.document import Document

# Load environment variables (e.g. GEMINI_API_KEY from .env)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def synthesize(question: str, docs: List[Document]) -> dict:
    """
    Synthesizes a short answer from a list of retrieved documents using Gemini.

    The output includes:
    - a concise answer under 80 words,
    - markdown-style citations like [1], [2],
    - a citation map with links to the original documents.

    Args:
        question (str): The user's original research question.
        docs (List[Document]): The list of documents to synthesize from.

    Returns:
        dict: {
            "status": "complete",
            "answer": str,
            "citations": List[Dict]
        }
    """

    print(">>> synthesize() called")
    print(">>> Question:", question)
    print(">>> Number of docs:", len(docs))

    # Step 1: Format documents into numbered context (e.g., [1], [2], ...)
    context = ""
    for idx, doc in enumerate(docs, 1):
        context += f"[{idx}] Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}\n\n"

    # Step 2: Prepare prompt for Gemini
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

    # Step 3: Send prompt to Gemini
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    # Step 4: Extract answer text from Gemini response
    answer = response.text.strip() if hasattr(response, "text") else str(response)
    print("📤 Raw Answer from Gemini:", answer)

    # Step 5: Extract all citation IDs from the answer (e.g. [1], [3, 4], etc.)
    matches = re.findall(r"\[(.*?)\]", answer)
    used_ids = set()
    for match in matches:
        for part in re.split(r"[,\s]+", match):
            part = part.strip()
            if part.isdigit():
                used_ids.add(int(part))
    used_ids = sorted(used_ids)
    print("🔢 Used citation IDs in answer:", used_ids)

    # Step 6: Create a mapping from original ID → compact ID
    id_mapping = {old: new for new, old in enumerate(used_ids, 1)}
    print("📑 ID mapping (old → new):", id_mapping)

    # Step 7: Replace citations in the answer text with compact IDs
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

    # Step 8: Build the final citation map (ID + title + URL)
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

    # Step 9: Return structured answer
    return {
        "status": "complete",
        "answer": updated_answer,
        "citations": citation_map
    }
