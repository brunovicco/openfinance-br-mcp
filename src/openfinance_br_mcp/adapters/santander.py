"""Adapter for Santander on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Banco Santander (Brasil) S.A. (ISPB: 90400888).
All request/parsing logic is inherited from DefaultOpenFinanceAdapter -
this file only supplies Santander's identity and default endpoints.

Santander's directory entry registers several AuthorisationServers
(personal, business, cards, real-estate financing, etc.) - the
personal/retail one (`santander-pf`) is used as the default here.

Example:
    >>> adapter = SantanderAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for Santander's personal/
# retail AuthorisationServer.
_SANTANDER_BASE = "https://trust-openbanking.api.santander.com.br/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from
# Santander's real OIDC discovery document.
_SANTANDER_TOKEN = "https://openbanking.api.santander.com.br/open-banking/security/v2/santander-pf/as/token.oauth2"  # noqa: E501,S105


class SantanderAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with Santander.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _SANTANDER_BASE,
        token_endpoint: str = _SANTANDER_TOKEN,
    ) -> None:
        """Initializes the Santander adapter.

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
            'santander'
        """
        return "santander"
