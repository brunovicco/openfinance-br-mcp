"""Pushed Authorization Requests (PAR) for FAPI-BR 2.0.

The FAPI-BR 2.2.0 security profile mandates PAR (RFC 9126) for every
authorization request, combined with JAR (RFC 9101 - the authorization
parameters themselves travel as a signed JWT in the ``request``
field, not as plain form parameters). The authorization server
responds with a short-lived ``request_uri``; the client then
redirects the user to
``{authorization_endpoint}?client_id=...&request_uri=...`` instead of
a URL carrying the parameters directly.

``response_type=code id_token`` and ``response_mode=fragment`` are
mandatory under this profile - both are set unconditionally below,
not left to the caller.

Example:
    >>> from openfinance_br_mcp.auth.pkce import PKCEChallenge
    >>> pkce = PKCEChallenge.generate()
    >>> result = await push_authorization_request(
    ...     http_client, par_endpoint=par_url, authorization_endpoint=authz_url,
    ...     issuer=issuer, scope="accounts", pkce=pkce,
    ... )
    >>> result.authorization_url
"""

import time
import uuid
from dataclasses import dataclass

import httpx
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.jwt_client_auth import (
    CLIENT_ASSERTION_TYPE,
    build_client_assertion,
    load_private_key,
)
from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

_REQUEST_OBJECT_TTL_SECONDS = 300


@dataclass
class PushedAuthorizationResult:
    """Result of a successful Pushed Authorization Request.

    Attributes:
        authorization_url: URL to redirect the user to at the bank.
        state: The 'state' value embedded in the signed request object
            - the caller must keep this to correlate the later
            callback (see tools/consent.py).
        nonce: The 'nonce' value embedded in the signed request object
            - the caller must keep this to verify the ID token
            returned after the user authorizes (see auth/id_token.py).
    """

    authorization_url: str
    state: str
    nonce: str


async def push_authorization_request(
    http_client: httpx.AsyncClient,
    *,
    par_endpoint: str,
    authorization_endpoint: str,
    issuer: str,
    scope: str,
    pkce: PKCEChallenge,
) -> PushedAuthorizationResult:
    """Submits a Pushed Authorization Request and returns the redirect URL.

    Args:
        http_client: HTTP client (mTLS-configured, per the separate
            transport-level certificate requirement).
        par_endpoint: The authorization server's
            pushed_authorization_request_endpoint (from OIDC discovery
            - see DirectoryClient.resolve_par_endpoint).
        authorization_endpoint: The authorization server's
            authorization_endpoint (see
            DirectoryClient.resolve_authorization_endpoint), used to
            build the final redirect URL.
        issuer: The authorization server's issuer, used as the
            request object's 'aud' claim.
        scope: Space-separated OAuth2 scopes to request.
        pkce: PKCE challenge for this authorization session - the
            caller is responsible for keeping the matching
            code_verifier to use at the token exchange step.

    Returns:
        PushedAuthorizationResult with the redirect URL and the
        state/nonce the caller must retain to complete the flow.

    Raises:
        AuthenticationError: If CLIENT_ID/the private key aren't
            configured, or the PAR request fails.
    """
    if not settings.client_id:
        raise AuthenticationError("CLIENT_ID is not configured", code="NO_CLIENT_ID")

    now = int(time.time())
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    request_claims = {
        "iss": settings.client_id,
        "aud": issuer,
        "response_type": "code id_token",
        # FAPI-BR 2.2.x mandates response_mode=fragment alongside
        # response_type=code id_token (RFC 6749 §4.2's hash-fragment
        # delivery) - previously omitted here despite the module
        # docstring claiming otherwise; see tools/consent.py for why
        # this makes the callback a paste-back flow, not an automatic
        # redirect this server can receive directly.
        "response_mode": "fragment",
        "client_id": settings.client_id,
        "redirect_uri": str(settings.redirect_uri),
        "scope": scope,
        "state": state,
        "nonce": nonce,
        "code_challenge": pkce.code_challenge,
        "code_challenge_method": pkce.code_challenge_method,
        # 'acr' as an essential ID token claim - required by the
        # FAPI-BR confidential client profile so the authorization
        # server asserts the authentication context class (e.g.
        # multi-factor) actually used, rather than leaving it
        # unconstrained.
        "claims": {"id_token": {"acr": {"essential": True}}},
        "iat": now,
        "exp": now + _REQUEST_OBJECT_TTL_SECONDS,
    }
    key = load_private_key()
    header = {"alg": settings.private_key_jwt_alg}
    if settings.private_key_kid:
        header["kid"] = settings.private_key_kid

    request_token = jwcrypto_jwt.JWT(header=header, claims=request_claims)
    request_token.make_signed_token(key)
    request_object = request_token.serialize()

    client_assertion = build_client_assertion(audience=par_endpoint)

    form = {
        "client_id": settings.client_id,
        "request": request_object,
        "client_assertion_type": CLIENT_ASSERTION_TYPE,
        "client_assertion": client_assertion,
    }

    try:
        response = await http_client.post(par_endpoint, data=form)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AuthenticationError(
            f"PAR request failed: HTTP {exc.response.status_code}",
            code="PAR_HTTP_ERROR",
        ) from exc
    except httpx.RequestError as exc:
        raise AuthenticationError(
            f"PAR request network error: {exc}", code="PAR_NETWORK_ERROR"
        ) from exc

    data = response.json()
    request_uri = data.get("request_uri")
    if not request_uri:
        raise AuthenticationError(
            "PAR response missing request_uri", code="PAR_NO_REQUEST_URI"
        )

    authorization_url = (
        f"{authorization_endpoint}?client_id={settings.client_id}"
        f"&request_uri={request_uri}"
    )
    return PushedAuthorizationResult(
        authorization_url=authorization_url, state=state, nonce=nonce
    )
