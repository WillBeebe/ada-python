
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

# from opentelemetry.sdk.metrics.export import InMemoryMetricReader
# from prometheus_client import start_http_server

prometheus_exporter = PrometheusMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[prometheus_exporter]))
meter = metrics.get_meter(__name__)

generate_text_counter = meter.create_counter(
    name="generate_text_counter",
    description="Total number of times generate_text is called",
    unit="1",
)

call_tool_counter = meter.create_counter(
    name="call_tool_counter",
    description="Total number of times a tool is called",
    unit="1",
)

# coordinator_queue_length = meter.create_gauge(
#     "coordinator_queue_length",
#     unit="items",
#     description="The active config version for each configuration",
# )

# def start_metrics_server():
#   start_http_server(port=8000, addr="0.0.0.0")
