"""Unit tests for auth/payment_consent.py's PaymentConsentManager."""

import httpx
import pytest
import respx

from openfinance_br_mcp.auth.payment_consent import (
    PaymentConsentManager,
    PaymentConsentStatus,
    PaymentDetails,
)
from openfinance_br_mcp.auth.payment_jws import sign_payment_payload
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import ConsentDeniedError, ConsentError

BANK_ID = "nubank"
SUBJECT_ID = "12345678900"
BANK_BASE_URL = "https://bank.example.com/open-banking"
ACCESS_TOKEN = "cc-token"  # noqa: S105
CONSENTS_URL = f"{BANK_BASE_URL}/payments/v4/consents"


def _payment() -> PaymentDetails:
    return PaymentDetails(
        amount="150.00",
        creditor_key="someone@example.com",
        creditor_key_type="EMAIL",
        debtor_account_id="acc-1",
    )


def _signed_response(data: dict) -> httpx.Response:
    return httpx.Response(200, content=sign_payment_payload(data))


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)


class TestCreate:
    """Tests for PaymentConsentManager.create()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_creates_consent_and_returns_consent_id(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(
            return_value=httpx.Response(
                201,
                content=sign_payment_payload(
                    {
                        "data": {
                            "consentId": "urn:bank:PC1",
                            "status": "AWAITING_AUTHORISATION",
                        }
                    }
                ),
            )
        )
        manager = PaymentConsentManager(http_client)

        consent_id = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )

        assert consent_id == "urn:bank:PC1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_consent_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(return_value=httpx.Response(400))
        manager = PaymentConsentManager(http_client)

        with pytest.raises(ConsentError, match="Failed to create payment consent"):
            await manager.create(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                payment=_payment(),
                access_token=ACCESS_TOKEN,
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_two_payments_for_same_subject_never_reuse_a_consent(
        self, http_client: httpx.AsyncClient
    ) -> None:
        """Unlike the data-sharing consent (auth/consent.py), a payment
        consent authorizes exactly one payment - a second call must
        always create (and cache) a brand new consent, never reuse the
        first one, even for the same subject/bank."""
        route = respx.post(CONSENTS_URL)
        route.side_effect = [
            httpx.Response(
                201,
                content=sign_payment_payload(
                    {"data": {"consentId": "urn:bank:PC1", "status": "x"}}
                ),
            ),
            httpx.Response(
                201,
                content=sign_payment_payload(
                    {"data": {"consentId": "urn:bank:PC2", "status": "x"}}
                ),
            ),
        ]
        manager = PaymentConsentManager(http_client)

        first = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )
        second = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )

        assert first == "urn:bank:PC1"
        assert second == "urn:bank:PC2"


class TestGetStatus:
    """Tests for PaymentConsentManager.get_status()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_raises_when_no_consent_was_ever_created(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = PaymentConsentManager(http_client)

        with pytest.raises(ConsentError, match="No payment consent found"):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                access_token=ACCESS_TOKEN,
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_authorised_status(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(
            return_value=httpx.Response(
                201,
                content=sign_payment_payload(
                    {"data": {"consentId": "urn:bank:PC1", "status": "x"}}
                ),
            )
        )
        manager = PaymentConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )
        respx.get(f"{CONSENTS_URL}/urn:bank:PC1").mock(
            return_value=_signed_response(
                {"data": {"consentId": "urn:bank:PC1", "status": "AUTHORISED"}}
            )
        )

        status = await manager.get_status(
            BANK_ID, SUBJECT_ID, bank_base_url=BANK_BASE_URL, access_token=ACCESS_TOKEN
        )

        assert status == PaymentConsentStatus.AUTHORISED

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejected_status_raises_consent_denied_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(
            return_value=httpx.Response(
                201,
                content=sign_payment_payload(
                    {"data": {"consentId": "urn:bank:PC1", "status": "x"}}
                ),
            )
        )
        manager = PaymentConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )
        respx.get(f"{CONSENTS_URL}/urn:bank:PC1").mock(
            return_value=_signed_response(
                {"data": {"consentId": "urn:bank:PC1", "status": "REJECTED"}}
            )
        )

        with pytest.raises(ConsentDeniedError):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                access_token=ACCESS_TOKEN,
            )


class TestMarkConsumed:
    """Tests for PaymentConsentManager.mark_consumed()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_marks_a_cached_consent_as_consumed(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(
            return_value=httpx.Response(
                201,
                content=sign_payment_payload(
                    {"data": {"consentId": "urn:bank:PC1", "status": "x"}}
                ),
            )
        )
        manager = PaymentConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            payment=_payment(),
            access_token=ACCESS_TOKEN,
        )

        await manager.mark_consumed(BANK_ID, SUBJECT_ID)

        cached = await manager._get_cached(BANK_ID, SUBJECT_ID)
        assert cached is not None
        assert cached["data"]["status"] == PaymentConsentStatus.CONSUMED

    @pytest.mark.asyncio
    async def test_no_op_when_no_consent_was_ever_created(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = PaymentConsentManager(http_client)
        await manager.mark_consumed(BANK_ID, SUBJECT_ID)  # must not raise
