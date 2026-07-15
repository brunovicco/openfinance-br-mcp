"""Default Open Finance Brasil (BCB schema) adapter.

Implements the request/parsing logic shared by every certified Open
Finance Brasil participant that follows the official BCB schema
literally (github.com/OpenBanking-Brasil/openapi). Concrete per-bank
adapters (NubankAdapter, SicoobAdapter, CaixaAdapter) subclass this
and only need to supply ``bank_id`` and their own ``base_url``/
``token_endpoint`` defaults. ``bank_id`` stays abstract here
(inherited from ``BankAdapter``): every concrete institution must
still name itself explicitly, including in error messages and parsing
defaults - never hardcode a specific bank's name in this shared class.

Example:
    >>> class MyBankAdapter(DefaultOpenFinanceAdapter):
    ...     @property
    ...     def bank_id(self) -> str:
    ...         return "my_bank"
"""

from datetime import UTC, datetime
from datetime import date as dt_date
from typing import Any

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from openfinance_br_mcp.adapters.base import BankAdapter, build_fapi_headers
from openfinance_br_mcp.auth.payment_jws import (
    decode_payment_response_unverified,
    sign_payment_payload,
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
    InvestmentList,
    InvestmentType,
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
        self._family_base_urls: dict[str, str] = {}

    def set_family_base_urls(self, family_base_urls: dict[str, str]) -> None:
        """Overrides per-API-family base URLs resolved via the Directory.

        Each Open Finance Brasil API family (accounts,
        credit-cards-accounts, payments, bank-fixed-incomes, funds,
        variable-incomes...) can be published at a different base URL,
        version, and even authorization server by the Directory of
        Participants - resolving only 'accounts' and reusing that
        single base_url for every other family (the previous behavior)
        silently assumed they all matched, which is not guaranteed.
        Set via a mutator rather than the constructor so every existing
        concrete adapter subclass (NubankAdapter, SicoobAdapter, ...)
        keeps working unchanged - see context.py::_build_real_adapters,
        which calls this after construction once each family has been
        resolved.

        Args:
            family_base_urls: Mapping of Directory ``ApiFamilyType`` to
                its resolved base URL (e.g. {'credit-cards-accounts':
                'https://.../open-banking'}). A family missing from
                this dict falls back to ``self.base_url`` (see
                ``_url_for``).
        """
        self._family_base_urls = family_base_urls

    def _url_for(self, api_family_type: str) -> str:
        """Returns the base URL to use for a given API family.

        Args:
            api_family_type: Directory ApiFamilyType (e.g. 'accounts',
                'credit-cards-accounts', 'payments',
                'bank-fixed-incomes').

        Returns:
            The family-specific base URL if one was resolved via
            ``set_family_base_urls``, otherwise ``self.base_url``
            (this adapter's default/'accounts' base URL - preserves
            prior behavior when per-family resolution isn't available,
            e.g. in mock mode or when the Directory doesn't publish
            that family for this bank).
        """
        return self._family_base_urls.get(api_family_type, self._base_url)

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
        try:
            response = await self._http.get(
                f"{self._url_for('accounts')}/accounts/v2/accounts",
                headers=build_fapi_headers(token),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BankAdapterError(
                f"{self.bank_id}: error listing accounts: {exc.response.status_code}",
                bank_id=self.bank_id,
                status_code=exc.response.status_code,
            ) from exc

        raw = response.json()
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
        try:
            response = await self._http.get(
                f"{self._url_for('accounts')}/accounts/v2/accounts/{account_id}/balances",
                headers=build_fapi_headers(token),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BankAdapterError(
                f"{self.bank_id}: error fetching balance: {exc.response.status_code}",
                bank_id=self.bank_id,
                status_code=exc.response.status_code,
            ) from exc

        raw = response.json().get("data", {})
        return AccountBalance(
            account_id=account_id,
            available_amount=raw.get("availableAmount", "0"),
            blocked_amount=raw.get("blockedAmount", "0"),
            automatically_invested_amount=raw.get("automaticallyInvestedAmount", "0"),
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
        params: dict[str, str | int] = {
            "page": filters.page,
            "page-size": filters.page_size,
        }
        if filters.date_from:
            params["fromBookingDate"] = filters.date_from.isoformat()
        if filters.date_to:
            params["toBookingDate"] = filters.date_to.isoformat()

        try:
            response = await self._http.get(
                f"{self._url_for('accounts')}/accounts/v2/accounts/"
                f"{filters.account_id}/transactions",
                headers=build_fapi_headers(token),
                params=params,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BankAdapterError(
                f"{self.bank_id}: error listing transactions: "
                f"{exc.response.status_code}",
                bank_id=self.bank_id,
                status_code=exc.response.status_code,
            ) from exc

        raw = response.json()
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

        Args:
            subject_id: User ID.

        Returns:
            List of credit card accounts.
        """
        token = await self._get_token(subject_id)
        response = await self._http.get(
            f"{self._url_for('credit-cards-accounts')}/credit-cards-accounts/v2/accounts",
            headers=build_fapi_headers(token),
        )
        response.raise_for_status()
        return [
            self._parse_credit_card(item) for item in response.json().get("data", [])
        ]

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
        response = await self._http.get(
            f"{self._url_for('credit-cards-accounts')}/credit-cards-accounts/v2/"
            f"accounts/{credit_card_account_id}/bills",
            headers=build_fapi_headers(token),
        )
        response.raise_for_status()
        return [self._parse_bill(item) for item in response.json().get("data", [])]

    async def list_pix_keys(self, subject_id: str, account_id: str) -> list[PixKey]:
        """Lists PIX keys for an account.

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

        Fetches a ``purpose='payment'`` token - never the data-sharing
        token ``get_accounts``/``list_transactions``/etc. use - since
        the Payments API requires its own dedicated consent (see
        auth/payment_consent.py, tools/payments.py). The request body
        is additionally signed as a JWS (auth/payment_jws.py) per the
        FAPI-BR message signing profile, which the Payments API
        requires on top of the bearer token and mTLS channel given its
        transactional nature; this project sends the compact JWS as
        the request body itself with ``Content-Type: application/jwt``,
        a defensible default documented in payment_jws.py's module
        docstring - some bank registrations may instead expect the
        JWS as a header alongside a plain JSON body, so confirm against
        the specific institution's OpenAPI spec before relying on this
        against a live sandbox (see IMPLEMENTATION_PLAN.md, P3). The
        response body is also a JWS (per the official spec, not plain
        JSON - a real ``response.json()`` call here would fail against
        a live bank), decoded via
        ``decode_payment_response_unverified``; verifying its signature
        against the bank's JWKS is deliberately deferred (this adapter
        has no DirectoryClient reference to fetch it) - tracked as a
        P3 follow-up.

        Args:
            subject_id: ID of the paying user.
            request: Payment data.

        Returns:
            Status of the initiated payment.

        Raises:
            BankAdapterError: On an HTTP failure.
        """
        token = await self._get_token(subject_id, purpose="payment")
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
            }
        }
        signed_payload = sign_payment_payload(payload)

        try:
            response = await self._http.post(
                f"{self._url_for('payments')}/payments/v4/pix/payments",
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

        raw = decode_payment_response_unverified(response.text).get("data", {})
        return PixPayment(
            payment_id=raw["paymentId"],
            status=PixPaymentStatus(raw.get("status", "PDNG")),
            amount=request.amount,
            end_to_end_id=raw.get("endToEndId"),
            created_at=datetime.now(UTC),
        )

    async def list_investments(self, subject_id: str) -> InvestmentList:
        """Lists fixed-income investments.

        Args:
            subject_id: User ID.

        Returns:
            List of CDBs and other fixed-income products.
        """
        token = await self._get_token(subject_id)
        response = await self._http.get(
            f"{self._url_for('bank-fixed-incomes')}/bank-fixed-incomes/v1/investments",
            headers=build_fapi_headers(token),
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        return InvestmentList(
            data=[self._parse_investment(item) for item in data],
            total_records=len(data),
        )

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
        tx_date_raw = raw.get("transactionDate", raw.get("bookingDate", ""))
        try:
            tx_date = dt_date.fromisoformat(tx_date_raw[:10])
        except ValueError:
            tx_date = dt_date.today()

        return Transaction(
            transaction_id=raw.get("transactionId", ""),
            completed_authorised_payment_type=PaymentType(
                raw.get("completedAuthorisedPaymentType", "DEBITO")
            ),
            credit_debit_type=CreditDebitType(raw.get("creditDebitType", "DEBITO")),
            transaction_name=raw.get("transactionName", ""),
            type=TransactionType(raw.get("type", "OUTROS")),
            amount=raw.get("amount", "0"),
            transaction_date=tx_date,
            counterpart_name=raw.get("counterpartName"),
        )

    def _parse_credit_card(self, raw: dict[str, Any]) -> CreditCardAccount:
        """Converts an API dict into a CreditCardAccount.

        Not a staticmethod (unlike the other parsers here): its
        fallback defaults need ``self.bank_id`` rather than a
        hardcoded institution name.

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
            bill_total_amount=raw.get("billTotalAmount", "0"),
            bill_minimum_amount=raw.get("billMinimumAmount", "0"),
        )

    def _parse_investment(self, raw: dict[str, Any]) -> BankFixedIncome:
        """Converts an API dict into a BankFixedIncome.

        Not a staticmethod, for the same reason as _parse_credit_card.

        Args:
            raw: Raw dictionary from the API.

        Returns:
            BankFixedIncome instance.
        """
        return BankFixedIncome(
            investment_id=raw.get("investmentId", ""),
            brand_name=raw.get("brandName", self.bank_id),
            investment_type=InvestmentType(raw.get("investmentType", "CDB")),
            gross_amount=raw.get("grossAmount", "0"),
            net_amount=raw.get("netAmount", "0"),
            indexer=raw.get("indexer"),
            contracted_rate=raw.get("contractedRate"),
        )
