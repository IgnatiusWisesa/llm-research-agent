import sys
import os
import json
import types
import pytest
from types import SimpleNamespace

# 🔧 Inject a mock version of `google.genai` module before importing anything that uses it
# This prevents actual API calls during tests
mock_genai = types.ModuleType("genai")
mock_genai.Client = lambda api_key=None: SimpleNamespace(
    models=SimpleNamespace(
        generate_content=lambda model, contents: SimpleNamespace(
            text=json.dumps({
                "need_more": False,
                "new_queries": [],
                "slots": ["winner", "goal_scorers"],
                "filled": ["winner", "goal_scorers"]
            })
        )
    )
)

# 🧩 Register the full mock structure under the 'google' namespace
google = types.ModuleType("google")
google.genai = mock_genai
sys.modules["google"] = google
sys.modules["google.genai"] = mock_genai

# 📁 Add the src directory to the import path so agent modules can be resolved
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# ✅ Import the reflect logic and dependencies AFTER mocks are set
from agent.nodes.reflect import reflect, get_genai_client as get_client_reflect
from agent.utils.slot_utils import get_genai_client as get_client_slots
from agent.types.document import Document

# 🧪 Automatically patch the Gemini client for every test to use the mock
@pytest.fixture(autouse=True)
def patch_clients(monkeypatch):
    monkeypatch.setattr("agent.nodes.reflect.get_genai_client", lambda: mock_genai.Client())
    monkeypatch.setattr("agent.utils.slot_utils.get_genai_client", lambda: mock_genai.Client())

# ✅ Test ① Happy path — slots are correctly extracted and filled
def test_reflect_slots():
    question = "Who won the 2022 FIFA World Cup and who scored the goals in the final?"
    docs = [
        Document(
            title="Argentina win World Cup",
            snippet="Argentina defeated France...",
            url="https://example.com/final"
        )
    ]
    result = reflect(question, docs)
    assert result["need_more"] is False
    assert "winner" in result["slots"]
    assert "goal_scorers" in result["slots"]
    assert "winner" in result["filled"]
    assert "goal_scorers" in result["filled"]

# ✅ Test ② No results — reflect should still return valid structure
def test_reflect_no_result():
    question = "Wingspan of a dragon in Hogwarts?"
    docs = []
    result = reflect(question, docs)
    assert isinstance(result, dict)
    assert "slots" in result
    assert "filled" in result

# ✅ Test ③ Simulate HTTP 429 error — reflect should raise
def test_reflect_http_429(monkeypatch):
    def raise_429(*args, **kwargs):
        raise Exception("429: Too Many Requests")

    mock_error_client = lambda: SimpleNamespace(models=SimpleNamespace(generate_content=raise_429))
    monkeypatch.setattr("agent.nodes.reflect.get_genai_client", mock_error_client)
    monkeypatch.setattr("agent.utils.slot_utils.get_genai_client", mock_error_client)

    with pytest.raises(Exception, match="429"):
        reflect("Who is US president?", [])

# ✅ Test ④ Simulate timeout — should raise TimeoutError
def test_reflect_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise TimeoutError("Request timed out")

    mock_timeout_client = lambda: SimpleNamespace(models=SimpleNamespace(generate_content=raise_timeout))
    monkeypatch.setattr("agent.nodes.reflect.get_genai_client", mock_timeout_client)
    monkeypatch.setattr("agent.utils.slot_utils.get_genai_client", mock_timeout_client)

    with pytest.raises(TimeoutError):
        reflect("What causes rainbows?", [])

# ✅ Test ⑤ Incomplete slot fill — triggers follow-up queries
def test_reflect_two_round_supplement(monkeypatch):
    def return_incomplete_slots(*args, **kwargs):
        return SimpleNamespace(text=json.dumps({
            "slots": ["author", "year"],
            "filled": ["author"],
            "need_more": True,
            "new_queries": ["When was it published?"]
        }))

    mock_partial_client = lambda: SimpleNamespace(models=SimpleNamespace(generate_content=return_incomplete_slots))
    monkeypatch.setattr("agent.nodes.reflect.get_genai_client", mock_partial_client)
    monkeypatch.setattr("agent.utils.slot_utils.get_genai_client", mock_partial_client)

    docs = [Document(title="Fitzgerald", snippet="F. Scott Fitzgerald", url="...")]
    result = reflect("Who wrote Gatsby?", docs)
    assert result["need_more"] is True
    assert "new_queries" in result
    assert result["new_queries"] == ["When was it published?"]
