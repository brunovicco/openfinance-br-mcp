"""Unit tests for observability/tool_tracing.py.

Deliberately avoids ``trace.set_tracer_provider()``: the OTel API only
allows setting the *global* provider once per process (subsequent
calls silently no-op with a warning), which would make these tests
order-dependent on whatever test_tracing.py's own
``configure_tracing()`` calls already did earlier in the same pytest
session. Instead, each test monkeypatches
``tool_tracing._tracer`` directly with a tracer bound to a throwaway
provider - fully isolated, no shared global state.
"""

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import StatusCode

from openfinance_br_mcp.observability import tool_tracing
from openfinance_br_mcp.observability.tool_tracing import traced_tool


@pytest.fixture
def span_exporter(monkeypatch: pytest.MonkeyPatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(tool_tracing, "_tracer", provider.get_tracer("test"))
    try:
        yield exporter
    finally:
        provider.shutdown()


class TestTracedTool:
    """Tests for the traced_tool decorator."""

    @pytest.mark.asyncio
    async def test_passes_through_the_return_value(self, span_exporter) -> None:
        @traced_tool
        async def my_tool(x: int) -> int:
            return x * 2

        result = await my_tool(21)

        assert result == 42

    @pytest.mark.asyncio
    async def test_reraises_the_original_exception(self, span_exporter) -> None:
        @traced_tool
        async def my_tool() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            await my_tool()

    @pytest.mark.asyncio
    async def test_creates_a_span_named_after_the_tool(self, span_exporter) -> None:
        @traced_tool
        async def list_accounts(subject_id: str) -> str:
            return subject_id

        await list_accounts("12345678900")

        spans = span_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "mcp.tool.list_accounts"

    @pytest.mark.asyncio
    async def test_records_bank_id_attribute_when_present(self, span_exporter) -> None:
        @traced_tool
        async def list_accounts(subject_id: str, bank: str) -> str:
            return subject_id

        await list_accounts(subject_id="123", bank="nubank")

        spans = span_exporter.get_finished_spans()
        assert spans[0].attributes["openfinance.bank_id"] == "nubank"

    @pytest.mark.asyncio
    async def test_omits_bank_id_attribute_when_absent(self, span_exporter) -> None:
        @traced_tool
        async def list_investments(subject_id: str) -> str:
            return subject_id

        await list_investments(subject_id="123")

        spans = span_exporter.get_finished_spans()
        assert "openfinance.bank_id" not in spans[0].attributes

    @pytest.mark.asyncio
    async def test_never_records_subject_id_on_the_span(self, span_exporter) -> None:
        """subject_id is a CPF - PII - and must never end up as a span
        attribute, unlike bank (a non-sensitive identifier)."""

        @traced_tool
        async def list_accounts(subject_id: str, bank: str) -> str:
            return subject_id

        await list_accounts(subject_id="12345678900", bank="nubank")

        spans = span_exporter.get_finished_spans()
        for value in spans[0].attributes.values():
            assert "12345678900" not in str(value)

    @pytest.mark.asyncio
    async def test_marks_span_as_error_on_exception(self, span_exporter) -> None:
        @traced_tool
        async def failing_tool() -> None:
            raise RuntimeError("bank unavailable")

        with pytest.raises(RuntimeError):
            await failing_tool()

        spans = span_exporter.get_finished_spans()
        assert spans[0].status.status_code == StatusCode.ERROR
        assert len(spans[0].events) == 1  # the recorded exception event
        assert spans[0].events[0].name == "exception"

    @pytest.mark.asyncio
    async def test_marks_span_as_ok_on_success(self, span_exporter) -> None:
        @traced_tool
        async def my_tool() -> str:
            return "ok"

        await my_tool()

        spans = span_exporter.get_finished_spans()
        assert spans[0].status.status_code == StatusCode.OK
