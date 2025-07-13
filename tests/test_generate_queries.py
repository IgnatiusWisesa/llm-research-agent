import sys
import os
from unittest.mock import MagicMock

# ✅ Add path to src so we can import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# ✅ Mock `google.genai` module BEFORE importing the real one
# This is important so that any import of genai.Client inside the function uses this mock instead

mock_genai = MagicMock()
mock_client = MagicMock()
mock_response = MagicMock()

# This mock response simulates Gemini returning a multi-line string of queries
mock_response.text = (
    "1. Who won 2022 World Cup?\n"
    "2. 2022 World Cup goal scorers\n"
    "3. Argentina vs France final score"
)

# Simulate Gemini client behavior
mock_client.models.generate_content.return_value = mock_response
mock_genai.Client.return_value = mock_client

# Inject our mock into sys.modules so any import of `google.genai` uses this
sys.modules["google.genai"] = mock_genai

# ✅ Now import the function to test
from agent.nodes.generate_queries import generate_queries

# ✅ Unit test
def test_generate_queries():
    queries = generate_queries("Who won the 2022 World Cup and who scored in the final?")
    print("🔍 Queries:", queries)

    assert isinstance(queries, list)
    assert len(queries) >= 3
