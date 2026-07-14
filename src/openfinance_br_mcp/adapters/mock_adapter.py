"""In-memory mock adapter for local development and demos.

Returns realistic canned data without any network access, real
credentials, or mTLS certificates - the primary day-to-day dev loop,
since the official Open Finance Brasil sandbox requires institutional
registration (cadastro@openfinancebrasil.org.br) rather than being
self-service.

Selected via ``ENVIRONMENT=mock`` (the default - see config.py).

Example:
    >>> adapter = MockOpenFinanceAdapter("nubank")
    >>> accounts = await adapter.get_accounts("12345678900")
    >>> accounts.data[0].account_id
    'mock-acc-001'
"""

from datetime import UTC, date, datetime
from decimal import Decimal

import httpx

from openfinance_br_mcp.adapters.base import BankAdapter
from openfinance_br_mcp.auth.token import TokenStore
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

_MOCK_ACCOUNT_ID = "mock-acc-001"
_MOCK_CREDIT_CARD_ID = "mock-cc-001"


class MockOpenFinanceAdapter(BankAdapter):
    """Canned, in-memory implementation of the BankAdapter contract.

    Never makes a real HTTP request - ``base_url``/``token_endpoint``
    are placeholder values that should never actually be dereferenced.

    Attributes:
        _bank_id: Bank identifier this instance impersonates (e.g.
            'nubank'), used to flavor canned responses and echoed
            back so callers can't accidentally mistake mock data for
            a specific real institution's real data.
    """

    def __init__(self, bank_id: str) -> None:
        """Initializes the mock adapter.

        Args:
            bank_id: Identifier of the bank this instance impersonates.
        """
        # Neither is ever dereferenced - every public method below is
        # overridden to return canned data without touching self._http
        # or calling self._get_token(). A real (unopened) client keeps
        # the constructor's type contract honest, unlike passing None.
        super().__init__(token_store=TokenStore(), http_client=httpx.AsyncClient())
        self._bank_id = bank_id

    @property
    def bank_id(self) -> str:
        """Bank identifier this instance impersonates."""
        return self._bank_id

    @property
    def base_url(self) -> str:
        """Placeholder - never dereferenced; mock never makes HTTP calls."""
        return f"mock://{self._bank_id}"

    @property
    def token_endpoint(self) -> str:
        """Placeholder - never dereferenced; mock never makes HTTP calls."""
        return f"mock://{self._bank_id}/token"

    async def get_accounts(self, subject_id: str) -> AccountList:
        """Returns a single canned checking account.

        Args:
            subject_id: User ID (accepted but not used by the mock).

        Returns:
            A one-item AccountList.
        """
        account = Account(
            account_id=_MOCK_ACCOUNT_ID,
            branch="0001",
            number="12345-6",
            check_digit="6",
            type=AccountType.CONTA_DEPOSITO_A_VISTA,
            subtype=AccountSubType.INDIVIDUAL,
            currency="BRL",
            compe_code="000",
            ispb_code="00000000",
        )
        return AccountList(data=[account], total_records=1, total_pages=1)

    async def get_balance(self, subject_id: str, account_id: str) -> AccountBalance:
        """Returns a canned balance for any account_id.

        Args:
            subject_id: User ID (accepted but not used by the mock).
            account_id: Account ID (echoed back, not validated).

        Returns:
            A fixed AccountBalance.
        """
        return AccountBalance(
            account_id=account_id,
            available_amount=Decimal("1250.75"),
            blocked_amount=Decimal("0"),
            automatically_invested_amount=Decimal("500.00"),
        )

    async def list_transactions(
        self,
        subject_id: str,
        filters: TransactionFilters,
    ) -> TransactionList:
        """Returns two canned transactions, ignoring date/page filters.

        Args:
            subject_id: User ID (accepted but not used by the mock).
            filters: Accepted but not applied - the mock always
                returns the same fixed pair of transactions.

        Returns:
            A two-item TransactionList.
        """
        transactions = [
            Transaction(
                transaction_id="mock-tx-001",
                completed_authorised_payment_type=PaymentType.DEBITO,
                credit_debit_type=CreditDebitType.DEBITO,
                transaction_name="COMPRA IFOOD*RESTAURANTE",
                type=TransactionType.PIX,
                amount=Decimal("45.90"),
                transaction_date=date(2026, 6, 15),
            ),
            Transaction(
                transaction_id="mock-tx-002",
                completed_authorised_payment_type=PaymentType.CREDITO,
                credit_debit_type=CreditDebitType.CREDITO,
                transaction_name="TRANSFERENCIA RECEBIDA",
                type=TransactionType.PIX,
                amount=Decimal("2500.00"),
                transaction_date=date(2026, 6, 5),
            ),
        ]
        return TransactionList(data=transactions, total_records=2, total_pages=1)

    async def get_credit_card_accounts(
        self, subject_id: str
    ) -> list[CreditCardAccount]:
        """Returns a single canned credit card account.

        Args:
            subject_id: User ID (accepted but not used by the mock).

        Returns:
            A one-item list of CreditCardAccount.
        """
        return [
            CreditCardAccount(
                credit_card_account_id=_MOCK_CREDIT_CARD_ID,
                brand_name=self._bank_id,
                name=f"{self._bank_id.title()} Mastercard",
                credit_card_network=CreditCardNetwork.MASTERCARD,
                available_credit_limit=Decimal("3000.00"),
                total_credit_limit=Decimal("5000.00"),
            )
        ]

    async def get_credit_card_bills(
        self, subject_id: str, credit_card_account_id: str
    ) -> list[Bill]:
        """Returns a single canned open bill.

        Args:
            subject_id: User ID (accepted but not used by the mock).
            credit_card_account_id: Card ID (echoed back, not validated).

        Returns:
            A one-item list of Bill.
        """
        return [
            Bill(
                bill_id="mock-bill-001",
                due_date=date(2026, 7, 10),
                bill_total_amount=Decimal("1200.00"),
                bill_minimum_amount=Decimal("120.00"),
            )
        ]

    async def list_pix_keys(self, subject_id: str, account_id: str) -> list[PixKey]:
        """Returns a single canned PIX key.

        Args:
            subject_id: User ID (accepted but not used by the mock).
            account_id: Account ID (echoed back, not validated).

        Returns:
            A one-item list of PixKey.
        """
        return [
            PixKey(
                key=f"mock-user@{self._bank_id}.example",
                key_type=PixKeyType.EMAIL,
                account_id=account_id,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        ]

    async def initiate_pix(
        self, subject_id: str, request: PixPaymentRequest
    ) -> PixPayment:
        """Simulates a successful PIX payment.

        Args:
            subject_id: User ID (accepted but not used by the mock).
            request: Payment request - its idempotency_key is echoed
                into the fake payment_id so repeated calls with the
                same key are visibly traceable in demos.

        Returns:
            A PixPayment with status ACSC (completed).
        """
        return PixPayment(
            payment_id=f"mock-pay-{request.idempotency_key[:8]}",
            status=PixPaymentStatus.ACSC,
            amount=request.amount,
            end_to_end_id=f"E00000000{datetime.now(UTC):%Y%m%d%H%M%S}",
            created_at=datetime.now(UTC),
        )

    async def list_investments(self, subject_id: str) -> InvestmentList:
        """Returns a single canned CDB investment.

        Args:
            subject_id: User ID (accepted but not used by the mock).

        Returns:
            A one-item InvestmentList.
        """
        investment = BankFixedIncome(
            investment_id="mock-inv-001",
            brand_name=self._bank_id,
            investment_type=InvestmentType.CDB,
            contracted_rate=Decimal("112.00"),
            indexer="CDI",
            gross_amount=Decimal("10500.00"),
            net_amount=Decimal("9800.00"),
        )
        return InvestmentList(data=[investment], total_records=1)
