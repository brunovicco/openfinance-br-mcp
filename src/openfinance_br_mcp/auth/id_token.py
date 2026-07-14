"""ID token decryption and verification for FAPI-BR 2.0.

FAPI-BR 2.2.0 mandates ID token encryption: the authorization server
returns a nested JWT - a JWE (RSA-OAEP + A256GCM) whose plaintext
payload is itself a signed JWT (JWS). This module decrypts the outer
JWE with the client's private key, verifies the inner JWS against the
bank's published JWKS, and validates the OIDC claims FAPI requires
(iss, aud, exp, nonce).

Two jwcrypto quirks to be aware of:

- Decrypting the outer layer requires ``expected_type="JWE"``
  explicitly - jwcrypto's default type-guessing heuristic picks "JWS"
  for this shape and raises a confusing ``TypeError`` otherwise.
- Passing any ``check_claims`` dict disables jwcrypto's *automatic*
  expiration check entirely (it only runs when ``check_claims`` is
  unset). Expiration must be re-requested explicitly via
  ``check_claims={"exp": None, ...}`` - omitting it would silently
  accept an expired ID token.

The FAPI-BR security profile requires the client's registered JWKS to
expose a key tagged ``"use":"enc"`` for the bank to select when
encrypting the ID token, distinct in the JWKS from any ``"use":"sig"``
signing key entry - but doesn't forbid that key's underlying RSA
material being the same as the signing key's. This module decrypts
with ``settings.id_token_decryption_key_path`` if set, falling back to
the same ``PRIVATE_KEY_PATH`` RSA key used for signing (see
jwt_client_auth.py) otherwise - set the former only if your bank's
registration was done with genuinely separate key pairs.

Example:
    >>> claims = verify_id_token(
    ...     raw_id_token, issuer=issuer, jwks=jwks, nonce=nonce,
    ... )
    >>> claims["sub"]
"""

import json
from typing import Any

from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.jwt_client_auth import load_private_key
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError


def decrypt_id_token(raw_id_token: str) -> str:
    """Decrypts the outer JWE, returning the inner signed JWS.

    Args:
        raw_id_token: The 'id_token' value received from the
            authorization server - a JWE per FAPI-BR 2.2.0.

    Returns:
        The inner JWS in compact serialization. Its signature has not
        been verified yet - use verify_id_token for that.

    Raises:
        AuthenticationError: If decryption fails (wrong key, malformed
            token, or the token isn't actually a JWE).
    """
    key = load_private_key(settings.id_token_decryption_key_path)
    try:
        decrypted = jwcrypto_jwt.JWT(key=key, jwt=raw_id_token, expected_type="JWE")
    except Exception as exc:
        raise AuthenticationError(
            f"Failed to decrypt ID token: {exc}", code="ID_TOKEN_DECRYPT_ERROR"
        ) from exc
    return str(decrypted.claims)


def verify_id_token(
    raw_id_token: str,
    *,
    issuer: str,
    jwks: dict[str, Any],
    nonce: str,
) -> dict[str, Any]:
    """Decrypts and fully verifies an ID token per FAPI-BR 2.0.

    Args:
        raw_id_token: The JWE-wrapped ID token as received.
        issuer: Expected 'iss' claim - the bank's authorization server
            issuer (see DirectoryClient.resolve()).
        jwks: The bank's JSON Web Key Set (see
            DirectoryClient.resolve_jwks), used to verify the inner
            signature.
        nonce: The nonce sent in the original authorization request -
            must match to prevent replay.

    Returns:
        The verified claims of the ID token.

    Raises:
        AuthenticationError: If CLIENT_ID is not configured, or
            decryption, signature verification, or claim validation
            fails (including expiration, per the 60s leeway jwcrypto
            applies).
    """
    if not settings.client_id:
        raise AuthenticationError("CLIENT_ID is not configured", code="NO_CLIENT_ID")

    inner_jws = decrypt_id_token(raw_id_token)

    header = jwcrypto_jwt.JWT(jwt=inner_jws).token.jose_header
    kid = header.get("kid")
    key_set = jwk.JWKSet.from_json(json.dumps(jwks))
    signing_key = key_set.get_key(kid) if kid else None
    if signing_key is None:
        raise AuthenticationError(
            f"No matching signing key (kid={kid!r}) found in the bank's JWKS",
            code="ID_TOKEN_KEY_NOT_FOUND",
        )

    try:
        verified = jwcrypto_jwt.JWT(
            key=signing_key,
            jwt=inner_jws,
            expected_type="JWS",
            check_claims={
                "aud": settings.client_id,
                "iss": issuer,
                "nonce": nonce,
                "exp": None,
                "iat": None,
            },
        )
    except Exception as exc:
        raise AuthenticationError(
            f"ID token signature/claims verification failed: {exc}",
            code="ID_TOKEN_INVALID",
        ) from exc

    claims: dict[str, Any] = json.loads(verified.claims)

    # 'acr' was requested as an essential claim (see auth/par.py's
    # 'claims': {'id_token': {'acr': {'essential': True}}}) - a bank
    # honoring that request always returns it; its absence means the
    # authorization server either ignored the essential-claims request
    # or asserted no authentication context class at all, either of
    # which the FAPI-BR confidential client profile treats as a
    # verification failure, not a value to silently default.
    if "acr" not in claims:
        raise AuthenticationError(
            "ID token is missing the mandatory 'acr' claim",
            code="ID_TOKEN_MISSING_ACR",
        )

    return claims
