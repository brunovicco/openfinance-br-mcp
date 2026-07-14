"""Adapter for Itaú Unibanco on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Itaú Unibanco (ISPB: 60701190). All
request/parsing logic is inherited from DefaultOpenFinanceAdapter -
this file only supplies Itaú's identity and default endpoints.

Example:
    >>> adapter = ItauAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for Itaú Unibanco.
_ITAU_BASE = "https://secure.opf.api.itau/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from Itaú's
# real OIDC discovery document.
_ITAU_TOKEN = "https://oauth2.opf.itau/as/token.oauth2"  # noqa: S105


class ItauAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with Itaú Unibanco.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _ITAU_BASE,
        token_endpoint: str = _ITAU_TOKEN,
    ) -> None:
        """Initializes the Itaú adapter.

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
            'itau'
        """
        return "itau"
