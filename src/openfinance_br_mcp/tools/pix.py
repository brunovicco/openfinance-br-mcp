"""MCP tools for PIX operations (Fase 3 of Open Finance Brasil).

Exposes ``list_pix_keys`` to query keys and ``initiate_pix`` to
initiate payments with guaranteed idempotency.

Idempotency for ``initiate_pix`` is implemented at two levels:
  1. The ``idempotency_key`` field is required and forwarded to the
     bank via the ``X-Idempotency-Key`` header.
  2. ``AppContext.idempotency_store`` (auth/idempotency_store.py)
     persists a hash of the payload alongside the response, safe
     across restarts and Kubernetes replicas (Redis-backed in
     production) - replacing the previous in-process
     ``pix_idempotency_cache`` dict, which never survived either.

``list_pix_keys`` remains restricted to ``environment='mock'``: it
calls a path not published in the official Accounts API family and
should be treated as demonstrative only.

``initiate_pix`` is no longer mock-only (P2): outside mock mode it now
requires an ``AUTHORISED`` payment consent obtained via
``start_payment_consent``/``complete_payment_consent``
(tools/payments.py) before it will call the bank, uses a per-consent
``purpose='payment:<consent_id>'`` token (never the data-sharing token - see
adapters/base.py), and signs the outgoing request as a JWS
(auth/payment_jws.py) per the FAPI-BR message signing profile. In mock
mode there is no payment consent resource to check against, so that
step is skipped and the mock adapter is called directly, as before.
"""

from pydantic import BaseModel

from openfinance_br_mcp.auth.payment_consent import (
    PaymentConsentStatus,
    payment_token_purpose,
)
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import ConsentError, ValidationError
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.pix import (
    CanonicalAmount,
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
    amount: CanonicalAmount,
    creditor_key: str,
    creditor_key_type: PixKeyType,
    debtor_account_id: str,
    idempotency_key: str,
    ctx: AppRequestContext,
    description: str = "",
    consent_id: str | None = None,
) -> PixPaymentResult:
    """Initiates a PIX payment via Open Finance Brasil. Requires an
    active payment consent. The idempotency_key field prevents
    duplicate charges on retries.

    Outside ``environment='mock'``, requires an ``AUTHORISED`` payment
    consent for this subject/bank, obtained beforehand via
    ``start_payment_consent`` + ``complete_payment_consent``
    (tools/payments.py) - a data-sharing consent alone is not
    sufficient. In mock mode this check is skipped entirely, since the
    mock adapter has no payment-consent resource to check against.

    Args:
        subject_id: Payer's CPF.
        bank: Identifier of the participating bank.
        amount: Canonical amount in BRL (e.g. ``"150.00"``).
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key.
        debtor_account_id: ID of the account to debit, returned by
            list_accounts.
        idempotency_key: Client-generated UUID to prevent duplicates.
        ctx: MCP request context, providing access to shared adapters
            and the persistent idempotency store.
        description: Payment description/reason (max 140 chars).
        consent_id: Payment consent returned by
            ``start_payment_consent``. Required outside mock mode.

    Returns:
        Status of the initiated (or previously cached) payment.
    """
    app: AppContext = ctx.request_context.lifespan_context

    adapter = app.adapters.get(bank)
    if adapter is None:
        raise ValidationError(f"Bank '{bank}' is not available.", code="UNKNOWN_BANK")

    request = PixPaymentRequest(
        amount=amount,
        creditor_key=creditor_key,
        creditor_key_type=creditor_key_type,
        debtor_account_id=debtor_account_id,
        description=description,
        idempotency_key=idempotency_key,
        consent_id=consent_id,
    )

    async def _do_payment() -> str:
        if app.directory is not None:
            if consent_id is None:
                raise ValidationError(
                    "consent_id is required outside mock mode.",
                    code="PAYMENT_CONSENT_ID_REQUIRED",
                )
            consent_api = await app.directory.resolve(bank, "payments-consents")
            pix_api = await app.directory.resolve(bank, "payments-pix")
            for resolved in (consent_api, pix_api):
                if resolved.api_version.split(".", 1)[0] != "5":
                    raise ValidationError(
                        f"Bank '{bank}' publishes {resolved.api_family_type} "
                        f"version '{resolved.api_version}', but this journey "
                        "requires Payments API v5.",
                        code="UNSUPPORTED_PAYMENTS_VERSION",
                    )
            consent_endpoint = consent_api.require_collection_endpoint("/consents")
            pix_api.require_collection_endpoint("/pix/payments")
            token_endpoint = await app.directory.resolve_token_endpoint(bank)
            try:
                payment_token = await app.token_store.get_valid_token(
                    bank,
                    subject_id,
                    app.http_client,
                    token_endpoint,
                    purpose=payment_token_purpose(consent_id),
                )
            except KeyError as exc:
                raise ConsentError(
                    f"No active payment consent session found for consent "
                    f"'{consent_id}' and subject '{subject_id}' at '{bank}' - "
                    "call start_payment_consent and complete_payment_consent first.",
                    code="NO_ACTIVE_PAYMENT_SESSION",
                ) from exc

            status = await app.payment_consent_manager.get_status(
                bank,
                subject_id,
                consent_id,
                consent_endpoint=consent_endpoint,
                access_token=payment_token.access_token,
                response_jwks=await app.directory.resolve_jwks(bank),
            )
            if status != PaymentConsentStatus.AUTHORISED:
                raise ConsentError(
                    f"Payment consent '{consent_id}' is '{status.value}', not "
                    "AUTHORISED.",
                    code="PAYMENT_CONSENT_NOT_AUTHORISED",
                )
            await app.payment_consent_manager.reserve_payment(
                bank, subject_id, consent_id, request
            )

        payment = await adapter.initiate_pix(subject_id, request)
        if app.directory is not None:
            assert consent_id is not None
            await app.payment_consent_manager.mark_consumed(
                bank, subject_id, consent_id
            )
        return PixPaymentResult(bank=bank, payment=payment).model_dump_json()

    result_json = await app.idempotency_store.get_or_compute(
        bank_id=bank,
        subject_id=subject_id,
        idempotency_key=idempotency_key,
        payload=request.model_dump(mode="json"),
        compute=_do_payment,
    )

    return PixPaymentResult.model_validate_json(result_json)
