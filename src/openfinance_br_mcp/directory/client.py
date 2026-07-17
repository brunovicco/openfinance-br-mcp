"""Client for the Open Finance Brasil Directory of Participants.

Resolves a bank's real, currently-certified base URL and OAuth2/OIDC
endpoints instead of hardcoding them per adapter - hardcoded URLs go
stale as institutions rotate hosts and bump API versions.

Matches organisations by ISPB (``RegistrationId`` in the directory
schema), not by name: ``OrganisationName`` strings are inconsistent
(legal suffixes, capitalization) and unsuitable for reliable fuzzy
matching, while ISPB is the stable identifier BCB already assigns to
every institution.

Example:
    >>> client = DirectoryClient(http_client, base_url=settings.bcb_directory_url)
    >>> resolved = await client.resolve("nubank", "accounts")
    >>> resolved.base_url
    'https://openbanking.api.nubank.com.br/open-banking'
"""

import asyncio
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog

from openfinance_br_mcp.directory.models import Organisation, ResolvedApi
from openfinance_br_mcp.exceptions import DirectoryError

log = structlog.get_logger(__name__)

_AVAILABLE_STATUS = "Active"

_ISPB_BY_BANK: dict[str, str] = {
    "nubank": "18236120",
    "caixa": "00360305",
    "sicoob": "04891850",
    "banco_do_brasil": "00000000",
    "bradesco": "60746948",
    "itau": "60701190",
    "santander": "90400888",
    "xp": "33264668",
    "picpay": "22896431",
    "btg": "30306294",
}


def _base_url_from_endpoint(endpoint: str) -> str:
    """Derives the '/open-banking' base URL from a full resource endpoint.

    Every Open Finance Brasil resource API URL observed follows the
    pattern '<host>/open-banking/<family>/<version>/<path>'. Adapters
    build requests by appending a known suffix to a base URL, so this
    trims the endpoint back to that common prefix.

    Args:
        endpoint: A full ApiDiscoveryEndpoint URL.

    Returns:
        The endpoint truncated to '<host>/open-banking'.

    Raises:
        DirectoryError: If the endpoint doesn't contain '/open-banking/'.
    """
    marker = "/open-banking/"
    index = endpoint.find(marker)
    if index == -1:
        raise DirectoryError(
            f"Endpoint '{endpoint}' does not follow the expected "
            "'/open-banking/' URL pattern",
            code="UNEXPECTED_ENDPOINT_SHAPE",
        )
    return endpoint[: index + len(marker) - 1]


def _version_key(version: str) -> tuple[int, int, int, int]:
    """Builds a sortable key for Directory semantic-version strings.

    Stable releases sort after prereleases carrying the same numeric
    version. Unknown shapes remain resolvable but sort below a valid
    semantic version.
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", version)
    if match is None:
        return (0, 0, 0, 0)
    major, minor, patch, suffix = match.groups()
    return (int(major), int(minor), int(patch), 1 if not suffix else 0)


class DirectoryClient:
    """Resolves bank endpoints via the Directory of Participants.

    Caches the full participants list in memory with a TTL matching
    the directory's own refresh cadence (~15 minutes), so repeated
    tool calls don't re-fetch the (currently ~100+ organisation) list
    on every request.

    Attributes:
        _http: HTTP client used for directory requests (no auth/mTLS
            required - the directory's read endpoints are public).
        _base_url: Base URL of the directory (production or sandbox).
        _cache_ttl: How long a fetched participants list stays valid.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        base_url: str,
        cache_ttl_seconds: int = 900,
    ) -> None:
        """Initializes the client.

        Args:
            http_client: HTTP client for directory requests.
            base_url: Directory base URL, e.g.
                'https://data.directory.openbankingbrasil.org.br'.
            cache_ttl_seconds: How long to reuse a fetched participants
                list before refetching. Defaults to 900s (15min),
                matching the directory's documented refresh cadence.
        """
        self._http = http_client
        self._base_url = base_url.rstrip("/")
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache: list[Organisation] | None = None
        self._cached_at: datetime | None = None
        self._lock = asyncio.Lock()
        self._discovery_cache: dict[str, dict[str, Any]] = {}
        self._jwks_cache: dict[str, dict[str, Any]] = {}

    async def _participants(self) -> list[Organisation]:
        """Returns the cached participants list, refetching if stale.

        Returns:
            List of all organisations currently in the directory.

        Raises:
            DirectoryError: If the directory request fails.
        """
        async with self._lock:
            if (
                self._cache is not None
                and self._cached_at is not None
                and datetime.now(UTC) - self._cached_at < self._cache_ttl
            ):
                return self._cache

            try:
                response = await self._http.get(f"{self._base_url}/participants")
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise DirectoryError(
                    f"Failed to fetch the participants directory: {exc}",
                    code="DIRECTORY_FETCH_ERROR",
                ) from exc

            self._cache = [
                Organisation.model_validate(item) for item in response.json()
            ]
            self._cached_at = datetime.now(UTC)
            log.info("directory_refreshed", organisation_count=len(self._cache))
            return self._cache

    async def _find_organisation(self, bank_id: str) -> Organisation:
        """Finds the organisation matching a bank_id's configured ISPB.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The matching Organisation.

        Raises:
            DirectoryError: If no ISPB is configured for bank_id, or no
                organisation with that ISPB exists in the directory.
        """
        ispb = _ISPB_BY_BANK.get(bank_id)
        if ispb is None:
            raise DirectoryError(
                f"No ISPB mapping configured for bank '{bank_id}'",
                bank_id=bank_id,
                code="UNKNOWN_BANK_ISPB",
            )

        organisations = await self._participants()
        for org in organisations:
            if org.RegistrationId == ispb:
                return org

        raise DirectoryError(
            f"No organisation with ISPB '{ispb}' found in the participants directory",
            bank_id=bank_id,
            code="ORGANISATION_NOT_FOUND",
        )

    async def resolve(self, bank_id: str, api_family_type: str) -> ResolvedApi:
        """Resolves a bank + API family to a live, certified endpoint.

        Args:
            bank_id: Identifier used by this project's adapters (e.g. 'nubank').
            api_family_type: Directory ApiFamilyType to resolve (e.g.
                'accounts', 'consents', 'payments-consents',
                'payments-pix').

        Returns:
            ResolvedApi with the base URL and issuer to use.

        Raises:
            DirectoryError: If the bank, its authorization server, or the
                requested API family cannot be resolved to an available
                endpoint.
        """
        org = await self._find_organisation(bank_id)
        candidates: list[ResolvedApi] = []

        if org.Status not in (None, _AVAILABLE_STATUS):
            raise DirectoryError(
                f"Organisation for bank '{bank_id}' is not active",
                bank_id=bank_id,
                code="ORGANISATION_NOT_ACTIVE",
            )

        for auth_server in org.AuthorisationServers:
            if auth_server.Status not in (None, _AVAILABLE_STATUS):
                continue
            for api_resource in auth_server.ApiResources:
                if (
                    api_resource.ApiFamilyType != api_family_type
                    or api_resource.Status != _AVAILABLE_STATUS
                    or not api_resource.ApiDiscoveryEndpoints
                ):
                    continue
                api_endpoints = [
                    endpoint.ApiEndpoint
                    for endpoint in api_resource.ApiDiscoveryEndpoints
                ]
                candidates.append(
                    ResolvedApi(
                        bank_id=bank_id,
                        api_family_type=api_family_type,
                        api_version=api_resource.ApiVersion,
                        base_url=_base_url_from_endpoint(api_endpoints[0]),
                        issuer=auth_server.Issuer,
                        openid_discovery_document=(auth_server.OpenIDDiscoveryDocument),
                        api_endpoints=api_endpoints,
                    )
                )

        if candidates:
            return max(candidates, key=lambda item: _version_key(item.api_version))

        raise DirectoryError(
            f"No available '{api_family_type}' API found for bank '{bank_id}'",
            bank_id=bank_id,
            code="API_FAMILY_NOT_FOUND",
        )

    async def resolve_discovery_document(self, bank_id: str) -> dict[str, Any]:
        """Fetches (and caches) the authorization server's OIDC discovery document.

        This is the spec-correct way to find token/authorization/PAR
        endpoints instead of guessing paths - see auth/jwt_client_auth.py
        and auth/par.py, which both need endpoints from this document.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The parsed '.well-known/openid-configuration' JSON document.

        Raises:
            DirectoryError: If the organisation or its discovery document
                cannot be resolved.
        """
        org = await self._find_organisation(bank_id)
        auth_server = next(
            (a for a in org.AuthorisationServers if a.OpenIDDiscoveryDocument), None
        )
        if auth_server is None or auth_server.OpenIDDiscoveryDocument is None:
            raise DirectoryError(
                f"No OpenID discovery document found for bank '{bank_id}'",
                bank_id=bank_id,
                code="NO_DISCOVERY_DOCUMENT",
            )

        discovery_url = auth_server.OpenIDDiscoveryDocument
        cached = self._discovery_cache.get(discovery_url)
        if cached is None:
            try:
                response = await self._http.get(discovery_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise DirectoryError(
                    f"Failed to fetch OpenID discovery document for '{bank_id}': {exc}",
                    bank_id=bank_id,
                    code="DISCOVERY_FETCH_ERROR",
                ) from exc
            cached = response.json()
            self._discovery_cache[discovery_url] = cached

        return cached

    async def resolve_token_endpoint(self, bank_id: str) -> str:
        """Resolves the OAuth2 token endpoint via OIDC discovery.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The resolved token_endpoint URL.

        Raises:
            DirectoryError: If the discovery document or the
                token_endpoint field cannot be resolved.
        """
        return await self._require_endpoint(bank_id, "token_endpoint")

    async def resolve_par_endpoint(self, bank_id: str) -> str:
        """Resolves the Pushed Authorization Request endpoint via OIDC discovery.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The resolved pushed_authorization_request_endpoint URL.

        Raises:
            DirectoryError: If the discovery document or that field
                cannot be resolved.
        """
        return await self._require_endpoint(
            bank_id, "pushed_authorization_request_endpoint"
        )

    async def resolve_authorization_endpoint(self, bank_id: str) -> str:
        """Resolves the OAuth2 authorization endpoint via OIDC discovery.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The resolved authorization_endpoint URL.

        Raises:
            DirectoryError: If the discovery document or that field
                cannot be resolved.
        """
        return await self._require_endpoint(bank_id, "authorization_endpoint")

    async def _require_endpoint(self, bank_id: str, field: str) -> str:
        """Resolves a single required field from the OIDC discovery document.

        Args:
            bank_id: Identifier used by this project's adapters.
            field: Name of the discovery document field to extract.

        Returns:
            The field's value.

        Raises:
            DirectoryError: If the discovery document or the field
                cannot be resolved.
        """
        document = await self.resolve_discovery_document(bank_id)
        value = document.get(field)
        if not value:
            raise DirectoryError(
                f"OpenID discovery document for '{bank_id}' has no {field}",
                bank_id=bank_id,
                code=f"NO_{field.upper()}",
            )
        return str(value)

    async def resolve_jwks(self, bank_id: str) -> dict[str, Any]:
        """Fetches (and caches) the authorization server's JWKS.

        Used to verify the signature of the inner JWS carried inside an
        encrypted ID token (see auth/id_token.py). Sourced from the
        directory's own PayloadSigningCertLocationUri field rather than
        the OIDC discovery document's 'jwks_uri' - the directory already
        captures it directly (see AuthorisationServer in models.py), so
        this avoids depending on a second, less consistently populated
        field for the same information.

        Args:
            bank_id: Identifier used by this project's adapters.

        Returns:
            The parsed JWKS document (e.g. {'keys': [...]}), ready for
            jwcrypto.jwk.JWKSet.from_json().

        Raises:
            DirectoryError: If the organisation has no
                PayloadSigningCertLocationUri, or fetching it fails.
        """
        org = await self._find_organisation(bank_id)
        auth_server = next(
            (a for a in org.AuthorisationServers if a.PayloadSigningCertLocationUri),
            None,
        )
        if auth_server is None or auth_server.PayloadSigningCertLocationUri is None:
            raise DirectoryError(
                f"No JWKS URL (PayloadSigningCertLocationUri) found for "
                f"bank '{bank_id}'",
                bank_id=bank_id,
                code="NO_JWKS_URL",
            )

        jwks_url = auth_server.PayloadSigningCertLocationUri
        cached = self._jwks_cache.get(jwks_url)
        if cached is None:
            try:
                response = await self._http.get(jwks_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise DirectoryError(
                    f"Failed to fetch JWKS for '{bank_id}': {exc}",
                    bank_id=bank_id,
                    code="JWKS_FETCH_ERROR",
                ) from exc
            cached = response.json()
            self._jwks_cache[jwks_url] = cached

        return cached
