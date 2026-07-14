"""Adapter for Bradesco on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Bradesco (ISPB: 60746948). All request/parsing
logic is inherited from DefaultOpenFinanceAdapter - this file only
supplies Bradesco's identity and default endpoints.

Example:
    >>> adapter = BradescoAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for Bradesco.
_BRADESCO_BASE = "https://api.bradesco.com/next/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters). Live OIDC discovery for
# Bradesco currently fails with a TLS certificate verification error
# (self-signed certificate in the chain, not trusted in this
# environment) - this value was still confirmed by re-fetching
# discovery with certificate verification disabled, so the path itself
# is real, just unconfirmed as trustworthy from this environment.
_BRADESCO_TOKEN = "https://api.bradesco.com/auth/next/open-banking/token"  # noqa: S105


class BradescoAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with Bradesco.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _BRADESCO_BASE,
        token_endpoint: str = _BRADESCO_TOKEN,
    ) -> None:
        """Initializes the Bradesco adapter.

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
            'bradesco'
        """
        return "bradesco"
