from prometheus_client import Counter, Histogram, Info
import time

# Metrics
PREDICTION_REQUEST_COUNT = Counter(
    'prediction_requests_total',
    'Total number of prediction requests'
)

PREDICTION_LATENCY = Histogram(
    'prediction_latency_seconds',
    'Time spent processing prediction requests',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

MODEL_INFO = Info('model_info', 'Information about the current model')

class MonitoringMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics only for prediction endpoints
        if request.url.path == "/predict":
            PREDICTION_REQUEST_COUNT.inc()
            PREDICTION_LATENCY.observe(time.time() - start_time)
        
        return response