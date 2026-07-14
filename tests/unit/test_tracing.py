"""Unit tests for observability/tracing.py."""

import base64

import pytest
from opentelemetry.sdk.trace import TracerProvider

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.observability.tracing import (
    _parse_otlp_headers,
    configure_tracing,
)


def _get_exporter_headers(provider: TracerProvider, index: int) -> dict:
    """White-box helper: reads back the headers an exporter was configured
    with, since OTLPSpanExporter exposes no public getter for this."""
    processor = provider._active_span_processor._span_processors[index]
    return dict(processor.span_exporter._session.headers)


class TestParseOtlpHeaders:
    """Tests for _parse_otlp_headers()."""

    def test_none_returns_empty_dict(self) -> None:
        assert _parse_otlp_headers(None) == {}

    def test_empty_string_returns_empty_dict(self) -> None:
        assert _parse_otlp_headers("") == {}

    def test_parses_single_pair(self) -> None:
        assert _parse_otlp_headers("x-api-key=abc123") == {"x-api-key": "abc123"}

    def test_parses_multiple_pairs(self) -> None:
        result = _parse_otlp_headers("a=1,b=2")
        assert result == {"a": "1", "b": "2"}

    def test_ignores_malformed_pairs_without_equals(self) -> None:
        result = _parse_otlp_headers("a=1,garbage,b=2")
        assert result == {"a": "1", "b": "2"}


class TestConfigureTracing:
    """Tests for configure_tracing()."""

    def test_returns_none_when_nothing_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "otel_exporter_otlp_endpoint", None)
        monkeypatch.setattr(settings, "langfuse_otlp_endpoint", None)

        assert configure_tracing() is None

    def test_returns_provider_with_generic_otlp_exporter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            settings, "otel_exporter_otlp_endpoint", "https://tempo.example.com/otlp"
        )
        monkeypatch.setattr(settings, "otel_exporter_otlp_headers", "x-api-key=secret")
        monkeypatch.setattr(settings, "langfuse_otlp_endpoint", None)

        provider = configure_tracing()

        try:
            assert isinstance(provider, TracerProvider)
            headers = _get_exporter_headers(provider, 0)
            assert headers["x-api-key"] == "secret"
        finally:
            if provider is not None:
                provider.shutdown()

    def test_returns_provider_with_langfuse_exporter_and_basic_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "otel_exporter_otlp_endpoint", None)
        monkeypatch.setattr(
            settings,
            "langfuse_otlp_endpoint",
            "https://cloud.langfuse.com/api/public/otel",
        )
        monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")

        from pydantic import SecretStr

        monkeypatch.setattr(settings, "langfuse_secret_key", SecretStr("sk-lf-test"))

        provider = configure_tracing()

        try:
            assert isinstance(provider, TracerProvider)
            headers = _get_exporter_headers(provider, 0)
            expected_auth = base64.b64encode(b"pk-lf-test:sk-lf-test").decode()
            assert headers["Authorization"] == f"Basic {expected_auth}"
            assert headers["x-langfuse-ingestion-version"] == "4"
        finally:
            if provider is not None:
                provider.shutdown()

    def test_fans_out_to_both_exporters_when_both_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from pydantic import SecretStr

        monkeypatch.setattr(
            settings, "otel_exporter_otlp_endpoint", "https://tempo.example.com/otlp"
        )
        monkeypatch.setattr(
            settings,
            "langfuse_otlp_endpoint",
            "https://cloud.langfuse.com/api/public/otel",
        )
        monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
        monkeypatch.setattr(settings, "langfuse_secret_key", SecretStr("sk-lf-test"))

        provider = configure_tracing()

        try:
            assert isinstance(provider, TracerProvider)
            assert len(provider._active_span_processor._span_processors) == 2
        finally:
            if provider is not None:
                provider.shutdown()
