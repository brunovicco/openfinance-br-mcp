"""Payment consent lifecycle for the Open Finance Brasil Payments API.

The Payments API has its own dedicated consent resource, entirely
separate from the data-sharing consent ``auth/consent.py`` manages -
initiating a PIX payment must never reuse a data-sharing consent's
access token (the bug this module replaces; see
``IMPLEMENTATION_PLAN.md`` P2 and the security review's finding #4).
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

Endpoint paths/payload shapes below follow the Payments API v5.0.0
OpenAPI spec as best understood at implementation time - this has NOT
been validated against a live BCB sandbox (tracked as
``IMPLEMENTATION_PLAN.md`` P3). Re-verify field names/required
properties against the current spec
(github.com/OpenBanking-Brasil/openapi/swagger-apis/payments) before
relying on this against a real institution.

Example:
    >>> manager = PaymentConsentManager(http_client=client)
    >>> consent_id = await manager.create(
    ...     "nubank", "user123", bank_base_url=base_url,
    ...     payment=payment_details, access_token=token,
    ... )
"""

import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.exceptions import ConsentDeniedError, ConsentError

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:payment_consent:"


def _composite_key(bank_id: str, subject_id: str) -> str:
    """Builds the composite cache key for a subject's payment consent at a bank.

    Args:
        bank_id: Identifier of the bank.
        subject_id: Identifier of the user.

    Returns:
        The composite key, e.g. 'nubank:12345678900'.
    """
    return f"{bank_id}:{subject_id}"


class PaymentConsentStatus(StrEnum):
    """Possible statuses of a BCB payment consent.

    Unlike the data-sharing Consents API (which has no 'CONSUMED'
    status - see auth/consent.py), the Payments API consent is single-
    use and does define one: once the payment it authorized has been
    created, the consent moves to CONSUMED and cannot authorize another
    payment. Verify this against the exact spec version in use during
    P3 sandbox validation.
    """

    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
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
        amount: Payment amount in BRL, as a string per the BCB
            schema's decimal-as-string convention.
        creditor_key: PIX key of the recipient.
        creditor_key_type: Type of the recipient's key (DICT).
        debtor_account_id: Payer's account ID.
        description: Payment description/reason (max 140 chars).
        payment_date: Date the payment should be executed (ISO 8601
            date). Defaults to today.
    """

    amount: str
    creditor_key: str
    creditor_key_type: str
    debtor_account_id: str
    description: str = Field(default="", max_length=140)
    payment_date: str = Field(
        default_factory=lambda: datetime.now(UTC).date().isoformat()
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

    async def _get_cached(self, bank_id: str, subject_id: str) -> dict[str, Any] | None:
        """Reads a subject's cached payment consent data at a bank, if any.

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.

        Returns:
            The cached consent data dict, or None.
        """
        raw = await self._store.get(_KEY_PREFIX + _composite_key(bank_id, subject_id))
        return json.loads(raw) if raw is not None else None

    async def _set_cached(
        self, bank_id: str, subject_id: str, data: dict[str, Any]
    ) -> None:
        """Writes a subject's payment consent data to the store.

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.
            data: The consent data to cache.
        """
        await self._store.set(
            _KEY_PREFIX + _composite_key(bank_id, subject_id), json.dumps(data)
        )

    async def create(
        self,
        bank_id: str,
        subject_id: str,
        bank_base_url: str,
        payment: PaymentDetails,
        access_token: str,
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
            bank_base_url: Base URL of the institution's Payments API.
            payment: The specific payment this consent will authorize.
            access_token: Access token used to authenticate against
                the payment consents endpoint (a client_credentials
                token, like the data consent flow).

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
                    "amount": payment.amount,
                    "details": {
                        "localInstrument": "DICT",
                        "proxy": payment.creditor_key,
                        "creditorAccount": {"accountId": payment.debtor_account_id},
                    },
                },
            }
        }

        try:
            response = await self._http.post(
                f"{bank_base_url}/payments/v1/consents",
                json=payload,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Failed to create payment consent: HTTP {exc.response.status_code}",
                code="PAYMENT_CONSENT_CREATE_ERROR",
            ) from exc

        await self._set_cached(bank_id, subject_id, data)
        consent_id = str(data["data"]["consentId"])

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
        bank_base_url: str,
        access_token: str,
    ) -> PaymentConsentStatus:
        """Queries the current payment consent status at the bank.

        Args:
            bank_id: Identifier of the bank - part of the cache key.
            subject_id: Identifier of the user.
            bank_base_url: Base URL of the institution.
            access_token: Access token.

        Returns:
            Current status of the payment consent.

        Raises:
            ConsentError: If the consent doesn't exist or the query fails.
            ConsentDeniedError: If the user denied the consent.
        """
        cached = await self._get_cached(bank_id, subject_id)
        if not cached:
            raise ConsentError(
                f"No payment consent found for subject '{subject_id}' at bank "
                f"'{bank_id}'",
                code="PAYMENT_CONSENT_NOT_FOUND",
            )

        consent_id = cached["data"]["consentId"]
        try:
            response = await self._http.get(
                f"{bank_base_url}/payments/v1/consents/{consent_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Error querying payment consent: HTTP {exc.response.status_code}",
                code="PAYMENT_CONSENT_STATUS_ERROR",
            ) from exc

        status = PaymentConsentStatus(data["data"]["status"])
        cached["data"]["status"] = status
        await self._set_cached(bank_id, subject_id, cached)

        if status == PaymentConsentStatus.REJECTED:
            raise ConsentDeniedError(
                "Payment consent was denied by the user",
                code="PAYMENT_CONSENT_REJECTED",
            )

        return status

    async def mark_consumed(self, bank_id: str, subject_id: str) -> None:
        """Marks a payment consent as consumed after its payment is created.

        A payment consent authorizes exactly one payment - once used,
        it must not be reusable for a second ``initiate_pix`` call.
        Called by the payment-initiation flow immediately after a
        successful payment creation (see tools/pix.py).

        Args:
            bank_id: Identifier of the bank.
            subject_id: Identifier of the user.
        """
        cached = await self._get_cached(bank_id, subject_id)
        if not cached:
            return
        cached["data"]["status"] = PaymentConsentStatus.CONSUMED
        await self._set_cached(bank_id, subject_id, cached)
        log.info("payment_consent_consumed", bank_id=bank_id, subject_id=subject_id)
