"""Unit tests for RFC 8705 mTLS client-cert binding support.

Uses a real self-signed X.509 certificate (cryptography) - genuine
DER/SHA-256 thumbprinting, not mocked crypto.
"""

import base64
import datetime
import hashlib
from urllib.parse import quote

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from openfinance_br_mcp.auth.mtls_binding import (
    MTLSClientCertMiddleware,
    client_cert_thumbprint,
    compute_cert_thumbprint,
)


def _make_self_signed_cert_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "test-mcp-client")]
    )
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("ascii")


@pytest.fixture
def client_cert_pem() -> str:
    return _make_self_signed_cert_pem()


async def _noop_receive() -> dict:
    return {}


async def _noop_send(_message: dict) -> None:
    pass


class TestComputeCertThumbprint:
    def test_matches_manual_sha256_of_der(self, client_cert_pem: str) -> None:
        cert = x509.load_pem_x509_certificate(client_cert_pem.encode("utf-8"))
        expected_digest = hashlib.sha256(
            cert.public_bytes(serialization.Encoding.DER)
        ).digest()
        expected = (
            base64.urlsafe_b64encode(expected_digest).rstrip(b"=").decode("ascii")
        )

        assert compute_cert_thumbprint(client_cert_pem) == expected

    def test_returns_none_for_malformed_pem(self) -> None:
        assert compute_cert_thumbprint("not a certificate") is None


class TestMTLSClientCertMiddleware:
    @pytest.mark.asyncio
    async def test_sets_contextvar_from_header(self, client_cert_pem: str) -> None:
        expected = compute_cert_thumbprint(client_cert_pem)
        seen_inside: list[str | None] = []

        async def inner_app(scope: dict, receive: object, send: object) -> None:
            seen_inside.append(client_cert_thumbprint.get())

        middleware = MTLSClientCertMiddleware(inner_app)
        scope = {
            "type": "http",
            "headers": [
                (b"x-ssl-client-cert", quote(client_cert_pem).encode("latin-1")),
            ],
        }

        await middleware(scope, _noop_receive, _noop_send)

        assert seen_inside == [expected]
        assert client_cert_thumbprint.get() is None  # reset after the call

    @pytest.mark.asyncio
    async def test_no_header_leaves_contextvar_none(self) -> None:
        seen_inside: list[str | None] = []

        async def inner_app(scope: dict, receive: object, send: object) -> None:
            seen_inside.append(client_cert_thumbprint.get())

        middleware = MTLSClientCertMiddleware(inner_app)
        scope = {"type": "http", "headers": []}

        await middleware(scope, _noop_receive, _noop_send)

        assert seen_inside == [None]

    @pytest.mark.asyncio
    async def test_non_http_scope_passes_through_untouched(self) -> None:
        calls = []

        async def inner_app(scope: dict, receive: object, send: object) -> None:
            calls.append(scope)

        middleware = MTLSClientCertMiddleware(inner_app)
        scope = {"type": "lifespan"}

        await middleware(scope, _noop_receive, _noop_send)

        assert calls == [scope]
