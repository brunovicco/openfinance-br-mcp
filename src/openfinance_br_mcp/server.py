"""Entry point of the openfinance-br-mcp MCP server.

Responsible for:
  - Configuring structured logging (structlog).
  - Building the FastMCP server and registering all tools.
  - Serving over stdio (local clients, e.g. Claude Desktop) or
    Streamable HTTP (remote/production deployments), per
    ``settings.mcp_transport``.

Shared dependencies (HTTP client, token store, bank adapters,
categorizer) are built once in ``context.app_lifespan`` and injected
into every tool call - see ``openfinance_br_mcp.context``.

Example:
    Run directly::

        uv run openfinance-mcp

    Or via module::

        python -m openfinance_br_mcp.server

    Override the transport for a single run::

        uv run openfinance-mcp --transport streamable-http
"""

import argparse
import logging
import sys
from typing import Any
from urllib.parse import urlparse

import httpx
import structlog
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from openfinance_br_mcp.auth.mcp_token_verifier import JWTTokenVerifier
from openfinance_br_mcp.auth.mtls_binding import MTLSClientCertMiddleware
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import app_lifespan
from openfinance_br_mcp.mcp_primitives import register_mcp_primitives
from openfinance_br_mcp.observability.logging_correlation import add_trace_context
from openfinance_br_mcp.observability.tracing import configure_tracing
from openfinance_br_mcp.tools.accounts import get_balance, list_accounts
from openfinance_br_mcp.tools.consent import (
    check_consent_status,
    complete_consent,
    revoke_consent,
    start_consent,
)
from openfinance_br_mcp.tools.credit_cards import (
    get_credit_card_bills,
    list_credit_cards,
)
from openfinance_br_mcp.tools.investments import (
    list_funds,
    list_investments,
    list_treasure_titles,
    list_variable_incomes,
)
from openfinance_br_mcp.tools.payments import (
    check_payment_consent_status,
    complete_payment_consent,
    start_payment_consent,
)
from openfinance_br_mcp.tools.pix import initiate_pix, list_pix_keys
from openfinance_br_mcp.tools.transactions import list_transactions

log = structlog.get_logger(__name__)


def _configure_logging() -> None:
    """Configures structlog with the format and level defined in Settings.

    Uses JSON in production (format='json') and colored output in the
    terminal during development (format='console').
    """
    level = getattr(logging, settings.log_level, logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_trace_context,
    ]

    renderer: Any
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )


def _build_transport_security() -> TransportSecuritySettings | None:
    """Builds DNS-rebinding protection settings for the HTTP transport.

    FastMCP auto-enables protection for loopback hosts. For any other
    bind host (e.g. 0.0.0.0 in a container), protection must be
    configured explicitly with the externally-visible origins -
    otherwise it stays disabled, which is unsafe for a networked
    deployment.

    Returns:
        TransportSecuritySettings to pass to FastMCP, or None to fall
        back to its default (loopback-only auto-protection).
    """
    if settings.mcp_http_host in ("127.0.0.1", "localhost", "::1"):
        return None

    if not settings.mcp_http_allowed_origins:
        log.warning(
            "mcp_http_allowed_origins_empty",
            detail=(
                "Binding to a non-loopback host without MCP_HTTP_ALLOWED_ORIGINS "
                "leaves DNS-rebinding protection disabled."
            ),
        )
        return None

    # allowed_hosts is checked against the bare Host header (e.g.
    # 'your-domain.com'), while allowed_origins is checked against the
    # scheme-prefixed Origin header (e.g. 'https://your-domain.com') -
    # a bare Host header can never equal a 'https://...' string, so
    # these must not be set to the same scheme-prefixed list. Derive
    # allowed_hosts from allowed_origins instead of requiring the two
    # to be configured (and kept in sync) separately.
    allowed_hosts = [
        urlparse(origin).netloc for origin in settings.mcp_http_allowed_origins
    ]

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=settings.mcp_http_allowed_origins,
    )


def _build_mcp_auth() -> tuple[AuthSettings | None, TokenVerifier | None]:
    """Builds MCP client OAuth 2.1 resource-server auth, if configured.

    Auth stays off by default (both return None) - config.py's
    validate_mcp_oauth_pair guarantees issuer_url and
    resource_server_url are either both set or both unset, so checking
    one here is sufficient. With auth off, the HTTP transport relies
    solely on staying bound to a loopback host (see
    _build_transport_security) for safety, which is what the MCP
    authorization spec permits for local/dev deployments.

    This verifier is deliberately independent from AppContext's shared
    http_client (built later, per-request-lifespan, for bank API
    calls) - keeping MCP-client-auth infrastructure and bank-auth
    infrastructure on separate HTTP clients is one more structural
    reason a client token could never accidentally ride along on a
    bank request. See auth/mcp_token_verifier.py's module docstring.

    Returns:
        (AuthSettings, TokenVerifier) if mcp_oauth_issuer_url is
        configured, otherwise (None, None).
    """
    if settings.mcp_oauth_issuer_url is None:
        return None, None

    assert (
        settings.mcp_oauth_resource_server_url is not None
    )  # see validate_mcp_oauth_pair

    auth_settings = AuthSettings(
        issuer_url=settings.mcp_oauth_issuer_url,
        resource_server_url=settings.mcp_oauth_resource_server_url,
        required_scopes=settings.mcp_oauth_required_scopes or None,
    )
    token_verifier = JWTTokenVerifier(
        httpx.AsyncClient(timeout=settings.http_timeout_seconds),
        issuer_url=str(settings.mcp_oauth_issuer_url),
        resource_server_url=str(settings.mcp_oauth_resource_server_url),
        jwks_cache_ttl_seconds=settings.mcp_oauth_jwks_cache_ttl_seconds,
        require_mtls_binding=settings.mcp_oauth_require_mtls_binding,
    )
    return auth_settings, token_verifier


async def _health(_request: Request) -> JSONResponse:
    """Liveness/readiness endpoint for the Streamable HTTP transport.

    Args:
        _request: Incoming Starlette request (unused).

    Returns:
        A minimal JSON payload confirming the process is serving.
    """
    return JSONResponse(
        {
            "status": "ok",
            "service": settings.server_name,
            "version": settings.server_version,
        }
    )


def build_server() -> FastMCP:
    """Builds the FastMCP server and registers all tools.

    Returns:
        Configured FastMCP instance, not yet running.
    """
    auth_settings, token_verifier = _build_mcp_auth()
    mcp = FastMCP(
        name=settings.server_name,
        instructions=(
            "Use read-only tools to inspect Open Finance data. Before initiating "
            "a real PIX payment, obtain and complete a dedicated payment consent, "
            "then preserve the same idempotency key for retries. Use the "
            "openfinance://banks/ resource to discover configured institutions."
        ),
        lifespan=app_lifespan,
        host=settings.mcp_http_host,
        port=settings.mcp_http_port,
        stateless_http=settings.mcp_http_stateless,
        json_response=True,
        transport_security=_build_transport_security(),
        auth=auth_settings,
        token_verifier=token_verifier,
    )

    read_only = ToolAnnotations(readOnlyHint=True)

    mcp.add_tool(
        list_accounts,
        annotations=read_only,
    )
    mcp.add_tool(
        get_balance,
        annotations=read_only,
    )
    mcp.add_tool(
        list_transactions,
        annotations=read_only,
    )
    mcp.add_tool(
        list_credit_cards,
        annotations=read_only,
    )
    mcp.add_tool(
        get_credit_card_bills,
        annotations=read_only,
    )
    mcp.add_tool(
        list_pix_keys,
        annotations=read_only,
    )
    mcp.add_tool(
        initiate_pix,
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=True, idempotentHint=True
        ),
    )
    mcp.add_tool(
        list_investments,
        annotations=read_only,
    )
    mcp.add_tool(
        list_funds,
        annotations=read_only,
    )
    mcp.add_tool(
        list_variable_incomes,
        annotations=read_only,
    )
    mcp.add_tool(
        list_treasure_titles,
        annotations=read_only,
    )
    mcp.add_tool(
        start_consent,
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False),
    )
    mcp.add_tool(
        complete_consent,
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False),
    )
    mcp.add_tool(
        check_consent_status,
        annotations=read_only,
    )
    mcp.add_tool(
        revoke_consent,
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=True, idempotentHint=True
        ),
    )
    mcp.add_tool(
        start_payment_consent,
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False),
    )
    mcp.add_tool(
        complete_payment_consent,
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False),
    )
    mcp.add_tool(
        check_payment_consent_status,
        annotations=read_only,
    )

    register_mcp_primitives(mcp)

    mcp.custom_route("/health", methods=["GET"])(_health)

    return mcp


def _run_streamable_http(mcp: FastMCP) -> None:
    """Serves the 'streamable-http' transport with mTLS binding wired in.

    Mirrors mcp.server.fastmcp.FastMCP.run_streamable_http_async, but
    inserts MTLSClientCertMiddleware ahead of the SDK's own
    AuthenticationMiddleware so JWTTokenVerifier can read the current
    request's proxy-forwarded client certificate via a contextvar (see
    auth/mtls_binding.py) - the SDK's TokenVerifier.verify_token(token)
    protocol only ever receives the bearer token, never the
    connection, so there is no other channel to pass this through.
    Only needed when MCP client OAuth is configured at all, since
    binding is enforced whenever a verified token happens to carry a
    'cnf' claim, not only when mcp_oauth_require_mtls_binding is set.
    """
    import anyio
    import uvicorn

    app = mcp.streamable_http_app()
    if mcp.settings.auth is not None:
        app.add_middleware(
            MTLSClientCertMiddleware,
            header_name=settings.mcp_oauth_mtls_cert_header,
        )

    async def _serve() -> None:
        config = uvicorn.Config(
            app,
            host=mcp.settings.host,
            port=mcp.settings.port,
            log_level=mcp.settings.log_level.lower(),
        )
        await uvicorn.Server(config).serve()

    anyio.run(_serve)


def main() -> None:
    """Synchronous entry point registered in pyproject.toml.

    Compatible with ``uv run openfinance-mcp`` and
    ``python -m openfinance_br_mcp.server``. Accepts an optional
    ``--transport`` flag overriding ``MCP_TRANSPORT`` for a single run.
    """
    parser = argparse.ArgumentParser(prog="openfinance-mcp")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default=settings.mcp_transport,
        help="MCP transport to serve (default: MCP_TRANSPORT env var, or 'stdio').",
    )
    args = parser.parse_args()

    _configure_logging()
    tracer_provider = configure_tracing()
    log.info(
        "server_start",
        name=settings.server_name,
        version=settings.server_version,
        log_level=settings.log_level,
        transport=args.transport,
        tracing_enabled=tracer_provider is not None,
    )

    mcp = build_server()
    if args.transport == "streamable-http":
        _run_streamable_http(mcp)
    else:
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
