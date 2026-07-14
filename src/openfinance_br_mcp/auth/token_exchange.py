"""Token endpoint grant exchanges for FAPI-BR 2.0.

Both grants below authenticate with private_key_jwt (RFC 7523, via
jwt_client_auth.build_client_assertion) rather than a plain client_id
field - the only client authentication method FAPI-BR 2.2.0 accepts.

  - Client credentials: used before a consent exists, to obtain an
    access token scoped to POST /consents (creating the consent
    resource the user will then authorize).
  - Authorization code: used after the user completes login+consent
    at the bank and the resulting code is exchanged for a
    consent-bound access/refresh token pair (see auth/par.py for how
    the authorization request that produces this code is built, and
    tools/consent.py for how the code itself is retrieved given
    FAPI-BR's mandatory response_mode=fragment).

Example:
    >>> token = await exchange_client_credentials(
    ...     http_client, token_endpoint=endpoint, scope="consents",
    ... )
"""

import httpx

from openfinance_br_mcp.auth.jwt_client_auth import (
    CLIENT_ASSERTION_TYPE,
    build_client_assertion,
)
from openfinance_br_mcp.auth.token import TokenResponse
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError


async def exchange_client_credentials(
    http_client: httpx.AsyncClient,
    *,
    token_endpoint: str,
    scope: str,
) -> TokenResponse:
    """Obtains an access token via grant_type=client_credentials.

    Args:
        http_client: HTTP client (mTLS-configured for the transport-
            level certificate requirement).
        token_endpoint: The authorization server's token endpoint (see
            DirectoryClient.resolve_token_endpoint).
        scope: Space-separated OAuth2 scopes to request (e.g. 'consents').

    Returns:
        TokenResponse with an access_token usable to create a consent.

    Raises:
        AuthenticationError: If CLIENT_ID/the private key aren't
            configured, or the token request fails.
    """
    if not settings.client_id:
        raise AuthenticationError("CLIENT_ID is not configured", code="NO_CLIENT_ID")

    client_assertion = build_client_assertion(audience=token_endpoint)
    form = {
        "grant_type": "client_credentials",
        "scope": scope,
        "client_id": settings.client_id,
        "client_assertion_type": CLIENT_ASSERTION_TYPE,
        "client_assertion": client_assertion,
    }
    return await _post_token_request(http_client, token_endpoint, form)


async def exchange_authorization_code(
    http_client: httpx.AsyncClient,
    *,
    token_endpoint: str,
    code: str,
    code_verifier: str,
) -> TokenResponse:
    """Exchanges an authorization code for a consent-bound token pair.

    Args:
        http_client: HTTP client (mTLS-configured).
        token_endpoint: The authorization server's token endpoint.
        code: The authorization code the user's browser was redirected
            back with, after completing login+consent at the bank.
        code_verifier: The PKCE code_verifier matching the
            code_challenge originally sent via push_authorization_request.

    Returns:
        TokenResponse with an access_token/refresh_token pair bound to
        the consent the user just authorized.

    Raises:
        AuthenticationError: If CLIENT_ID/the private key aren't
            configured, or the token request fails.
    """
    if not settings.client_id:
        raise AuthenticationError("CLIENT_ID is not configured", code="NO_CLIENT_ID")

    client_assertion = build_client_assertion(audience=token_endpoint)
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": str(settings.redirect_uri),
        "code_verifier": code_verifier,
        "client_id": settings.client_id,
        "client_assertion_type": CLIENT_ASSERTION_TYPE,
        "client_assertion": client_assertion,
    }
    return await _post_token_request(http_client, token_endpoint, form)


async def _post_token_request(
    http_client: httpx.AsyncClient, token_endpoint: str, form: dict[str, str]
) -> TokenResponse:
    """Posts a token request and wraps failures as AuthenticationError.

    Args:
        http_client: HTTP client to use.
        token_endpoint: URL to post to.
        form: Already-built form-encoded request body.

    Returns:
        The parsed TokenResponse.

    Raises:
        AuthenticationError: If the request fails at the HTTP or
            network level.
    """
    try:
        response = await http_client.post(token_endpoint, data=form)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AuthenticationError(
            f"Token request failed: HTTP {exc.response.status_code}",
            code="TOKEN_EXCHANGE_HTTP_ERROR",
        ) from exc
    except httpx.RequestError as exc:
        raise AuthenticationError(
            f"Token request network error: {exc}", code="TOKEN_EXCHANGE_NETWORK_ERROR"
        ) from exc

    return TokenResponse(response.json())
