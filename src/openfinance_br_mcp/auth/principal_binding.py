"""Binding between an authenticated MCP client principal and subject_id.

Every MCP tool that operates on bank data takes a ``subject_id``
(typically a CPF) as a plain string argument - nothing in the tool
signature itself ties that value to *who is calling*. Over the
'stdio' transport this is fine (there is exactly one local user, and
no separate MCP-client identity to speak of). Over 'streamable-http'
with MCP client OAuth configured (see auth/mcp_token_verifier.py),
though, an authenticated principal could otherwise pass an arbitrary
CPF and read another person's accounts/consent status - the server
verifies *that a* caller is authenticated, but never checks *which*
subject_id that caller is allowed to act on.

This module closes that gap by recording, at the one point identity is
genuinely established end-to-end - a subject successfully completing
the FAPI-BR consent flow (tools/consent.py::complete_consent) while
authenticated to this server as a given MCP principal - that this
principal may act on that subject_id. Every other tool taking a
subject_id then checks the binding before proceeding (see
tools/principal_guard.py).

When no MCP client OAuth is configured at all (get_access_token()
returns None - true for 'stdio' and for an HTTP deployment that
intentionally runs without auth, which config.py's
validate-outside-loopback check restricts to a loopback bind host),
binding is not enforced: there is no separate principal identity to
bind against in the first place.

Example:
    >>> bindings = PrincipalBindingStore()
    >>> await bindings.bind("12345678900", "client-abc")
    >>> await bindings.is_bound("12345678900", "client-abc")
    True
    >>> await bindings.is_bound("12345678900", "someone-else")
    False
"""

import structlog

from openfinance_br_mcp.auth.store_protocol import InMemoryStore, KeyValueStore

log = structlog.get_logger(__name__)

_KEY_PREFIX = "openfinance:principal_binding:"


def _key(subject_id: str, principal: str) -> str:
    """Builds the store key for one (subject_id, principal) pair.

    Args:
        subject_id: Identifier of the user (typically a CPF).
        principal: Identifier of the authenticated MCP client
            (AccessToken.client_id, falling back to .subject).

    Returns:
        The composite store key.
    """
    return f"{_KEY_PREFIX}{subject_id}:{principal}"


class PrincipalBindingStore:
    """Tracks which authenticated MCP principals may act on which subject_ids.

    Backed by a pluggable ``KeyValueStore`` (in-memory by default),
    matching TokenStore/ConsentManager - pass the same RedisStore those
    use so a binding created by one Kubernetes replica is visible to
    every other replica.
    """

    def __init__(self, store: KeyValueStore | None = None) -> None:
        """Initializes the store.

        Args:
            store: Backing KeyValueStore. Defaults to a new
                InMemoryStore.
        """
        self._store: KeyValueStore = store if store is not None else InMemoryStore()

    async def bind(self, subject_id: str, principal: str) -> None:
        """Records that principal may act on subject_id.

        Args:
            subject_id: Identifier of the user (typically a CPF).
            principal: Identifier of the authenticated MCP client.
        """
        await self._store.set(_key(subject_id, principal), "1")
        log.info("principal_bound", subject_id=subject_id, principal=principal)

    async def is_bound(self, subject_id: str, principal: str) -> bool:
        """Checks whether principal has previously been bound to subject_id.

        Args:
            subject_id: Identifier of the user (typically a CPF).
            principal: Identifier of the authenticated MCP client.

        Returns:
            True if this exact (subject_id, principal) pair was bound.
        """
        return await self._store.get(_key(subject_id, principal)) is not None
