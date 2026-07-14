"""Unit tests for observability/logging_correlation.py."""

from opentelemetry.sdk.trace import TracerProvider

from openfinance_br_mcp.observability.logging_correlation import add_trace_context


def test_noop_when_no_span_is_active() -> None:
    event_dict = add_trace_context(None, "info", {"event": "test"})

    assert "trace_id" not in event_dict
    assert "span_id" not in event_dict


def test_injects_trace_and_span_id_inside_an_active_span() -> None:
    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    try:
        with tracer.start_as_current_span("test-span"):
            event_dict = add_trace_context(None, "info", {"event": "test"})
    finally:
        provider.shutdown()

    assert "trace_id" in event_dict
    assert "span_id" in event_dict
    assert len(event_dict["trace_id"]) == 32
    assert len(event_dict["span_id"]) == 16

    # Both should be valid hex strings.
    int(event_dict["trace_id"], 16)
    int(event_dict["span_id"], 16)


def test_preserves_existing_event_dict_fields() -> None:
    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    try:
        with tracer.start_as_current_span("test-span"):
            event_dict = add_trace_context(
                None, "info", {"event": "hello", "extra": 42}
            )
    finally:
        provider.shutdown()

    assert event_dict["event"] == "hello"
    assert event_dict["extra"] == 42
