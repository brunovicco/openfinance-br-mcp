"""Consent lifecycle management for Open Finance Brasil.

Consent is a stateful object at the BCB:
  AWAITING_AUTHORISATION → AUTHORISED/REJECTED

This module is responsible for creating, querying, and revoking
consents via POST /consents/v3/consents. Creation is idempotent by
design: multiple calls with the same parameters return the same
consent as long as it is still valid.

The returned consent_id goes into the 'consent:<id>' scope of the
PAR/JAR authorization request built by auth/par.py - this module only
manages the consent resource itself, not the authorization redirect
(see tools/consent.py for the full orchestration).

Example:
    >>> manager = ConsentManager(http_client=client)
    >>> scopes = ["accounts", "transactions"]
    >>> consent_id = await manager.create(
    ...     "user123", bank_base_url=base_url, scopes=scopes, access_token=token,
    ... )
"""

import json
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import httpx
import structlog

from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import ConsentDeniedError, ConsentError

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:consent:"

# Maps this project's simplified scope names to the real OAuth2 scope
# each API family's OpenAPI spec declares
# (github.com/OpenBanking-Brasil/openapi/swagger-apis/<family>) - the
# scope name always matches the family's path prefix (e.g. the
# 'credit-cards' family's own scope is 'credit-cards-accounts', not
# 'credit-cards').
CONSENT_SCOPE_MAP = {
    "accounts": "accounts",
    "transactions": "accounts",
    "credit_cards": "credit-cards-accounts",
    "pix": "payments",
    "investments": "bank-fixed-incomes funds variable-incomes treasure-titles",
}


class ConsentStatus(StrEnum):
    """Possible statuses of a BCB consent.

    Per the Consents API OpenAPI spec (v3.3.1,
    github.com/OpenBanking-Brasil/openapi, swagger-apis/consents) -
    note there is no 'CONSUMED' status; don't add one without checking
    the spec directly, since it's easy to assume one exists by analogy
    with other OAuth2 consent flows.
    """

    AWAITING_AUTHORISATION = "AWAITING_AUTHORISATION"
    AUTHORISED = "AUTHORISED"
    REJECTED = "REJECTED"


class ConsentManager:
    """Manages the consent lifecycle on Open Finance Brasil.

    Backed by a pluggable ``KeyValueStore`` (in-memory by default) so
    consent state can be shared across Kubernetes replicas - see
    auth/token.py's module docstring for the same rationale, which
    applies identically here.

    Attributes:
        _http: HTTP client configured with mTLS.
        _store: Underlying key-value store for consent state.
    """

    def __init__(
        self, http_client: httpx.AsyncClient, store: KeyValueStore | None = None
    ) -> None:
        """Initializes the manager.

        Args:
            http_client: httpx client with cert/mTLS configured.
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore (this project's original behavior).
        """
        self._http = http_client
        self._store: KeyValueStore = store if store is not None else InMemoryStore()

    async def _get_cached(self, subject_id: str) -> dict[str, Any] | None:
        """Reads a subject's cached consent data, if any.

        Args:
            subject_id: Identifier of the user.

        Returns:
            The cached consent data dict, or None.
        """
        raw = await self._store.get(_KEY_PREFIX + subject_id)
        return json.loads(raw) if raw is not None else None

    async def _set_cached(self, subject_id: str, data: dict[str, Any]) -> None:
        """Writes a subject's consent data to the store.

        Args:
            subject_id: Identifier of the user.
            data: The consent data to cache.
        """
        await self._store.set(_KEY_PREFIX + subject_id, json.dumps(data))

    async def create(
        self,
        subject_id: str,
        bank_base_url: str,
        scopes: list[str],
        access_token: str,
    ) -> str:
        """Creates a consent resource and returns its consentId.

        Idempotent: if an AWAITING or AUTHORISED consent already
        exists for the subject, returns its ID without creating a new
        one. The caller is responsible for driving the user through
        the actual authorization step (PAR/JAR - see auth/par.py and
        tools/consent.py), which needs this ID as part of the
        'consent:<id>' scope value.

        Args:
            subject_id: Identifier of the user.
            bank_base_url: Base URL of the institution (e.g.
                'https://api.nubank.com.br').
            scopes: List of desired scopes (e.g. ['accounts', 'transactions']).
            access_token: Access token used to authenticate against the
                consents endpoint (a client_credentials token - see
                auth/token_exchange.py).

        Returns:
            The created (or reused) consent's consentId.

        Raises:
            ConsentError: If creation fails at the bank's API.
        """
        existing = await self._get_cached(subject_id)
        if existing and existing["data"]["status"] in (
            ConsentStatus.AWAITING_AUTHORISATION,
            ConsentStatus.AUTHORISED,
        ):
            log.info("consent_reuse", subject_id=subject_id)
            return str(existing["data"]["consentId"])

        expiry = datetime.now(UTC) + timedelta(hours=settings.consent_expiry_hours)
        permissions = self._build_permissions(scopes)

        payload = {
            "data": {
                "loggedUser": {
                    "document": {"identification": subject_id, "rel": "CPF"}
                },
                "expirationDateTime": expiry.isoformat(),
                "permissions": permissions,
            }
        }

        try:
            response = await self._http.post(
                f"{bank_base_url}/consents/v3/consents",
                json=payload,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Failed to create consent: HTTP {exc.response.status_code}",
                code="CONSENT_CREATE_ERROR",
            ) from exc

        await self._set_cached(subject_id, data)
        consent_id = str(data["data"]["consentId"])

        log.info("consent_created", subject_id=subject_id, consent_id=consent_id)
        return consent_id

    async def get_status(
        self,
        subject_id: str,
        bank_base_url: str,
        access_token: str,
    ) -> ConsentStatus:
        """Queries the current consent status at the bank.

        Args:
            subject_id: Identifier of the user.
            bank_base_url: Base URL of the institution.
            access_token: Access token.

        Returns:
            Current status of the consent.

        Raises:
            ConsentError: If the consent doesn't exist or the query fails.
            ConsentDeniedError: If the user denied the consent.
        """
        cached = await self._get_cached(subject_id)
        if not cached:
            raise ConsentError(
                f"No consent found for subject '{subject_id}'",
                code="CONSENT_NOT_FOUND",
            )

        consent_id = cached["data"]["consentId"]
        try:
            response = await self._http.get(
                f"{bank_base_url}/consents/v3/consents/{consent_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ConsentError(
                f"Error querying consent: HTTP {exc.response.status_code}",
                code="CONSENT_STATUS_ERROR",
            ) from exc

        status = ConsentStatus(data["data"]["status"])
        cached["data"]["status"] = status
        await self._set_cached(subject_id, cached)

        if status == ConsentStatus.REJECTED:
            raise ConsentDeniedError(
                "Consent was denied by the user",
                code="CONSENT_REJECTED",
            )

        return status

    async def revoke(
        self,
        subject_id: str,
        bank_base_url: str,
        access_token: str,
    ) -> None:
        """Revokes a user's consent.

        Args:
            subject_id: Identifier of the user.
            bank_base_url: Base URL of the institution.
            access_token: Access token.
        """
        cached = await self._get_cached(subject_id)
        if not cached:
            return

        consent_id = cached["data"]["consentId"]
        await self._http.delete(
            f"{bank_base_url}/consents/v3/consents/{consent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        await self._store.delete(_KEY_PREFIX + subject_id)
        log.info("consent_revoked", subject_id=subject_id, consent_id=consent_id)

    @staticmethod
    def _build_permissions(scopes: list[str]) -> list[str]:
        """Builds the list of BCB permissions from simplified scopes.

        Args:
            scopes: List of human-readable scopes (e.g. ['accounts', 'transactions']).

        Returns:
            List of permissions in the BCB format (e.g. ['ACCOUNTS_READ', ...]).
        """
        permission_map: dict[str, list[str]] = {
            "accounts": [
                "ACCOUNTS_READ",
                "ACCOUNTS_BALANCES_READ",
                "ACCOUNTS_TRANSACTIONS_READ",
                "ACCOUNTS_OVERDRAFT_LIMITS_READ",
            ],
            "credit_cards": [
                "CREDIT_CARDS_ACCOUNTS_READ",
                "CREDIT_CARDS_ACCOUNTS_BILLS_READ",
                "CREDIT_CARDS_ACCOUNTS_BILLS_TRANSACTIONS_READ",
                "CREDIT_CARDS_ACCOUNTS_LIMITS_READ",
                "CREDIT_CARDS_ACCOUNTS_TRANSACTIONS_READ",
            ],
            "investments": [
                "BANK_FIXED_INCOMES_READ",
                "CREDIT_FIXED_INCOMES_READ",
                "FUNDS_READ",
                "VARIABLE_INCOMES_READ",
                "TREASURE_TITLES_READ",
            ],
        }

        permissions: list[str] = []
        for scope in scopes:
            permissions.extend(permission_map.get(scope, []))
        return list(dict.fromkeys(permissions))  # dedupe while preserving order
