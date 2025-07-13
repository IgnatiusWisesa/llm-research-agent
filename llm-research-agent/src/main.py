# src/main.py

import sys
import os
import asyncio
import json

# ✅ Add the current directory (/app/src) to PYTHONPATH
# This ensures local modules can be imported correctly,
# whether you're running the script locally or inside Docker.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent.pipeline import run_pipeline
from agent.utils.telemetry import setup_tracer

if __name__ == "__main__":
    # 🔧 Initialize OpenTelemetry tracer for tool performance monitoring and observability
    setup_tracer()

    # ❓ Get the question from command-line arguments, or use a default one if not provided
    question = sys.argv[1] if len(sys.argv) > 1 else "What is AI?"

    # 🚀 Run the main pipeline asynchronously to process the question
    result = asyncio.run(run_pipeline(question))

    # 🖨️ Print the final result in nicely formatted JSON
    print(json.dumps(result, indent=2))
