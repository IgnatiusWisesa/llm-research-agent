# src/main.py
import sys
import asyncio
import json
from agent.pipeline import run_pipeline

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"
    result = asyncio.run(run_pipeline(question))
    print(json.dumps(result, indent=2))
