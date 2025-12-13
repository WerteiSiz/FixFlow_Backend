"""Optional OpenTelemetry setup for Users service.
Non-fatal if libs missing.
"""
import os
import logging

logger = logging.getLogger("service_users.tracing")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
    OTEL_AVAILABLE = True
except Exception:
    OTEL_AVAILABLE = False


def setup_tracing(app=None, service_name="service_users"):
    if not OTEL_AVAILABLE:
        logger.debug("OpenTelemetry not available; tracing disabled")
        return None

    collector = os.getenv("OTEL_COLLECTOR_URL")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    if collector:
        endpoint = collector.rstrip('/') + '/v1/traces'
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    if app is not None:
        try:
            app.add_middleware(OpenTelemetryMiddleware)
        except Exception:
            logger.exception("Failed to add OpenTelemetry ASGI middleware")

    return trace.get_tracer(__name__)
