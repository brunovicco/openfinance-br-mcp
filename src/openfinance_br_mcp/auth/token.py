"""OAuth2 token management for Open Finance Brasil.

Responsible for storing, refreshing, and invalidating access tokens.
Refreshing takes a lock (from the same ``KeyValueStore`` backing the
data itself) to guarantee idempotency: multiple concurrent callers
never trigger multiple simultaneous refreshes.

Storage is pluggable via ``store_protocol.KeyValueStore`` (default:
``InMemoryStore`` - 12-Factor: stateless process, no state assumed to
survive a restart). Pass a ``RedisStore`` (auth/redis_backend.py) to
share tokens across Kubernetes replicas (see k8s/deployment.yaml) -
its ``lock()`` is a real distributed lock, so refresh idempotency
holds across replicas too.

Example:
    >>> store = TokenStore()
    >>> await store.save("user123", token_response)
    >>> token = await store.get_valid_token("user123", http_client)
"""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog

from openfinance_br_mcp.auth.jwt_client_auth import (
    CLIENT_ASSERTION_TYPE,
    build_client_assertion,
)
from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.exceptions import TokenRefreshError

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:token:"


class TokenResponse(dict[str, Any]):
    """Raw response from the /token endpoint enriched with a timestamp.

    Extends ``dict`` to stay compatible with the server's raw JSON
    response, adding ``obtained_at`` to compute expiration.

    Attributes:
        access_token: Bearer token for the data APIs.
        token_type: Always 'Bearer'.
        expires_in: Validity, in seconds.
        refresh_token: Token used for silent renewal.
        scope: Scopes granted by the user.
        obtained_at: UTC timestamp of when the token was obtained.
    """

    @property
    def access_token(self) -> str:
        """Returns the access token."""
        return str(self["access_token"])

    @property
    def refresh_token(self) -> str | None:
        """Returns the refresh token, if present."""
        return self.get("refresh_token")

    @property
    def expires_in(self) -> int:
        """Returns the validity in seconds (default 900s = 15min)."""
        return int(self.get("expires_in", 900))

    @property
    def obtained_at(self) -> datetime:
        """Returns the UTC timestamp when the token was obtained."""
        ts = self.get("_obtained_at")
        if isinstance(ts, datetime):
            return ts
        return datetime.now(UTC)

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Checks whether the token has expired or is about to.

        Args:
            buffer_seconds: Safety window before actual expiration.
                Avoids using a token that expires mid-request.

        Returns:
            True if the token is expired or will expire within the
            window.
        """
        expiry = self.obtained_at + timedelta(seconds=self.expires_in - buffer_seconds)
        return datetime.now(UTC) >= expiry


def _serialize_token(token: TokenResponse) -> str:
    """Serializes a TokenResponse to JSON, encoding _obtained_at as text.

    Args:
        token: The token to serialize.

    Returns:
        JSON string.
    """
    data = dict(token)
    obtained_at = data.get("_obtained_at")
    if isinstance(obtained_at, datetime):
        data["_obtained_at"] = obtained_at.isoformat()
    return json.dumps(data)


def _deserialize_token(raw: str) -> TokenResponse:
    """Deserializes a TokenResponse from JSON, decoding _obtained_at back.

    Args:
        raw: JSON string produced by _serialize_token.

    Returns:
        The reconstructed TokenResponse.
    """
    data = json.loads(raw)
    obtained_at = data.get("_obtained_at")
    if isinstance(obtained_at, str):
        data["_obtained_at"] = datetime.fromisoformat(obtained_at)
    return TokenResponse(data)


class TokenStore:
    """Stores and refreshes tokens, with concurrency safety per subject.

    Backed by a pluggable ``KeyValueStore`` (in-memory by default - see
    module docstring). Refreshing is idempotent: only one caller
    performs the refresh at a time for a given subject - across every
    replica when backed by RedisStore, since the lock itself comes
    from the store.

    Attributes:
        _store: Underlying key-value store, also the source of the
            per-subject lock used for refresh idempotency.
    """

    def __init__(self, store: KeyValueStore | None = None) -> None:
        """Initializes the store.

        Args:
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore (this project's original behavior).
        """
        self._store: KeyValueStore = store if store is not None else InMemoryStore()

    def _lock_key(self, subject_id: str) -> str:
        """Builds the lock key for a subject.

        Deliberately distinct from the data key (``_KEY_PREFIX +
        subject_id``) - RedisStore.lock() SETs its own value directly
        under this key, which would otherwise clobber the stored token.

        Args:
            subject_id: Unique identifier of the user/consent.

        Returns:
            The lock key for this subject.
        """
        return f"{_KEY_PREFIX}lock:{subject_id}"

    async def save(self, subject_id: str, token: TokenResponse) -> None:
        """Persists a token for a subject.

        Args:
            subject_id: Identifier of the user/consent.
            token: Response from the /token endpoint.
        """
        token["_obtained_at"] = datetime.now(UTC)
        async with self._store.lock(self._lock_key(subject_id)):
            await self._store.set(_KEY_PREFIX + subject_id, _serialize_token(token))
        log.info("token_saved", subject_id=subject_id, expires_in=token.expires_in)

    async def get_valid_token(
        self,
        subject_id: str,
        http_client: httpx.AsyncClient,
        token_endpoint: str,
    ) -> TokenResponse:
        """Returns a valid token, refreshing it automatically if needed.

        The lock guarantees that even under high concurrency only one
        refresh is executed for a given subject - across every replica
        when backed by RedisStore (see store_protocol.py/redis_backend.py).

        Args:
            subject_id: Identifier of the user.
            http_client: Authenticated HTTP client used for the refresh.
            token_endpoint: URL of the institution's /token endpoint.

        Returns:
            TokenResponse with a valid access_token.

        Raises:
            KeyError: If no token exists for the subject.
            TokenRefreshError: If the refresh fails.
        """
        async with self._store.lock(self._lock_key(subject_id)):
            raw = await self._store.get(_KEY_PREFIX + subject_id)
            if raw is None:
                raise KeyError(subject_id)
            token = _deserialize_token(raw)
            if not token.is_expired():
                return token

            log.info("token_refresh_start", subject_id=subject_id)
            refreshed = await self._refresh(token, http_client, token_endpoint)
            refreshed["_obtained_at"] = datetime.now(UTC)
            await self._store.set(_KEY_PREFIX + subject_id, _serialize_token(refreshed))
            log.info("token_refresh_ok", subject_id=subject_id)
            return refreshed

    async def _refresh(
        self,
        token: TokenResponse,
        http_client: httpx.AsyncClient,
        token_endpoint: str,
    ) -> TokenResponse:
        """Performs the refresh via grant_type=refresh_token.

        Args:
            token: Current token with a refresh_token.
            http_client: HTTP client (with mTLS configured).
            token_endpoint: URL of the /token endpoint.

        Returns:
            New TokenResponse.

        Raises:
            TokenRefreshError: If the server returns an error.
        """
        if not token.refresh_token:
            raise TokenRefreshError(
                "Refresh token missing - the user must re-authenticate",
                code="NO_REFRESH_TOKEN",
            )

        try:
            client_assertion = build_client_assertion(audience=token_endpoint)
            response = await http_client.post(
                token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token,
                    "client_id": settings.client_id,
                    "client_assertion_type": CLIENT_ASSERTION_TYPE,
                    "client_assertion": client_assertion,
                },
            )
            response.raise_for_status()
            return TokenResponse(response.json())
        except httpx.HTTPStatusError as exc:
            raise TokenRefreshError(
                f"Token refresh failed: HTTP {exc.response.status_code}",
                code="REFRESH_HTTP_ERROR",
            ) from exc
        except httpx.RequestError as exc:
            raise TokenRefreshError(
                f"Network error while refreshing the token: {exc}",
                code="REFRESH_NETWORK_ERROR",
            ) from exc

    async def revoke(self, subject_id: str) -> None:
        """Removes the token for a subject (logout/revocation).

        Args:
            subject_id: Identifier of the user to log out.
        """
        await self._store.delete(_KEY_PREFIX + subject_id)
        log.info("token_revoked", subject_id=subject_id)
