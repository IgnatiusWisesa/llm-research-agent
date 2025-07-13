import os
import re
from typing import List
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env (e.g. GEMINI_API_KEY)
load_dotenv()

# Initialize the Gemini client using the API key from environment
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_queries(question: str) -> List[str]:
    """
    Given a natural language question from the user,
    generate 3–5 concise and distinct web search queries
    using the Gemini LLM.

    Args:
        question (str): The original question from the user.

    Returns:
        List[str]: A list of 3–5 suggested web search queries.
    """

    # Prompt template instructing the model to return queries only, no explanation
    prompt = f"""
You are a helpful assistant.

Break down the user's question into 3 to 5 distinct English web search queries.

Only output each query on its own line. Avoid explanations.

User question:
{question}
"""

    # Call Gemini to generate the queries
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"parts": [{"text": prompt}]}]
    )

    # Extract the raw text from the model's response
    raw_output = response.text if hasattr(response, "text") else str(response)

    # Clean and normalize each line into a proper search query
    queries = [
        re.sub(r"^\d+\.\s*", "", q.strip("-• \n"))  # remove list numbering/bullets
        for q in raw_output.strip().split("\n")
        if q.strip()  # skip empty lines
    ]

    return queries
