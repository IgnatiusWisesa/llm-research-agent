# 🧠 LLM Research UI (Frontend)

A minimal frontend built with **React + Vite**, designed to interact with the [LLM Research Agent](https://github.com/IgnatiusWisesa/llm-research-agent).  
This interface allows users to input natural language questions and receive concise, cited answers powered by Gemini and real-time web search.

![React](https://img.shields.io/badge/React-18-blue?logo=react)
![Vite](https://img.shields.io/badge/Vite-5-purple?logo=vite)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Features

- 🌐 Simple research UI connected to FastAPI backend
- 🔁 Hot Module Replacement via Vite
- 🧼 Preconfigured with ESLint for code quality
- 💡 Instant citation-based answer rendering
- 🔒 CORS-ready (communicates with `http://localhost:8000`)

---

## 📦 Tech Stack

- **React 18**
- **Vite**
- **Axios** for HTTP requests
- **Tailwind CSS** (optional, if used)
- **FastAPI** backend (see [llm-research-agent](https://github.com/IgnatiusWisesa/llm-research-agent))

---

## 📂 Folder Structure

```
llm-research-ui/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Styles (Tailwind or custom)
├── .eslintrc.cjs           # Linting rules
├── vite.config.js          # Vite config
├── package.json
└── README.md
```

---

## 🛠️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/IgnatiusWisesa/llm-research-ui.git
cd llm-research-ui
```

### 2. Install dependencies

```bash
npm install
```

### 3. Run the development server

```bash
npm run dev
```

Then open `http://localhost:5173` in your browser.

> Make sure the backend (`llm-research-agent`) is also running at `http://localhost:8000`

---

## 🔄 Backend API Expectation

This frontend assumes the backend exposes:

```
POST /api/query
Content-Type: application/json

{
  "question": "Your natural language question"
}
```

Response:

```json
{
  "status": "complete",
  "answer": "The quick answer with [1] [2]",
  "citations": [
    { "id": 1, "title": "Title", "url": "https://..." }
  ]
}
```

---

## 🧪 Linting (Optional)

```bash
npm run lint
```

---

## 📄 License

MIT © 2025 Ignatius Wisesa
