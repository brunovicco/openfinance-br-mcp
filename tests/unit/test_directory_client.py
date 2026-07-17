"""Unit tests for DirectoryClient.

Fixtures are trimmed-down but structurally faithful reproductions of a
real fetch of https://data.directory.openbankingbrasil.org.br/participants
performed on 2026-07-13 (verified field names and a real Nubank entry
shape), not guessed data.
"""

import httpx
import pytest
import respx

from openfinance_br_mcp.directory.client import DirectoryClient
from openfinance_br_mcp.exceptions import DirectoryError

DIRECTORY_BASE = "https://data.directory.openbankingbrasil.org.br"


def _nubank_organisation() -> dict:
    """Trimmed but structurally real Nubank directory entry."""
    return {
        "OrganisationId": "aaaaaaaa-0000-0000-0000-000000000001",
        "OrganisationName": "NU PAGAMENTOS S.A. - INSTITUICAO DE PAGAMENTO",
        "RegistrationId": "18236120",
        "Status": "Active",
        "AuthorisationServers": [
            {
                "AuthorisationServerId": "bbbbbbbb-0000-0000-0000-000000000001",
                "Issuer": "https://openbanking.api.nubank.com.br/api/pub/",
                "OpenIDDiscoveryDocument": (
                    "https://openbanking.api.nubank.com.br/api/pub/"
                    ".well-known/openid-configuration"
                ),
                "PayloadSigningCertLocationUri": "https://openbanking.api.nubank.com.br/api/pub/jwks",
                "Status": "Active",
                "ApiResources": [
                    {
                        "ApiResourceId": "cccccccc-0000-0000-0000-000000000001",
                        "ApiVersion": "2.5.0",
                        "ApiFamilyType": "accounts",
                        "Status": "Active",
                        "CertificationStatus": "Self-Certified",
                        "ApiDiscoveryEndpoints": [
                            {
                                "ApiDiscoveryId": "dddddddd-0001",
                                "ApiEndpoint": "https://openbanking.api.nubank.com.br"
                                "/open-banking/accounts/v2/accounts",
                            }
                        ],
                    },
                    {
                        "ApiResourceId": "cccccccc-0000-0000-0000-000000000002",
                        "ApiVersion": "1.0.0",
                        "ApiFamilyType": "payments-pix",
                        "Status": "Pending",
                        "CertificationStatus": "Self-Certified",
                        "ApiDiscoveryEndpoints": [
                            {
                                "ApiDiscoveryId": "dddddddd-0002",
                                "ApiEndpoint": "https://openbanking.api.nubank.com.br"
                                "/open-banking/payments/v5/pix/payments",
                            }
                        ],
                    },
                ],
            }
        ],
    }


@pytest.fixture
def mock_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


class TestResolve:
    """Tests for DirectoryClient.resolve()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_returns_correct_base_url(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """resolve() should derive the '/open-banking' base URL from the
        real ApiDiscoveryEndpoint, matching the confirmed live Nubank host."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        result = await client.resolve("nubank", "accounts")

        assert result.base_url == "https://openbanking.api.nubank.com.br/open-banking"
        assert result.api_version == "2.5.0"
        assert result.issuer == "https://openbanking.api.nubank.com.br/api/pub/"

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_ignores_non_available_api_resources(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """An ApiResource with Status != 'Active' must not be resolved."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError, match="payments-pix"):
            await client.resolve("nubank", "payments-pix")

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_selects_latest_active_version_and_exact_endpoint(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        organisation = _nubank_organisation()
        resources = organisation["AuthorisationServers"][0]["ApiResources"]
        for version in ("4.0.1", "5.0.0"):
            resources.append(
                {
                    "ApiVersion": version,
                    "ApiFamilyType": "payments-consents",
                    "Status": "Active",
                    "ApiDiscoveryEndpoints": [
                        {
                            "ApiEndpoint": (
                                "https://openbanking.api.nubank.com.br/"
                                f"open-banking/payments/v{version[0]}/consents"
                            )
                        }
                    ],
                }
            )
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[organisation])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        result = await client.resolve("nubank", "payments-consents")

        assert result.api_version == "5.0.0"
        assert result.require_collection_endpoint("/consents").endswith(
            "/payments/v5/consents"
        )

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_raises_for_unmapped_bank_id(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """A bank_id with no configured ISPB must raise before any HTTP call."""
        route = respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError, match="No ISPB mapping"):
            await client.resolve("unknown_bank", "accounts")

        assert route.call_count == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_raises_when_organisation_absent_from_directory(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """A configured ISPB not present in the live directory must raise clearly."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError, match="18236120"):
            await client.resolve("nubank", "accounts")

    @pytest.mark.asyncio
    @respx.mock
    async def test_participants_list_is_cached_within_ttl(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """Two resolve() calls within the TTL window must only fetch once."""
        route = respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        client = DirectoryClient(
            mock_http_client, base_url=DIRECTORY_BASE, cache_ttl_seconds=900
        )

        await client.resolve("nubank", "accounts")
        await client.resolve("nubank", "accounts")

        assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_directory_http_failure_raises_directory_error(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """A non-2xx directory response must raise DirectoryError,
        not leak httpx's exception."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(503)
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError):
            await client.resolve("nubank", "accounts")


class TestResolveTokenEndpoint:
    """Tests for DirectoryClient.resolve_token_endpoint()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_token_endpoint_via_oidc_discovery(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """The token endpoint should come from the OIDC discovery
        document, not a guess."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        discovery_url = "https://openbanking.api.nubank.com.br/api/pub/.well-known/openid-configuration"
        respx.get(discovery_url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "issuer": "https://openbanking.api.nubank.com.br/api/pub/",
                    "token_endpoint": "https://openbanking.api.nubank.com.br/api/pub/token",
                    "authorization_endpoint": "https://openbanking.api.nubank.com.br/api/pub/authorize",
                    "pushed_authorization_request_endpoint": "https://openbanking.api.nubank.com.br/api/pub/par",
                },
            )
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        token_endpoint = await client.resolve_token_endpoint("nubank")

        expected = "https://openbanking.api.nubank.com.br/api/pub/token"  # noqa: S105
        assert token_endpoint == expected

    @pytest.mark.asyncio
    @respx.mock
    async def test_discovery_document_is_cached(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """Two calls for the same bank must only fetch the discovery document once."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        discovery_url = "https://openbanking.api.nubank.com.br/api/pub/.well-known/openid-configuration"
        discovery_route = respx.get(discovery_url).mock(
            return_value=httpx.Response(200, json={"token_endpoint": "https://x/token"})
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        await client.resolve_token_endpoint("nubank")
        await client.resolve_token_endpoint("nubank")

        assert discovery_route.call_count == 1


class TestResolveJwks:
    """Tests for DirectoryClient.resolve_jwks()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_resolve_jwks_via_payload_signing_cert_location(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        """The JWKS should come from the directory's own
        PayloadSigningCertLocationUri, not a guessed path."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        jwks_url = "https://openbanking.api.nubank.com.br/api/pub/jwks"
        respx.get(jwks_url).mock(
            return_value=httpx.Response(200, json={"keys": [{"kid": "k1"}]})
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        jwks = await client.resolve_jwks("nubank")

        assert jwks == {"keys": [{"kid": "k1"}]}

    @pytest.mark.asyncio
    @respx.mock
    async def test_jwks_is_cached(self, mock_http_client: httpx.AsyncClient) -> None:
        """Two calls for the same bank must only fetch the JWKS once."""
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        jwks_url = "https://openbanking.api.nubank.com.br/api/pub/jwks"
        jwks_route = respx.get(jwks_url).mock(
            return_value=httpx.Response(200, json={"keys": []})
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        await client.resolve_jwks("nubank")
        await client.resolve_jwks("nubank")

        assert jwks_route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_raises_when_no_payload_signing_cert_location(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        org = _nubank_organisation()
        org["AuthorisationServers"][0]["PayloadSigningCertLocationUri"] = None
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[org])
        )
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError, match="No JWKS URL"):
            await client.resolve_jwks("nubank")

    @pytest.mark.asyncio
    @respx.mock
    async def test_jwks_http_failure_raises_directory_error(
        self, mock_http_client: httpx.AsyncClient
    ) -> None:
        respx.get(f"{DIRECTORY_BASE}/participants").mock(
            return_value=httpx.Response(200, json=[_nubank_organisation()])
        )
        jwks_url = "https://openbanking.api.nubank.com.br/api/pub/jwks"
        respx.get(jwks_url).mock(return_value=httpx.Response(503))
        client = DirectoryClient(mock_http_client, base_url=DIRECTORY_BASE)

        with pytest.raises(DirectoryError):
            await client.resolve_jwks("nubank")
