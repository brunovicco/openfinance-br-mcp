"""OpenTelemetry tracing setup: fan-out to a generic OTLP backend and/or
Langfuse from a single TracerProvider.

Tracing is entirely off by default: ``configure_tracing()`` returns
None (and instruments nothing) unless at least one of
``OTEL_EXPORTER_OTLP_ENDPOINT`` or ``LANGFUSE_OTLP_ENDPOINT`` is
configured, so the mock/dev loop stays free of tracing overhead and
noise.

Both exporters are plain OTLP/HTTP (Langfuse doesn't support gRPC,
which keeps both exporters on the same code path). Langfuse's auth
scheme is Basic Auth with base64(public_key:secret_key), plus an
``x-langfuse-ingestion-version`` header.

The OTel SDK's log signal is still experimental in Python - this
project keeps ``structlog``->stdout as its log transport and instead
correlates logs to traces via
``observability.logging_correlation.add_trace_context``, a structlog
processor that injects the active span's trace_id/span_id.

Example:
    >>> provider = configure_tracing()
    >>> if provider is not None:
    ...     ...  # tracing is active
"""

import base64

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from openfinance_br_mcp.config import settings

log = structlog.get_logger(__name__)


def _traces_endpoint(base_url: str) -> str:
    """Appends the OTLP/HTTP traces path to a collector base URL.

    ``OTLPSpanExporter`` only auto-appends '/v1/traces' when its
    endpoint is picked up implicitly from the OTEL_EXPORTER_OTLP_ENDPOINT
    env var - passing ``endpoint=`` explicitly (required here so two
    independent exporters, generic + Langfuse, can be configured from
    one process) bypasses that entirely. Without this, spans get
    POSTed to the bare collector URL (e.g. '.../api/public/otel'),
    which Langfuse rejects with 404 - it only accepts traffic at
    '.../api/public/otel/v1/traces'.

    Args:
        base_url: The collector's base URL (Langfuse or generic OTLP).

    Returns:
        The base URL with '/v1/traces' appended.
    """
    return f"{base_url.rstrip('/')}/v1/traces"


def _parse_otlp_headers(raw: str | None) -> dict[str, str]:
    """Parses OTel's standard 'key1=value1,key2=value2' header string.

    Args:
        raw: The raw header string, or None.

    Returns:
        A headers dict, empty if raw is None/empty.
    """
    if not raw:
        return {}
    headers: dict[str, str] = {}
    for pair in raw.split(","):
        if "=" not in pair:
            continue
        key, _, value = pair.partition("=")
        headers[key.strip()] = value.strip()
    return headers


def configure_tracing() -> TracerProvider | None:
    """Builds a TracerProvider fanning out to whichever exporters are set.

    Also registers httpx/asyncio auto-instrumentation and DSPy
    instrumentation (for the transaction categorizer) against the same
    provider, and installs it as the global tracer provider.

    Returns:
        The configured TracerProvider, or None if neither
        OTEL_EXPORTER_OTLP_ENDPOINT nor LANGFUSE_OTLP_ENDPOINT is set -
        tracing stays off, nothing is instrumented.
    """
    if settings.otel_exporter_otlp_endpoint is None and (
        settings.langfuse_otlp_endpoint is None
    ):
        return None

    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_endpoint is not None:
        exporter = OTLPSpanExporter(
            endpoint=_traces_endpoint(str(settings.otel_exporter_otlp_endpoint)),
            headers=_parse_otlp_headers(settings.otel_exporter_otlp_headers),
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        log.info(
            "otel_generic_exporter_configured",
            endpoint=str(settings.otel_exporter_otlp_endpoint),
        )

    if settings.langfuse_otlp_endpoint is not None:
        assert settings.langfuse_public_key is not None
        assert settings.langfuse_secret_key is not None
        auth_string = (
            f"{settings.langfuse_public_key}:"
            f"{settings.langfuse_secret_key.get_secret_value()}"
        )
        auth_header = base64.b64encode(auth_string.encode()).decode()
        exporter = OTLPSpanExporter(
            endpoint=_traces_endpoint(str(settings.langfuse_otlp_endpoint)),
            headers={
                "Authorization": f"Basic {auth_header}",
                "x-langfuse-ingestion-version": "4",
            },
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        log.info("otel_langfuse_exporter_configured")

    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    AsyncioInstrumentor().instrument(tracer_provider=provider)
    _instrument_dspy(provider)

    return provider


def _instrument_dspy(provider: TracerProvider) -> None:
    """Instruments DSPy's LM calls (the transaction categorizer).

    Args:
        provider: The TracerProvider to attach spans to.
    """
    from openinference.instrumentation import TraceConfig
    from openinference.instrumentation.dspy import DSPyInstrumentor

    trace_config = TraceConfig(
        hide_inputs=not settings.otel_capture_dspy_content,
        hide_outputs=not settings.otel_capture_dspy_content,
    )
    DSPyInstrumentor().instrument(tracer_provider=provider, config=trace_config)
