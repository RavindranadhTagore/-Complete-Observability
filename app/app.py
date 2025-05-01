from flask import Flask, request
import time
import logging
from prometheus_client import Counter, Summary, generate_latest
from jaeger_client import Config
import opentracing

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Prometheus metrics
REQUEST_COUNT = Counter("app_requests_total", "Total HTTP requests")
REQUEST_LATENCY = Summary("app_request_latency_seconds", "Request latency")

# Tracing with Jaeger
def init_tracer(service):
    config = Config(config={"sampler": {"type": "const", "param": 1},
                            "logging": True},
                    service_name=service)
    return config.initialize_tracer()

tracer = init_tracer("sample-app")
opentracing.tracer = tracer

@app.route("/")
@REQUEST_LATENCY.time()
def index():
    with tracer.start_span("index-span") as span:
        span.set_tag("endpoint", "/")
        logger.info("Handling request to /")
        time.sleep(0.5)
        REQUEST_COUNT.inc()
        return "Hello from observability app!"

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
