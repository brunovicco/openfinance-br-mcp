"""Unit tests for auth/payment_jws.py's payment request/response signing."""

import base64
import json

import pytest
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.payment_jws import (
    sign_payment_payload,
    verify_payment_response,
)
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

PAYLOAD = {"data": {"payment": {"amount": "150.00"}}}


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
    monkeypatch.setattr(settings, "private_key_kid", "test-kid")


class TestSignPaymentPayload:
    """Tests for sign_payment_payload()."""

    def test_produces_a_compact_jws_carrying_the_payload(
        self, rsa_public_key_pem: str
    ) -> None:
        signed = sign_payment_payload(PAYLOAD)

        assert signed.count(".") == 2  # header.payload.signature

        public_key = jwk.JWK.from_pem(rsa_public_key_pem.encode())
        verified = jwcrypto_jwt.JWT(key=public_key, jwt=signed, expected_type="JWS")
        assert json.loads(verified.claims) == PAYLOAD

    def test_header_carries_the_configured_kid(self) -> None:
        signed = sign_payment_payload(PAYLOAD)
        header_b64 = signed.split(".")[0]
        padded = header_b64 + "=" * (-len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(padded))
        assert header["kid"] == "test-kid"

    def test_raises_when_private_key_path_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "private_key_path", None)
        with pytest.raises(AuthenticationError):
            sign_payment_payload(PAYLOAD)


class TestVerifyPaymentResponse:
    """Tests for verify_payment_response()."""

    def test_verifies_a_correctly_signed_response(
        self, rsa_public_key_pem: str
    ) -> None:
        signed = sign_payment_payload(PAYLOAD)
        key = jwk.JWK.from_pem(rsa_public_key_pem.encode())
        key.update(kid="test-kid")
        jwks = {"keys": [json.loads(key.export_public())]}

        result = verify_payment_response(signed, jwks=jwks)

        assert result == PAYLOAD

    def test_raises_on_malformed_jws(self) -> None:
        with pytest.raises(AuthenticationError, match="not a well-formed JWS"):
            verify_payment_response("not-a-jws", jwks={"keys": []})

    def test_raises_when_kid_not_found_in_jwks(self, rsa_public_key_pem: str) -> None:
        signed = sign_payment_payload(PAYLOAD)

        with pytest.raises(AuthenticationError, match="No matching signing key"):
            verify_payment_response(signed, jwks={"keys": []})

    def test_raises_on_signature_mismatch_with_wrong_key(self) -> None:
        signed = sign_payment_payload(PAYLOAD)
        other_key = jwk.JWK.generate(kty="RSA", size=2048, kid="test-kid")
        jwks = {"keys": [json.loads(other_key.export_public())]}

        with pytest.raises(AuthenticationError, match="signature verification failed"):
            verify_payment_response(signed, jwks=jwks)
