"""Pydantic schemas for the Open Finance Brasil Directory of Participants.

Models a subset of the real response shape of
``GET https://data.directory.openbankingbrasil.org.br/participants``
(public, unauthenticated, refreshed by the BCB roughly every 15
minutes). Only the fields this project actually consumes are
declared; unrecognized fields are ignored (Pydantic v2's default
``BaseModel`` behavior), since the real payload carries dozens of
fields unrelated to endpoint resolution (address, tags, domain
claims, etc.).

Field names intentionally keep the directory's own PascalCase
convention rather than being renamed to snake_case, so the schema
here is a direct, greppable mirror of the live API.

Example:
    >>> from openfinance_br_mcp.directory.models import Organisation
    >>> org = Organisation.model_validate(raw_dict)
    >>> org.RegistrationId  # the institution's ISPB code
    '18236120'
"""

from urllib.parse import urlparse

from pydantic import BaseModel, Field

from openfinance_br_mcp.exceptions import DirectoryError


class ApiDiscoveryEndpoint(BaseModel):
    """A single concrete API endpoint URL for an ApiResource.

    Attributes:
        ApiDiscoveryId: Directory-internal identifier for this endpoint entry.
        ApiEndpoint: The actual HTTPS URL of the resource collection
            (e.g. '.../open-banking/accounts/v2/accounts').
    """

    ApiDiscoveryId: str | None = None
    ApiEndpoint: str


class ApiResource(BaseModel):
    """A certified API family exposed by an AuthorisationServer.

    Attributes:
        ApiResourceId: Directory-internal identifier for this resource entry.
        ApiVersion: Semantic version of the certified API (e.g. '2.5.0').
        ApiFamilyType: API family slug (e.g. 'accounts',
            'payments-consents', 'payments-pix', 'consents', 'resources',
            'credit-cards-accounts'). Payment consent and PIX initiation
            are registered as separate family types in the Directory.
        Status: 'Active' when the API is live and usable (verified
            against a live directory fetch); other values indicate it
            should not be resolved.
        CertificationStatus: e.g. 'Self-Certified', 'Certified'.
        ApiDiscoveryEndpoints: Concrete endpoint URLs for this API family.
    """

    ApiResourceId: str | None = None
    ApiVersion: str
    ApiFamilyType: str
    Status: str | None = None
    CertificationStatus: str | None = None
    ApiDiscoveryEndpoints: list[ApiDiscoveryEndpoint] = Field(default_factory=list)


class AuthorisationServer(BaseModel):
    """An OAuth2/OIDC authorization server operated by a participant.

    Attributes:
        AuthorisationServerId: Directory-internal identifier.
        Issuer: OAuth2/OIDC issuer URL, used as the FAPI-BR ``iss``.
        OpenIDDiscoveryDocument: URL of the '.well-known/openid-configuration'
            document - the spec-correct way to discover the real
            token/authorization/PAR endpoints, instead of guessing paths.
        PayloadSigningCertLocationUri: JWKS URL for validating signed
            responses from this authorization server.
        Status: 'Active' when usable.
        ApiResources: API families certified under this authorization server.
    """

    AuthorisationServerId: str | None = None
    Issuer: str | None = None
    OpenIDDiscoveryDocument: str | None = None
    PayloadSigningCertLocationUri: str | None = None
    Status: str | None = None
    ApiResources: list[ApiResource] = Field(default_factory=list)


class Organisation(BaseModel):
    """A participating institution in the Open Finance Brasil ecosystem.

    Attributes:
        OrganisationId: Directory-internal identifier.
        OrganisationName: Legal/trading name as registered.
        RegistrationId: The institution's 8-digit ISPB code - the
            reliable key for matching a directory entry to a known
            bank_id, since OrganisationName varies in ways not worth
            fuzzy-matching (legal suffixes, capitalization, etc.).
        Status: 'Active' when the organisation is a live participant.
        AuthorisationServers: Authorization servers operated by this
            organisation.
    """

    OrganisationId: str
    OrganisationName: str
    RegistrationId: str | None = None
    Status: str | None = None
    AuthorisationServers: list[AuthorisationServer] = Field(default_factory=list)


class ResolvedApi(BaseModel):
    """Result of resolving a bank + API family to a live, certified endpoint.

    Attributes:
        bank_id: Identifier used by this project's adapters (e.g. 'nubank').
        api_family_type: The resolved ApiFamilyType (e.g. 'accounts').
        api_version: The certified version of that API family.
        base_url: Base URL adapters should build request paths from
            (derived from the first matching ApiDiscoveryEndpoint by
            trimming it back to the '/open-banking' path segment
            common to every Open Finance Brasil resource API).
        issuer: The OAuth2/OIDC issuer for this organisation's
            authorization server.
        openid_discovery_document: URL to fetch for the real
            token/authorization/PAR endpoints.
        api_endpoints: Exact resource URLs published for this family.
            Payment flows use these values directly instead of rebuilding
            a URL from a host plus a locally-maintained version constant.
    """

    bank_id: str
    api_family_type: str
    api_version: str
    base_url: str
    issuer: str | None
    openid_discovery_document: str | None
    api_endpoints: list[str] = Field(default_factory=list)

    def require_collection_endpoint(self, path_suffix: str) -> str:
        """Returns the exact collection endpoint matching ``path_suffix``.

        Args:
            path_suffix: Expected URL path suffix, for example
                ``/consents`` or ``/pix/payments``.

        Returns:
            The exact URL published in ``ApiDiscoveryEndpoints``.

        Raises:
            DirectoryError: If this resolved family did not publish a
                concrete collection endpoint with the requested suffix.
        """
        normalized_suffix = "/" + path_suffix.strip("/")
        for endpoint in self.api_endpoints:
            path = urlparse(endpoint).path.rstrip("/")
            if "{" not in endpoint and path.endswith(normalized_suffix):
                return endpoint.rstrip("/")
        raise DirectoryError(
            f"No collection endpoint ending in '{normalized_suffix}' was "
            f"published for '{self.api_family_type}' at bank '{self.bank_id}'",
            bank_id=self.bank_id,
            code="API_ENDPOINT_NOT_FOUND",
        )
