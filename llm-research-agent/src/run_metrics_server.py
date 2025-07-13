# src/run_metrics_server.py

from prometheus_client import make_wsgi_app
from werkzeug.serving import run_simple

# Only expose Prometheus WSGI app
application = make_wsgi_app()

if __name__ == "__main__":
    run_simple("0.0.0.0", 8000, application)
