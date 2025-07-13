
# LLM Research Agent (CLI)

A command-line tool that takes a natural language question, decomposes it into search queries, fetches real-time web results, reflects on the completeness of the information, and synthesizes a cited answer — powered by Gemini and Google CSE.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- Query Generation — Breaks down a question into 3–5 relevant search queries.
- Web Search Tool — Uses Google Custom Search API to fetch relevant results.
- Reflective Slot Check — Uses Gemini to verify if all required information slots are filled.
- Synthesis Engine — Synthesizes a short, beginner-friendly answer with [Markdown-style citations].
- Redis Cache — Speeds up repeated queries with caching (max 50 entries).
- Unit Tests — Tests reflect function across 5 scenarios: normal, no docs, two-round, 429, timeout.

---

## Project Structure

```
llm-research-agent/
├── src/
│   ├── main.py
│   └── agent/
│       ├── nodes/
│       │   ├── generate_queries.py
│       │   ├── reflect.py
│       │   └── synthesize.py
│       ├── tools/
│       │   └── websearch.py
│       ├── types/
│       │   └── document.py
│       └── utils/
│           ├── slot_utils.py
│           └── cache_utils.py
├── tests/
│   ├── test_reflect.py
│   ├── test_queries.py
│   └── conftest.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone and Install

```bash
git clone https://github.com/IgnatiusWisesa/llm-research-agent.git
cd llm-research-agent

# Install dependencies
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env
```

### 2. Set Up .env

```
GEMINI_API_KEY=your_google_genai_key
GOOGLE_API_KEY=your_google_search_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
REDIS_HOST=localhost
```

---

## Run Tests

```bash
pytest -q tests/
```

Tests cover:

- Happy path
- No results
- HTTP 429 (rate limited)
- Timeout
- Two-round supplement (follow-up queries)

---

## CLI Usage Example

```bash
python src/main.py "Who won the 2022 FIFA World Cup and who scored the goals?"
```

Example Output:

```json
{
  "status": "complete",
  "answer": "Argentina won the 2022 World Cup final against France [1]. Lionel Messi and Kylian Mbappé were the top scorers [1].",
  "citations": [
    {
      "id": 1,
      "title": "Argentina wins World Cup",
      "url": "https://example.com/final"
    }
  ]
}
```

---

## Python API Usage

```python
from agent.nodes.synthesize import synthesize
from agent.types.document import Document

question = "Explain black holes like I'm five."

docs = [
    Document(
        title="What Is a Black Hole?",
        snippet="A black hole is a place in space where gravity is so strong that nothing—not even light—can escape.",
        url="https://example.com/black-hole"
    )
]

answer = synthesize(question, docs)
print(answer)
```

---

## Architecture Flow

graph TD
    A[User Question] --> B[generate_queries()]
    B --> C[WebSearchTool.run()]
    C --> D[Documents]
    D --> E[reflect()]
    E -->|need_more=False| F[synthesize()]
    E -->|need_more=True| G[Suggest new queries]
    F --> H[Final Answer + Citations]
    G --> H
    H --> I[Save to Redis Cache]

---

## Requirements

- Python 3.11+
- Redis (locally or via Docker)
- Google CSE + API Key
- Gemini API Key

---

## License

MIT License  
© 2025 Ignatius Wisesa
