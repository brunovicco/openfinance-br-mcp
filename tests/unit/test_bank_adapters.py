"""Cross-bank tests for every concrete BankAdapter.

All banks inherit their request/parsing behavior from
DefaultOpenFinanceAdapter rather than each having its own copy. These
tests run the same assertions against every adapter to prove that
shared behavior holds identically across institutions, and
specifically regression-test a bug fixed when Sicoob/Caixa were
extracted from inheriting NubankAdapter directly: error messages used
to hardcode "Nubank" even when raised from a different bank's adapter
instance.
"""

import json
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.adapters.banco_do_brasil import (
    _BANCO_DO_BRASIL_BASE,
    BancoDoBrasilAdapter,
)
from openfinance_br_mcp.adapters.bradesco import _BRADESCO_BASE, BradescoAdapter
from openfinance_br_mcp.adapters.btg import _BTG_BASE, BTGAdapter
from openfinance_br_mcp.adapters.caixa import _CAIXA_BASE, CaixaAdapter
from openfinance_br_mcp.adapters.itau import _ITAU_BASE, ItauAdapter
from openfinance_br_mcp.adapters.nubank import _NUBANK_BASE, NubankAdapter
from openfinance_br_mcp.adapters.picpay import _PICPAY_BASE, PicPayAdapter
from openfinance_br_mcp.adapters.santander import _SANTANDER_BASE, SantanderAdapter
from openfinance_br_mcp.adapters.sicoob import _SICOOB_BASE, SicoobAdapter
from openfinance_br_mcp.adapters.xp import _XP_BASE, XPAdapter
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import BankAdapterError
from openfinance_br_mcp.schemas.pix import PixKeyType, PixPaymentRequest
from openfinance_br_mcp.schemas.transaction import TransactionFilters

SUBJECT_ID = "12345678900"


@pytest.fixture(autouse=True)
def _configure_private_key(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    """initiate_pix signs its payload as a JWS (auth/payment_jws.py),
    which requires a configured signing key - every adapter test in
    this module goes through the same fixture, whether or not the
    individual test happens to call initiate_pix."""
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)

ADAPTER_CASES = [
    pytest.param(NubankAdapter, _NUBANK_BASE, "nubank", id="nubank"),
    pytest.param(SicoobAdapter, _SICOOB_BASE, "sicoob", id="sicoob"),
    pytest.param(CaixaAdapter, _CAIXA_BASE, "caixa", id="caixa"),
    pytest.param(
        BancoDoBrasilAdapter,
        _BANCO_DO_BRASIL_BASE,
        "banco_do_brasil",
        id="banco_do_brasil",
    ),
    pytest.param(BradescoAdapter, _BRADESCO_BASE, "bradesco", id="bradesco"),
    pytest.param(ItauAdapter, _ITAU_BASE, "itau", id="itau"),
    pytest.param(SantanderAdapter, _SANTANDER_BASE, "santander", id="santander"),
    pytest.param(XPAdapter, _XP_BASE, "xp", id="xp"),
    pytest.param(PicPayAdapter, _PICPAY_BASE, "picpay", id="picpay"),
    pytest.param(BTGAdapter, _BTG_BASE, "btg", id="btg"),
]


@pytest.fixture
async def token_store() -> TokenStore:
    """Preloaded with the same token under every bank_id in ADAPTER_CASES.

    A single fixture instance is reused across every parametrized bank
    in this module, and TokenStore's cache key is now composite
    (bank_id:subject_id, see auth/token.py P0.1) - saving under every
    known bank_id here means whichever adapter_cls a given test
    invocation constructs finds its token regardless of which bank it
    is.
    """
    store = TokenStore()
    for case in ADAPTER_CASES:
        bank_id = case.id
        assert bank_id is not None
        token = TokenResponse(
            {
                "access_token": "test-token",
                "expires_in": 3600,
                "_obtained_at": datetime.now(UTC),
            }
        )
        await store.save(bank_id, SUBJECT_ID, token)
        # initiate_pix fetches a purpose='payment' token (see
        # adapters/base.py._get_token), never the data-sharing one
        # above - save one here too so every parametrized bank's
        # initiate_pix test has something to find.
        await store.save(
            bank_id,
            SUBJECT_ID,
            TokenResponse(
                {
                    "access_token": "test-payment-token",
                    "expires_in": 3600,
                    "_obtained_at": datetime.now(UTC),
                }
            ),
            purpose="payment",
        )
    return store


@pytest.mark.parametrize(
    ("adapter_cls", "expected_base_url", "expected_bank_id"), ADAPTER_CASES
)
def test_bank_id_and_default_base_url(
    adapter_cls: type,
    expected_base_url: str,
    expected_bank_id: str,
    token_store: TokenStore,
) -> None:
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    assert adapter.bank_id == expected_bank_id
    assert adapter.base_url == expected_base_url


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_accounts_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "accountId": "acc-1",
                        "number": "12345-6",
                        "checkDigit": "6",
                    }
                ],
                "meta": {"totalRecords": 1, "totalPages": 1},
            },
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    result = await adapter.get_accounts(SUBJECT_ID)

    assert result.total_records == 1
    assert result.data[0].account_id == "acc-1"


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_accounts_http_error_names_the_correct_bank(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    """Regression test: before the DefaultOpenFinanceAdapter extraction,
    Sicoob/Caixa inherited NubankAdapter directly and every error
    message hardcoded 'Nubank', regardless of which bank actually
    failed."""
    respx.get(f"{base_url}/accounts/v2/accounts").mock(return_value=httpx.Response(500))
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    with pytest.raises(BankAdapterError, match=expected_bank_id) as exc_info:
        await adapter.get_accounts(SUBJECT_ID)

    assert exc_info.value.bank_id == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_balance_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts/acc-1/balances").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "availableAmount": "100.00",
                    "blockedAmount": "0.00",
                    "automaticallyInvestedAmount": "0.00",
                }
            },
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    balance = await adapter.get_balance(SUBJECT_ID, "acc-1")

    assert balance.available_amount == Decimal("100.00")


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_balance_http_error_names_the_correct_bank(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts/acc-1/balances").mock(
        return_value=httpx.Response(500)
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    with pytest.raises(BankAdapterError, match=expected_bank_id) as exc_info:
        await adapter.get_balance(SUBJECT_ID, "acc-1")

    assert exc_info.value.bank_id == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_list_transactions_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts/acc-1/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "transactionId": "tx-1",
                        "transactionName": "COMPRA",
                        "amount": "10.00",
                        "transactionDate": "2026-01-01",
                    }
                ],
                "meta": {"totalRecords": 1, "totalPages": 1},
            },
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    result = await adapter.list_transactions(
        SUBJECT_ID, TransactionFilters(account_id="acc-1")
    )

    assert result.total_records == 1
    assert result.data[0].transaction_id == "tx-1"


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_list_transactions_http_error_names_the_correct_bank(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts/acc-1/transactions").mock(
        return_value=httpx.Response(500)
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    with pytest.raises(BankAdapterError, match=expected_bank_id) as exc_info:
        await adapter.list_transactions(
            SUBJECT_ID, TransactionFilters(account_id="acc-1")
        )

    assert exc_info.value.bank_id == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_credit_card_accounts_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/credit-cards-accounts/v2/accounts").mock(
        return_value=httpx.Response(
            200, json={"data": [{"creditCardAccountId": "cc-1"}]}
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    cards = await adapter.get_credit_card_accounts(SUBJECT_ID)

    assert cards[0].credit_card_account_id == "cc-1"
    assert cards[0].brand_name == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_get_credit_card_bills_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/credit-cards-accounts/v2/accounts/cc-1/bills").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "billId": "bill-1",
                        "dueDate": "2026-02-10",
                        "billTotalAmount": "500.00",
                        "billMinimumAmount": "50.00",
                    }
                ]
            },
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    bills = await adapter.get_credit_card_bills(SUBJECT_ID, "cc-1")

    assert bills[0].bill_id == "bill-1"


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_list_pix_keys_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/accounts/v2/accounts/acc-1/pix-keys").mock(
        return_value=httpx.Response(
            200, json={"data": [{"key": "user@example.com", "keyType": "EMAIL"}]}
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    keys = await adapter.list_pix_keys(SUBJECT_ID, "acc-1")

    assert keys[0].key == "user@example.com"
    assert keys[0].account_id == "acc-1"


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_initiate_pix_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.post(f"{base_url}/payments/v4/pix/payments").mock(
        return_value=httpx.Response(
            201, json={"data": {"paymentId": "pay-1", "status": "ACSC"}}
        )
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())
    request = PixPaymentRequest(
        amount=Decimal("50.00"),
        creditor_key="recipient@example.com",
        creditor_key_type=PixKeyType.EMAIL,
        debtor_account_id="acc-1",
        idempotency_key="idem-1",
    )

    payment = await adapter.initiate_pix(SUBJECT_ID, request)

    assert payment.payment_id == "pay-1"


@pytest.mark.asyncio
@respx.mock
async def test_initiate_pix_sends_signed_jws_with_payment_purpose_token(
    token_store: TokenStore, rsa_public_key_pem: str
) -> None:
    """initiate_pix must (1) use the purpose='payment' token, never the
    data-sharing one, and (2) sign the request body as a JWS
    (auth/payment_jws.py) rather than sending plain JSON - both required
    by the FAPI-BR Payments API profile (see P2 of the implementation
    plan)."""
    route = respx.post(f"{_NUBANK_BASE}/payments/v4/pix/payments").mock(
        return_value=httpx.Response(
            201, json={"data": {"paymentId": "pay-1", "status": "ACSC"}}
        )
    )
    adapter = NubankAdapter(token_store, httpx.AsyncClient())
    request = PixPaymentRequest(
        amount=Decimal("50.00"),
        creditor_key="recipient@example.com",
        creditor_key_type=PixKeyType.EMAIL,
        debtor_account_id="acc-1",
        idempotency_key="idem-1",
    )

    await adapter.initiate_pix(SUBJECT_ID, request)

    sent = route.calls[0].request
    assert sent.headers["Authorization"] == "Bearer test-payment-token"
    assert sent.headers["Content-Type"] == "application/jwt"
    assert sent.headers["X-Idempotency-Key"] == "idem-1"

    public_key = jwk.JWK.from_pem(rsa_public_key_pem.encode())
    verified = jwcrypto_jwt.JWT(
        key=public_key, jwt=sent.content.decode(), expected_type="JWS"
    )
    claims = json.loads(verified.claims)
    assert claims["data"]["creditor"]["key"] == "recipient@example.com"


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_initiate_pix_http_error_names_the_correct_bank(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.post(f"{base_url}/payments/v4/pix/payments").mock(
        return_value=httpx.Response(500)
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())
    request = PixPaymentRequest(
        amount=Decimal("50.00"),
        creditor_key="recipient@example.com",
        creditor_key_type=PixKeyType.EMAIL,
        debtor_account_id="acc-1",
        idempotency_key="idem-1",
    )

    with pytest.raises(BankAdapterError, match=expected_bank_id) as exc_info:
        await adapter.initiate_pix(SUBJECT_ID, request)

    assert exc_info.value.bank_id == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_list_investments_parses_response(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    respx.get(f"{base_url}/bank-fixed-incomes/v1/investments").mock(
        return_value=httpx.Response(200, json={"data": [{"investmentId": "inv-1"}]})
    )
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    result = await adapter.list_investments(SUBJECT_ID)

    assert result.total_records == 1
    assert result.data[0].investment_id == "inv-1"
    assert result.data[0].brand_name == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
def test_credit_card_default_brand_name_is_bank_specific(
    adapter_cls: type, base_url: str, expected_bank_id: str, token_store: TokenStore
) -> None:
    """Regression test: the parser's fallback brand_name used to
    hardcode 'Nubank' too, even for Sicoob/Caixa cards missing a
    brandName field in the raw response."""
    adapter = adapter_cls(token_store, httpx.AsyncClient())

    card = adapter._parse_credit_card({"creditCardAccountId": "cc-1"})

    assert card.brand_name == expected_bank_id


@pytest.mark.parametrize(("adapter_cls", "base_url", "expected_bank_id"), ADAPTER_CASES)
@pytest.mark.asyncio
@respx.mock
async def test_bank_http_calls_never_use_an_mcp_client_token(
    adapter_cls: type, base_url: str, expected_bank_id: str
) -> None:
    """Structural proof that MCP client tokens (verified by
    JWTTokenVerifier, see auth/mcp_token_verifier.py) can never be
    forwarded as a bearer token to a bank's API - the MCP
    authorization spec's explicit prohibition on token passthrough.

    An adapter's only source of a bearer token is TokenStore
    (populated exclusively by the FAPI-BR consent/token-exchange flow
    in auth/token.py and auth/token_exchange.py); nothing in
    adapters/default_adapter.py has any way to read an incoming MCP
    request's Authorization header. This test seeds TokenStore with a
    distinctive FAPI-BR token and an entirely separate, never-stored
    'MCP client token' value, then confirms only the former ever
    reaches the bank."""
    fapi_br_token = "fapi-br-bank-token-abc123"  # noqa: S105
    mcp_client_token = "mcp-client-oauth-token-xyz789"  # noqa: S105

    store = TokenStore()
    await store.save(
        expected_bank_id,
        SUBJECT_ID,
        TokenResponse(
            {
                "access_token": fapi_br_token,
                "expires_in": 3600,
                "_obtained_at": datetime.now(UTC),
            }
        ),
    )
    route = respx.get(f"{base_url}/accounts/v2/accounts").mock(
        return_value=httpx.Response(200, json={"data": [], "meta": {}})
    )
    adapter = adapter_cls(store, httpx.AsyncClient())

    await adapter.get_accounts(SUBJECT_ID)

    sent_auth_header = route.calls[0].request.headers["Authorization"]
    assert sent_auth_header == f"Bearer {fapi_br_token}"
    assert mcp_client_token not in sent_auth_header
