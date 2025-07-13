from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.pipeline import run_pipeline

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Instrument Prometheus
Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class QueryRequest(BaseModel):
    question: str

# Endpoint utama
@app.post("/api/query")
async def query_llm(request: QueryRequest):
    result = await run_pipeline(request.question)
    return result
