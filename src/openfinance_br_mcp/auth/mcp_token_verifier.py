"""MCP client OAuth 2.1 resource-server token verification.

Two completely separate token universes exist in this codebase:

  1. MCP client tokens (this module) - issued by an external OAuth2/
     OIDC identity provider to authenticate whoever is calling this
     server over the 'streamable-http' transport (e.g. Claude Desktop,
     an orchestration agent). Verified here, audience-bound to this
     server's own URL (RFC 8707).
  2. FAPI-BR bank tokens (auth/token.py, auth/token_exchange.py) -
     issued by each participating bank's authorization server,
     obtained via private_key_jwt/PAR, used only against that bank's
     Open Finance APIs (see adapters/default_adapter.py).

These must never cross: forwarding an MCP client's bearer token to a
bank API (or vice versa) would violate the MCP authorization spec's
explicit prohibition on token passthrough. This module's audience
check also means such a token would simply be rejected by a bank's
API even if it were sent by mistake - it was never issued for that
audience. See docs/en/authorization.md.

This server does not run its own OAuth Authorization Server (per the
"AS/RS separation" pattern the MCP SDK - mcp.server.auth.provider -
documents as preferred over its older, still-supported all-in-one
OAuthAuthorizationServerProvider): JWTTokenVerifier only ever
*verifies* tokens issued elsewhere.

Optionally enforces RFC 8705 mutual-TLS certificate-bound access
tokens on top of the plain bearer check, see auth/mtls_binding.py.

Example:
    >>> verifier = JWTTokenVerifier(
    ...     httpx.AsyncClient(),
    ...     issuer_url="https://idp.example.com",
    ...     resource_server_url="https://mcp.example.com",
    ... )
    >>> access_token = await verifier.verify_token(bearer_token)
"""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt
from mcp.server.auth.provider import AccessToken

from openfinance_br_mcp.auth.mtls_binding import client_cert_thumbprint

log = structlog.get_logger(__name__)


class JWTTokenVerifier:
    """Verifies MCP client bearer tokens issued by an external OAuth2/OIDC IdP.

    Fetches the issuer's JWKS via standard OIDC discovery
    ('{issuer}/.well-known/openid-configuration' -> 'jwks_uri'),
    caching it for ``jwks_cache_ttl_seconds``. Validates the JWS
    signature, 'iss', 'aud' (must include resource_server_url - the
    audience binding that makes token passthrough structurally
    rejectable), and 'exp'.

    Never raises: verify_token() returns None for any failure (bad
    signature, wrong audience, expired, network error fetching JWKS,
    malformed token, mTLS certificate-binding mismatch, etc.),
    matching the TokenVerifier protocol's contract - the caller
    (mcp.server.auth.middleware.bearer_auth.BearerAuthBackend) treats
    None as "unauthenticated" and responds 401, not a 500.

    If a token carries a 'cnf.x5t#S256' confirmation claim (RFC 8705
    mutual-TLS certificate-bound access token), it is only accepted
    when the current request's client certificate - forwarded by a
    trusted reverse proxy and read via the ``client_cert_thumbprint``
    contextvar (see auth/mtls_binding.py) - has that same thumbprint.
    When ``require_mtls_binding`` is True, tokens *without* a 'cnf'
    claim are rejected outright, closing the downgrade path where an
    attacker replays a stolen bearer token that was never cert-bound
    in the first place.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        *,
        issuer_url: str,
        resource_server_url: str,
        jwks_cache_ttl_seconds: int = 900,
        require_mtls_binding: bool = False,
    ) -> None:
        """Initializes the verifier.

        Args:
            http_client: HTTP client for JWKS/discovery requests (no
                auth needed - these are public endpoints).
            issuer_url: The OAuth2/OIDC issuer expected in the token's
                'iss' claim.
            resource_server_url: This server's own canonical URL,
                expected in the token's 'aud' claim (RFC 8707).
            jwks_cache_ttl_seconds: How long to reuse a fetched JWKS
                before refetching.
            require_mtls_binding: If True, reject any token lacking a
                'cnf.x5t#S256' claim (RFC 8705 mTLS certificate
                binding), instead of only enforcing the binding when
                present. Requires a reverse proxy in front of this
                server that terminates mTLS and forwards the client
                certificate (see auth/mtls_binding.py).
        """
        self._http = http_client
        self._issuer_url = issuer_url.rstrip("/")
        self._resource_server_url = resource_server_url
        self._cache_ttl = timedelta(seconds=jwks_cache_ttl_seconds)
        self._require_mtls_binding = require_mtls_binding
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cached_at: datetime | None = None

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verifies a bearer token per the TokenVerifier protocol.

        Args:
            token: The raw bearer token string (no 'Bearer ' prefix).

        Returns:
            AccessToken with the verified claims, or None if the
            token is invalid, expired, or fails audience/issuer checks.
        """
        try:
            jwks = await self._get_jwks()
            header = jwcrypto_jwt.JWT(jwt=token).token.jose_header
            kid = header.get("kid")
            key_set = jwk.JWKSet.from_json(json.dumps(jwks))
            signing_key = key_set.get_key(kid) if kid else None
            if signing_key is None:
                log.warning("mcp_token_key_not_found", kid=kid)
                return None

            verified = jwcrypto_jwt.JWT(
                key=signing_key,
                jwt=token,
                expected_type="JWS",
                check_claims={
                    "iss": self._issuer_url,
                    "aud": self._resource_server_url,
                    "exp": None,
                },
            )
        except Exception as exc:
            log.warning("mcp_token_verification_failed", error=str(exc))
            return None

        claims = json.loads(verified.claims)
        if not self._check_mtls_binding(claims):
            return None
        return self._to_access_token(token, claims)

    def _check_mtls_binding(self, claims: dict[str, Any]) -> bool:
        """Enforces RFC 8705 certificate binding, if applicable.

        Args:
            claims: The already signature/iss/aud/exp-verified claims.

        Returns:
            True if the token may proceed: either it carries no
            'cnf.x5t#S256' claim and binding isn't mandatory, or it
            does and matches the current request's client
            certificate thumbprint.
        """
        cnf = claims.get("cnf")
        bound_thumbprint = cnf.get("x5t#S256") if isinstance(cnf, dict) else None

        if bound_thumbprint is None:
            if self._require_mtls_binding:
                log.warning("mcp_token_missing_mtls_binding")
                return False
            return True

        current_thumbprint = client_cert_thumbprint.get()
        if current_thumbprint is None or current_thumbprint != bound_thumbprint:
            log.warning(
                "mcp_token_mtls_binding_mismatch",
                has_client_cert=current_thumbprint is not None,
            )
            return False
        return True

    def _to_access_token(self, token: str, claims: dict[str, Any]) -> AccessToken:
        """Maps verified JWT claims onto the SDK's AccessToken model.

        Args:
            token: The original raw token string.
            claims: The verified claims.

        Returns:
            Populated AccessToken.
        """
        scope_claim = claims.get("scope", "")
        scopes = (
            scope_claim.split() if isinstance(scope_claim, str) else list(scope_claim)
        )
        client_id = claims.get("client_id") or claims.get("azp") or claims.get("sub")
        return AccessToken(
            token=token,
            client_id=str(client_id) if client_id else "",
            scopes=scopes,
            expires_at=int(claims["exp"]) if "exp" in claims else None,
            resource=self._resource_server_url,
            subject=claims.get("sub"),
            claims=claims,
        )

    async def _get_jwks(self) -> dict[str, Any]:
        """Returns the cached JWKS, refetching via OIDC discovery if stale.

        Returns:
            The parsed JWKS document.

        Raises:
            httpx.HTTPError: If the discovery document or JWKS fetch fails.
            KeyError: If the discovery document has no 'jwks_uri'.
        """
        now = datetime.now(UTC)
        if (
            self._jwks_cache is not None
            and self._jwks_cached_at is not None
            and now - self._jwks_cached_at < self._cache_ttl
        ):
            return self._jwks_cache

        discovery = await self._http.get(
            f"{self._issuer_url}/.well-known/openid-configuration"
        )
        discovery.raise_for_status()
        jwks_uri = discovery.json()["jwks_uri"]

        jwks_response = await self._http.get(jwks_uri)
        jwks_response.raise_for_status()
        jwks: dict[str, Any] = jwks_response.json()
        self._jwks_cache = jwks
        self._jwks_cached_at = now
        return jwks
