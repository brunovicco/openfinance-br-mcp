"""Unit tests for ID token decryption and verification (FAPI-BR 2.0)."""

import time

import pytest
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.id_token import decrypt_id_token, verify_id_token
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import AuthenticationError

ISSUER = "https://bank.example.com/"
NONCE = "test-nonce"


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)


@pytest.fixture
def bank_key() -> jwk.JWK:
    """A throwaway RSA key standing in for the bank's ID-token signing key."""
    return jwk.JWK.generate(kty="RSA", size=2048, kid="bank-kid-1")


@pytest.fixture
def bank_jwks(bank_key: jwk.JWK) -> dict:
    """A JWKS document containing only the public half of bank_key."""
    return {"keys": [dict(bank_key.export_public(as_dict=True))]}


def _build_id_token(
    *,
    client_public_key_pem: str,
    signing_key: jwk.JWK,
    claims: dict,
    kid: str = "bank-kid-1",
) -> str:
    """Builds a nested JWE(JWS) ID token, mirroring what a bank returns."""
    inner = jwcrypto_jwt.JWT(header={"alg": "PS256", "kid": kid}, claims=claims)
    inner.make_signed_token(signing_key)
    inner_compact = inner.serialize()

    client_public_key = jwk.JWK.from_pem(client_public_key_pem.encode())
    outer = jwcrypto_jwt.JWT(
        header={"alg": "RSA-OAEP", "enc": "A256GCM", "cty": "JWT"},
        claims=inner_compact,
    )
    outer.make_encrypted_token(client_public_key)
    return str(outer.serialize())


def _valid_claims() -> dict:
    now = int(time.time())
    return {
        "iss": ISSUER,
        "sub": "user-123",
        "aud": "test-client-id",
        "nonce": NONCE,
        "iat": now,
        "exp": now + 300,
    }


class TestDecryptIdToken:
    """Tests for decrypt_id_token()."""

    def test_returns_inner_jws(
        self, bank_key: jwk.JWK, rsa_public_key_pem: str
    ) -> None:
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=_valid_claims(),
        )

        inner = decrypt_id_token(token)

        assert inner.count(".") == 2  # compact JWS has 3 dot-separated parts

    def test_raises_on_wrong_decryption_key(self, bank_key: jwk.JWK) -> None:
        # Encrypted to some other, unrelated public key - not the one
        # configured via settings.private_key_path - so decryption must fail.
        unrelated_public_key_pem = (
            jwk.JWK.generate(kty="RSA", size=2048).export_to_pem().decode()
        )
        token = _build_id_token(
            client_public_key_pem=unrelated_public_key_pem,
            signing_key=bank_key,
            claims=_valid_claims(),
        )

        with pytest.raises(AuthenticationError, match="Failed to decrypt"):
            decrypt_id_token(token)


class TestVerifyIdToken:
    """Tests for verify_id_token()."""

    def test_returns_claims_for_valid_token(
        self, bank_key: jwk.JWK, bank_jwks: dict, rsa_public_key_pem: str
    ) -> None:
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=_valid_claims(),
        )

        claims = verify_id_token(token, issuer=ISSUER, jwks=bank_jwks, nonce=NONCE)

        assert claims["sub"] == "user-123"
        assert claims["aud"] == "test-client-id"

    def test_raises_when_client_id_missing(
        self, monkeypatch: pytest.MonkeyPatch, bank_jwks: dict
    ) -> None:
        monkeypatch.setattr(settings, "client_id", None)
        with pytest.raises(AuthenticationError, match="CLIENT_ID"):
            verify_id_token("irrelevant", issuer=ISSUER, jwks=bank_jwks, nonce=NONCE)

    def test_raises_on_signature_mismatch(
        self, bank_key: jwk.JWK, rsa_public_key_pem: str
    ) -> None:
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=_valid_claims(),
        )
        other_key = jwk.JWK.generate(kty="RSA", size=2048, kid="bank-kid-1")
        wrong_jwks = {"keys": [dict(other_key.export_public(as_dict=True))]}

        with pytest.raises(AuthenticationError, match="verification failed"):
            verify_id_token(token, issuer=ISSUER, jwks=wrong_jwks, nonce=NONCE)

    def test_raises_on_nonce_mismatch(
        self, bank_key: jwk.JWK, bank_jwks: dict, rsa_public_key_pem: str
    ) -> None:
        claims = _valid_claims()
        claims["nonce"] = "different-nonce"
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=claims,
        )

        with pytest.raises(AuthenticationError, match="verification failed"):
            verify_id_token(token, issuer=ISSUER, jwks=bank_jwks, nonce=NONCE)

    def test_raises_on_issuer_mismatch(
        self, bank_key: jwk.JWK, bank_jwks: dict, rsa_public_key_pem: str
    ) -> None:
        claims = _valid_claims()
        claims["iss"] = "https://impostor.example.com/"
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=claims,
        )

        with pytest.raises(AuthenticationError, match="verification failed"):
            verify_id_token(token, issuer=ISSUER, jwks=bank_jwks, nonce=NONCE)

    def test_raises_on_expired_token(
        self, bank_key: jwk.JWK, bank_jwks: dict, rsa_public_key_pem: str
    ) -> None:
        claims = _valid_claims()
        claims["exp"] = int(time.time()) - 3600
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=claims,
        )

        with pytest.raises(AuthenticationError, match="verification failed"):
            verify_id_token(token, issuer=ISSUER, jwks=bank_jwks, nonce=NONCE)

    def test_raises_when_kid_not_in_jwks(
        self, bank_key: jwk.JWK, rsa_public_key_pem: str
    ) -> None:
        token = _build_id_token(
            client_public_key_pem=rsa_public_key_pem,
            signing_key=bank_key,
            claims=_valid_claims(),
            kid="unknown-kid",
        )
        empty_jwks: dict = {"keys": []}

        with pytest.raises(AuthenticationError, match="No matching signing key"):
            verify_id_token(token, issuer=ISSUER, jwks=empty_jwks, nonce=NONCE)
