"""JWS message signing/verification for the Open Finance Brasil Payments API.

Unlike the data-sharing APIs (Accounts, Credit Cards, ...), the
Payments API requires the request and response *bodies* themselves to
be signed as a JWS (detached or embedded payload, per the FAPI-BR
message signing profile) - a valid bearer token and TLS channel are
not considered sufficient given the transactional (money-moving)
nature of these calls. This module signs an outgoing payment request
body with the client's own private key (reusing the same key
``jwt_client_auth.py`` uses for ``private_key_jwt``/JAR - the FAPI-BR
profile permits, but doesn't require, a separate signing key pair) and
verifies an incoming signed response against the bank's published
JWKS.

This is intentionally a thin, focused module: it signs/verifies a JSON
payload as a compact JWS, using the same key-loading and algorithm
conventions already established for JAR/private_key_jwt. It does not
implement JWS detached-payload variants some FAPI-BR message-signing
guidance permits (this project's payloads are small; embedding is the
simpler, unambiguous default here) - if a given bank's registration
requires detached signatures, add a second function rather than
overloading this one.

Example:
    >>> signed = sign_payment_payload({"data": {"payment": {...}}})
    >>> claims = verify_payment_response(signed_response, jwks=bank_jwks)
"""

import json
from typing import Any

from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.jwt_client_auth import load_private_key
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError


def sign_payment_payload(payload: dict[str, Any]) -> str:
    """Signs a payment request payload as a compact JWS.

    Args:
        payload: The JSON-serializable payment request body (e.g. the
            ``{"data": {...}}`` envelope ``initiate_pix`` builds).

    Returns:
        Compact JWS serialization (``header.payload.signature``),
        suitable for sending as the payment request body per the
        FAPI-BR message signing profile - some bank registrations
        expect this in the request body itself, others as a header
        alongside a plain JSON body; consult that bank's OpenAPI spec
        before wiring the HTTP call (see adapters/default_adapter.py).

    Raises:
        AuthenticationError: If PRIVATE_KEY_PATH is not configured, or
            the key can't be loaded.
    """
    key = load_private_key()
    header = {"alg": settings.private_key_jwt_alg}
    if settings.private_key_kid:
        header["kid"] = settings.private_key_kid

    token = jwcrypto_jwt.JWT(header=header, claims=payload)
    token.make_signed_token(key)
    return str(token.serialize())


def verify_payment_response(
    signed_response: str, *, jwks: dict[str, Any]
) -> dict[str, Any]:
    """Verifies a bank's signed payment response and returns its payload.

    Args:
        signed_response: Compact JWS string received from the bank.
        jwks: The bank's JSON Web Key Set (see
            DirectoryClient.resolve_jwks), used to verify the
            signature.

    Returns:
        The verified response payload.

    Raises:
        AuthenticationError: If the signature doesn't verify, the
            signing key isn't found in the bank's JWKS, or the
            response isn't a well-formed JWS.
    """
    try:
        header = jwcrypto_jwt.JWT(jwt=signed_response).token.jose_header
    except Exception as exc:
        raise AuthenticationError(
            f"Payment response is not a well-formed JWS: {exc}",
            code="PAYMENT_RESPONSE_MALFORMED",
        ) from exc

    kid = header.get("kid")
    key_set = jwk.JWKSet.from_json(json.dumps(jwks))
    signing_key = key_set.get_key(kid) if kid else None
    if signing_key is None:
        raise AuthenticationError(
            f"No matching signing key (kid={kid!r}) found in the bank's JWKS "
            "for the payment response",
            code="PAYMENT_RESPONSE_KEY_NOT_FOUND",
        )

    try:
        verified = jwcrypto_jwt.JWT(
            key=signing_key, jwt=signed_response, expected_type="JWS"
        )
    except Exception as exc:
        raise AuthenticationError(
            f"Payment response signature verification failed: {exc}",
            code="PAYMENT_RESPONSE_INVALID_SIGNATURE",
        ) from exc

    result: dict[str, Any] = json.loads(verified.claims)
    return result
