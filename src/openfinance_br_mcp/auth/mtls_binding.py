"""RFC 8705 mutual-TLS certificate-bound access tokens, for MCP clients.

The MCP client OAuth 2.1 token verifier (mcp_token_verifier.py) checks
'iss'/'aud'/'exp'/signature, but a bearer token that only proves those
can be replayed by anyone who steals it. RFC 8705 closes that gap by
binding the token to the TLS client certificate presented when it was
issued: the token carries a 'cnf.x5t#S256' claim (base64url SHA-256
thumbprint of the client cert's DER encoding), and the resource server
must reject the token unless the *same* certificate authenticates the
current connection.

This server does not terminate TLS itself for the 'streamable-http'
transport - it expects to sit behind a reverse proxy/gateway (nginx,
Envoy, a cloud load balancer) that terminates mTLS, validates the
client certificate against a trusted CA, and forwards it to the app
via an HTTP header (nginx's $ssl_client_escaped_cert convention: the
PEM certificate, URL-encoded). That proxy MUST strip/overwrite any
client-supplied copy of this header - if it doesn't, a client can
forge the header and this binding check becomes worthless. See
docs/en/authorization.md for the required proxy configuration.

MTLSClientCertMiddleware runs ahead of the MCP SDK's BearerAuthBackend
(whose TokenVerifier.verify_token(token: str) protocol - see
mcp/server/auth/provider.py - takes only the token, never the
connection) and stashes the current request's client-cert thumbprint
in a contextvar, since that's the only channel available to get this
value from ASGI scope into JWTTokenVerifier.verify_token without
forking the SDK's middleware.
"""

import base64
import hashlib
from contextvars import ContextVar
from urllib.parse import unquote

import structlog
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from starlette.types import ASGIApp, Receive, Scope, Send

log = structlog.get_logger(__name__)

DEFAULT_CLIENT_CERT_HEADER = "x-ssl-client-cert"

client_cert_thumbprint: ContextVar[str | None] = ContextVar(
    "client_cert_thumbprint", default=None
)


def compute_cert_thumbprint(pem_cert: str) -> str | None:
    """Computes the RFC 8705 'x5t#S256' confirmation value for a PEM cert.

    Args:
        pem_cert: PEM-encoded X.509 certificate.

    Returns:
        Base64url-encoded (no padding) SHA-256 digest of the
        certificate's DER encoding, or None if pem_cert is malformed.
    """
    try:
        cert = x509.load_pem_x509_certificate(pem_cert.encode("utf-8"))
        der = cert.public_bytes(Encoding.DER)
    except ValueError as exc:
        log.warning("mtls_client_cert_unparseable", error=str(exc))
        return None
    digest = hashlib.sha256(der).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class MTLSClientCertMiddleware:
    """ASGI middleware that surfaces the proxy-forwarded client cert.

    Reads ``header_name`` (case-insensitive, URL-decoded PEM
    certificate - nginx's ``$ssl_client_escaped_cert``/AWS ALB's
    ``x-amzn-mtls-clientcert`` convention) off each HTTP request,
    computes its RFC 8705 thumbprint, and publishes it via the
    ``client_cert_thumbprint`` contextvar for the duration of that
    request so ``JWTTokenVerifier.verify_token`` can read it.
    """

    def __init__(
        self, app: ASGIApp, *, header_name: str = DEFAULT_CLIENT_CERT_HEADER
    ) -> None:
        self._app = app
        self._header_name = header_name.lower().encode("latin-1")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        thumbprint = None
        for key, value in scope.get("headers", []):
            if key.lower() == self._header_name:
                pem_cert = unquote(value.decode("latin-1"))
                thumbprint = compute_cert_thumbprint(pem_cert)
                break

        token = client_cert_thumbprint.set(thumbprint)
        try:
            await self._app(scope, receive, send)
        finally:
            client_cert_thumbprint.reset(token)
