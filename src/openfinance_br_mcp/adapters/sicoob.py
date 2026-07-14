"""Adapter for Sicoob on Open Finance Brasil.

Implements the BankAdapter contract for the Sistema de Cooperativas
de Crédito do Brasil - Sicoob.

Sicoob follows the same Open Finance BCB schema, differing only in
base URLs and token endpoint - all parsing logic is inherited from
DefaultOpenFinanceAdapter (Open/Closed Principle) rather than a
concrete bank's adapter. Sicoob is self-certified at the same API
versions as Nubank and Caixa for every family this project uses, but
that hasn't been validated against a real response body - worth
confirming once real credentials are available.

base_url/token_endpoint below are the last-resort hardcoded fallback,
used only if a live Directory resolution fails (see
context.py::_build_real_adapters); the production host values are
unverified guesses.

Example:
    >>> adapter = SicoobAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

_SICOOB_BASE = "https://api.sicoob.com.br/open-banking"
_SICOOB_TOKEN = "https://api.sicoob.com.br/oauth2/token"  # noqa: S105


class SicoobAdapter(DefaultOpenFinanceAdapter):
    """Adapter for Sicoob - inherits DefaultOpenFinanceAdapter's parsing logic.

    Sicoob follows the same Open Finance BCB schema, differing only
    in the base URLs and the token endpoint.
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _SICOOB_BASE,
        token_endpoint: str = _SICOOB_TOKEN,
    ) -> None:
        """Initializes the Sicoob adapter.

        Args:
            token_store: Shared token store.
            http_client: HTTP client configured with mTLS.
            base_url: API base URL. See module docstring - fallback
                default, unverified for production.
            token_endpoint: Token endpoint URL. Same fallback caveat.
        """
        super().__init__(
            token_store, http_client, base_url=base_url, token_endpoint=token_endpoint
        )

    @property
    def bank_id(self) -> str:
        """Bank identifier.

        Returns:
            'sicoob'
        """
        return "sicoob"
