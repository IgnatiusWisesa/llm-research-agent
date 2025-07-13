import os
import json
from typing import List
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file (especially GEMINI_API_KEY)
load_dotenv()

def get_genai_client():
    """
    Creates and returns a Gemini API client using the API key from environment variables.
    """
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_slots_llm(question: str) -> List[str]:
    """
    Uses Gemini to extract the relevant 'information slots' from a user's question.
    
    These slots are key pieces of information (e.g., 'winner', 'date') that need to be filled 
    in order to fully answer the question.

    Parameters:
    - question (str): the input question from the user

    Returns:
    - List[str]: a list of slot names extracted from the question
    """
    client = get_genai_client()

    # Construct a prompt that instructs the model to return only the required slots as a JSON array
    prompt = f"""
You are a helpful assistant that extracts relevant information "slots" from a user question.

Only return a JSON array of slot names that should be filled to fully answer the question.

Possible slots include (but are not limited to):
- "winner"
- "score"
- "goal_scorers"
- "location"
- "date"
- "referee"
- "teams"
- "top_scorer"
- "attendance"

Do not explain your answer. Just return a JSON list of slot strings.

Question: {question}
"""

    # Send the prompt to Gemini
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    # Extract the raw text response from Gemini
    text = response.text.strip() if hasattr(response, "text") else str(response)
    print("📤 Raw slots from LLM:", text)

    # Try to parse the JSON string into a Python list
    try:
        slots = json.loads(text)
        # Ensure all items in the list are strings
        return [slot for slot in slots if isinstance(slot, str)]
    except Exception as e:
        print("⚠️ Failed to parse slot list:", e)
        return []
