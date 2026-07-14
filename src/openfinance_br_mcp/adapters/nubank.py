"""Adapter for Nubank on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by Nubank (ISPB: 18236120). All request/parsing
logic is inherited from DefaultOpenFinanceAdapter, this file only
supplies Nubank's identity and default endpoints.

The base URL and token endpoint are configurable via constructor
arguments to support both sandbox and production environments (see
DirectoryClient, which resolves the live values for sandbox/production
instead of the hardcoded defaults below).

Example:
    >>> adapter = NubankAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for Nubank.
_NUBANK_BASE = "https://openbanking.api.nubank.com.br/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint()
# fails (see context.py::_build_real_adapters), this path is not
# confirmed against Nubank's real OIDC discovery document. Live
# resolution currently fails with a TLS certificate verification error
# (likely an ICP-Brasil root CA not present in the local trust store),
# not necessarily an mTLS client-auth requirement.
_NUBANK_TOKEN = "https://openbanking.api.nubank.com.br/api/pub/token"  # noqa: S105


class NubankAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with Nubank.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _NUBANK_BASE,
        token_endpoint: str = _NUBANK_TOKEN,
    ) -> None:
        """Initializes the Nubank adapter.

        Args:
            token_store: Shared token store.
            http_client: HTTP client configured with mTLS.
            base_url: API base URL. Defaults to the hardcoded constant;
                callers resolving via DirectoryClient (sandbox/production)
                should pass the live-resolved value instead.
            token_endpoint: Token endpoint URL. See base_url; this one
                remains an unconfirmed guess pending the FAPI-BR auth flow.
        """
        super().__init__(
            token_store, http_client, base_url=base_url, token_endpoint=token_endpoint
        )

    @property
    def bank_id(self) -> str:
        """Bank identifier.

        Returns:
            'nubank'
        """
        return "nubank"
