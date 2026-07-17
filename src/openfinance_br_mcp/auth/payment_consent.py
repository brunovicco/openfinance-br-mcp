"""Payment consent lifecycle for the Open Finance Brasil Payments API.

The Payments API has its own dedicated consent resource, entirely
separate from the data-sharing consent ``auth/consent.py`` manages -
initiating a PIX payment must never reuse a data-sharing consent's
access token.
The sequence is:

  1. Create a payment consent here (``PaymentConsentManager.create``),
     describing the specific payment (creditor, amount, date) the user
     will be asked to authorize - a payment consent authorizes exactly
     one payment, unlike a data consent's broader, reusable scope.
  2. Drive the user through PAR/JAR authorization exactly like the data
     consent flow (see ``auth/par.py``, ``tools/consent.py``), with
     this consent's ID embedded in the ``payments`` scope.
  3. Exchange the resulting code for a payment-consent-bound access
     token, then confirm the consent's status
     (``PaymentConsentManager.get_status``) before creating the actual
     payment.

Endpoints come from the ``payments-consents`` Directory family and the
flow requires Payments API v5. Request and response bodies use signed
JWS content. Real-bank
interoperability has not been validated (see ``VALIDATION.md``).

Example:
    >>> manager = PaymentConsentManager(http_client=client)
    >>> consent_id = await manager.create(
    ...     "nubank", "user123", bank_base_url=base_url,
    ...     payment=payment_details, access_token=token,
    ... )
"""

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

from openfinance_br_mcp.adapters.base import build_fapi_headers
from openfinance_br_mcp.auth.payment_jws import (
    sign_payment_payload,
    verify_payment_response,
)
from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.exceptions import (
    ConsentDeniedError,
    ConsentError,
    ValidationError,
)
from openfinance_br_mcp.schemas.pix import PixPaymentRequest

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:payment_consent:"


def _composite_key(bank_id: str, subject_id: str, consent_id: str) -> str:
    """Builds the cache key for one payment journey.

    Args:
        bank_id: Identifier of the bank.
        subject_id: Identifier of the user.
        consent_id: Bank-issued payment consent identifier.

    Returns:
        The composite key, e.g. 'nubank:12345678900:urn:bank:C1'.
    """
    return f"{bank_id}:{subject_id}:{consent_id}"


def payment_token_purpose(consent_id: str) -> str:
    """Returns the TokenStore namespace for one payment consent."""
    return f"payment:{consent_id}"


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _payload_hash(data: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(data).encode()).hexdigest()


def _canonical_amount(value: Decimal) -> str:
    return format(value, ".2f")


class PaymentConsentStatus(StrEnum):
    """Possible statuses of a BCB payment consent.

    Unlike the data-sharing Consents API (which has no 'CONSUMED'
    status - see auth/consent.py), the Payments API consent is single-
    use and moves to CONSUMED after the authorized payment is created.
    """

    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    AUTHORISED = "AUTHORISED"
    REJECTED = "REJECTED"
    CONSUMED = "CONSUMED"


class PaymentDetails(BaseModel):
    """Describes the single payment a payment consent authorizes.

    A payment consent is scoped to exactly one payment - amount,
    creditor, and date are part of the consent itself, not decided
    later at payment-creation time (contrast with the data consent's
    broader, reusable scopes in auth/consent.py).

    Attributes:
        amount: Payment amount in BRL. It is kept as ``Decimal`` locally
            and serialized to the API's canonical two-decimal string.
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key (DICT).
        debtor_account_id: Payer's account ID.
        description: Payment description/reason (max 140 chars).
        payment_date: Date the payment should be executed (ISO 8601
            date). Defaults to today.
    """

    amount: Decimal = Field(decimal_places=2, gt=Decimal("0"))
    creditor_key: str
    creditor_key_type: str
    debtor_account_id: str
    description: str = Field(default="", max_length=140)
    payment_date: str = Field(
        default_factory=lambda: datetime.now(UTC).date().isoformat()
    )

    def authorized_payload(self) -> dict[str, str]:
        """Returns the canonical local snapshot persisted for this consent."""
        return {
            "currency": "BRL",
            "amount": _canonical_amount(self.amount),
            "payment_date": self.payment_date,
            "local_instrument": "DICT",
            "creditor_key": self.creditor_key,
            "creditor_key_type": self.creditor_key_type,
            "debtor_account_id": self.debtor_account_id,
            "description": self.description,
        }

    def initiation_hash(self) -> str:
        """Hashes fields that must be identical at payment creation."""
        payload = self.authorized_payload()
        payload.pop("payment_date")
        return _payload_hash(payload)


def _request_initiation_hash(request: PixPaymentRequest) -> str:
    return _payload_hash(
        {
            "currency": "BRL",
            "amount": _canonical_amount(request.amount),
            "local_instrument": "DICT",
            "creditor_key": request.creditor_key,
            "creditor_key_type": request.creditor_key_type.value,
            "debtor_account_id": request.debtor_account_id,
            "description": request.description,
        }
    )


class PaymentConsentManager:
    """Manages the Payments API's dedicated consent lifecycle.

    Backed by a pluggable ``KeyValueStore`` (in-memory by default) so
    state can be shared across Kubernetes replicas - mirrors
    ConsentManager (auth/consent.py) and TokenStore (auth/token.py) for
    the same reason.

    Attributes:
        _http: HTTP client configured with mTLS.
        _store: Underlying key-value store for payment consent state.
    """

    def __init__(
        self, http_client: httpx.AsyncClient, store: KeyValueStore | None = None
    ) -> None:
        """Initializes the manager.

        Args:
            http_client: httpx client with cert/mTLS configured.
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore.
        """
        self._http = http_client
        self._store: KeyValueStore = store if store is not None else InMemoryStore()

    def _store_key(self, bank_id: str, subject_id: str, consent_id: str) -> str:
        return _KEY_PREFIX + _composite_key(bank_id, subject_id, consent_id)

    async def _get_cached(
        self, bank_id: str, subject_id: str, consent_id: str
    ) -> dict[str, Any] | None:
        """Reads one cached payment journey, if any.

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.
            consent_id: Bank-issued payment consent identifier.

        Returns:
            The cached consent data dict, or None.
        """
        raw = await self._store.get(self._store_key(bank_id, subject_id, consent_id))
        return json.loads(raw) if raw is not None else None

    async def _set_cached(
        self,
        bank_id: str,
        subject_id: str,
        consent_id: str,
        data: dict[str, Any],
    ) -> None:
        """Writes a subject's payment consent data to the store.

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.
            consent_id: Bank-issued payment consent identifier.
            data: The consent data to cache.
        """
        await self._store.set(
            self._store_key(bank_id, subject_id, consent_id), json.dumps(data)
        )

    async def create(
        self,
        bank_id: str,
        subject_id: str,
        consent_endpoint: str,
        payment: PaymentDetails,
        access_token: str,
        response_jwks: dict[str, Any],
    ) -> str:
        """Creates a payment consent resource and returns its consentId.

        Not idempotent by scope-reuse the way the data consent is
        (auth/consent.py): a payment consent authorizes one specific
        payment, so a new payment always creates a new consent rather
        than reusing a cached one, even if the previous one is still
        AWAITING_AUTHORISATION.

        Args:
            bank_id: Identifier of the bank - part of the cache key.
            subject_id: Identifier of the paying user.
            consent_endpoint: Exact collection endpoint published for
                ``payments-consents`` by the Directory.
            payment: The specific payment this consent will authorize.
            access_token: Access token used to authenticate against
                the payment consents endpoint (a client_credentials
                token, like the data consent flow).
            response_jwks: Institution JWKS used to verify the response JWS.

        Returns:
            The created consent's consentId.

        Raises:
            ConsentError: If creation fails at the bank's API.
        """
        payload = {
            "data": {
                "loggedUser": {
                    "document": {"identification": subject_id, "rel": "CPF"}
                },
                "payment": {
                    "type": "PIX",
                    "date": payment.payment_date,
                    "currency": "BRL",
                    "amount": _canonical_amount(payment.amount),
                    "details": {
                        "localInstrument": "DICT",
                        "proxy": payment.creditor_key,
                    },
                },
                "debtorAccount": {"accountId": payment.debtor_account_id},
            }
        }

        signed_payload = sign_payment_payload(payload)
        try:
            response = await self._http.post(
                consent_endpoint,
                content=signed_payload,
                headers={
                    **build_fapi_headers(access_token),
                    "Content-Type": "application/jwt",
                },
            )
            response.raise_for_status()
            data = verify_payment_response(response.text, jwks=response_jwks)
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Failed to create payment consent: HTTP {exc.response.status_code}",
                code="PAYMENT_CONSENT_CREATE_ERROR",
            ) from exc

        consent_id = str(data["data"]["consentId"])
        await self._set_cached(
            bank_id,
            subject_id,
            consent_id,
            {
                "data": data["data"],
                "authorized_payment": payment.authorized_payload(),
                "authorized_payload_hash": payment.initiation_hash(),
            },
        )

        log.info(
            "payment_consent_created",
            bank_id=bank_id,
            subject_id=subject_id,
            consent_id=consent_id,
        )
        return consent_id

    async def get_status(
        self,
        bank_id: str,
        subject_id: str,
        consent_id: str,
        consent_endpoint: str,
        access_token: str,
        response_jwks: dict[str, Any],
    ) -> PaymentConsentStatus:
        """Queries the current payment consent status at the bank.

        Args:
            bank_id: Identifier of the bank - part of the cache key.
            subject_id: Identifier of the user.
            consent_id: Exact payment journey to query.
            consent_endpoint: Exact collection endpoint published by
                the Directory.
            access_token: Access token.
            response_jwks: Institution JWKS used to verify the response JWS.

        Returns:
            Current status of the payment consent.

        Raises:
            ConsentError: If the consent doesn't exist or the query fails.
            ConsentDeniedError: If the user denied the consent.
        """
        cached = await self._get_cached(bank_id, subject_id, consent_id)
        if not cached:
            raise ConsentError(
                f"No payment consent found for subject '{subject_id}' at bank "
                f"'{bank_id}'",
                code="PAYMENT_CONSENT_NOT_FOUND",
            )

        try:
            response = await self._http.get(
                f"{consent_endpoint}/{consent_id}",
                headers=build_fapi_headers(access_token),
            )
            response.raise_for_status()
            data = verify_payment_response(response.text, jwks=response_jwks)
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Error querying payment consent: HTTP {exc.response.status_code}",
                code="PAYMENT_CONSENT_STATUS_ERROR",
            ) from exc

        status = PaymentConsentStatus(data["data"]["status"])
        key = self._store_key(bank_id, subject_id, consent_id)
        async with self._store.lock(f"{key}:lock"):
            latest = await self._get_cached(bank_id, subject_id, consent_id)
            if latest is None:
                raise ConsentError(
                    f"Payment consent '{consent_id}' disappeared while its "
                    "status was being refreshed",
                    code="PAYMENT_CONSENT_NOT_FOUND",
                )
            latest["data"]["status"] = status
            await self._set_cached(bank_id, subject_id, consent_id, latest)

        if status == PaymentConsentStatus.REJECTED:
            raise ConsentDeniedError(
                "Payment consent was denied by the user",
                code="PAYMENT_CONSENT_REJECTED",
            )

        return status

    async def reserve_payment(
        self,
        bank_id: str,
        subject_id: str,
        consent_id: str,
        request: PixPaymentRequest,
    ) -> None:
        """Atomically binds an authorised journey to one idempotency key."""
        key = self._store_key(bank_id, subject_id, consent_id)
        async with self._store.lock(f"{key}:lock"):
            cached = await self._get_cached(bank_id, subject_id, consent_id)
            if not cached:
                raise ConsentError(
                    f"No payment consent '{consent_id}' found for subject "
                    f"'{subject_id}' at bank '{bank_id}'",
                    code="PAYMENT_CONSENT_NOT_FOUND",
                )
            expected_hash = cached.get("authorized_payload_hash")
            if expected_hash != _request_initiation_hash(request):
                raise ValidationError(
                    "The PIX payment differs from the payload authorized by "
                    "this payment consent.",
                    code="PAYMENT_DIVERGES_FROM_CONSENT",
                )
            reservation = cached.get("payment_reservation")
            if reservation not in (None, request.idempotency_key):
                raise ConsentError(
                    "This payment consent is already reserved by another "
                    "payment request.",
                    code="PAYMENT_CONSENT_ALREADY_RESERVED",
                )
            status = PaymentConsentStatus(cached["data"]["status"])
            if status != PaymentConsentStatus.AUTHORISED:
                raise ConsentError(
                    f"Payment consent '{consent_id}' is '{status.value}', "
                    "not AUTHORISED.",
                    code="PAYMENT_CONSENT_NOT_AUTHORISED",
                )
            cached["payment_reservation"] = request.idempotency_key
            await self._set_cached(bank_id, subject_id, consent_id, cached)

    async def mark_consumed(
        self, bank_id: str, subject_id: str, consent_id: str
    ) -> None:
        """Marks a payment consent as consumed after its payment is created.

        A payment consent authorizes exactly one payment - once used,
        it must not be reusable for a second ``initiate_pix`` call.
        Called by the payment-initiation flow immediately after a
        successful payment creation (see tools/pix.py).

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.
            consent_id: Exact payment journey that was consumed.
        """
        key = self._store_key(bank_id, subject_id, consent_id)
        async with self._store.lock(f"{key}:lock"):
            cached = await self._get_cached(bank_id, subject_id, consent_id)
            if not cached:
                return
            cached["data"]["status"] = PaymentConsentStatus.CONSUMED
            await self._set_cached(bank_id, subject_id, consent_id, cached)
        log.info(
            "payment_consent_consumed",
            bank_id=bank_id,
            subject_id=subject_id,
            consent_id=consent_id,
        )
