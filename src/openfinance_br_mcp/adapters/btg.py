"""Adapter for BTG Pactual on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Banco BTG Pactual S.A. (ISPB: 30306294). All
request/parsing logic is inherited from DefaultOpenFinanceAdapter -
this file only supplies BTG's identity and default endpoints.

BTG's directory entry registers several AuthorisationServers, one per
brand under its group (BTG+, BTG+ Business, BTG Pactual Digital,
Necton, EQI, Kinvo) - the main BTG+ personal/retail one is used as the
default here.

Example:
    >>> adapter = BTGAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for BTG's main retail
# (BTG+) AuthorisationServer.
_BTG_BASE = "https://api.mais.ob.btgpactual.com/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from BTG's
# real OIDC discovery document.
_BTG_TOKEN = "https://matls-open.btgmais.com/token"  # noqa: S105


class BTGAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with BTG Pactual.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _BTG_BASE,
        token_endpoint: str = _BTG_TOKEN,
    ) -> None:
        """Initializes the BTG adapter.

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
            'btg'
        """
        return "btg"
