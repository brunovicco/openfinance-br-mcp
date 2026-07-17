"""Default adapter for the Open Finance Brasil schemas.

Concrete bank adapters provide their identifier and endpoint defaults while
this class shares request and response mapping. Read APIs use the generated
clients under ``clients/`` with the adapter's mTLS-configured HTTP client.
Payment writes remain explicit because their bodies use ``application/jwt``;
``list_pix_keys`` is an adapter-specific demonstration extension.

Example:
    >>> class MyBankAdapter(DefaultOpenFinanceAdapter):
    ...     @property
    ...     def bank_id(self) -> str:
    ...         return "my_bank"
"""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from datetime import date as dt_date
from decimal import Decimal
from http import HTTPStatus
from typing import Any

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from clients.accounts_v2_4_2.api.accounts import (
    accounts_get_accounts,
    accounts_get_accounts_account_id_balances,
    accounts_get_accounts_account_id_transactions,
)
from clients.accounts_v2_4_2.client import AuthenticatedClient as AccountsAuthClient
from clients.accounts_v2_4_2.models.response_account_balances import (
    ResponseAccountBalances,
)
from clients.accounts_v2_4_2.models.response_account_list import ResponseAccountList
from clients.accounts_v2_4_2.models.response_account_transactions import (
    ResponseAccountTransactions,
)
from clients.accounts_v2_4_2.types import UNSET as ACCOUNTS_UNSET
from clients.bank_fixed_incomes_v1_1_0.api.balances import (
    bankt_fixed_incomes_get_investments_investment_id_balances as bfi_get_balances,
)
from clients.bank_fixed_incomes_v1_1_0.api.product_identification import (
    bankt_fixed_incomes_get_investments_investment_id as bfi_get_product_identification,
)
from clients.bank_fixed_incomes_v1_1_0.api.product_list import (
    bankt_fixed_incomes_get_investments as bfi_get_investments,
)
from clients.bank_fixed_incomes_v1_1_0.client import (
    AuthenticatedClient as BankFixedIncomesAuthClient,
)
from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_balances import (  # noqa: E501
    ResponseBankFixedIncomesBalances,
)
from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_product_identification import (  # noqa: E501
    ResponseBankFixedIncomesProductIdentification,
)
from clients.bank_fixed_incomes_v1_1_0.models.response_bank_fixed_incomes_product_list import (  # noqa: E501
    ResponseBankFixedIncomesProductList,
)
from clients.credit_cards_v2_3_1.api.credit_card import (
    credit_cards_get_accounts,
)
from clients.credit_cards_v2_3_1.api.credit_card import (
    credit_cards_get_accounts_credit_card_account_id_bills as cc_get_bills,
)
from clients.credit_cards_v2_3_1.api.credit_card import (
    credit_cards_get_accounts_credit_card_account_id_limits as cc_get_limits,
)
from clients.credit_cards_v2_3_1.client import (
    AuthenticatedClient as CreditCardsAuthClient,
)
from clients.credit_cards_v2_3_1.models.response_credit_card_accounts_bills import (
    ResponseCreditCardAccountsBills,
)
from clients.credit_cards_v2_3_1.models.response_credit_card_accounts_limits import (
    ResponseCreditCardAccountsLimits,
)
from clients.credit_cards_v2_3_1.models.response_credit_card_accounts_list import (
    ResponseCreditCardAccountsList,
)
from clients.funds_v1_1_0.api.balances import (
    funds_get_investments_investment_id_balances as funds_get_balances,
)
from clients.funds_v1_1_0.api.product_identification import (
    funds_get_investments_investment_id as funds_get_product_identification,
)
from clients.funds_v1_1_0.api.product_list import (
    funds_get_investments,
)
from clients.funds_v1_1_0.client import AuthenticatedClient as FundsAuthClient
from clients.funds_v1_1_0.models.response_funds_balances import ResponseFundsBalances
from clients.funds_v1_1_0.models.response_funds_product_identification import (  # noqa: E501
    ResponseFundsProductIdentification,
)
from clients.funds_v1_1_0.models.response_funds_product_list import (
    ResponseFundsProductList,
)
from clients.treasure_titles_v1_1_0.api.balances import (
    treasure_titles_get_investments_investment_id_balances as tt_get_balances,
)
from clients.treasure_titles_v1_1_0.api.product_identification import (
    treasure_titles_get_investments_investment_id as tt_get_product_identification,
)
from clients.treasure_titles_v1_1_0.api.product_list import (
    treasure_titles_get_investments,
)
from clients.treasure_titles_v1_1_0.client import (
    AuthenticatedClient as TreasureTitlesAuthClient,
)
from clients.treasure_titles_v1_1_0.models.response_treasure_titles_balances import (  # noqa: E501
    ResponseTreasureTitlesBalances,
)
from clients.treasure_titles_v1_1_0.models.response_treasure_titles_identify_product import (  # noqa: E501
    ResponseTreasureTitlesIdentifyProduct,
)
from clients.treasure_titles_v1_1_0.models.response_treasure_titles_list_product import (  # noqa: E501
    ResponseTreasureTitlesListProduct,
)
from clients.variable_incomes_v1_3_0.api.balances import (
    variable_incomes_get_investments_investment_id_balances as vi_get_balances,
)
from clients.variable_incomes_v1_3_0.api.product_identification import (
    variable_incomes_get_investments_investment_id as vi_get_product_identification,
)
from clients.variable_incomes_v1_3_0.api.product_list import (
    variable_incomes_get_investments,
)
from clients.variable_incomes_v1_3_0.client import (
    AuthenticatedClient as VariableIncomesAuthClient,
)
from clients.variable_incomes_v1_3_0.models.response_variable_incomes_balances import (  # noqa: E501
    ResponseVariableIncomesBalances,
)
from clients.variable_incomes_v1_3_0.models.response_variable_incomes_product_identification import (  # noqa: E501
    ResponseVariableIncomesProductIdentification,
)
from clients.variable_incomes_v1_3_0.models.response_variable_incomes_product_list import (  # noqa: E501
    ResponseVariableIncomesProductList,
)
from openfinance_br_mcp.adapters.base import (
    BankAdapter,
    BankEndpoints,
    build_fapi_call_kwargs,
    build_fapi_headers,
)
from openfinance_br_mcp.auth.payment_consent import payment_token_purpose
from openfinance_br_mcp.auth.payment_jws import (
    sign_payment_payload,
    verify_payment_response,
)
from openfinance_br_mcp.auth.token import TokenStore
from openfinance_br_mcp.exceptions import BankAdapterError
from openfinance_br_mcp.schemas.account import (
    Account,
    AccountBalance,
    AccountList,
    AccountSubType,
    AccountType,
)
from openfinance_br_mcp.schemas.credit_card import (
    Bill,
    CreditCardAccount,
    CreditCardNetwork,
)
from openfinance_br_mcp.schemas.investment import (
    BankFixedIncome,
    Fund,
    FundList,
    InvestmentList,
    InvestmentType,
    TreasureTitle,
    TreasureTitleList,
    VariableIncome,
    VariableIncomeList,
)
from openfinance_br_mcp.schemas.pix import (
    PixKey,
    PixKeyType,
    PixPayment,
    PixPaymentRequest,
    PixPaymentStatus,
)
from openfinance_br_mcp.schemas.transaction import (
    CreditDebitType,
    PaymentType,
    Transaction,
    TransactionFilters,
    TransactionList,
    TransactionType,
)

log = structlog.get_logger(__name__)

# Stable version path used to build each generated client's base URL from the
# family URL returned by the Directory of Participants.
_FAMILY_VERSIONS: dict[str, str] = {
    "accounts": "v2",
    "credit-cards-accounts": "v2",
    "consents": "v3",
    "bank-fixed-incomes": "v1",
    "funds": "v1",
    "variable-incomes": "v1",
    "treasure-titles": "v1",
}


class DefaultOpenFinanceAdapter(BankAdapter):
    """BCB-schema Open Finance adapter, neutral across institutions.

    ``bank_id`` remains abstract (see ``BankAdapter``) - subclasses
    must still declare it explicitly.
    """

    def __init__(
        self,
        token_store: TokenStore,
        http_client: httpx.AsyncClient,
        *,
        base_url: str,
        token_endpoint: str,
    ) -> None:
        """Initializes the adapter.

        Args:
            token_store: Shared token store.
            http_client: HTTP client configured with mTLS.
            base_url: This institution's API base URL.
            token_endpoint: This institution's /token endpoint URL.
        """
        super().__init__(token_store, http_client)
        self._base_url = base_url
        self._token_endpoint = token_endpoint
        self._endpoints = BankEndpoints()
        self._fail_closed_endpoints = False
        self._payment_jwks_resolver: Callable[[], Awaitable[dict[str, Any]]] | None = (
            None
        )
        # Lazily-built, per-family generated clients - see
        # _generated_client for why these can't just reuse self._http.
        self._generated_clients: dict[str, Any] = {}
        # Deliberately NOT derived from global `settings` here (e.g.
        # settings.mtls_enabled) - this adapter must stay constructible
        # and usable with a bare, cert-less http_client in tests (see
        # tests/unit/test_bank_adapters.py, which never calls
        # configure_generated_clients below) without ever touching a
        # real filesystem cert path. context.py::_build_real_adapters
        # calls configure_generated_clients explicitly for real,
        # non-mock adapters, passing the same mTLS config self._http
        # itself was built with (see _build_http_client).
        self._generated_client_timeout = httpx.Timeout(30.0)
        self._generated_client_httpx_args: dict[str, Any] = {"http2": True}

    def configure_generated_clients(
        self, *, timeout: httpx.Timeout, httpx_args: dict[str, Any]
    ) -> None:
        """Configures the httpx.AsyncClient each generated client lazily builds.

        See ``_generated_client`` for why generated clients can't just
        reuse ``self._http`` and instead each lazily build/cache their
        own internal ``httpx.AsyncClient``. Not set from the
        constructor (see the comment above the defaults in
        ``__init__``) so adapters stay safely constructible in tests
        without ever touching a real mTLS cert path - only
        ``context.py::_build_real_adapters`` calls this, mirroring the
        same config ``self._http`` itself was built with.

        Args:
            timeout: Request timeout for every generated client's
                internal httpx.AsyncClient.
            httpx_args: Extra ``httpx.AsyncClient`` kwargs (e.g.
                ``{'http2': True, 'cert': (cert_path, key_path)}``).

        Resets the per-family generated-client cache (see
        ``_generated_client``): any client already built from the old
        config would otherwise keep using it.
        """
        self._generated_client_timeout = timeout
        self._generated_client_httpx_args = httpx_args
        self._generated_clients.clear()

    def set_endpoints(
        self, endpoints: BankEndpoints, *, fail_closed: bool = False
    ) -> None:
        """Overrides per-API-family base URLs resolved via the Directory.

        Each Open Finance Brasil API family (accounts,
        credit-cards-accounts, payments, bank-fixed-incomes, funds,
        variable-incomes...) can be published at a different base URL,
        version, and even authorization server by the Directory of
        Participants - resolving only 'accounts' and reusing that
        single base_url for every other family (the pre-P1.2 behavior)
        silently assumed they all matched, which is not guaranteed.
        Set via a mutator rather than the constructor so every existing
        concrete adapter subclass (NubankAdapter, SicoobAdapter, ...)
        keeps working unchanged - see context.py::_build_real_adapters,
        which calls this after construction once each family has been
        resolved.

        Args:
            endpoints: Typed catalog of resolved family URLs.
            fail_closed: Reject a missing family instead of falling back
                to the adapter's default Accounts host. Enabled for every
                normal sandbox/production adapter.

        Resets the per-family generated-client cache (see
        ``_generated_client``): any client built from the old catalog
        would otherwise keep pointing at a stale base_url.
        """
        self._endpoints = endpoints
        self._fail_closed_endpoints = fail_closed
        self._generated_clients.clear()

    def configure_payment_jwks_resolver(
        self, resolver: Callable[[], Awaitable[dict[str, Any]]]
    ) -> None:
        """Injects the bank-JWKS resolver used for payment responses."""
        self._payment_jwks_resolver = resolver

    def _url_for(self, api_family_type: str) -> str:
        """Returns the base URL to use for a given API family.

        Args:
            api_family_type: Directory ApiFamilyType (e.g. 'accounts',
                'credit-cards-accounts', 'payments',
                'bank-fixed-incomes').

        Returns:
            The family-specific, versioned base URL if one was
            resolved via ``set_endpoints``, otherwise ``self.base_url``
            (this adapter's default/'accounts' base URL - preserves
            prior behavior when per-family resolution isn't available,
            e.g. in mock mode or when the Directory doesn't publish
            that family for this bank).
        """
        resolved = self._endpoints.get(api_family_type)
        if resolved is not None:
            return resolved
        if self._fail_closed_endpoints:
            raise BankAdapterError(
                f"{self.bank_id}: API family '{api_family_type}' is unavailable",
                bank_id=self.bank_id,
                code="API_FAMILY_UNAVAILABLE",
            )
        return self._base_url

    def _client_base_url(self, api_family_type: str) -> str:
        """Returns the fully-versioned base URL a generated client needs.

        A generated client's operation functions build request URLs as
        paths relative to its ``base_url`` (e.g. '/accounts',
        '/accounts/{id}/balances') - it must be constructed with the
        family + version segment already included
        ('.../open-banking/accounts/v2'), not just the bare
        '/open-banking' prefix ``_url_for`` (and the Directory itself)
        returns.

        Args:
            api_family_type: Directory ApiFamilyType - must be a key of
                ``_FAMILY_VERSIONS``.

        Returns:
            The versioned base URL for this family.
        """
        version = _FAMILY_VERSIONS[api_family_type]
        return f"{self._url_for(api_family_type)}/{api_family_type}/{version}"

    def _generated_client(self, api_family_type: str, client_cls: type[Any]) -> Any:
        """Returns the cached generated client for a family, building it
        on first use.

        A generated client's ``base_url`` differs per API family (see
        ``_client_base_url``), so it cannot simply reuse this adapter's
        single shared ``self._http`` (whose own ``base_url`` is unset/
        shared across every bank and family, which would make every
        generated operation's relative URL - e.g. '/accounts' -
        resolve to a host-less, broken request; confirmed by direct
        testing: ``client.set_async_httpx_client(self._http)`` makes
        ``get_async_httpx_client()`` return ``self._http``
        unconditionally, discarding the generated client's own
        ``base_url`` entirely). Each generated client therefore lazily
        builds and caches its *own* internal ``httpx.AsyncClient``,
        configured via ``configure_generated_clients`` (defaults to a
        plain, cert-less client - see that method's docstring for why)
        - ``timeout`` is the ``Client`` dataclass's own field (it
        forwards it to ``httpx.AsyncClient`` itself), while
        ``cert``/``http2`` go through ``httpx_args`` (passing
        ``timeout`` through both would collide: 'got multiple values
        for keyword argument timeout', confirmed by testing).

        Args:
            api_family_type: Directory ApiFamilyType - must be a key of
                ``_FAMILY_VERSIONS``, and the cache key used here.
            client_cls: The family's generated ``AuthenticatedClient``
                class (e.g. ``clients.accounts_v2_4_2.client
                .AuthenticatedClient``).

        Returns:
            A ``client_cls`` instance targeting this family's
            versioned base URL. ``token=""`` is a required-but-unused
            field on ``AuthenticatedClient`` (see
            ``build_fapi_call_kwargs``'s docstring) - this project
            always passes ``authorization`` per call instead of
            relying on the client's own token-injection.
        """
        cached = self._generated_clients.get(api_family_type)
        if cached is None:
            cached = client_cls(
                base_url=self._client_base_url(api_family_type),
                token="",
                timeout=self._generated_client_timeout,
                httpx_args=self._generated_client_httpx_args,
            )
            self._generated_clients[api_family_type] = cached
        return cached

    def _accounts_client(self) -> AccountsAuthClient:
        """Returns the cached generated Accounts API client for this bank.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.accounts_v2_4_2.api.accounts.*`` operation.
        """
        client: AccountsAuthClient = self._generated_client(
            "accounts", AccountsAuthClient
        )
        return client

    def _credit_cards_client(self) -> CreditCardsAuthClient:
        """Returns the cached generated Credit Cards Accounts API client.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.credit_cards_v2_3_1.api.credit_card.*`` operation.
        """
        client: CreditCardsAuthClient = self._generated_client(
            "credit-cards-accounts", CreditCardsAuthClient
        )
        return client

    def _bank_fixed_incomes_client(self) -> BankFixedIncomesAuthClient:
        """Returns the cached generated Bank Fixed Incomes API client.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.bank_fixed_incomes_v1_1_0.api.*`` operation.
        """
        client: BankFixedIncomesAuthClient = self._generated_client(
            "bank-fixed-incomes", BankFixedIncomesAuthClient
        )
        return client

    def _funds_client(self) -> FundsAuthClient:
        """Returns the cached generated Funds API client.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.funds_v1_1_0.api.*`` operation.
        """
        client: FundsAuthClient = self._generated_client("funds", FundsAuthClient)
        return client

    def _variable_incomes_client(self) -> VariableIncomesAuthClient:
        """Returns the cached generated Variable Incomes API client.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.variable_incomes_v1_3_0.api.*`` operation.
        """
        client: VariableIncomesAuthClient = self._generated_client(
            "variable-incomes", VariableIncomesAuthClient
        )
        return client

    def _treasure_titles_client(self) -> TreasureTitlesAuthClient:
        """Returns the cached generated Treasure Titles API client.

        Returns:
            AuthenticatedClient ready to pass to any
            ``clients.treasure_titles_v1_1_0.api.*`` operation.
        """
        client: TreasureTitlesAuthClient = self._generated_client(
            "treasure-titles", TreasureTitlesAuthClient
        )
        return client

    async def aclose(self) -> None:
        """Closes every lazily-built per-family generated-client httpx.AsyncClient.

        Called during server shutdown (see
        ``context.py::app_lifespan``) - each cached generated client
        (see ``_generated_client``) owns its own internal
        ``httpx.AsyncClient``, separate from ``self._http`` (which the
        caller closes itself), and those need their own explicit close
        to avoid leaking connections.
        """
        for client in self._generated_clients.values():
            await client.get_async_httpx_client().aclose()
        self._generated_clients.clear()

    def _require(self, response: Any, expected_type: type, action: str) -> Any:
        """Unwraps a generated operation's Response, or raises.

        Every generated operation's ``asyncio_detailed`` returns a
        ``Response[SuccessModel | ResponseError]`` (or
        ``ResponseErrorMetaSingle`` for some families) - this checks
        for HTTP 200 and the expected success model in one place
        instead of repeating the same two-part check at every call
        site.

        Args:
            response: The ``Response`` returned by a generated
                operation's ``asyncio_detailed``.
            expected_type: The success model class expected on 200
                (e.g. ``ResponseAccountList``).
            action: Short description of the call, used in the error
                message (e.g. 'listing accounts').

        Returns:
            ``response.parsed``, narrowed to ``expected_type``.

        Raises:
            BankAdapterError: If the status isn't 200 or the parsed
                body isn't the expected success model.
        """
        status_code = int(response.status_code)
        if status_code != HTTPStatus.OK or not isinstance(
            response.parsed, expected_type
        ):
            raise BankAdapterError(
                f"{self.bank_id}: error {action}: {status_code}",
                bank_id=self.bank_id,
                status_code=status_code,
            )
        return response.parsed

    @staticmethod
    def _extract_amount(raw: dict[str, Any], key: str, default: str = "0") -> Decimal:
        """Unwraps a required BCB monetary sub-object into a Decimal.

        Every monetary value in the real Open Finance Brasil APIs is a
        nested ``{"amount": "123.45", "currency": "BRL"}`` object, not
        a flat string directly on the parent object - confirmed via
        the generated models (e.g.
        ``clients/accounts_v2_4_2/models/account_balances_data.py``),
        which this file's parsing previously didn't account for (see
        this module's docstring).

        Returns a ``Decimal`` rather than the raw string (as this
        method did before pyright/Pylance was checked against this
        file): every caller immediately feeds the result into a
        Pydantic model field typed ``Decimal`` - Pydantic itself
        coerces a plain ``str`` at runtime, so mypy's Pydantic plugin
        never flagged it, but pyright has no such plugin and correctly
        treats passing a ``str`` where ``Decimal`` is declared as a
        type error. Also handles the value already being a
        ``Decimal`` (not just a nested dict or plain string): several
        call sites (``list_investments``/``list_funds``/
        ``list_variable_incomes``/``list_treasure_titles``) extract an
        amount once into a flat ``detail`` dict that gets merged back
        into ``raw`` and re-extracted a second time by the ``_parse_*``
        method - ``Decimal(str(value))`` round-trips a ``Decimal``
        input back to an equal ``Decimal`` unchanged, so the second
        extraction stays correct either way.

        Args:
            raw: The parent dict (already unwrapped via a generated
                model's ``.to_dict()``).
            key: The camelCase key holding the amount sub-object (e.g.
                'availableAmount').
            default: Returned (as a ``Decimal``) if the key is missing
                or its 'amount' sub-key is missing.

        Returns:
            The amount as a ``Decimal``, ready for a Pydantic model field.
        """
        value = raw.get(key)
        if isinstance(value, dict):
            amount = value.get("amount")
            return Decimal(str(amount)) if amount is not None else Decimal(default)
        if value is None:
            return Decimal(default)
        return Decimal(str(value))

    @staticmethod
    def _extract_optional_amount(raw: dict[str, Any], key: str) -> Decimal | None:
        """Same as ``_extract_amount``, for optional monetary fields.

        Args:
            raw: The parent dict.
            key: The camelCase key holding the amount sub-object.

        Returns:
            The amount as a ``Decimal``, or ``None`` if absent.
        """
        value = raw.get(key)
        if isinstance(value, dict):
            amount = value.get("amount")
            return Decimal(str(amount)) if amount is not None else None
        return Decimal(str(value)) if value is not None else None

    @property
    def base_url(self) -> str:
        """Base URL of this institution's Open Finance API.

        Returns:
            API base URL.
        """
        return self._base_url

    @property
    def token_endpoint(self) -> str:
        """This institution's /token endpoint.

        Returns:
            Token endpoint URL.
        """
        return self._token_endpoint

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def get_accounts(self, subject_id: str) -> AccountList:
        """Lists the user's accounts.

        Args:
            subject_id: User ID.

        Returns:
            List of checking, savings, and prepaid accounts.

        Raises:
            BankAdapterError: On a non-recoverable HTTP failure.
        """
        token = await self._get_token(subject_id)
        client = self._accounts_client()
        response = await accounts_get_accounts.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(response, ResponseAccountList, "listing accounts")

        raw = parsed.to_dict()
        accounts = [self._parse_account(item) for item in raw.get("data", [])]
        meta = raw.get("meta", {})
        return AccountList(
            data=accounts,
            total_records=meta.get("totalRecords", len(accounts)),
            total_pages=meta.get("totalPages", 1),
        )

    async def get_balance(self, subject_id: str, account_id: str) -> AccountBalance:
        """Returns the balance of an account.

        Args:
            subject_id: User ID.
            account_id: Account ID.

        Returns:
            Available and blocked balance.

        Raises:
            BankAdapterError: On an HTTP failure.
        """
        token = await self._get_token(subject_id)
        client = self._accounts_client()
        response = await accounts_get_accounts_account_id_balances.asyncio_detailed(
            account_id, client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(response, ResponseAccountBalances, "fetching balance")

        raw = parsed.to_dict().get("data", {})
        return AccountBalance(
            account_id=account_id,
            available_amount=self._extract_amount(raw, "availableAmount"),
            blocked_amount=self._extract_amount(raw, "blockedAmount"),
            automatically_invested_amount=self._extract_amount(
                raw, "automaticallyInvestedAmount"
            ),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def list_transactions(
        self,
        subject_id: str,
        filters: TransactionFilters,
    ) -> TransactionList:
        """Returns the statement of an account with filters.

        Args:
            subject_id: User ID.
            filters: Date and pagination filters.

        Returns:
            List of transactions for the requested period.

        Raises:
            BankAdapterError: On an HTTP failure.
        """
        token = await self._get_token(subject_id)
        client = self._accounts_client()
        response = await accounts_get_accounts_account_id_transactions.asyncio_detailed(
            filters.account_id,
            client=client,
            page=filters.page,
            page_size=filters.page_size,
            from_booking_date=(
                filters.date_from if filters.date_from else ACCOUNTS_UNSET
            ),
            to_booking_date=filters.date_to if filters.date_to else ACCOUNTS_UNSET,
            **build_fapi_call_kwargs(token),
        )
        parsed = self._require(
            response, ResponseAccountTransactions, "listing transactions"
        )

        raw = parsed.to_dict()
        transactions = [self._parse_transaction(item) for item in raw.get("data", [])]
        meta = raw.get("meta", {})
        return TransactionList(
            data=transactions,
            total_records=meta.get("totalRecords", len(transactions)),
            total_pages=meta.get("totalPages", 1),
        )

    async def get_credit_card_accounts(
        self, subject_id: str
    ) -> list[CreditCardAccount]:
        """Lists credit card accounts.

        Per-account available/total credit limits are fetched via a
        separate call to the '/limits' endpoint (see
        ``_fetch_credit_card_limits``) and merged in before parsing -
        the real Credit Cards Accounts spec never returns them inline
        on the account list itself (confirmed against the generated
        ``CreditCardAccountsData`` model, see this module's
        docstring), unlike this method's pre-P1.1 assumption. A
        per-card limits fetch failure is logged and simply leaves that
        card's limits unset rather than failing the whole listing.

        Args:
            subject_id: User ID.

        Returns:
            List of credit card accounts.
        """
        token = await self._get_token(subject_id)
        client = self._credit_cards_client()
        response = await credit_cards_get_accounts.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(
            response, ResponseCreditCardAccountsList, "listing credit cards"
        )
        raw_accounts: list[dict[str, Any]] = parsed.to_dict().get("data", [])

        limits_results = await asyncio.gather(
            *(
                self._fetch_credit_card_limits(
                    client, token, item["creditCardAccountId"]
                )
                for item in raw_accounts
            ),
            return_exceptions=True,
        )
        for item, limits in zip(raw_accounts, limits_results, strict=True):
            if isinstance(limits, BaseException):
                log.warning(
                    "credit_card_limits_fetch_failed",
                    bank_id=self.bank_id,
                    credit_card_account_id=item.get("creditCardAccountId"),
                    error=str(limits),
                )
                continue
            if limits is not None:
                available, total = limits
                item["availableCreditLimit"] = available
                item["totalCreditLimit"] = total

        return [self._parse_credit_card(item) for item in raw_accounts]

    async def _fetch_credit_card_limits(
        self, client: CreditCardsAuthClient, token: str, credit_card_account_id: str
    ) -> tuple[Decimal | None, Decimal | None] | None:
        """Fetches and extracts the total credit limit for one card.

        Args:
            client: Generated Credit Cards Accounts client.
            token: Access token for this call.
            credit_card_account_id: ID of the card account.

        Returns:
            ``(available_amount, total_amount)`` from the limit record
            whose ``creditLineLimitType`` is 'LIMITE_CREDITO_TOTAL' (the
            consolidated total, as opposed to a per-modality limit) -
            or ``None`` if the call fails or no such record is present
            (some institutions may only publish per-modality limits).
        """
        response = await cc_get_limits.asyncio_detailed(
            credit_card_account_id, client=client, **build_fapi_call_kwargs(token)
        )
        status_code = int(response.status_code)
        if status_code != HTTPStatus.OK or not isinstance(
            response.parsed, ResponseCreditCardAccountsLimits
        ):
            return None

        lines: list[dict[str, Any]] = response.parsed.to_dict().get("data", [])
        total_line = next(
            (
                line
                for line in lines
                if line.get("creditLineLimitType") == "LIMITE_CREDITO_TOTAL"
            ),
            None,
        )
        if total_line is None:
            return None

        return (
            self._extract_optional_amount(total_line, "availableAmount"),
            self._extract_optional_amount(total_line, "limitAmount"),
        )

    async def get_credit_card_bills(
        self, subject_id: str, credit_card_account_id: str
    ) -> list[Bill]:
        """Lists the bills of a credit card.

        Args:
            subject_id: User ID.
            credit_card_account_id: ID of the credit card account.

        Returns:
            List of open and past bills.
        """
        token = await self._get_token(subject_id)
        client = self._credit_cards_client()
        response = await cc_get_bills.asyncio_detailed(
            credit_card_account_id, client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(
            response, ResponseCreditCardAccountsBills, "listing credit card bills"
        )
        return [self._parse_bill(item) for item in parsed.to_dict().get("data", [])]

    async def list_pix_keys(self, subject_id: str, account_id: str) -> list[PixKey]:
        """Lists PIX keys for an account.

        Proprietary, non-standard extension: the official Accounts
        family spec (verified directly against
        github.com/OpenBanking-Brasil/openapi, P1.1) has no
        '/pix-keys' endpoint at all - no generated client exists for
        it, so this remains a manual call. Kept only for the mock
        environment: P0.9 already makes this raise outside
        ``environment == 'mock'``, before this method is ever reached
        against a real bank (see ``tools/pix.py``).

        Args:
            subject_id: User ID.
            account_id: Account ID.

        Returns:
            List of registered PIX keys.
        """
        token = await self._get_token(subject_id)
        response = await self._http.get(
            f"{self._url_for('accounts')}/accounts/v2/accounts/{account_id}/pix-keys",
            headers=build_fapi_headers(token),
        )
        response.raise_for_status()
        return [
            PixKey(
                key=item["key"],
                key_type=PixKeyType(item["keyType"]),
                account_id=account_id,
            )
            for item in response.json().get("data", [])
        ]

    async def initiate_pix(
        self, subject_id: str, request: PixPaymentRequest
    ) -> PixPayment:
        """Initiates a PIX payment.

        Uses the ``idempotency_key`` field as the ``X-Idempotency-Key``
        header to guarantee that retries don't result in duplicates -
        note that request-level idempotency is now primarily enforced
        one layer up, in ``tools/pix.py``, via the persistent
        ``IdempotencyStore`` (auth/idempotency_store.py); this header
        is kept as a defense-in-depth signal to the bank's own API.

        Fetches a per-consent ``purpose='payment:<consent_id>'`` token -
        never the data-sharing token ``get_accounts``/
        ``list_transactions``/etc. use - since
        the Payments API requires its own dedicated consent (see
        auth/payment_consent.py, tools/payments.py). The request body
        is additionally signed as a JWS (auth/payment_jws.py) per the
        FAPI-BR message signing profile, which the Payments API
        requires on top of the bearer token and mTLS channel given its
        transactional nature. Sent manually via ``self._http`` rather
        than a generated client: ``openapi-python-client`` cannot
        generate typed methods for ``application/jwt`` request bodies
        (see this module's docstring and ``clients/__init__.py``) -
        this project sends the compact JWS as the request body itself
        with ``Content-Type: application/jwt``, a defensible default
        documented in payment_jws.py's module docstring; some bank
        registrations may instead expect the JWS as a header alongside
        a plain JSON body, so confirm against the specific
        institution's OpenAPI spec before relying on a live environment.
        The response body is verified as a JWS against the institution
        JWKS resolved from the Directory; a missing resolver or invalid
        signature fails closed before any payment identifier is trusted.

        Args:
            subject_id: ID of the paying user.
            request: Payment data.

        Returns:
            Status of the initiated payment.

        Raises:
            BankAdapterError: On an HTTP failure.
        """
        if request.consent_id is None:
            raise BankAdapterError(
                f"{self.bank_id}: consent_id is required for a real PIX payment",
                bank_id=self.bank_id,
                code="PAYMENT_CONSENT_ID_REQUIRED",
            )
        payment_endpoint = self._endpoints.get("payments-pix")
        if payment_endpoint is None:
            raise BankAdapterError(
                f"{self.bank_id}: payments-pix endpoint is unavailable",
                bank_id=self.bank_id,
                code="API_FAMILY_UNAVAILABLE",
            )
        if self._payment_jwks_resolver is None:
            raise BankAdapterError(
                f"{self.bank_id}: payment response verifier is not configured",
                bank_id=self.bank_id,
                code="PAYMENT_RESPONSE_VERIFIER_UNAVAILABLE",
            )

        token = await self._get_token(
            subject_id, purpose=payment_token_purpose(request.consent_id)
        )
        payload = {
            "data": {
                "localInstrument": "DICT",
                "payment": {
                    "amount": str(request.amount),
                    "currency": "BRL",
                },
                "creditor": {
                    "key": request.creditor_key,
                    "keyType": request.creditor_key_type.value,
                },
                "debtorAccount": {"accountId": request.debtor_account_id},
                "remittanceInformation": request.description,
                "consentId": request.consent_id,
            }
        }
        signed_payload = sign_payment_payload(payload)

        try:
            response = await self._http.post(
                payment_endpoint,
                content=signed_payload,
                headers={
                    **build_fapi_headers(token),
                    "Content-Type": "application/jwt",
                    "X-Idempotency-Key": request.idempotency_key,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BankAdapterError(
                f"{self.bank_id}: error initiating PIX: {exc.response.status_code}",
                bank_id=self.bank_id,
                status_code=exc.response.status_code,
            ) from exc

        response_jwks = await self._payment_jwks_resolver()
        raw = verify_payment_response(response.text, jwks=response_jwks).get("data", {})
        return PixPayment(
            payment_id=raw["paymentId"],
            status=PixPaymentStatus(raw.get("status", "PDNG")),
            amount=request.amount,
            end_to_end_id=raw.get("endToEndId"),
            created_at=datetime.now(UTC),
        )

    async def list_investments(self, subject_id: str) -> InvestmentList:
        """Lists fixed-income investments.

        The product-list endpoint only identifies each investment
        (brand, type, ID) - the real spec (confirmed against the
        generated ``ResponseBankFixedIncomesProductListDataItem``
        model, see this module's docstring) never inlines balance or
        rate data there, unlike this method's pre-P1.1 assumption.
        Gross/net amounts and rate/indexer are fetched per-investment
        (balances + product-identification, concurrently) and merged
        in before parsing. An investment whose detail fetch fails is
        logged and dropped from the result rather than failing the
        whole listing.

        Args:
            subject_id: User ID.

        Returns:
            List of CDBs and other fixed-income products.
        """
        token = await self._get_token(subject_id)
        client = self._bank_fixed_incomes_client()
        response = await bfi_get_investments.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(
            response, ResponseBankFixedIncomesProductList, "listing investments"
        )
        raw_items: list[dict[str, Any]] = parsed.to_dict().get("data", [])

        details = await asyncio.gather(
            *(
                self._fetch_investment_detail(client, token, item["investmentId"])
                for item in raw_items
            ),
            return_exceptions=True,
        )
        merged: list[dict[str, Any]] = []
        for item, detail in zip(raw_items, details, strict=True):
            if isinstance(detail, BaseException):
                log.warning(
                    "investment_detail_fetch_failed",
                    bank_id=self.bank_id,
                    investment_id=item.get("investmentId"),
                    error=str(detail),
                )
                continue
            merged.append({**item, **detail})

        return InvestmentList(
            data=[self._parse_investment(item) for item in merged],
            total_records=len(merged),
        )

    async def _fetch_investment_detail(
        self, client: BankFixedIncomesAuthClient, token: str, investment_id: str
    ) -> dict[str, Any]:
        """Fetches and flattens one investment's balance + identification.

        Args:
            client: Generated Bank Fixed Incomes client.
            token: Access token for these calls.
            investment_id: ID of the investment.

        Returns:
            Flat dict with the legacy-shaped keys ``_parse_investment``
            expects ('grossAmount', 'netAmount', 'indexer',
            'contractedRate', 'issueUnitPrice', 'issueDate', 'dueDate',
            'gracePeriodDate') - whichever of the two calls succeeded;
            a failed call simply omits its keys rather than raising,
            so a bank missing one of the two still contributes partial
            data instead of dropping the investment entirely.
        """
        balances_response, identification_response = await asyncio.gather(
            bfi_get_balances.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
            bfi_get_product_identification.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
        )

        detail: dict[str, Any] = {}

        if int(balances_response.status_code) == HTTPStatus.OK and isinstance(
            balances_response.parsed, ResponseBankFixedIncomesBalances
        ):
            balances = balances_response.parsed.to_dict().get("data", {})
            detail["grossAmount"] = self._extract_amount(balances, "grossAmount")
            detail["netAmount"] = self._extract_amount(balances, "netAmount")
        else:
            log.warning(
                "investment_balances_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(balances_response.status_code),
            )

        is_ok = int(identification_response.status_code) == HTTPStatus.OK
        if is_ok and isinstance(
            identification_response.parsed,
            ResponseBankFixedIncomesProductIdentification,
        ):
            identification = identification_response.parsed.to_dict().get("data", {})
            remuneration = identification.get("remuneration", {})
            detail["indexer"] = remuneration.get("indexer")
            detail["contractedRate"] = remuneration.get(
                "preFixedRate"
            ) or remuneration.get("postFixedIndexerPercentage")
            detail["issueUnitPrice"] = self._extract_optional_amount(
                identification, "issueUnitPrice"
            )
            detail["issueDate"] = identification.get("issueDate")
            detail["dueDate"] = identification.get("dueDate")
            detail["gracePeriodDate"] = identification.get("gracePeriodDate")
        else:
            log.warning(
                "investment_identification_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(identification_response.status_code),
            )

        return detail

    async def list_funds(self, subject_id: str) -> FundList:
        """Lists investment fund positions (P1.3).

        Same two-call pattern as ``list_investments``: the product-list
        endpoint only identifies each fund (brand, CNPJ, investment ID,
        ANBIMA category) - quota quantity/price and gross/net amounts
        live on the separate ``/balances`` endpoint, and the fund's own
        name/CNPJ (distinct from the managing institution's) on
        ``/{investmentId}`` (product identification). Fetched
        concurrently per fund; a detail-fetch failure logs and drops
        that fund rather than failing the whole listing.

        Args:
            subject_id: User ID.

        Returns:
            List of investment funds.
        """
        token = await self._get_token(subject_id)
        client = self._funds_client()
        response = await funds_get_investments.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(response, ResponseFundsProductList, "listing funds")
        raw_items: list[dict[str, Any]] = parsed.to_dict().get("data", [])

        details = await asyncio.gather(
            *(
                self._fetch_fund_detail(client, token, item["investmentId"])
                for item in raw_items
            ),
            return_exceptions=True,
        )
        merged: list[dict[str, Any]] = []
        for item, detail in zip(raw_items, details, strict=True):
            if isinstance(detail, BaseException):
                log.warning(
                    "fund_detail_fetch_failed",
                    bank_id=self.bank_id,
                    investment_id=item.get("investmentId"),
                    error=str(detail),
                )
                continue
            merged.append({**item, **detail})

        return FundList(
            data=[self._parse_fund(item) for item in merged],
            total_records=len(merged),
        )

    async def _fetch_fund_detail(
        self, client: FundsAuthClient, token: str, investment_id: str
    ) -> dict[str, Any]:
        """Fetches and flattens one fund's balance + product identification.

        Args:
            client: Generated Funds client.
            token: Access token for these calls.
            investment_id: ID of the fund.

        Returns:
            Flat dict with the legacy-shaped keys ``_parse_fund``
            expects - whichever of the two calls succeeded.
        """
        balances_response, identification_response = await asyncio.gather(
            funds_get_balances.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
            funds_get_product_identification.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
        )

        detail: dict[str, Any] = {}

        if int(balances_response.status_code) == HTTPStatus.OK and isinstance(
            balances_response.parsed, ResponseFundsBalances
        ):
            balances = balances_response.parsed.to_dict().get("data", {})
            detail["referenceDate"] = balances.get("referenceDate")
            detail["quotaQuantity"] = balances.get("quotaQuantity")
            detail["quotaGrossPriceValue"] = self._extract_optional_amount(
                balances, "quotaGrossPriceValue"
            )
            detail["grossAmount"] = self._extract_amount(balances, "grossAmount")
            detail["netAmount"] = self._extract_amount(balances, "netAmount")
        else:
            log.warning(
                "fund_balances_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(balances_response.status_code),
            )

        is_ok = int(identification_response.status_code) == HTTPStatus.OK
        if is_ok and isinstance(
            identification_response.parsed, ResponseFundsProductIdentification
        ):
            identification = identification_response.parsed.to_dict().get("data", {})
            detail["fundName"] = identification.get("name")
            detail["fundCnpj"] = identification.get("cnpjNumber")
        else:
            log.warning(
                "fund_identification_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(identification_response.status_code),
            )

        return detail

    async def list_variable_incomes(self, subject_id: str) -> VariableIncomeList:
        """Lists variable income asset positions (P1.3): stocks, ETFs,
        and other exchange-traded assets.

        Same two-call pattern as ``list_investments``: the product-list
        endpoint only identifies each asset (brand, CNPJ, investment
        ID) - ISIN/ticker come from product identification, and
        quantity/closing price/gross amount from ``/balances``. Fetched
        concurrently per asset; a detail-fetch failure logs and drops
        that asset rather than failing the whole listing.

        Args:
            subject_id: User ID.

        Returns:
            List of variable income assets.
        """
        token = await self._get_token(subject_id)
        client = self._variable_incomes_client()
        response = await variable_incomes_get_investments.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(
            response, ResponseVariableIncomesProductList, "listing variable incomes"
        )
        raw_items: list[dict[str, Any]] = parsed.to_dict().get("data", [])

        details = await asyncio.gather(
            *(
                self._fetch_variable_income_detail(client, token, item["investmentId"])
                for item in raw_items
            ),
            return_exceptions=True,
        )
        merged: list[dict[str, Any]] = []
        for item, detail in zip(raw_items, details, strict=True):
            if isinstance(detail, BaseException):
                log.warning(
                    "variable_income_detail_fetch_failed",
                    bank_id=self.bank_id,
                    investment_id=item.get("investmentId"),
                    error=str(detail),
                )
                continue
            merged.append({**item, **detail})

        return VariableIncomeList(
            data=[self._parse_variable_income(item) for item in merged],
            total_records=len(merged),
        )

    async def _fetch_variable_income_detail(
        self, client: VariableIncomesAuthClient, token: str, investment_id: str
    ) -> dict[str, Any]:
        """Fetches and flattens one asset's identification + balance.

        Args:
            client: Generated Variable Incomes client.
            token: Access token for these calls.
            investment_id: ID of the asset.

        Returns:
            Flat dict with the legacy-shaped keys
            ``_parse_variable_income`` expects - whichever of the two
            calls succeeded.
        """
        identification_response, balances_response = await asyncio.gather(
            vi_get_product_identification.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
            vi_get_balances.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
        )

        detail: dict[str, Any] = {}

        is_ok = int(identification_response.status_code) == HTTPStatus.OK
        if is_ok and isinstance(
            identification_response.parsed,
            ResponseVariableIncomesProductIdentification,
        ):
            identification = identification_response.parsed.to_dict().get("data", {})
            detail["isinCode"] = identification.get("isinCode")
            detail["ticker"] = identification.get("ticker")
        else:
            log.warning(
                "variable_income_identification_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(identification_response.status_code),
            )

        if int(balances_response.status_code) == HTTPStatus.OK and isinstance(
            balances_response.parsed, ResponseVariableIncomesBalances
        ):
            balances = balances_response.parsed.to_dict().get("data", {})
            detail["referenceDate"] = balances.get("referenceDate")
            detail["quantity"] = balances.get("quantity")
            detail["closingPrice"] = self._extract_optional_amount(
                balances, "closingPrice"
            )
            detail["grossAmount"] = self._extract_amount(balances, "grossAmount")
        else:
            log.warning(
                "variable_income_balances_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(balances_response.status_code),
            )

        return detail

    async def list_treasure_titles(self, subject_id: str) -> TreasureTitleList:
        """Lists treasury bond (Tesouro Direto) positions (P1.3).

        Same two-call pattern as ``list_investments``: the product-list
        endpoint only identifies each title (brand, CNPJ, investment
        ID) - ISIN/name/dates come from product identification, and
        quantity/updated price/gross/net amount from ``/balances``.
        Fetched concurrently per title; a detail-fetch failure logs and
        drops that title rather than failing the whole listing.

        Args:
            subject_id: User ID.

        Returns:
            List of treasury bonds.
        """
        token = await self._get_token(subject_id)
        client = self._treasure_titles_client()
        response = await treasure_titles_get_investments.asyncio_detailed(
            client=client, **build_fapi_call_kwargs(token)
        )
        parsed = self._require(
            response, ResponseTreasureTitlesListProduct, "listing treasure titles"
        )
        raw_items: list[dict[str, Any]] = parsed.to_dict().get("data", [])

        details = await asyncio.gather(
            *(
                self._fetch_treasure_title_detail(client, token, item["investmentId"])
                for item in raw_items
            ),
            return_exceptions=True,
        )
        merged: list[dict[str, Any]] = []
        for item, detail in zip(raw_items, details, strict=True):
            if isinstance(detail, BaseException):
                log.warning(
                    "treasure_title_detail_fetch_failed",
                    bank_id=self.bank_id,
                    investment_id=item.get("investmentId"),
                    error=str(detail),
                )
                continue
            merged.append({**item, **detail})

        return TreasureTitleList(
            data=[self._parse_treasure_title(item) for item in merged],
            total_records=len(merged),
        )

    async def _fetch_treasure_title_detail(
        self, client: TreasureTitlesAuthClient, token: str, investment_id: str
    ) -> dict[str, Any]:
        """Fetches and flattens one title's identification + balance.

        Args:
            client: Generated Treasure Titles client.
            token: Access token for these calls.
            investment_id: ID of the title.

        Returns:
            Flat dict with the legacy-shaped keys
            ``_parse_treasure_title`` expects - whichever of the two
            calls succeeded.
        """
        identification_response, balances_response = await asyncio.gather(
            tt_get_product_identification.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
            tt_get_balances.asyncio_detailed(
                investment_id, client=client, **build_fapi_call_kwargs(token)
            ),
        )

        detail: dict[str, Any] = {}

        is_ok = int(identification_response.status_code) == HTTPStatus.OK
        if is_ok and isinstance(
            identification_response.parsed, ResponseTreasureTitlesIdentifyProduct
        ):
            identification = identification_response.parsed.to_dict().get("data", {})
            detail["isinCode"] = identification.get("isinCode")
            detail["productName"] = identification.get("productName")
            detail["dueDate"] = identification.get("dueDate")
            detail["purchaseDate"] = identification.get("purchaseDate")
        else:
            log.warning(
                "treasure_title_identification_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(identification_response.status_code),
            )

        if int(balances_response.status_code) == HTTPStatus.OK and isinstance(
            balances_response.parsed, ResponseTreasureTitlesBalances
        ):
            balances = balances_response.parsed.to_dict().get("data", {})
            detail["quantity"] = balances.get("quantity")
            detail["updatedUnitPrice"] = self._extract_optional_amount(
                balances, "updatedUnitPrice"
            )
            detail["grossAmount"] = self._extract_amount(balances, "grossAmount")
            detail["netAmount"] = self._extract_amount(balances, "netAmount")
        else:
            log.warning(
                "treasure_title_balances_fetch_failed",
                bank_id=self.bank_id,
                investment_id=investment_id,
                status_code=int(balances_response.status_code),
            )

        return detail

    # Parsing helpers (private)
    @staticmethod
    def _parse_account(raw: dict[str, Any]) -> Account:
        """Converts an API dict into an Account.

        Args:
            raw: Raw dictionary returned by the API.

        Returns:
            Validated Account instance.
        """
        return Account(
            account_id=raw["accountId"],
            branch=raw.get("branchCode", "0001"),
            number=raw["number"],
            check_digit=raw.get("checkDigit"),
            type=AccountType(raw.get("type", "CONTA_DEPOSITO_A_VISTA")),
            subtype=AccountSubType(raw.get("subtype", "INDIVIDUAL")),
            currency=raw.get("currency", "BRL"),
            compe_code=raw.get("compeCode"),
            ispb_code=raw.get("ispb"),
        )

    @staticmethod
    def _parse_transaction(raw: dict[str, Any]) -> Transaction:
        """Converts an API dict into a Transaction.

        Args:
            raw: Raw dictionary from the API.

        Returns:
            Validated Transaction instance.
        """
        # The real field is 'transactionDateTime' (a full datetime
        # string) - 'transactionDate'/'bookingDate' don't exist on the
        # real AccountTransactionsData schema at all (confirmed against
        # the generated model, see this module's docstring); kept as
        # fallbacks only in case a given bank's response also happens
        # to carry one of those non-standard keys.
        tx_date_raw = raw.get(
            "transactionDateTime",
            raw.get("transactionDate", raw.get("bookingDate", "")),
        )
        try:
            tx_date = dt_date.fromisoformat(tx_date_raw[:10])
        except ValueError:
            tx_date = dt_date.today()

        return Transaction(
            transaction_id=raw.get("transactionId", ""),
            completed_authorised_payment_type=PaymentType(
                raw.get("completedAuthorisedPaymentType", "TRANSACAO_EFETIVADA")
            ),
            credit_debit_type=CreditDebitType(raw.get("creditDebitType", "DEBITO")),
            transaction_name=raw.get("transactionName", ""),
            type=TransactionType(raw.get("type", "OUTROS")),
            amount=DefaultOpenFinanceAdapter._extract_amount(raw, "transactionAmount"),
            transaction_date=tx_date,
            counterpart_name=raw.get("counterpartName"),
        )

    def _parse_credit_card(self, raw: dict[str, Any]) -> CreditCardAccount:
        """Converts an API dict into a CreditCardAccount.

        Not a staticmethod (unlike the other parsers here): its
        fallback defaults need ``self.bank_id`` rather than a
        hardcoded institution name. ``availableCreditLimit``/
        ``totalCreditLimit`` are populated by the caller
        (``get_credit_card_accounts``) from a separate '/limits' call,
        not present on this raw dict as returned by the real accounts
        list endpoint itself.

        Args:
            raw: Raw dictionary from the API.

        Returns:
            CreditCardAccount instance.
        """
        return CreditCardAccount(
            credit_card_account_id=raw["creditCardAccountId"],
            brand_name=raw.get("brandName", self.bank_id),
            name=raw.get("name", f"{self.bank_id} card"),
            credit_card_network=CreditCardNetwork(
                raw.get("creditCardNetwork", "MASTERCARD")
            ),
            available_credit_limit=raw.get("availableCreditLimit"),
            total_credit_limit=raw.get("totalCreditLimit"),
        )

    @staticmethod
    def _parse_bill(raw: dict[str, Any]) -> Bill:
        """Converts an API dict into a Bill.

        Args:
            raw: Raw dictionary from the API.

        Returns:
            Bill instance.
        """
        return Bill(
            bill_id=raw.get("billId", ""),
            due_date=dt_date.fromisoformat(raw["dueDate"][:10]),
            bill_total_amount=DefaultOpenFinanceAdapter._extract_amount(
                raw, "billTotalAmount"
            ),
            bill_minimum_amount=DefaultOpenFinanceAdapter._extract_amount(
                raw, "billMinimumAmount"
            ),
        )

    def _parse_investment(self, raw: dict[str, Any]) -> BankFixedIncome:
        """Converts an API dict into a BankFixedIncome.

        Not a staticmethod, for the same reason as _parse_credit_card.

        Args:
            raw: Raw dictionary from the API - the merged shape built
                by ``list_investments``/``_fetch_investment_detail``.

        Returns:
            BankFixedIncome instance.
        """
        issue_date = raw.get("issueDate")
        due_date = raw.get("dueDate")
        grace_period_date = raw.get("gracePeriodDate")
        return BankFixedIncome(
            investment_id=raw.get("investmentId", ""),
            brand_name=raw.get("brandName", self.bank_id),
            investment_type=InvestmentType(raw.get("investmentType", "CDB")),
            gross_amount=self._extract_amount(raw, "grossAmount"),
            net_amount=self._extract_amount(raw, "netAmount"),
            indexer=raw.get("indexer"),
            contracted_rate=raw.get("contractedRate"),
            issue_unit_price=self._extract_optional_amount(raw, "issueUnitPrice"),
            issue_date=dt_date.fromisoformat(issue_date[:10]) if issue_date else None,
            due_date=dt_date.fromisoformat(due_date[:10]) if due_date else None,
            grace_period_date=(
                dt_date.fromisoformat(grace_period_date[:10])
                if grace_period_date
                else None
            ),
        )

    def _parse_fund(self, raw: dict[str, Any]) -> Fund:
        """Converts an API dict into a Fund.

        Args:
            raw: Raw dictionary from the API - the merged shape built
                by ``list_funds``/``_fetch_fund_detail``.

        Returns:
            Fund instance.
        """
        reference_date = raw.get("referenceDate")
        return Fund(
            investment_id=raw.get("investmentId", ""),
            brand_name=raw.get("brandName", self.bank_id),
            company_cnpj=raw.get("companyCnpj", ""),
            fund_name=raw.get("fundName"),
            fund_cnpj=raw.get("fundCnpj"),
            anbima_category=raw.get("anbimaCategory"),
            quota_quantity=Decimal(str(raw.get("quotaQuantity") or "0")),
            quota_gross_price_value=self._extract_optional_amount(
                raw, "quotaGrossPriceValue"
            )
            or Decimal("0"),
            reference_date=(
                dt_date.fromisoformat(reference_date[:10]) if reference_date else None
            ),
            gross_amount=self._extract_amount(raw, "grossAmount"),
            net_amount=self._extract_amount(raw, "netAmount"),
        )

    def _parse_variable_income(self, raw: dict[str, Any]) -> VariableIncome:
        """Converts an API dict into a VariableIncome.

        Args:
            raw: Raw dictionary from the API - the merged shape built
                by ``list_variable_incomes``/``_fetch_variable_income_detail``.

        Returns:
            VariableIncome instance.
        """
        reference_date = raw.get("referenceDate")
        return VariableIncome(
            investment_id=raw.get("investmentId", ""),
            brand_name=raw.get("brandName", self.bank_id),
            company_cnpj=raw.get("companyCnpj", ""),
            isin_code=raw.get("isinCode"),
            ticker=raw.get("ticker"),
            quantity=Decimal(str(raw.get("quantity") or "0")),
            closing_price=self._extract_optional_amount(raw, "closingPrice")
            or Decimal("0"),
            reference_date=(
                dt_date.fromisoformat(reference_date[:10]) if reference_date else None
            ),
            gross_amount=self._extract_amount(raw, "grossAmount"),
        )

    def _parse_treasure_title(self, raw: dict[str, Any]) -> TreasureTitle:
        """Converts an API dict into a TreasureTitle.

        Args:
            raw: Raw dictionary from the API - the merged shape built
                by ``list_treasure_titles``/``_fetch_treasure_title_detail``.

        Returns:
            TreasureTitle instance.
        """
        due_date = raw.get("dueDate")
        purchase_date = raw.get("purchaseDate")
        return TreasureTitle(
            investment_id=raw.get("investmentId", ""),
            brand_name=raw.get("brandName", self.bank_id),
            company_cnpj=raw.get("companyCnpj", ""),
            isin_code=raw.get("isinCode"),
            product_name=raw.get("productName"),
            due_date=dt_date.fromisoformat(due_date[:10]) if due_date else None,
            purchase_date=(
                dt_date.fromisoformat(purchase_date[:10]) if purchase_date else None
            ),
            quantity=Decimal(str(raw.get("quantity") or "0")),
            updated_unit_price=self._extract_optional_amount(raw, "updatedUnitPrice")
            or Decimal("0"),
            gross_amount=self._extract_amount(raw, "grossAmount"),
            net_amount=self._extract_amount(raw, "netAmount"),
        )
