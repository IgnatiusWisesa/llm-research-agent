# telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import logging

def setup_tracer(service_name: str = "llm-agent"):
    try:
        provider = TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception as e:
        logging.warning(f"⚠️ Failed to initialize OpenTelemetry exporter: {e}")
