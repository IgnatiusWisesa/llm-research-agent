# 🤖 LLM Research Agent (CLI + API)

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
- 📊 **OpenTelemetry & Prometheus** — Collects tool call counts and latencies
- 🧪 **Unit Tests** — Covers normal use, timeout, no docs, retry, and 429 fallback

---

## 📁 Project Structure

```
llm-research-agent/
├── src/
│   ├── main.py
│   ├── api_server.py
│   └── agent/
│       ├── nodes/
│       ├── tools/
│       ├── types/
│       └── utils/
├── tests/
├── docker-compose.yaml
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

```env
GEMINI_API_KEY=your_google_genai_key
GOOGLE_API_KEY=your_google_search_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
REDIS_HOST=localhost
```

---

## 🧪 Run Unit Tests

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

## 🧠 CLI Usage

```bash
python src/main.py "Compare Kubernetes HPA and KEDA"
```

---

## 🖥️ Run the Backend API Server

```bash
uvicorn agent.api_server:app --reload --app-dir src
```

- FastAPI runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Metrics endpoint: [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)
- Query endpoint: `POST /api/query` with JSON body:

```json
{
  "question": "What is the difference between Kubernetes HPA and KEDA?"
}
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

## 📊 Monitoring & Metrics

This app uses `prometheus-fastapi-instrumentator` and `OpenTelemetry` to expose internal performance metrics.

- Prometheus-compatible metrics at: `GET /metrics`
- Includes:
  - GC stats
  - Tool call counts & latencies
  - HTTP request durations and status codes

---

## 📄 License

MIT License  
© 2025 [Ignatius Wisesa](https://github.com/IgnatiusWisesa)
