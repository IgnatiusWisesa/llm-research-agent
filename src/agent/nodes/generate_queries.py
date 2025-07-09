import os
from google import genai
import re

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_queries(question: str) -> list[str]:
    # print("[generate_queries] using Gemini")

    prompt = (
        "Break down the user's question into 3 to 5 distinct English web search queries.\n\n"
        f"User question: {question}\n"
        "Search queries:\n"
    )

    response = client.models.generate_content(
        model="gemini-1.5-flash",  # atau "gemini-1.5-pro", tergantung quota-mu
        contents=[{"parts": [{"text": prompt}]}]
    )

    output = response.text
    queries = [
        re.sub(r"^\d+\.\s*", "", q.strip("-• \n"))
        for q in output.strip().split("\n")
        if q.strip()
    ]

    return queries
