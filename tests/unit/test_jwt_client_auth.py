"""Unit tests for private_key_jwt client assertion building."""

import json
import time

import pytest
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.jwt_client_auth import (
    CLIENT_ASSERTION_TYPE,
    build_client_assertion,
    load_private_key,
)
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

AUDIENCE = "https://bank.example.com/token"


def _verify_and_decode(token: str, public_key_pem: str, *, audience: str) -> dict:
    """Verifies a JWS token's signature and returns its claims as a dict."""
    public_key = jwk.JWK.from_pem(public_key_pem.encode())
    verified = jwcrypto_jwt.JWT(
        key=public_key, jwt=token, expected_type="JWS", check_claims={"aud": audience}
    )
    claims: dict = json.loads(verified.claims)
    return claims


def _unverified_header(token: str) -> dict:
    """Returns a JWS token's header without verifying the signature."""
    parsed = jwcrypto_jwt.JWT(jwt=token)
    header: dict = parsed.token.jose_header
    return header


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
    monkeypatch.setattr(settings, "private_key_kid", "test-kid")


class TestLoadPrivateKey:
    """Tests for load_private_key()."""

    def test_raises_when_not_configured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "private_key_path", None)
        with pytest.raises(AuthenticationError, match="PRIVATE_KEY_PATH"):
            load_private_key()

    def test_raises_when_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "private_key_path", "/does/not/exist.pem")
        with pytest.raises(AuthenticationError, match="Failed to read"):
            load_private_key()

    def test_raises_when_file_not_a_valid_key(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        bad_key_path = tmp_path / "not-a-key.pem"
        bad_key_path.write_text("this is not a PEM key")
        monkeypatch.setattr(settings, "private_key_path", str(bad_key_path))
        with pytest.raises(AuthenticationError, match="not a valid"):
            load_private_key()

    def test_reads_configured_key_as_jwk(self, rsa_private_key_path: str) -> None:
        key = load_private_key()
        assert key.get("kty") == "RSA"
        assert key.has_private


class TestBuildClientAssertion:
    """Tests for build_client_assertion()."""

    def test_raises_when_client_id_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "client_id", None)
        with pytest.raises(AuthenticationError, match="CLIENT_ID"):
            build_client_assertion(audience=AUDIENCE)

    def test_produces_a_verifiable_jwt_with_expected_claims(
        self, rsa_public_key_pem: str
    ) -> None:
        token = build_client_assertion(audience=AUDIENCE)

        claims = _verify_and_decode(token, rsa_public_key_pem, audience=AUDIENCE)

        assert claims["iss"] == "test-client-id"
        assert claims["sub"] == "test-client-id"
        assert claims["aud"] == AUDIENCE
        assert "jti" in claims
        now = int(time.time())
        assert claims["iat"] <= now
        assert claims["exp"] > now

    def test_uses_ps256_by_default(self, rsa_public_key_pem: str) -> None:
        assert settings.private_key_jwt_alg == "PS256"
        token = build_client_assertion(audience=AUDIENCE)
        assert _unverified_header(token)["alg"] == "PS256"

    def test_includes_kid_header_when_configured(self) -> None:
        token = build_client_assertion(audience=AUDIENCE)
        assert _unverified_header(token)["kid"] == "test-kid"

    def test_each_call_produces_a_unique_jti(self, rsa_public_key_pem: str) -> None:
        first = _verify_and_decode(
            build_client_assertion(audience=AUDIENCE),
            rsa_public_key_pem,
            audience=AUDIENCE,
        )
        second = _verify_and_decode(
            build_client_assertion(audience=AUDIENCE),
            rsa_public_key_pem,
            audience=AUDIENCE,
        )
        assert first["jti"] != second["jti"]


def test_client_assertion_type_matches_rfc7523() -> None:
    assert (
        CLIENT_ASSERTION_TYPE
        == "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    )
