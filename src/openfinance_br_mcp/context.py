"""Application context and lifespan for the MCP server.

Centralizes the dependency graph (TokenStore → HTTP client → Adapters
→ Categorizer). FastMCP injects the ``AppContext`` instance into every
tool call via ``ctx.request_context.lifespan_context``.

Adapter construction branches on ``settings.environment``:
  - 'mock' (default): in-memory MockOpenFinanceAdapter per bank, no
    network access or credentials required.
  - 'sandbox'/'production': real adapters, with base URLs resolved via
    DirectoryClient against the live Directory of Participants. A
    per-bank resolution failure is logged and falls back to that
    adapter's hardcoded default URL rather than failing server
    startup entirely - one bank's directory hiccup shouldn't take down
    every other bank.

Example:
    >>> mcp = FastMCP("openfinance-br-mcp", lifespan=app_lifespan)
    >>> @mcp.tool()
    ... async def my_tool(ctx: AppRequestContext) -> str:
    ...     app = ctx.request_context.lifespan_context
    ...     return app.adapters["nubank"].bank_id
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx
import structlog
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from starlette.requests import Request

from openfinance_br_mcp.adapters.banco_do_brasil import BancoDoBrasilAdapter
from openfinance_br_mcp.adapters.base import BankAdapter, BankEndpoints
from openfinance_br_mcp.adapters.bradesco import BradescoAdapter
from openfinance_br_mcp.adapters.btg import BTGAdapter
from openfinance_br_mcp.adapters.caixa import CaixaAdapter
from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.adapters.itau import ItauAdapter
from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.adapters.nubank import NubankAdapter
from openfinance_br_mcp.adapters.picpay import PicPayAdapter
from openfinance_br_mcp.adapters.santander import SantanderAdapter
from openfinance_br_mcp.adapters.sicoob import SicoobAdapter
from openfinance_br_mcp.adapters.xp import XPAdapter
from openfinance_br_mcp.auth.authorization_session import AuthorizationSessionStore
from openfinance_br_mcp.auth.consent import ConsentManager
from openfinance_br_mcp.auth.idempotency_store import IdempotencyStore
from openfinance_br_mcp.auth.payment_consent import PaymentConsentManager
from openfinance_br_mcp.auth.principal_binding import PrincipalBindingStore
from openfinance_br_mcp.auth.redis_backend import RedisStore
from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.auth.token import TokenStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.directory.client import DirectoryClient
from openfinance_br_mcp.directory.models import ResolvedApi
from openfinance_br_mcp.exceptions import DirectoryError
from openfinance_br_mcp.tools.categorizer import TransactionCategorizer, get_categorizer

log = structlog.get_logger(__name__)


class _AdapterFactory(Protocol):
    """Shape of a concrete adapter's constructor.

    DefaultOpenFinanceAdapter.__init__ itself requires base_url/
    token_endpoint (it has no institution to default to) - but every
    concrete subclass (NubankAdapter, SicoobAdapter, CaixaAdapter)
    re-declares __init__ with its own defaults for both. This Protocol
    describes that actual, shared call shape so _build_real_adapters
    can construct an adapter with only some kwargs supplied, which
    `dict[str, type[DefaultOpenFinanceAdapter]]` cannot express (that
    would type-check against the parent's stricter, default-less
    signature instead).
    """

    def __call__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = ...,
        token_endpoint: str = ...,
    ) -> DefaultOpenFinanceAdapter: ...


_ADAPTER_CLASSES: dict[str, _AdapterFactory] = {
    "nubank": NubankAdapter,
    "sicoob": SicoobAdapter,
    "caixa": CaixaAdapter,
    "banco_do_brasil": BancoDoBrasilAdapter,
    "bradesco": BradescoAdapter,
    "itau": ItauAdapter,
    "santander": SantanderAdapter,
    "xp": XPAdapter,
    "picpay": PicPayAdapter,
    "btg": BTGAdapter,
}


@dataclass
class AppContext:
    """Shared dependencies available to every MCP tool call.

    Attributes:
        http_client: Shared HTTP client, configured with mTLS when enabled.
        token_store: OAuth2 token store shared by all adapters - backed
            by Redis when settings.redis_url is set, otherwise in-memory
            (see _build_shared_store).
        adapters: Registry of bank adapters, keyed by bank_id.
        categorizer: DSPy-based transaction categorizer.
        consent_manager: Manages consent creation/status/revocation
            against each bank's Consents API.
        authorization_sessions: Bridges start_consent and
            complete_consent across the two separate tool calls a
            single consent flow requires (see tools/consent.py).
        principal_bindings: Tracks which authenticated MCP client
            principal may act on which subject_id - see
            auth/principal_binding.py and tools/principal_guard.py.
        payment_consent_manager: Manages the Payments API's own,
            dedicated consent lifecycle - separate from
            consent_manager (data-sharing consents). See
            auth/payment_consent.py and tools/payments.py.
        idempotency_store: Persistent, cross-replica idempotency
            record for initiate_pix, replacing the old in-process
            pix_idempotency_cache. See auth/idempotency_store.py.
        directory: Shared DirectoryClient for resolving real bank
            endpoints. None in mock mode, where there is nothing to
            resolve.
        pix_idempotency_cache: Deprecated in-process idempotency cache,
            kept only so any external code still reading this
            attribute doesn't break outright - initiate_pix now uses
            idempotency_store instead. Scoped to the server process
            lifetime.
    """

    http_client: httpx.AsyncClient
    token_store: TokenStore
    adapters: dict[str, BankAdapter]
    categorizer: TransactionCategorizer
    consent_manager: ConsentManager
    authorization_sessions: AuthorizationSessionStore
    principal_bindings: PrincipalBindingStore
    payment_consent_manager: PaymentConsentManager
    idempotency_store: IdempotencyStore
    directory: DirectoryClient | None
    pix_idempotency_cache: dict[str, str] = field(default_factory=dict)


AppRequestContext = Context[ServerSession, AppContext, Request]
"""Fully-parameterized Context type for use as a tool's ``ctx`` parameter."""


def _build_http_client() -> httpx.AsyncClient:
    """Builds the shared HTTP client used by all bank adapters.

    mTLS is skipped in mock mode even if MTLS_ENABLED=true (its
    default): MockOpenFinanceAdapter never dereferences this client,
    and loading a client cert that doesn't exist on disk (the common
    case for a fresh mock-mode checkout) would otherwise crash server
    startup for a client that's never actually used.

    Returns:
        AsyncClient configured with HTTP/2 and, when applicable, mTLS.
    """
    kwargs: dict[str, Any] = {
        "timeout": settings.http_timeout_seconds,
        "http2": True,
    }
    if settings.mtls_enabled and settings.environment != "mock":
        kwargs["cert"] = (settings.mtls_cert_path, settings.mtls_key_path)
    return httpx.AsyncClient(**kwargs)


def _generated_client_httpx_args() -> dict[str, Any]:
    """httpx.AsyncClient kwargs for every generated client's own internal client.

    Each generated client (see
    ``adapters/default_adapter.py::_generated_client``) lazily builds
    and caches its own ``httpx.AsyncClient`` rather than reusing the
    single shared one this module builds via ``_build_http_client`` -
    a generated client's ``base_url`` differs per API family, which a
    single shared client (with no fixed base_url of its own) can't
    represent. This mirrors ``_build_http_client``'s mTLS/HTTP2 config
    so those internal clients present the same certificate; only
    called from ``_build_real_adapters``, itself only reached outside
    ``environment == 'mock'`` (see ``app_lifespan``), so no separate
    mock-mode guard is needed here unlike ``_build_http_client``.

    Returns:
        kwargs dict for ``adapter.configure_generated_clients(...,
        httpx_args=...)``.
    """
    kwargs: dict[str, Any] = {"http2": True}
    if settings.mtls_enabled:
        kwargs["cert"] = (settings.mtls_cert_path, settings.mtls_key_path)
    return kwargs


def _build_shared_store() -> KeyValueStore:
    """Builds the store shared by TokenStore and ConsentManager.

    Returns:
        A RedisStore when settings.redis_url is configured (shared
        across Kubernetes replicas), otherwise an InMemoryStore
        (single-process only - correct for mock mode and local dev).
    """
    if settings.redis_url is not None:
        log.info("shared_store_backend", backend="redis")
        return RedisStore(settings.redis_url)
    log.info("shared_store_backend", backend="in-memory")
    return InMemoryStore()


async def _build_mock_adapters() -> dict[str, BankAdapter]:
    """Builds in-memory mock adapters for every known bank.

    Returns:
        Dictionary of MockOpenFinanceAdapter instances, keyed by bank_id.
    """
    return {bank_id: MockOpenFinanceAdapter(bank_id) for bank_id in _ADAPTER_CLASSES}


# Every Open Finance Brasil API family this project's adapters call,
# beyond 'accounts' (already required to build the adapter itself -
# see _build_real_adapters). Each can be published at a different base
# URL/version/authorization server by the Directory of Participants;
# resolving only 'accounts' and reusing that URL for all of them
# (the pre-P1.2 behavior) silently assumed they matched, which isn't
# guaranteed. See adapters/default_adapter.py::set_endpoints. Maps each
# Directory ApiFamilyType (hyphenated, as published) to the matching
# BankEndpoints field name (underscored) - 'consents', 'funds',
# 'variable-incomes', and 'treasure-titles' were added in P1.2's
# review pass; only 'credit-cards-accounts'/'payments'/
# 'bank-fixed-incomes' were resolved before it, since those were the
# only families DefaultOpenFinanceAdapter had methods for at the time.
_ADDITIONAL_API_FAMILIES = (
    "credit-cards-accounts",
    "payments",
    "consents",
    "bank-fixed-incomes",
    "funds",
    "variable-incomes",
    "treasure-titles",
)


async def _resolve_endpoints(directory: DirectoryClient, bank_id: str) -> BankEndpoints:
    """Resolves every additional API family's base URL for one bank.

    Best-effort per family: a family the Directory doesn't publish (or
    fails to resolve) for this bank is simply left unset on the
    returned catalog - DefaultOpenFinanceAdapter._url_for falls back to
    the adapter's main ('accounts') base_url for any missing family, so
    a partial result here degrades gracefully rather than failing the
    whole adapter.

    Args:
        directory: Shared DirectoryClient.
        bank_id: Identifier used by this project's adapters.

    Returns:
        BankEndpoints with whichever families resolved successfully
        set, and the rest left as ``None``.
    """
    resolved_urls: dict[str, str] = {}
    for family in _ADDITIONAL_API_FAMILIES:
        try:
            resolved: ResolvedApi = await directory.resolve(bank_id, family)
        except DirectoryError as exc:
            log.warning(
                "family_resolution_failed",
                bank_id=bank_id,
                api_family_type=family,
                error=exc.message,
                code=exc.code,
                detail=(
                    "This family falls back to the adapter's main "
                    "('accounts') base_url - see _url_for()."
                ),
            )
            continue
        resolved_urls[family.replace("-", "_")] = resolved.base_url
        log.info(
            "family_resolution_ok",
            bank_id=bank_id,
            api_family_type=family,
            base_url=resolved.base_url,
        )
    return BankEndpoints(**resolved_urls)


async def _build_real_adapters(
    token_store: TokenStore, http_client: httpx.AsyncClient, directory: DirectoryClient
) -> dict[str, BankAdapter]:
    """Builds real adapters, resolving base URLs via DirectoryClient.

    Args:
        token_store: Shared token store to inject into each adapter.
        http_client: Shared HTTP client to inject into each adapter
            (also used, unauthenticated, for directory requests).
        directory: Shared DirectoryClient - reused (not rebuilt here)
            so its participants-list cache is shared with the consent
            flow tools, which also resolve endpoints via this instance.

    Returns:
        Dictionary of real bank adapters, keyed by bank_id. Whether a
        bank whose endpoint can't be resolved is included at all
        depends on ``settings.directory_fallback_mode``:
          - 'fail_closed' (default, and the only mode config.py allows
            outside environment='mock' - see
            Settings.validate_oauth_required_outside_loopback's sibling
            check is analogous in spirit): the bank is simply left out
            of the returned dict. Tools calling an unresolved bank get
            a clear "bank not available" ValidationError (see
            tools/accounts.py) instead of silently talking to a
            possibly stale or wrong hardcoded URL.
          - 'hardcoded_fallback': falls back to that adapter's
            hardcoded default base_url/token_endpoint, logged as a
            warning - only intended for local dev against a bank whose
            sandbox Directory entry is incomplete.
    """
    adapters: dict[str, BankAdapter] = {}
    fallback_allowed = settings.directory_fallback_mode == "hardcoded_fallback"

    for bank_id, adapter_cls in _ADAPTER_CLASSES.items():
        try:
            resolved = await directory.resolve(bank_id, "accounts")
        except DirectoryError as exc:
            log.warning(
                "directory_resolution_failed",
                bank_id=bank_id,
                error=exc.message,
                code=exc.code,
                fallback_mode=settings.directory_fallback_mode,
                detail=(
                    "Falling back to this adapter's hardcoded default base_url."
                    if fallback_allowed
                    else "Bank excluded from app.adapters (fail_closed)."
                ),
            )
            if fallback_allowed:
                adapter = adapter_cls(token_store, http_client)
                adapter.set_endpoints(await _resolve_endpoints(directory, bank_id))
                adapter.configure_generated_clients(
                    timeout=httpx.Timeout(settings.http_timeout_seconds),
                    httpx_args=_generated_client_httpx_args(),
                )
                adapters[bank_id] = adapter
            continue

        log.info("directory_resolution_ok", bank_id=bank_id, base_url=resolved.base_url)

        try:
            token_endpoint = await directory.resolve_token_endpoint(bank_id)
        except DirectoryError as exc:
            log.warning(
                "token_endpoint_resolution_failed",
                bank_id=bank_id,
                error=exc.message,
                code=exc.code,
                fallback_mode=settings.directory_fallback_mode,
                detail=(
                    "Falling back to this adapter's hardcoded token_endpoint."
                    if fallback_allowed
                    else "Bank excluded from app.adapters (fail_closed)."
                ),
            )
            if fallback_allowed:
                adapter = adapter_cls(
                    token_store, http_client, base_url=resolved.base_url
                )
                adapter.set_endpoints(await _resolve_endpoints(directory, bank_id))
                adapter.configure_generated_clients(
                    timeout=httpx.Timeout(settings.http_timeout_seconds),
                    httpx_args=_generated_client_httpx_args(),
                )
                adapters[bank_id] = adapter
            continue

        log.info(
            "token_endpoint_resolution_ok",
            bank_id=bank_id,
            token_endpoint=token_endpoint,
        )
        adapter = adapter_cls(
            token_store,
            http_client,
            base_url=resolved.base_url,
            token_endpoint=token_endpoint,
        )
        endpoints = await _resolve_endpoints(directory, bank_id)
        adapter.set_endpoints(endpoints)
        adapter.configure_generated_clients(
            timeout=httpx.Timeout(settings.http_timeout_seconds),
            httpx_args=_generated_client_httpx_args(),
        )
        adapters[bank_id] = adapter

    return adapters


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Builds and tears down the application's shared dependencies.

    Args:
        server: The FastMCP server instance being started.

    Yields:
        AppContext available to every tool call for the lifetime of the
        server process.
    """
    http_client = _build_http_client()
    shared_store = _build_shared_store()
    token_store = TokenStore(store=shared_store)

    directory: DirectoryClient | None = None
    if settings.environment == "mock":
        adapters = await _build_mock_adapters()
    else:
        directory_url = (
            settings.bcb_sandbox_directory_url
            if settings.environment == "sandbox"
            else settings.bcb_directory_url
        )
        directory = DirectoryClient(http_client, base_url=str(directory_url))
        adapters = await _build_real_adapters(token_store, http_client, directory)

    categorizer = get_categorizer()
    consent_manager = ConsentManager(http_client, store=shared_store)
    authorization_sessions = AuthorizationSessionStore(store=shared_store)
    principal_bindings = PrincipalBindingStore(store=shared_store)
    payment_consent_manager = PaymentConsentManager(http_client, store=shared_store)
    idempotency_store = IdempotencyStore(store=shared_store)

    log.info(
        "app_context_ready",
        environment=settings.environment,
        banks=list(adapters),
        transport=settings.mcp_transport,
    )
    try:
        yield AppContext(
            http_client=http_client,
            token_store=token_store,
            adapters=adapters,
            categorizer=categorizer,
            consent_manager=consent_manager,
            authorization_sessions=authorization_sessions,
            principal_bindings=principal_bindings,
            payment_consent_manager=payment_consent_manager,
            idempotency_store=idempotency_store,
            directory=directory,
        )
    finally:
        for adapter in adapters.values():
            await adapter.aclose()
        await http_client.aclose()
        if isinstance(shared_store, RedisStore):
            await shared_store.aclose()
        log.info("app_context_closed")
