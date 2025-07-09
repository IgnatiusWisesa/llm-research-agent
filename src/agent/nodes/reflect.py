import os
import json
import re
from typing import List, Dict, Any
from google import genai
from agent.types.document import Document
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def reflect(question: str, docs: List[Document]) -> Dict[str, Any]:
    print(">>> reflect() called")
    print(">>> Question:", question)
    print(">>> Number of docs:", len(docs))

    context = "\n\n".join(
        f"Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}" for doc in docs
    )

    prompt = f"""You're a helpful research assistant.

Here is the original question: {question}

And here are the search results:
{context}

Are the documents above sufficient to answer the question?

If YES, respond with:
{{
  "need_more": false,
  "new_queries": []
}}

If NOT, respond with:
{{
  "need_more": true,
  "new_queries": ["query1", "query2"]
}}

Only return valid JSON.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    text = response.text if hasattr(response, "text") else str(response)
    print("[reflect] Raw Gemini response:")
    print(text)

    try:
        # Bersihin kode blok markdown ```json ... ```
        cleaned = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
        return json.loads(cleaned)
    except Exception as e:
        print("[reflect] Failed to parse response as JSON. Raw response above.")
        raise e
