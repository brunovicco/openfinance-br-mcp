"""Unit tests for the payment-journey aggregate."""

import json
from decimal import Decimal

import httpx
import pytest
import respx
from jwcrypto import jwk

from openfinance_br_mcp.auth.payment_consent import (
    PaymentConsentManager,
    PaymentConsentStatus,
    PaymentDetails,
)
from openfinance_br_mcp.auth.payment_jws import sign_payment_payload
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import (
    AuthenticationError,
    ConsentDeniedError,
    ConsentError,
    ValidationError,
)
from openfinance_br_mcp.schemas.pix import (
    PixKeyType,
    PixPaymentRequest,
)

BANK_ID = "nubank"
SUBJECT_ID = "12345678900"
ACCESS_TOKEN = "cc-token"  # noqa: S105
CONSENT_ID = "urn:bank:PC1"
CONSENTS_URL = "https://bank.example.com/open-banking/payments/v5/consents"


def _payment(*, amount: str = "150.00") -> PaymentDetails:
    return PaymentDetails(
        amount=amount,
        creditor_key="someone@example.com",
        creditor_key_type="EMAIL",
        debtor_account_id="acc-1",
        description="invoice-1",
    )


def _request(*, amount: str = "150.00", key: str = "idem-1") -> PixPaymentRequest:
    return PixPaymentRequest(
        amount=Decimal(amount),
        creditor_key="someone@example.com",
        creditor_key_type=PixKeyType.EMAIL,
        debtor_account_id="acc-1",
        description="invoice-1",
        idempotency_key=key,
        consent_id=CONSENT_ID,
    )


def _jwks(public_key_pem: str) -> dict[str, object]:
    key = jwk.JWK.from_pem(public_key_pem.encode())
    key.update(kid="test-kid")
    return {"keys": [json.loads(key.export_public())]}


def _signed_response(data: dict[str, object], *, status: int = 200) -> httpx.Response:
    return httpx.Response(status, content=sign_payment_payload(data))


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
    monkeypatch.setattr(settings, "private_key_kid", "test-kid")


async def _create(
    manager: PaymentConsentManager, response_jwks: dict[str, object]
) -> str:
    return await manager.create(
        BANK_ID,
        SUBJECT_ID,
        consent_endpoint=CONSENTS_URL,
        payment=_payment(),
        access_token=ACCESS_TOKEN,
        response_jwks=response_jwks,
    )


class TestCreate:
    @pytest.mark.asyncio
    @respx.mock
    async def test_verifies_response_and_persists_a_journey(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        route = respx.post(CONSENTS_URL).mock(
            return_value=_signed_response(
                {
                    "data": {
                        "consentId": CONSENT_ID,
                        "status": "AWAITING_AUTHORISATION",
                    }
                },
                status=201,
            )
        )
        manager = PaymentConsentManager(http_client)

        consent_id = await _create(manager, _jwks(rsa_public_key_pem))

        assert consent_id == CONSENT_ID
        assert route.calls[0].request.headers["x-fapi-interaction-id"]
        cached = await manager._get_cached(BANK_ID, SUBJECT_ID, CONSENT_ID)
        assert cached is not None
        assert cached["authorized_payment"]["amount"] == "150.00"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_response_with_wrong_signature(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(CONSENTS_URL).mock(
            return_value=_signed_response(
                {"data": {"consentId": CONSENT_ID, "status": "x"}}, status=201
            )
        )
        manager = PaymentConsentManager(http_client)
        wrong_key = jwk.JWK.generate(kty="RSA", size=2048, kid="test-kid")

        with pytest.raises(AuthenticationError, match="signature verification failed"):
            await _create(manager, {"keys": [json.loads(wrong_key.export_public())]})

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_consent_error(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        respx.post(CONSENTS_URL).mock(return_value=httpx.Response(400))
        manager = PaymentConsentManager(http_client)

        with pytest.raises(ConsentError, match="Failed to create payment consent"):
            await _create(manager, _jwks(rsa_public_key_pem))

    @pytest.mark.asyncio
    @respx.mock
    async def test_simultaneous_journeys_do_not_overwrite_each_other(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        route = respx.post(CONSENTS_URL)
        route.side_effect = [
            _signed_response(
                {"data": {"consentId": CONSENT_ID, "status": "x"}}, status=201
            ),
            _signed_response(
                {"data": {"consentId": "urn:bank:PC2", "status": "x"}},
                status=201,
            ),
        ]
        manager = PaymentConsentManager(http_client)
        response_jwks = _jwks(rsa_public_key_pem)

        first = await _create(manager, response_jwks)
        second = await _create(manager, response_jwks)

        assert await manager._get_cached(BANK_ID, SUBJECT_ID, first) is not None
        assert await manager._get_cached(BANK_ID, SUBJECT_ID, second) is not None


class TestStatusAndReservation:
    @pytest.mark.asyncio
    async def test_missing_exact_journey_is_rejected(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        manager = PaymentConsentManager(http_client)
        with pytest.raises(ConsentError, match="No payment consent found"):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                CONSENT_ID,
                consent_endpoint=CONSENTS_URL,
                access_token=ACCESS_TOKEN,
                response_jwks=_jwks(rsa_public_key_pem),
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_status_is_verified_and_rejection_is_raised(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        response_jwks = _jwks(rsa_public_key_pem)
        respx.post(CONSENTS_URL).mock(
            return_value=_signed_response(
                {"data": {"consentId": CONSENT_ID, "status": "x"}}, status=201
            )
        )
        manager = PaymentConsentManager(http_client)
        await _create(manager, response_jwks)
        respx.get(f"{CONSENTS_URL}/{CONSENT_ID}").mock(
            return_value=_signed_response(
                {"data": {"consentId": CONSENT_ID, "status": "REJECTED"}}
            )
        )

        with pytest.raises(ConsentDeniedError):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                CONSENT_ID,
                consent_endpoint=CONSENTS_URL,
                access_token=ACCESS_TOKEN,
                response_jwks=response_jwks,
            )

    @pytest.mark.asyncio
    async def test_reservation_rejects_payload_divergence(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = PaymentConsentManager(http_client)
        await manager._set_cached(
            BANK_ID,
            SUBJECT_ID,
            CONSENT_ID,
            {
                "data": {"consentId": CONSENT_ID, "status": "AUTHORISED"},
                "authorized_payment": _payment().authorized_payload(),
                "authorized_payload_hash": _payment().initiation_hash(),
            },
        )

        with pytest.raises(ValidationError, match="differs"):
            await manager.reserve_payment(
                BANK_ID, SUBJECT_ID, CONSENT_ID, _request(amount="999.00")
            )

    @pytest.mark.asyncio
    async def test_reservation_is_single_use_but_same_key_is_retryable(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = PaymentConsentManager(http_client)
        await manager._set_cached(
            BANK_ID,
            SUBJECT_ID,
            CONSENT_ID,
            {
                "data": {"consentId": CONSENT_ID, "status": "AUTHORISED"},
                "authorized_payment": _payment().authorized_payload(),
                "authorized_payload_hash": _payment().initiation_hash(),
            },
        )

        await manager.reserve_payment(BANK_ID, SUBJECT_ID, CONSENT_ID, _request())
        await manager.reserve_payment(BANK_ID, SUBJECT_ID, CONSENT_ID, _request())
        with pytest.raises(ConsentError, match="already reserved"):
            await manager.reserve_payment(
                BANK_ID, SUBJECT_ID, CONSENT_ID, _request(key="idem-2")
            )

        await manager.mark_consumed(BANK_ID, SUBJECT_ID, CONSENT_ID)
        cached = await manager._get_cached(BANK_ID, SUBJECT_ID, CONSENT_ID)
        assert cached is not None
        assert cached["data"]["status"] == PaymentConsentStatus.CONSUMED
