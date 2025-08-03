from prometheus_client import start_http_server, Counter

MESSAGES_PROCESSED = Counter(
    'forecast_consumer_messages_total', 'Kafka messages processed'
)

def start_metrics_server():
    start_http_server(9000)
