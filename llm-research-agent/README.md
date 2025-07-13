# 🤖 LLM Research Agent (CLI)

A command-line research assistant that takes a natural language question, decomposes it into search queries, fetches real-time web results, reflects on coverage, and synthesizes a short, cited answer — powered by **Gemini** and **Google Custom Search**.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Gemini API](https://img.shields.io/badge/Gemini-1.5--flash-yellow)
![Redis Cache](https://img.shields.io/badge/Redis-enabled-red)

---

## ✨ Features

- ✅ **Query Generator** — Breaks the question into 3–5 useful search queries
- 🔍 **Web Search** — Uses Google CSE to retrieve real-time search results
- 🧠 **Reflective Check** — Uses Gemini to verify if all information slots are covered
- 🧾 **Synthesis Engine** — Answers questions with markdown-style citations
- 🔄 **Citation Remapping** — Compresses citation IDs (e.g., `[1, 2]` instead of `[3, 7]`)
- ⚡ **Redis Caching** — Caches previous results for speed and repeatability
- 🧪 **Unit Tests** — Covers normal use, timeout, no docs, retry, and 429 fallback

---

## 📁 Project Structure

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

## 🚀 Getting Started

### 1. Clone the Repo & Install Dependencies

```bash
git clone https://github.com/IgnatiusWisesa/llm-research-agent.git
cd llm-research-agent

pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure `.env`

```
GEMINI_API_KEY=your_google_genai_key
GOOGLE_API_KEY=your_google_search_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
REDIS_HOST=localhost
```

---

## ✅ Run Unit Tests

```bash
pytest -q tests/
```

Scenarios tested:
- ✔️ Happy path
- ⛔ No results
- 🔁 Two-round follow-up
- 🔄 Timeout + retries
- 🚫 HTTP 429 (rate-limited)

---

## 🧠 CLI Example

```bash
python src/main.py "Who won the 2022 FIFA World Cup?"
```

Output:

```json
{
  "status": "complete",
  "answer": "Argentina won the 2022 FIFA World Cup, defeating France 4-2 on penalties after a 3-3 draw. [1, 2]",
  "citations": [
    {
      "id": 1,
      "title": "2022 FIFA World Cup final - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_final"
    },
    {
      "id": 2,
      "title": "How Argentina won the 2022 World Cup - ESPN",
      "url": "https://www.espn.com/soccer/story/_/id/123456"
    }
  ]
}
```

---

## 🐍 Python API Usage

```python
from agent.nodes.synthesize import synthesize
from agent.types.document import Document

question = "Explain black holes like I'm five."

docs = [
    Document(
        title="What Is a Black Hole?",
        snippet="A black hole is a place in space where gravity is so strong nothing can escape.",
        url="https://example.com/black-hole"
    )
]

result = synthesize(question, docs)
print(result["answer"])
```

---

## 🧭 Architecture Flow

```text
    [User Question]
           ↓
  generate_queries()
           ↓
   WebSearchTool.run()
           ↓
        Documents
           ↓
         reflect()
        ↙       ↘
   enough?      suggest new queries
     ↓
 synthesize()
     ↓
[Answer + Citations]
     ↓
     Cache (Redis)
```

---

## 📦 Requirements

- Python 3.11+
- Redis (optional but recommended)
- Gemini API Key (via Google AI Studio)
- Google CSE API Key + Custom Search Engine ID

---

## 📄 License

MIT License  
© 2025 [Ignatius Wisesa](https://github.com/IgnatiusWisesa)