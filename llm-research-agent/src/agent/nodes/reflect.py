import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai

from agent.types.document import Document
from agent.utils.slot_utils import extract_slots_llm

# Load environment variables (e.g. GEMINI_API_KEY from .env)
load_dotenv()

# Helper function to initialize the Gemini client
def get_genai_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def reflect(question: str, docs: List[Document]) -> Dict[str, Any]:
    """
    Analyze whether the retrieved documents can answer the given question
    by checking which information 'slots' are filled.

    Args:
        question (str): The user's original question.
        docs (List[Document]): List of retrieved web documents.

    Returns:
        Dict[str, Any]: A dictionary with:
            - "slots": list of expected information slots
            - "filled": list of slots that are answerable from the docs
            - "need_more": bool, whether more info is needed
            - "new_queries": list of follow-up queries to fill missing info
    """

    print(">>> reflect() called")
    print(">>> Question:", question)
    print(">>> Number of docs:", len(docs))

    # Step 1: Extract information slots from the question using Gemini
    slots = extract_slots_llm(question)
    print("🎯 Extracted slots:", slots)

    # Step 2: Build a readable context string from retrieved documents
    context = "\n\n".join(
        f"Title: {doc.title}\nSnippet: {doc.snippet}\nURL: {doc.url}"
        for doc in docs
    )

    # Step 3: Construct prompt for the LLM to check slot coverage
    prompt = f"""You're a helpful research assistant.

Your job is to check if the following retrieved search results are sufficient to answer the question by filling each required information slot.

Question: {question}

Slots: {json.dumps(slots)}

Search Results:
{context}

Instructions:
- "slots": list all required slots from the question.
- "filled": only include slots that can be confidently filled from the search results.
- If any important slot is missing or unclear, set "need_more" to true and include follow-up "new_queries".
- If all slots are filled, set "need_more" to false and leave "new_queries" empty.

Respond with valid JSON in this format:
{{
  "slots": [...],
  "filled": [...],
  "need_more": true/false,
  "new_queries": ["query1", "query2"]
}}
"""

    # Step 4: Call Gemini to get structured reflection
    client = get_genai_client()
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    # Step 5: Extract plain text from Gemini response
    text = response.text if hasattr(response, "text") else str(response)
    print("[reflect] Raw Gemini response:")
    print(text)

    # Step 6: Attempt to parse the JSON output from the model
    try:
        # Remove optional ```json markdown wrapper if present
        cleaned = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
        return json.loads(cleaned)
    except Exception as e:
        print("[reflect] Failed to parse response as JSON.")
        raise e
