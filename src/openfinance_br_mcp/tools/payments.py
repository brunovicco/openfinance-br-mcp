"""MCP tools for the Payments API's dedicated consent flow (Fase 3, P2).

Mirrors tools/consent.py's orchestration (PAR/JAR, ID token
verification, authorization_code exchange) but against the Payments
API's own consent resource (auth/payment_consent.py) - a payment
consent authorizes exactly one specific payment (amount, creditor,
date), never reused across payments the way a data-sharing consent can
be reused across API calls.

Sequence a caller drives through these tools:

  1. ``start_payment_consent`` creates a payment consent describing the
     exact payment, and returns a URL for the user to open in a
     browser to authorize it.
  2. ``complete_payment_consent`` is called after the user finishes at
     the bank; it exchanges the code for a payment-bound access token
     (saved under TokenStore's ``purpose='payment'`` namespace, never
     colliding with a data-sharing token for the same subject/bank -
     see auth/token.py).
  3. ``check_payment_consent_status`` queries the consent's current
     status. Once AUTHORISED, ``initiate_pix`` (tools/pix.py) creates
     the actual payment and marks the consent CONSUMED.

Restricted to environment='mock' at the tool layer (see
``_require_mock_environment`` in tools/pix.py) until this journey has
been validated against a real BCB sandbox - see
IMPLEMENTATION_PLAN.md, P2/P3.
"""

from datetime import UTC, datetime
from typing import cast
from urllib.parse import parse_qs, urlparse

from mcp.server.auth.middleware.auth_context import get_access_token
from pydantic import BaseModel

from openfinance_br_mcp.auth.authorization_session import PendingAuthorization
from openfinance_br_mcp.auth.id_token import verify_id_token
from openfinance_br_mcp.auth.par import push_authorization_request
from openfinance_br_mcp.auth.payment_consent import PaymentConsentStatus, PaymentDetails
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.auth.token_exchange import (
    exchange_authorization_code,
    exchange_client_credentials,
)
from openfinance_br_mcp.context import AppContext, AppRequestContext
from openfinance_br_mcp.exceptions import (
    AuthenticationError,
    ConsentDeniedError,
    ConsentError,
    ValidationError,
)
from openfinance_br_mcp.observability.tool_tracing import traced_tool
from openfinance_br_mcp.schemas.pix import PixKeyType
from openfinance_br_mcp.tools.aliases import BankId
from openfinance_br_mcp.tools.errors import translate_errors
from openfinance_br_mcp.tools.principal_guard import require_principal_binding

_AUTHORIZATION_SESSION_MINUTES = 15


class StartPaymentConsentResult(BaseModel):
    """Result of ``start_payment_consent``."""

    bank: BankId
    consent_id: str
    authorization_url: str
    expires_in_minutes: int


class CompletePaymentConsentResult(BaseModel):
    """Result of ``complete_payment_consent``."""

    bank: BankId
    subject_id: str
    consent_id: str
    status: str


class PaymentConsentStatusResult(BaseModel):
    """Result of ``check_payment_consent_status``."""

    bank: BankId
    status: str


def _require_directory(app: AppContext) -> None:
    """Raises ValidationError if the current environment has no DirectoryClient.

    Args:
        app: The current AppContext.

    Raises:
        ValidationError: If ``app.directory`` is None (environment=mock).
    """
    if app.directory is None:
        raise ValidationError(
            "The payment consent flow is not applicable in mock mode - "
            "initiate_pix works directly against mock data without a real "
            "payment consent. Set ENVIRONMENT=sandbox or 'production' to use "
            "start_payment_consent.",
            code="PAYMENT_CONSENT_NOT_APPLICABLE_IN_MOCK",
        )


@traced_tool
@translate_errors
@require_principal_binding
async def start_payment_consent(
    subject_id: str,
    bank: BankId,
    amount: str,
    creditor_key: str,
    creditor_key_type: PixKeyType,
    debtor_account_id: str,
    ctx: AppRequestContext,
    description: str = "",
) -> StartPaymentConsentResult:
    """Starts the Open Finance Brasil Payments API consent flow for one
    specific PIX payment.

    Creates a payment consent describing exactly this payment, then
    builds a FAPI-BR compliant (PAR + JAR) authorization URL. The user
    must open this URL, log in, and authorize this specific payment at
    the bank. Once redirected back, call ``complete_payment_consent``
    with the resulting URL, then ``initiate_pix`` to actually create
    the payment.

    Args:
        subject_id: Payer's CPF (digits only) or internal ID.
        bank: Identifier of the participating bank.
        amount: Payment amount in BRL (e.g. '150.00').
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key.
        debtor_account_id: ID of the account to debit.
        ctx: MCP request context, providing access to shared dependencies.
        description: Payment description/reason (max 140 chars).

    Returns:
        The payment consent ID and the URL the user must open to
        authorize it.
    """
    app: AppContext = ctx.request_context.lifespan_context
    _require_directory(app)
    assert app.directory is not None  # narrowed by _require_directory

    resolved = await app.directory.resolve(bank, "payments-consents")
    if resolved.issuer is None:
        raise ConsentError(
            f"No OAuth2/OIDC issuer resolved for bank '{bank}'",
            code="NO_ISSUER",
        )
    token_endpoint = await app.directory.resolve_token_endpoint(bank)
    par_endpoint = await app.directory.resolve_par_endpoint(bank)
    authorization_endpoint = await app.directory.resolve_authorization_endpoint(bank)

    client_credentials_token = await exchange_client_credentials(
        app.http_client, token_endpoint=token_endpoint, scope="payments"
    )

    payment = PaymentDetails(
        amount=amount,
        creditor_key=creditor_key,
        creditor_key_type=creditor_key_type.value,
        debtor_account_id=debtor_account_id,
        description=description,
    )
    consent_id = await app.payment_consent_manager.create(
        bank,
        subject_id,
        bank_base_url=resolved.base_url,
        payment=payment,
        access_token=client_credentials_token.access_token,
    )

    pkce = PKCEChallenge.generate()
    par_result = await push_authorization_request(
        app.http_client,
        par_endpoint=par_endpoint,
        authorization_endpoint=authorization_endpoint,
        issuer=resolved.issuer,
        scope=f"openid payments consent:{consent_id}".strip(),
        pkce=pkce,
    )

    await app.authorization_sessions.save(
        par_result.state,
        PendingAuthorization(
            bank_id=bank,
            bank_base_url=resolved.base_url,
            consent_id=consent_id,
            subject_id=subject_id,
            pkce=pkce,
            nonce=par_result.nonce,
            issuer=resolved.issuer,
            token_endpoint=token_endpoint,
            created_at=datetime.now(UTC),
        ),
    )

    return StartPaymentConsentResult(
        bank=bank,
        consent_id=consent_id,
        authorization_url=par_result.authorization_url,
        expires_in_minutes=_AUTHORIZATION_SESSION_MINUTES,
    )


@traced_tool
@translate_errors
async def complete_payment_consent(
    callback_url: str, ctx: AppRequestContext
) -> CompletePaymentConsentResult:
    """Completes a payment consent flow using the URL the bank
    redirected the user to after authorizing (or denying) the payment.

    Args:
        callback_url: The full URL the user's browser landed on after
            authorizing (or denying) the payment consent at the bank.
        ctx: MCP request context, providing access to shared dependencies.

    Returns:
        The final payment consent status after completing the exchange.
    """
    app: AppContext = ctx.request_context.lifespan_context

    parsed = urlparse(callback_url)
    params = parse_qs(parsed.fragment or parsed.query)

    def _single(name: str) -> str | None:
        values = params.get(name)
        return values[0] if values else None

    error = _single("error")
    if error:
        raise ConsentDeniedError(
            f"Payment authorization was not granted: {error} - "
            f"{_single('error_description') or 'no further detail provided'}",
            code="PAYMENT_AUTHORIZATION_DENIED",
        )

    state = _single("state")
    code = _single("code")
    if not state or not code:
        raise ValidationError(
            "callback_url is missing 'code' or 'state' - paste the full "
            "URL your browser was redirected to after authorizing the "
            "payment at the bank.",
            code="INVALID_CALLBACK_URL",
        )

    session = await app.authorization_sessions.pop(state)

    token = await exchange_authorization_code(
        app.http_client,
        token_endpoint=session.token_endpoint,
        code=code,
        code_verifier=session.pkce.code_verifier,
    )

    id_token_raw = _single("id_token")
    if not id_token_raw:
        raise AuthenticationError(
            "Callback is missing the mandatory 'id_token' fragment parameter",
            code="MISSING_ID_TOKEN",
        )
    if app.directory is None:
        raise ValidationError(
            "ID token verification requires a DirectoryClient, unavailable "
            "in mock mode.",
            code="PAYMENT_CONSENT_NOT_APPLICABLE_IN_MOCK",
        )
    jwks = await app.directory.resolve_jwks(session.bank_id)
    verify_id_token(id_token_raw, issuer=session.issuer, jwks=jwks, nonce=session.nonce)

    await app.token_store.save(
        session.bank_id, session.subject_id, token, purpose="payment"
    )

    status = await app.payment_consent_manager.get_status(
        session.bank_id,
        session.subject_id,
        bank_base_url=session.bank_base_url,
        access_token=token.access_token,
    )

    access_token = get_access_token()
    if access_token is not None:
        principal = access_token.client_id or access_token.subject or ""
        await app.principal_bindings.bind(session.subject_id, principal)

    return CompletePaymentConsentResult(
        bank=cast(BankId, session.bank_id),
        subject_id=session.subject_id,
        consent_id=session.consent_id,
        status=status.value,
    )


@traced_tool
@translate_errors
@require_principal_binding
async def check_payment_consent_status(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> PaymentConsentStatusResult:
    """Checks the current status of a user's payment consent at a bank.

    Args:
        subject_id: Payer's CPF or internal ID.
        bank: Identifier of the participating bank.
        ctx: MCP request context, providing access to shared dependencies.

    Returns:
        The payment consent's current status.
    """
    app: AppContext = ctx.request_context.lifespan_context
    _require_directory(app)
    assert app.directory is not None

    resolved = await app.directory.resolve(bank, "payments-consents")
    token_endpoint = await app.directory.resolve_token_endpoint(bank)
    try:
        token = await app.token_store.get_valid_token(
            bank, subject_id, app.http_client, token_endpoint, purpose="payment"
        )
    except KeyError as exc:
        raise ConsentError(
            f"No active payment consent session found for subject "
            f"'{subject_id}' at '{bank}' - call start_payment_consent and "
            "complete_payment_consent first.",
            code="NO_ACTIVE_PAYMENT_SESSION",
        ) from exc

    status: PaymentConsentStatus = await app.payment_consent_manager.get_status(
        bank,
        subject_id,
        bank_base_url=resolved.base_url,
        access_token=token.access_token,
    )
    return PaymentConsentStatusResult(bank=bank, status=status.value)
