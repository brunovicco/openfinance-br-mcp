"""private_key_jwt client authentication for FAPI-BR 2.0.

The FAPI-BR 2.2.0 security profile mandates ``private_key_jwt`` as the
*only* client authentication method at the token endpoint - mTLS and
``client_secret``-based methods are not accepted. This module builds
the signed JWT assertion RFC 7523 requires.

Uses ``jwcrypto``, which supports PS256 andis also used for ID token
decryption (RSA-OAEP + A256GCM).

Example:
    >>> assertion = build_client_assertion(audience="https://bank.example/token")
    >>> # sent as client_assertion + client_assertion_type in the token request body
"""

import time
import uuid
from pathlib import Path

from jwcrypto import jwk, jwt

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
_ASSERTION_TTL_SECONDS = 300


def load_private_key(path: str | None = None) -> jwk.JWK:
    """Loads a PEM-encoded private key from disk as a JWK.

    Args:
        path: Path to the PEM key. Defaults to settings.private_key_path
            (the key used to sign private_key_jwt client assertions and
            PAR/JAR request objects) - pass
            settings.id_token_decryption_key_path explicitly to load a
            distinct key for ID token decryption instead (see
            id_token.py's module docstring for why a bank's client
            registration may require these to differ).

    Returns:
        The key, ready to sign or decrypt with.

    Raises:
        AuthenticationError: If no path is configured (neither the
            argument nor PRIVATE_KEY_PATH), the file can't be read, or
            its contents aren't a valid PEM key.
    """
    key_path = path or settings.private_key_path
    if not key_path:
        raise AuthenticationError(
            "PRIVATE_KEY_PATH is not configured - required for "
            "private_key_jwt client authentication outside mock mode",
            code="NO_PRIVATE_KEY",
        )
    try:
        pem_bytes = Path(key_path).read_bytes()
    except OSError as exc:
        raise AuthenticationError(
            f"Failed to read private key at '{key_path}': {exc}",
            code="PRIVATE_KEY_READ_ERROR",
        ) from exc

    try:
        return jwk.JWK.from_pem(pem_bytes)
    except Exception as exc:
        raise AuthenticationError(
            f"Private key at '{key_path}' is not a valid PEM-encoded key: {exc}",
            code="PRIVATE_KEY_INVALID",
        ) from exc


def build_client_assertion(*, audience: str) -> str:
    """Builds a signed private_key_jwt client assertion (RFC 7523).

    Args:
        audience: The 'aud' claim - the token or PAR endpoint URL this
            assertion authenticates the client to.

    Returns:
        Signed compact JWT string, ready to send as the
        ``client_assertion`` form field alongside
        ``client_assertion_type=CLIENT_ASSERTION_TYPE``.

    Raises:
        AuthenticationError: If CLIENT_ID or the private key is not
            configured.
    """
    if not settings.client_id:
        raise AuthenticationError("CLIENT_ID is not configured", code="NO_CLIENT_ID")

    key = load_private_key()
    now = int(time.time())
    claims = {
        "iss": settings.client_id,
        "sub": settings.client_id,
        "aud": audience,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + _ASSERTION_TTL_SECONDS,
    }
    header = {"alg": settings.private_key_jwt_alg}
    if settings.private_key_kid:
        header["kid"] = settings.private_key_kid

    token = jwt.JWT(header=header, claims=claims)
    token.make_signed_token(key)
    return str(token.serialize())
