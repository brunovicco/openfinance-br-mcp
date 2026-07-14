"""Tracking of pending FAPI-BR authorization requests.

Bridges ``start_consent`` (which pushes a PAR request and returns a
URL for the user to open in a browser) and ``complete_consent`` (which
the user/assistant calls after pasting back the browser's final
redirect URL) - see ``tools/consent.py`` for why this two-step,
paste-back shape is necessary given FAPI-BR's mandatory
``response_mode=fragment``.

Backed by a pluggable ``KeyValueStore`` (in-memory by default),
matching ``TokenStore``/``ConsentManager`` (auth/token.py,
auth/consent.py) - passing the same ``RedisStore`` those use ensures a
pending session created by one Kubernetes replica (start_consent
hitting pod A) is visible to another (complete_consent landing on pod
B). The ``save()`` call also sets a Redis TTL matching
``_SESSION_TTL`` so expired sessions clean themselves up there without
a bespoke sweep.

Example:
    >>> store = AuthorizationSessionStore()
    >>> await store.save("state-abc", pending_authorization)
    >>> session = await store.pop("state-abc")
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog

from openfinance_br_mcp.auth.pkce import PKCEChallenge
from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.exceptions import ConsentError

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:authorization_session:"
_SESSION_TTL = timedelta(minutes=15)


@dataclass
class PendingAuthorization:
    """State needed to complete an authorization after the user consents.

    Attributes:
        bank_id: Identifier used by this project's adapters.
        bank_base_url: Base URL of the institution's resource APIs -
            needed again at completion time to query the consent's
            final status.
        consent_id: The consentId created via ConsentManager.create(),
            embedded in the PAR request's 'consent:<id>' scope.
        subject_id: Identifier of the user going through the flow.
        pkce: The PKCE challenge sent with the authorization request -
            its code_verifier is required at the token exchange step.
        nonce: The nonce sent with the authorization request - must
            match the ID token's 'nonce' claim to prevent replay.
        issuer: The authorization server's issuer, expected as the ID
            token's 'iss' claim.
        token_endpoint: The authorization server's token endpoint, for
            the authorization_code exchange.
        created_at: When this session was created, for TTL expiry.
    """

    bank_id: str
    bank_base_url: str
    consent_id: str
    subject_id: str
    pkce: PKCEChallenge
    nonce: str
    issuer: str
    token_endpoint: str
    created_at: datetime


def _serialize_session(session: PendingAuthorization) -> str:
    """Serializes a PendingAuthorization to JSON.

    Args:
        session: The session to serialize.

    Returns:
        JSON string.
    """
    return json.dumps(
        {
            "bank_id": session.bank_id,
            "bank_base_url": session.bank_base_url,
            "consent_id": session.consent_id,
            "subject_id": session.subject_id,
            "pkce": session.pkce.model_dump(),
            "nonce": session.nonce,
            "issuer": session.issuer,
            "token_endpoint": session.token_endpoint,
            "created_at": session.created_at.isoformat(),
        }
    )


def _deserialize_session(raw: str) -> PendingAuthorization:
    """Deserializes a PendingAuthorization from JSON.

    Args:
        raw: JSON string produced by _serialize_session.

    Returns:
        The reconstructed PendingAuthorization.
    """
    data = json.loads(raw)
    return PendingAuthorization(
        bank_id=data["bank_id"],
        bank_base_url=data["bank_base_url"],
        consent_id=data["consent_id"],
        subject_id=data["subject_id"],
        pkce=PKCEChallenge.model_validate(data["pkce"]),
        nonce=data["nonce"],
        issuer=data["issuer"],
        token_endpoint=data["token_endpoint"],
        created_at=datetime.fromisoformat(data["created_at"]),
    )


class AuthorizationSessionStore:
    """Stores PendingAuthorization objects keyed by the OAuth2 'state' value.

    Backed by a pluggable ``KeyValueStore`` (in-memory by default - see
    module docstring). Expiry is checked lazily, on ``pop()`` of that
    specific key, rather than swept proactively across every stored
    session - KeyValueStore has no ``keys()``/``scan()`` to enumerate
    everything. With RedisStore, the TTL passed to ``set()`` cleans up
    abandoned sessions (started but never completed) automatically;
    with InMemoryStore (which ignores ttl_seconds), an abandoned
    session lingers until the process restarts.
    """

    def __init__(self, store: KeyValueStore | None = None) -> None:
        """Initializes the store.

        Args:
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore (this project's original behavior).
        """
        self._store: KeyValueStore = store if store is not None else InMemoryStore()

    async def save(self, state: str, session: PendingAuthorization) -> None:
        """Stores a pending authorization under its 'state' value.

        Args:
            state: The 'state' value sent in the authorization request.
            session: The session to store.
        """
        await self._store.set(
            _KEY_PREFIX + state,
            _serialize_session(session),
            ttl_seconds=int(_SESSION_TTL.total_seconds()),
        )

    async def pop(self, state: str) -> PendingAuthorization:
        """Retrieves and removes a pending authorization by 'state'.

        Single-use by design: a 'state' value must not be replayable
        once the flow it corresponds to has been completed.

        Args:
            state: The 'state' value from the callback URL.

        Returns:
            The matching PendingAuthorization.

        Raises:
            ConsentError: If no session matches 'state' (unknown,
                already completed, or expired).
        """
        raw = await self._store.get(_KEY_PREFIX + state)
        session = _deserialize_session(raw) if raw is not None else None
        await self._store.delete(_KEY_PREFIX + state)

        if session is None:
            raise ConsentError(
                "No pending authorization matches this 'state' - it may "
                "have already been completed, or the session expired "
                "(15 minute limit). Call start_consent again.",
                code="AUTHORIZATION_SESSION_NOT_FOUND",
            )

        if datetime.now(UTC) - session.created_at > _SESSION_TTL:
            log.info("authorization_session_expired", state=state)
            raise ConsentError(
                "No pending authorization matches this 'state' - it may "
                "have already been completed, or the session expired "
                "(15 minute limit). Call start_consent again.",
                code="AUTHORIZATION_SESSION_NOT_FOUND",
            )

        return session
