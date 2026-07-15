"""MCP tools for the FAPI-BR 2.0 consent/authorization flow.

Exposes the tools that together drive Open Finance Brasil's required
user-consent journey:

  1. ``start_consent`` creates a consent resource at the bank and
     returns a URL for the user to open in a browser to authorize it.
  2. ``complete_consent`` is called after the user finishes at the
     bank and is redirected; it exchanges the authorization code for
     an access token bound to the consent.
  3. ``check_consent_status``/``revoke_consent`` query or revoke an
     existing consent.

FAPI-BR 2.2.0 mandates ``response_mode=fragment`` for the
authorization redirect (RFC 6749 §4.2's hash-fragment delivery): the
authorization code and ID token are appended to the redirect_uri as a
URL fragment, which browsers never transmit to a server in an HTTP
request. There is structurally no way for this MCP server to receive
that callback automatically - the user must copy the final URL from
their browser's address bar after completing login+consent at the
bank, and pass it to ``complete_consent``. This mirrors the
device-code/paste-back pattern common to CLI OAuth tools, and is the
only shape compatible with the mandated response_mode (it is not a
design choice made for convenience - no in-process HTTP listener could
receive this callback either, since fragments are never sent over the
wire at all).

Not available when ``environment=mock``: there is no real bank to
consent with, and the mock adapters already return data without a
consent.
"""

from datetime import UTC, datetime
from typing import cast
from urllib.parse import parse_qs, urlparse

from mcp.server.auth.middleware.auth_context import get_access_token
from pydantic import BaseModel

from openfinance_br_mcp.auth.authorization_session import PendingAuthorization
from openfinance_br_mcp.auth.consent import CONSENT_SCOPE_MAP
from openfinance_br_mcp.auth.id_token import verify_id_token
from openfinance_br_mcp.auth.par import push_authorization_request
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.auth.token import TokenResponse
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
from openfinance_br_mcp.tools.aliases import BankId, ConsentScopes
from openfinance_br_mcp.tools.errors import translate_errors
from openfinance_br_mcp.tools.principal_guard import require_principal_binding

_AUTHORIZATION_SESSION_MINUTES = 15


class StartConsentResult(BaseModel):
    """Result of ``start_consent``."""

    bank: BankId
    consent_id: str
    authorization_url: str
    expires_in_minutes: int


class CompleteConsentResult(BaseModel):
    """Result of ``complete_consent``."""

    bank: BankId
    subject_id: str
    consent_id: str
    status: str


class ConsentStatusResult(BaseModel):
    """Result of ``check_consent_status``."""

    bank: BankId
    status: str


class RevokeConsentResult(BaseModel):
    """Result of ``revoke_consent``."""

    bank: BankId
    subject_id: str
    revoked: bool


def _require_directory(app: AppContext) -> None:
    """Raises ValidationError if the current environment has no DirectoryClient.

    Args:
        app: The current AppContext.

    Raises:
        ValidationError: If ``app.directory`` is None (environment=mock).
    """
    if app.directory is None:
        raise ValidationError(
            "The consent flow is not applicable in mock mode - mock data "
            "tools (list_accounts, list_transactions, etc.) work directly "
            "without a real consent. Set ENVIRONMENT=sandbox or "
            "'production' to use start_consent.",
            code="CONSENT_NOT_APPLICABLE_IN_MOCK",
        )


@traced_tool
@translate_errors
async def start_consent(
    subject_id: str,
    bank: BankId,
    scopes: ConsentScopes,
    ctx: AppRequestContext,
    request_url_elicitation: bool = False,
) -> StartConsentResult:
    """Starts the Open Finance Brasil consent flow for a user at a bank.

    Creates a consent resource at the bank, then builds a FAPI-BR
    compliant (PAR + JAR) authorization URL. The user must open this
    URL in a browser, log in, and authorize the requested scopes at
    the bank. Once redirected back, call ``complete_consent`` with the
    resulting URL to finish the flow.

    Args:
        subject_id: User's CPF (digits only) or internal ID.
        bank: Identifier of the participating bank.
        scopes: Desired data-sharing scopes, e.g. ['accounts',
            'balances', 'transactions', 'overdraft_limits',
            'credit_card_accounts', 'credit_card_limits',
            'credit_card_bills', 'credit_card_transactions',
            'bank_fixed_incomes', 'funds', 'variable_incomes',
            'treasure_titles']. Does NOT include 'pix'/payments -
            payment initiation uses a separate, dedicated payment
            consent (Payments API), not this data-sharing consent; see
            tools/pix.py.
        ctx: MCP request context, providing access to shared dependencies.
        request_url_elicitation: Ask a compatible MCP client to open the
            bank authorization URL using URL-mode elicitation. The URL is
            always returned as well, so clients without elicitation support
            can continue with the existing copy-and-open flow.

    Returns:
        The consent ID and the URL the user must open to authorize it.
    """
    app: AppContext = ctx.request_context.lifespan_context
    _require_directory(app)
    assert app.directory is not None  # narrowed by _require_directory

    resolved = await app.directory.resolve(bank, "consents")
    if resolved.issuer is None:
        raise ConsentError(
            f"No OAuth2/OIDC issuer resolved for bank '{bank}'",
            code="NO_ISSUER",
        )
    token_endpoint = await app.directory.resolve_token_endpoint(bank)
    par_endpoint = await app.directory.resolve_par_endpoint(bank)
    authorization_endpoint = await app.directory.resolve_authorization_endpoint(bank)

    client_credentials_token = await exchange_client_credentials(
        app.http_client, token_endpoint=token_endpoint, scope="consents"
    )

    consent_id = await app.consent_manager.create(
        bank,
        subject_id,
        bank_base_url=resolved.base_url,
        scopes=scopes,
        access_token=client_credentials_token.access_token,
    )

    consent_scopes = " ".join(
        dict.fromkeys(CONSENT_SCOPE_MAP.get(s, s) for s in scopes)
    )
    pkce = PKCEChallenge.generate()
    par_result = await push_authorization_request(
        app.http_client,
        par_endpoint=par_endpoint,
        authorization_endpoint=authorization_endpoint,
        issuer=resolved.issuer,
        scope=f"openid consent:{consent_id} {consent_scopes}".strip(),
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

    if request_url_elicitation:
        await ctx.elicit_url(
            message=(
                f"Open {bank}'s authorization page to approve access to your "
                "Open Finance data. Authentication happens directly at the bank."
            ),
            url=par_result.authorization_url,
            elicitation_id=par_result.state,
        )

    return StartConsentResult(
        bank=bank,
        consent_id=consent_id,
        authorization_url=par_result.authorization_url,
        expires_in_minutes=_AUTHORIZATION_SESSION_MINUTES,
    )


@traced_tool
@translate_errors
async def complete_consent(
    callback_url: str, ctx: AppRequestContext
) -> CompleteConsentResult:
    """Completes a consent flow using the URL the bank redirected the
    user to after they finished logging in and authorizing.

    Because FAPI-BR mandates response_mode=fragment, that URL's
    parameters live after a '#', not a '?' - copy the complete address
    bar contents after being redirected, not just the query string.

    Args:
        callback_url: The full URL the user's browser landed on after
            authorizing (or denying) consent at the bank.
        ctx: MCP request context, providing access to shared dependencies.

    Returns:
        The final consent status after completing the exchange.
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
            f"Authorization was not granted: {error} - "
            f"{_single('error_description') or 'no further detail provided'}",
            code="AUTHORIZATION_DENIED",
        )

    state = _single("state")
    code = _single("code")
    if not state or not code:
        raise ValidationError(
            "callback_url is missing 'code' or 'state' - paste the full "
            "URL your browser was redirected to after completing consent "
            "at the bank.",
            code="INVALID_CALLBACK_URL",
        )

    session = await app.authorization_sessions.pop(state)

    token = await exchange_authorization_code(
        app.http_client,
        token_endpoint=session.token_endpoint,
        code=code,
        code_verifier=session.pkce.code_verifier,
    )

    # The authorization request was built with response_type="code
    # id_token" (see auth/par.py) - the authorization server is
    # therefore expected to always return an id_token alongside the
    # code. Treating its absence as optional would silently accept a
    # bank response that doesn't match what was actually requested;
    # fail closed instead of persisting a bank token with no verified
    # identity behind it.
    id_token_raw = _single("id_token")
    if not id_token_raw:
        raise AuthenticationError(
            "Callback is missing the mandatory 'id_token' fragment "
            "parameter - the authorization request was made with "
            "response_type='code id_token', so a compliant "
            "authorization server always includes one.",
            code="MISSING_ID_TOKEN",
        )
    if app.directory is None:
        raise ValidationError(
            "ID token verification requires a DirectoryClient, unavailable "
            "in mock mode.",
            code="CONSENT_NOT_APPLICABLE_IN_MOCK",
        )
    jwks = await app.directory.resolve_jwks(session.bank_id)
    verify_id_token(id_token_raw, issuer=session.issuer, jwks=jwks, nonce=session.nonce)

    await app.token_store.save(session.bank_id, session.subject_id, token)

    status = await app.consent_manager.get_status(
        session.bank_id,
        session.subject_id,
        bank_base_url=session.bank_base_url,
        access_token=token.access_token,
    )

    # This is the one point identity is genuinely established
    # end-to-end: the caller just completed a real login+consent at
    # the bank for this exact subject_id. Record the binding so every
    # other tool taking subject_id can verify the *same* authenticated
    # MCP principal is the one acting on it (see
    # auth/principal_binding.py, tools/principal_guard.py). A no-op
    # when there's no MCP client OAuth configured (get_access_token()
    # is None) - see that module's docstring for why that's safe.
    access_token = get_access_token()
    if access_token is not None:
        principal = access_token.client_id or access_token.subject or ""
        await app.principal_bindings.bind(session.subject_id, principal)

    return CompleteConsentResult(
        bank=cast(BankId, session.bank_id),
        subject_id=session.subject_id,
        consent_id=session.consent_id,
        status=status.value,
    )


@traced_tool
@translate_errors
@require_principal_binding
async def check_consent_status(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> ConsentStatusResult:
    """Checks the current status of a user's consent at a bank.

    Args:
        subject_id: User's CPF or internal ID.
        bank: Identifier of the participating bank.
        ctx: MCP request context, providing access to shared dependencies.

    Returns:
        The consent's current status.
    """
    app: AppContext = ctx.request_context.lifespan_context
    _require_directory(app)
    assert app.directory is not None

    resolved = await app.directory.resolve(bank, "consents")
    token_endpoint = await app.directory.resolve_token_endpoint(bank)
    token = await _require_token(app, subject_id, token_endpoint, bank)

    status = await app.consent_manager.get_status(
        bank,
        subject_id,
        bank_base_url=resolved.base_url,
        access_token=token.access_token,
    )
    return ConsentStatusResult(bank=bank, status=status.value)


@traced_tool
@translate_errors
@require_principal_binding
async def revoke_consent(
    subject_id: str, bank: BankId, ctx: AppRequestContext
) -> RevokeConsentResult:
    """Revokes a user's consent at a bank and forgets the local token.

    Args:
        subject_id: User's CPF or internal ID.
        bank: Identifier of the participating bank.
        ctx: MCP request context, providing access to shared dependencies.

    Returns:
        Confirmation that the consent was revoked.
    """
    app: AppContext = ctx.request_context.lifespan_context
    _require_directory(app)
    assert app.directory is not None

    resolved = await app.directory.resolve(bank, "consents")
    token_endpoint = await app.directory.resolve_token_endpoint(bank)
    token = await _require_token(app, subject_id, token_endpoint, bank)

    await app.consent_manager.revoke(
        bank,
        subject_id,
        bank_base_url=resolved.base_url,
        access_token=token.access_token,
    )
    await app.token_store.revoke(bank, subject_id)
    return RevokeConsentResult(bank=bank, subject_id=subject_id, revoked=True)


async def _require_token(
    app: AppContext, subject_id: str, token_endpoint: str, bank: BankId
) -> TokenResponse:
    """Fetches the subject's stored token, translating KeyError to ConsentError.

    Args:
        app: The current AppContext.
        subject_id: User's CPF or internal ID.
        token_endpoint: Token endpoint to use if a refresh is needed.
        bank: Identifier of the bank, for the error message.

    Returns:
        A valid TokenResponse.

    Raises:
        ConsentError: If no consent session exists for this subject/bank.
    """
    try:
        return await app.token_store.get_valid_token(
            bank, subject_id, app.http_client, token_endpoint
        )
    except KeyError as exc:
        raise ConsentError(
            f"No active consent session found for subject '{subject_id}' "
            f"at '{bank}' - call start_consent and complete_consent first.",
            code="NO_ACTIVE_SESSION",
        ) from exc
