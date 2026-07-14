"""Manual OpenTelemetry spans for MCP tool calls.

There is no official MCP instrumentation to auto-generate these spans
(unlike httpx/asyncio, which have off-the-shelf
``opentelemetry-instrumentation-*`` packages) - this wraps each tool
function in a span named after the tool, mirroring how
``tools/errors.py::translate_errors`` wraps every tool function today.

Only structural attributes are recorded on the span: the tool's name
and, when present, the ``bank`` argument. Never ``subject_id`` (a
CPF - PII) or any bank data (account numbers, transaction
descriptions, amounts) - this module has no visibility into response
bodies at all, by design.

Example:
    >>> @traced_tool
    ... @translate_errors
    ... async def my_tool(subject_id: str, bank: BankId, ctx) -> ...:
    ...     ...
"""

import functools
from collections.abc import Awaitable, Callable

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

_tracer = trace.get_tracer("openfinance_br_mcp.tools")


def traced_tool[**P, T](fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Wraps an MCP tool function in a span named after the tool.

    Args:
        fn: Async tool function to wrap. Apply this as the outermost
            decorator, above ``@translate_errors``, so the span covers
            the domain-error translation too.

    Returns:
        Wrapped function producing one span per call.
    """

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with _tracer.start_as_current_span(f"mcp.tool.{fn.__name__}") as span:
            bank = kwargs.get("bank")
            if bank is not None:
                span.set_attribute("openfinance.bank_id", str(bank))
            result = await fn(*args, **kwargs)
            span.set_status(Status(StatusCode.OK))
            return result

    return wrapper
