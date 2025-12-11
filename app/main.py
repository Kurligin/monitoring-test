from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'demo_api_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'demo_api_request_latency_seconds',
    'Request latency',
    ['endpoint']
)

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/api/hello")
def hello():
    start = time.time()
    # какая-то бизнес-логика
    time.sleep(0.1)
    latency = time.time() - start
    REQUEST_LATENCY.labels(endpoint="/api/hello").observe(latency)
    REQUEST_COUNT.labels(method="GET", endpoint="/api/hello", http_status="200").inc()
    return jsonify(message="Hello from monitored API")

# Заворачиваем Flask в WSGI-комбайн с /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)