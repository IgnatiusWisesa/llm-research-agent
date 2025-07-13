# metrics_server.py
from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

def create_metrics_app():
    app = Flask("dummy")
    application = DispatcherMiddleware(app, {
        "/metrics": make_wsgi_app()
    })
    return application

if __name__ == "__main__":
    app = create_metrics_app()
    run_simple("0.0.0.0", 8000, app)
