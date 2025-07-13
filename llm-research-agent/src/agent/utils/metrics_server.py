# metrics_server.py
from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

def create_metrics_app():
    # 🔧 We create a minimal Flask app (used only as a placeholder root app)
    app = Flask(__name__)  # Previously: Flask("dummy")

    # ⚙️ Combine Flask with Prometheus metrics at /metrics
    application = DispatcherMiddleware(app, {
        "/metrics": make_wsgi_app()
    })
    return application

if __name__ == "__main__":
    # 🚀 Run the combined WSGI app on port 8000
    app = create_metrics_app()
    run_simple("0.0.0.0", 8000, app)
