"""MCP tools for PIX operations (Fase 3 of Open Finance Brasil).

Exposes ``list_pix_keys`` to query keys and ``initiate_pix`` to
initiate payments with guaranteed idempotency.

Idempotency for ``initiate_pix`` is implemented at two levels:
  1. The ``idempotency_key`` field is required and forwarded to the
     bank via the ``X-Idempotency-Key`` header.
  2. ``AppContext.pix_idempotency_cache`` prevents duplicate
     resubmissions within the same server process lifetime.

Both tools are restricted to ``environment='mock'`` until the
Payments API v5 journey (dedicated payment consent, signed JWS
request/response, persistent idempotency store keyed by payload hash)
is implemented - see the project's implementation plan, P2. Today's
``initiate_pix`` calls ``/payments/v4/pix/payments`` using the data-
sharing consent's access token, which does not follow the official
payment-consent flow and would very likely be rejected (or worse,
behave unpredictably) against a real bank. ``list_pix_keys`` also
calls a path not published in the official Accounts API family and
should be treated as demonstrative only.
"""

from decimal import Decimal

from pydantic import BaseModel

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.pix import (
    PixKey,
    PixKeyType,
    PixPayment,
    PixPaymentRequest,
)
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors
from openfinance_br_mcp.tools.principal_guard import require_principal_binding


def _require_mock_environment(tool_name: str) -> None:
    """Raises ValidationError unless running in mock mode.

    Args:
        tool_name: Name of the calling tool, for the error message.

    Raises:
        ValidationError: If settings.environment != 'mock'.
    """
    if settings.environment != "mock":
        raise ValidationError(
            f"'{tool_name}' is only available in environment='mock'. The "
            "real Open Finance Brasil Payments API journey (dedicated "
            "payment consent, signed JWS requests, persistent "
            "idempotency) is not yet implemented here - see the "
            "project's implementation plan, phase P2.",
            code="TOOL_MOCK_ONLY",
        )


class PixKeyListResult(BaseModel):
    """Result of ``list_pix_keys``."""

    bank: BankId
    account_id: str
    pix_keys: list[PixKey]


class PixPaymentResult(BaseModel):
    """Result of ``initiate_pix``."""

    bank: BankId
    payment: PixPayment


@traced_tool
@translate_errors
@require_principal_binding
async def list_pix_keys(
    subject_id: str, bank: BankId, account_id: str, ctx: AppRequestContext
) -> PixKeyListResult:
    """Lists the PIX keys (CPF, email, phone, EVP) registered to a
    bank account via Open Finance Brasil.

    Only available in environment='mock' - see module docstring.

    Args:
        subject_id: User's CPF.
        bank: Identifier of the participating bank.
        account_id: Account ID.
        ctx: MCP request context, providing access to shared adapters.

    Returns:
        The PIX keys registered to the given account.
    """
    _require_mock_environment("list_pix_keys")
    app: AppContext = ctx.request_context.lifespan_context
    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    keys = await adapter.list_pix_keys(subject_id, account_id)
    return PixKeyListResult(bank=bank, account_id=account_id, pix_keys=keys)


@traced_tool
@translate_errors
@require_principal_binding
async def initiate_pix(
    subject_id: str,
    bank: BankId,
    amount: float,
    creditor_key: str,
    creditor_key_type: PixKeyType,
    debtor_account_id: str,
    idempotency_key: str,
    ctx: AppRequestContext,
    description: str = "",
) -> PixPaymentResult:
    """Initiates a PIX payment via Open Finance Brasil. Requires an
    active payment consent. The idempotency_key field prevents
    duplicate charges on retries.

    Only available in environment='mock' - see module docstring. The
    real Payments API v5 journey (dedicated payment consent, signed
    JWS requests, persistent cross-replica idempotency) is not yet
    implemented.

    Args:
        subject_id: Payer's CPF.
        bank: Identifier of the participating bank.
        amount: Amount in BRL (e.g. 150.00). Must be greater than zero.
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key.
        debtor_account_id: ID of the account to debit, returned by
            list_accounts.
        idempotency_key: Client-generated UUID to prevent duplicates.
        ctx: MCP request context, providing access to shared adapters
            and the idempotency cache.
        description: Payment description/reason (max 140 chars).

    Returns:
        Status of the initiated (or previously cached) payment.
    """
    _require_mock_environment("initiate_pix")
    app: AppContext = ctx.request_context.lifespan_context

    cached = app.pix_idempotency_cache.get(idempotency_key)
    if cached is not None:
        return PixPaymentResult.model_validate_json(cached)

    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    request = PixPaymentRequest(
        # Converted via str() to avoid binary float precision artifacts
        # (e.g. Decimal(0.1) != Decimal("0.1")) in a monetary field.
        amount=Decimal(str(amount)),
        creditor_key=creditor_key,
        creditor_key_type=creditor_key_type,
        debtor_account_id=debtor_account_id,
        description=description,
        idempotency_key=idempotency_key,
    )

    payment = await adapter.initiate_pix(subject_id, request)
    result = PixPaymentResult(bank=bank, payment=payment)
    app.pix_idempotency_cache[idempotency_key] = result.model_dump_json()
    return result
