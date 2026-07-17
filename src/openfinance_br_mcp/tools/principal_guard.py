"""Decorator enforcing the MCP-principal / subject_id binding on tools.

See ``auth/principal_binding.py`` for the rationale. Apply this
decorator to every tool that receives a ``subject_id`` argument and
operates on bank data (list_accounts, get_balance, list_transactions,
list_credit_cards, get_credit_card_bills, list_investments,
list_funds, list_variable_incomes, list_treasure_titles,
list_pix_keys, initiate_pix, check_consent_status, revoke_consent).
``start_consent`` and ``complete_consent`` are deliberately excluded:
no binding can exist yet before a consent flow has ever completed for
that subject_id (complete_consent is where the binding is first
created - see tools/consent.py), and starting a consent flow for a
CPF the caller doesn't control cannot itself leak data - the flow
still requires completing a real login at the bank.

Example:
    >>> @traced_tool
    ... @translate_errors
    ... @require_principal_binding
    ... async def list_accounts(subject_id: str, bank: BankId, ctx) -> ...:
    ...     ...
"""

import functools
from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from mcp.server.auth.middleware.auth_context import get_access_token

from openfinance_br_mcp.auth.mcp_principal import principal_from_access_token
from openfinance_br_mcp.exceptions import ValidationError

log = structlog.get_logger(__name__)


def require_principal_binding[**P, T](
    fn: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    """Rejects calls whose subject_id isn't bound to the current MCP principal.

    A no-op whenever ``get_access_token()`` returns None - true for the
    'stdio' transport, and for an HTTP deployment intentionally running
    without MCP client OAuth (which config.py restricts to a loopback
    bind host). In both cases there is no separate principal identity
    to check a binding against.

    Args:
        fn: Async tool function to wrap. Must accept ``subject_id`` and
            ``ctx`` as keyword arguments, matching every tool in this
            project (FastMCP always invokes tools with keyword
            arguments matching their parameter names).

    Returns:
        Wrapped function that raises ValidationError when the
        authenticated MCP principal has no recorded binding to the
        requested subject_id.
    """

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        access_token = get_access_token()
        if access_token is None:
            return await fn(*args, **kwargs)

        subject_id = kwargs.get("subject_id")
        ctx: Any = kwargs.get("ctx")
        if not isinstance(subject_id, str) or ctx is None:
            # Tool doesn't take subject_id/ctx the expected way - nothing
            # to bind-check; let it proceed rather than crash on a
            # decorator applied out of scope.
            return await fn(*args, **kwargs)

        principal = principal_from_access_token(access_token)
        app = ctx.request_context.lifespan_context
        if not await app.principal_bindings.is_bound(subject_id, principal):
            log.warning(
                "principal_binding_denied",
                tool=fn.__name__,
                principal=principal,
            )
            raise ValidationError(
                "This subject_id is not linked to the authenticated MCP "
                "principal - complete the consent flow (start_consent / "
                "complete_consent) for this subject_id first.",
                code="SUBJECT_NOT_BOUND",
            )
        return await fn(*args, **kwargs)

    return wrapper
