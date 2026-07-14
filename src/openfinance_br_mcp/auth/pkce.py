"""PKCE (Proof Key for Code Exchange) implementation for FAPI 1.0 Advanced.

The BCB requires the FAPI 1.0 Advanced profile for all client-facing
data APIs. This module generates and validates the ``code_verifier``
and ``code_challenge`` parameters as defined in RFC 7636.

Example:
    >>> from openfinance_br_mcp.auth.pkce import PKCEChallenge
    >>> challenge = PKCEChallenge.generate()
    >>> print(challenge.code_challenge_method)
    'S256'
"""

import hashlib
import secrets
from base64 import urlsafe_b64encode

from pydantic import BaseModel, Field

_VERIFIER_MIN_LENGTH = 43
_VERIFIER_MAX_LENGTH = 128
_VERIFIER_BYTES = 32  # results in ~43 base64url chars


class PKCEChallenge(BaseModel):
    """code_verifier/code_challenge pair generated for an OAuth2 session.

    Attributes:
        code_verifier: High-entropy random string (RFC 7636 §4.1).
        code_challenge: SHA-256 hash of the verifier, base64url-encoded
            without padding.
        code_challenge_method: Always 'S256' (the BCB does not accept
            'plain').
    """

    code_verifier: str = Field(
        ...,
        min_length=_VERIFIER_MIN_LENGTH,
        max_length=_VERIFIER_MAX_LENGTH,
        description="Code verifier - keep secret until the token exchange",
    )
    code_challenge: str = Field(..., description="Base64url SHA-256 of the verifier")
    code_challenge_method: str = Field(default="S256")

    @classmethod
    def generate(cls) -> "PKCEChallenge":
        """Generates a new cryptographically secure verifier/challenge pair.

        Uses ``secrets.token_bytes`` to guarantee adequate entropy.
        The challenge is computed as
        ``BASE64URL(SHA256(ASCII(code_verifier)))``, per RFC 7636 §4.2.

        Returns:
            PKCEChallenge instance ready to use in the OAuth2 flow.

        Example:
            >>> challenge = PKCEChallenge.generate()
            >>> len(challenge.code_verifier) >= 43
            True
        """
        raw = secrets.token_bytes(_VERIFIER_BYTES)
        code_verifier = urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

        return cls(code_verifier=code_verifier, code_challenge=code_challenge)

    def verify(self, verifier: str) -> bool:
        """Verifies whether a verifier matches the stored challenge.

        Useful for tests and callback-server-side validation.

        Args:
            verifier: The code_verifier to validate.

        Returns:
            True if the verifier's SHA-256 hash matches the challenge.
        """
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        expected = urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return secrets.compare_digest(expected, self.code_challenge)
