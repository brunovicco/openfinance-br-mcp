"""Adapter for PicPay on Open Finance Brasil.

Implements the BankAdapter contract by consuming the Open Finance
endpoints published by PicPay (ISPB: 22896431). All request/parsing
logic is inherited from DefaultOpenFinanceAdapter - this file only
supplies PicPay's identity and default endpoints.

Example:
    >>> adapter = PicPayAdapter(token_store=store, http_client=client)
    >>> accounts = await adapter.get_accounts("user123")
"""

import httpx

from openfinance_br_mcp.adapters.default_adapter import DefaultOpenFinanceAdapter
from openfinance_br_mcp.auth.token import TokenStore

# Production Directory of Participants host for PicPay.
_PICPAY_BASE = "https://resources-mtls.openbanking.picpay.com/open-banking"

# Last-resort fallback if DirectoryClient.resolve_token_endpoint() fails
# (see context.py::_build_real_adapters) - live-resolved from PicPay's
# real OIDC discovery document.
_PICPAY_TOKEN = "https://oidc-mtls.openbanking.picpay.com/token"  # noqa: S105


class PicPayAdapter(DefaultOpenFinanceAdapter):
    """Concrete adapter for Open Finance integration with PicPay.

    Uses tenacity for automatic retries on transient 5xx errors
    (inherited from DefaultOpenFinanceAdapter).
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = _PICPAY_BASE,
        token_endpoint: str = _PICPAY_TOKEN,
    ) -> None:
        """Initializes the PicPay adapter.

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
            'picpay'
        """
        return "picpay"
