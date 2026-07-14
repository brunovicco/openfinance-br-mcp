"""Abstract interface for participating-bank adapters.

Defines the contract that every adapter must implement, following
SOLID principles:
  - Open/Closed: new banks add a subclass without changing existing code.
  - Liskov Substitution: any adapter can be used wherever BankAdapter
    is expected.
  - Interface Segregation: the interface exposes only what the tools need.

Example:
    >>> class MyBankAdapter(BankAdapter):
    ...     @property
    ...     def bank_id(self) -> str:
    ...         return "my_bank"
    ...     async def get_accounts(self, ...) -> AccountList:
    ...         ...
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any

import httpx
import structlog

from openfinance_br_mcp.auth.token import TokenStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.schemas.account import AccountBalance, AccountList
from openfinance_br_mcp.schemas.credit_card import Bill, CreditCardAccount
from openfinance_br_mcp.schemas.investment import InvestmentList
from openfinance_br_mcp.schemas.pix import PixKey, PixPayment, PixPaymentRequest
from openfinance_br_mcp.schemas.transaction import TransactionFilters, TransactionList

log = structlog.get_logger(__name__)


def build_fapi_headers(access_token: str) -> dict[str, str]:
    """Builds the header set required on every FAPI-BR protected resource call.

    The FAPI-BR security profile requires 'x-fapi-interaction-id' on
    every call to a protected resource (accounts, consents, payments,
    etc.) - the authorization server may reject requests missing it,
    and it's the correlation ID used to trace a single request across
    client and bank logs. Previously only 'Authorization' was sent.

    Args:
        access_token: Bearer token for the request.

    Returns:
        Headers dict with 'Authorization' and a freshly generated
        'x-fapi-interaction-id'.
    """
    return {
        "Authorization": f"Bearer {access_token}",
        "x-fapi-interaction-id": str(uuid.uuid4()),
    }


class BankAdapter(ABC):
    """Contract for integrating with institutions participating in
    Open Finance Brasil.

    Attributes:
        _token_store: Token store shared with the server.
        _http: HTTP client configured with mTLS for this institution.
    """

    def __init__(self, token_store: TokenStore, http_client: httpx.AsyncClient) -> None:
        """Initializes the adapter with injected dependencies.

        Args:
            token_store: Store used to obtain access tokens.
            http_client: HTTP client configured with mTLS for this institution.
        """
        self._token_store = token_store
        self._http = http_client

    @property
    @abstractmethod
    def bank_id(self) -> str:
        """Unique identifier of the bank (e.g. 'nubank', 'sicoob').

        Returns:
            snake_case string identifying the bank.
        """
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL of this institution's Open Finance APIs.

        Returns:
            Base URL without a trailing slash.
        """
        ...

    @property
    @abstractmethod
    def token_endpoint(self) -> str:
        """URL of the /token endpoint used to refresh tokens.

        Returns:
            Full URL of the token endpoint.
        """
        ...

    @abstractmethod
    async def get_accounts(self, subject_id: str) -> AccountList:
        """Lists all of the user's accounts at this institution.

        Args:
            subject_id: Identifier of the authenticated user.

        Returns:
            Paginated list of accounts.
        """
        ...

    @abstractmethod
    async def get_balance(self, subject_id: str, account_id: str) -> AccountBalance:
        """Returns the balance of a specific account.

        Args:
            subject_id: Identifier of the user.
            account_id: Account ID.

        Returns:
            Current balance of the account.
        """
        ...

    @abstractmethod
    async def list_transactions(
        self,
        subject_id: str,
        filters: TransactionFilters,
    ) -> TransactionList:
        """Returns the statement of an account with optional filters.

        Args:
            subject_id: Identifier of the user.
            filters: Date, type, and pagination filters.

        Returns:
            Paginated list of transactions.
        """
        ...

    @abstractmethod
    async def get_credit_card_accounts(
        self, subject_id: str
    ) -> list[CreditCardAccount]:
        """Lists the user's credit card accounts.

        Args:
            subject_id: Identifier of the user.

        Returns:
            List of credit card accounts.
        """
        ...

    @abstractmethod
    async def get_credit_card_bills(
        self, subject_id: str, credit_card_account_id: str
    ) -> list[Bill]:
        """Returns the bills of a credit card.

        Args:
            subject_id: Identifier of the user.
            credit_card_account_id: ID of the credit card account.

        Returns:
            List of bills.
        """
        ...

    @abstractmethod
    async def list_pix_keys(self, subject_id: str, account_id: str) -> list[PixKey]:
        """Lists PIX keys linked to an account.

        Args:
            subject_id: Identifier of the user.
            account_id: Account ID.

        Returns:
            List of registered PIX keys.
        """
        ...

    @abstractmethod
    async def initiate_pix(
        self, subject_id: str, request: PixPaymentRequest
    ) -> PixPayment:
        """Initiates a PIX payment.

        Args:
            subject_id: Identifier of the paying user.
            request: Payment data with an idempotency_key.

        Returns:
            Result of the payment initiation.
        """
        ...

    @abstractmethod
    async def list_investments(self, subject_id: str) -> InvestmentList:
        """Lists the user's fixed-income investments.

        Args:
            subject_id: Identifier of the user.

        Returns:
            List of investments.
        """
        ...

    async def _get_token(self, subject_id: str) -> str:
        """Obtains a valid access token for the subject.

        Delegates to the TokenStore, which refreshes automatically
        if needed.

        Args:
            subject_id: Identifier of the user.

        Returns:
            Access token as a string.
        """
        token = await self._token_store.get_valid_token(
            self.bank_id,
            subject_id,
            self._http,
            self.token_endpoint,
        )
        return token.access_token

    def _build_http_client(self) -> httpx.AsyncClient:
        """Builds an HTTP client configured with mTLS for this institution.

        Returns:
            AsyncClient ready to use, with timeout and mTLS configured.
        """
        kwargs: dict[str, Any] = {
            "timeout": settings.http_timeout_seconds,
            "http2": True,
        }

        if settings.mtls_enabled:
            kwargs["cert"] = (settings.mtls_cert_path, settings.mtls_key_path)

        return httpx.AsyncClient(**kwargs)
