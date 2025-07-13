# telemetry.py

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import logging

def setup_tracer(service_name: str = "llm-agent"):
    """
    ✅ Initializes OpenTelemetry tracing for the service.
    
    This sets up a tracer provider that exports trace data to an OTLP-compatible
    collector (like Prometheus + Grafana or OpenTelemetry Collector).
    """

    try:
        # 🎯 Define the tracer provider with a resource identifying this service
        provider = TracerProvider(
            resource=Resource.create({SERVICE_NAME: service_name})
        )

        # 🚀 Configure the span exporter to send trace data to the OTLP HTTP endpoint
        processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
        )

        # 🔌 Register the span processor with the provider
        provider.add_span_processor(processor)

        # 🌐 Set this provider as the global tracer for the app
        trace.set_tracer_provider(provider)

    except Exception as e:
        # ⚠️ Gracefully handle failure if tracing is not available
        logging.warning(f"⚠️ Failed to initialize OpenTelemetry exporter: {e}")
