"""structlog processor correlating log entries to the active OTel span.

The OTel SDK's own logs signal is still experimental in Python, so
this project keeps structlog->stdout as its log transport rather than
migrating logging onto OTel. This processor bridges the two: any log
call made while a span is active gets that span's trace_id/span_id
attached, so logs and traces can be joined in whatever backend
receives them.

A no-op when no span is active (e.g. tracing isn't configured, or the
log call happens outside any traced tool call) - trace.get_current_span()
then returns an invalid span context, which this simply skips.

Example:
    >>> structlog.configure(processors=[add_trace_context, ...])
"""

from typing import Any

from opentelemetry import trace


def add_trace_context(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Injects the active span's trace_id/span_id into a structlog event.

    Args:
        _logger: The wrapped logger (unused - required by structlog's
            processor signature).
        _method_name: The log method name (unused).
        event_dict: The structlog event dict being built.

    Returns:
        The same event_dict, with trace_id/span_id added if a span is
        currently active.
    """
    span_context = trace.get_current_span().get_span_context()
    if span_context.is_valid:
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict
