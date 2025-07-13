# src/main.py

import sys
import os
import asyncio
import json

# ✅ Force /app/src to be on PYTHONPATH (for Docker or CLI runs)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent.pipeline import run_pipeline
from agent.utils.telemetry import setup_tracer

if __name__ == "__main__":
    setup_tracer()

    question = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"
    result = asyncio.run(run_pipeline(question))
    print(json.dumps(result, indent=2))
