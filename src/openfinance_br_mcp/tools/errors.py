"""Error translation boundary between domain exceptions and MCP tools.

Domain code raises ``OpenFinanceError`` subclasses (see
``openfinance_br_mcp.exceptions``). MCP tool functions must instead
raise ``mcp.server.fastmcp.exceptions.ToolError``, which FastMCP turns
into a well-formed protocol-level tool error automatically. This
module provides a single decorator to perform that translation at the
tool boundary, replacing the previous ad hoc JSON-error construction
in ``BaseTool.safe_execute``.

Unexpected (non-domain) exceptions are intentionally left to propagate:
FastMCP already catches them and reports a generic tool error to the
client without crashing the server or leaking internal details.
"""

import functools
from collections.abc import Awaitable, Callable

import structlog
from mcp.server.fastmcp.exceptions import ToolError

from openfinance_br_mcp.exceptions import OpenFinanceError

log = structlog.get_logger(__name__)


def translate_errors[**P, T](
    fn: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    """Translates ``OpenFinanceError`` into ``ToolError`` for MCP tools.

    Args:
        fn: Async tool function to wrap.

    Returns:
        Wrapped function that raises ``ToolError`` on domain failures.
    """

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await fn(*args, **kwargs)
        except OpenFinanceError as exc:
            log.warning(
                "tool_domain_error", tool=fn.__name__, error=exc.message, code=exc.code
            )
            raise ToolError(exc.message) from exc

    return wrapper
