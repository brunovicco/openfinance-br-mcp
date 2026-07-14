"""Adapter for Banco do Brasil on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Banco do Brasil (ISPB: 00000000). All
request/parsing logic is inherited from DefaultOpenFinanceAdapter -
this file only supplies Banco do Brasil's identity and default
endpoints.

Example:
    >>> adapter = BancoDoBrasilAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for Banco do Brasil.
_BANCO_DO_BRASIL_BASE = (
    "https://customerdata-mtls.of.bb.com.br/bancodobrasil/open-banking"
)

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from Banco do
# Brasil's real OIDC discovery document.
_BANCO_DO_BRASIL_TOKEN = "https://oauth-mtls.of.bb.com.br/token"  # noqa: S105


class BancoDoBrasilAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with Banco do Brasil.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _BANCO_DO_BRASIL_BASE,
        token_endpoint: str = _BANCO_DO_BRASIL_TOKEN,
    ) -> None:
        """Initializes the Banco do Brasil adapter.

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
            'banco_do_brasil'
        """
        return "banco_do_brasil"
