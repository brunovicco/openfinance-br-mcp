"""Adapter for XP on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Banco XP S.A. (ISPB: 33264668). All
request/parsing logic is inherited from DefaultOpenFinanceAdapter -
this file only supplies XP's identity and default endpoints.

XP's directory entry registers several AuthorisationServers, one per
brand/brokerage under its group (XP itself, Rico, Clear, Modal, XP
Empresas, Azimut, Monte Bravo, WHG) - the main XP retail one is used
as the default here.

Example:
    >>> adapter = XPAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for XP's main retail
# AuthorisationServer.
_XP_BASE = "https://matls-banking-openfinance.xpi.com.br/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from XP's
# real OIDC discovery document.
_XP_TOKEN = "https://matls-banking-openfinance.xpi.com.br/orgs/xp/token"  # noqa: S105


class XPAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with XP.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _XP_BASE,
        token_endpoint: str = _XP_TOKEN,
    ) -> None:
        """Initializes the XP adapter.

        Args:
            token_store: Shared token store.
            http_client: HTTP client configured with mTLS.
            base_url: API base URL. Defaults to the hardcoded constant;
                callers resolving via DirectoryClient (sandbox/production)
                should pass the live-resolved value instead.
            token_endpoint: Token endpoint URL. See base_url.
        """
        super().__init__(
            token_store, http_client, base_url=base_url, token_endpoint=token_endpoint
        )

    @property
    def bank_id(self) -> str:
        """Bank identifier.

        Returns:
            'xp'
        """
        return "xp"
