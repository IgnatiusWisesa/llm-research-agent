# src/run_metrics_server.py

from prometheus_client import make_wsgi_app
from werkzeug.serving import run_simple

# ✅ Create a standalone WSGI app that exposes Prometheus metrics
# This will make metrics like tool call counts and latency accessible at /metrics
application = make_wsgi_app()

if __name__ == "__main__":
    # 🚀 Start a simple HTTP server on port 8000, listening on all network interfaces
    # You can access the metrics at http://localhost:8000/metrics
    run_simple("0.0.0.0", 8000, application)
