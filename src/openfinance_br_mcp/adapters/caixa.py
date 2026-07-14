"""Adapter for Caixa Econômica Federal on Open Finance Brasil.

Implements the BankAdapter contract for Caixa, inheriting
DefaultOpenFinanceAdapter's parsing logic (Open/Closed Principle)
rather than a concrete bank's adapter. Caixa is self-certified at the
same API versions as Nubank and Sicoob for every family this project
uses (accounts, credit-cards-accounts, payments-pix, bank-fixed-incomes),
but that hasn't been validated against a real response body - CEF has
documented particularities in savings-account balance fields worth
revisiting once real credentials are available.

base_url/token_endpoint below are the last-resort hardcoded fallback
(see context.py::_build_real_adapters) used only if a live
DirectoryClient resolution fails; the production host values are
unverified guesses.

Example:
    >>> adapter = CaixaAdapter(token_store=store, http_client=client)
    >>> balance = await adapter.get_balance("user123", "acc_001")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

_CAIXA_BASE = "https://api.caixa.gov.br/open-banking"
_CAIXA_TOKEN = "https://api.caixa.gov.br/auth/oauth2/token"  # noqa: S105


class CaixaAdapter(DefaultOpenFinanceAdapter):
    """Adapter for Caixa Econômica Federal - inherits
    DefaultOpenFinanceAdapter's parsing logic.

    Follows the same Open Finance BCB schema. Adapts only URLs.
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _CAIXA_BASE,
        token_endpoint: str = _CAIXA_TOKEN,
    ) -> None:
        """Initializes the Caixa adapter.

        Args:
            token_store: Shared token store.
            http_client: HTTP client configured with mTLS.
            base_url: API base URL. See module docstring - unverified.
            token_endpoint: Token endpoint URL. Also unverified.
        """
        super().__init__(
            token_store, http_client, base_url=base_url, token_endpoint=token_endpoint
        )

    @property
    def bank_id(self) -> str:
        """Bank identifier.

        Returns:
            'caixa'
        """
        return "caixa"
