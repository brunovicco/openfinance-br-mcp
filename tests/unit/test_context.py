"""Unit tests for context.py's environment-based adapter construction."""

import httpx
import pytest
import respx

from openfinance_br_mcp.adapters.caixa import CaixaAdapter
from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.adapters.nubank import (
    _NUBANK_BASE,
    _NUBANK_TOKEN,
    NubankAdapter,
)
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import (
    _build_mock_adapters,
    _build_real_adapters,
    app_lifespan,
)
from openfinance_br_mcp.directory.client import DirectoryClient


def _nubank_organisation_with_resolved_host(*, with_discovery: bool = False) -> dict:
    """A minimal directory entry resolving to a host distinct from
    _NUBANK_BASE, so tests can tell "resolved via directory" apart
    from "fell back to the hardcoded default".

    Args:
        with_discovery: Whether to include OpenIDDiscoveryDocument -
            needed to test token_endpoint resolution; omitted by
            default so existing base_url-only tests are unaffected.
    """
    auth_server: dict = {
        "AuthorisationServerId": "as-1",
        "Issuer": "https://resolved.example.com/api/pub/",
        "Status": "Active",
        "ApiResources": [
            {
                "ApiResourceId": "res-1",
                "ApiVersion": "2.5.0",
                "ApiFamilyType": "accounts",
                "Status": "Active",
                "ApiDiscoveryEndpoints": [
                    {
                        "ApiEndpoint": "https://resolved.example.com/open-banking/accounts/v2/accounts"
                    }
                ],
            }
        ],
    }
    if with_discovery:
        auth_server["OpenIDDiscoveryDocument"] = (
            "https://resolved.example.com/.well-known/openid-configuration"
        )
    return {
        "OrganisationId": "org-1",
        "OrganisationName": "NU PAGAMENTOS S.A.",
        "RegistrationId": "18236120",
        "Status": "Active",
        "AuthorisationServers": [auth_server],
    }


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


class TestBuildMockAdapters:
    """Tests for _build_mock_adapters()."""

    @pytest.mark.asyncio
    async def test_returns_mock_adapter_per_known_bank(self) -> None:
        adapters = await _build_mock_adapters()

        assert set(adapters) == {
            "nubank",
            "sicoob",
            "caixa",
            "banco_do_brasil",
            "bradesco",
            "itau",
            "santander",
            "xp",
            "picpay",
            "btg",
        }
        assert all(isinstance(a, MockOpenFinanceAdapter) for a in adapters.values())
        assert adapters["nubank"].bank_id == "nubank"


class TestBuildRealAdapters:
    """Tests for _build_real_adapters()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_uses_directory_resolved_base_url_when_available(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A successful directory resolution should win over the
        adapter's hardcoded default.

        Explicitly opts into directory_fallback_mode='hardcoded_fallback':
        this fixture has no OpenIDDiscoveryDocument, so token_endpoint
        resolution fails even though base_url resolves fine - under
        the default 'fail_closed' (P0.6) that would exclude the bank
        entirely, but this test's intent is specifically the *partial*
        fallback behavior (base_url from the directory, token_endpoint
        from the hardcoded default)."""
        monkeypatch.setattr(settings, "environment", "production")
        monkeypatch.setattr(settings, "directory_fallback_mode", "hardcoded_fallback")
        respx.get(f"{settings.bcb_directory_url}participants").mock(
            return_value=httpx.Response(
                200, json=[_nubank_organisation_with_resolved_host()]
            )
        )

        from openfinance_br_mcp.auth.token import TokenStore

        directory = DirectoryClient(
            http_client, base_url=str(settings.bcb_directory_url)
        )
        adapters = await _build_real_adapters(TokenStore(), http_client, directory)

        assert isinstance(adapters["nubank"], NubankAdapter)
        assert (
            adapters["nubank"].base_url == "https://resolved.example.com/open-banking"
        )
        # No OpenIDDiscoveryDocument in this fixture - token_endpoint
        # resolution must fail gracefully and fall back, independent
        # of base_url having resolved successfully.
        assert adapters["nubank"].token_endpoint == _NUBANK_TOKEN

    @pytest.mark.asyncio
    @respx.mock
    async def test_uses_directory_resolved_token_endpoint_when_discovery_available(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression test for a real gap found in review: base_url was
        being resolved via the directory, but token_endpoint never was -
        every adapter kept the hardcoded (unverified) guess even when a
        real OIDC discovery document was resolvable."""
        monkeypatch.setattr(settings, "environment", "production")
        respx.get(f"{settings.bcb_directory_url}participants").mock(
            return_value=httpx.Response(
                200,
                json=[_nubank_organisation_with_resolved_host(with_discovery=True)],
            )
        )
        respx.get("https://resolved.example.com/.well-known/openid-configuration").mock(
            return_value=httpx.Response(
                200, json={"token_endpoint": "https://resolved.example.com/token"}
            )
        )

        from openfinance_br_mcp.auth.token import TokenStore

        directory = DirectoryClient(
            http_client, base_url=str(settings.bcb_directory_url)
        )
        adapters = await _build_real_adapters(TokenStore(), http_client, directory)

        expected_token_endpoint = "https://resolved.example.com/token"  # noqa: S105
        assert adapters["nubank"].token_endpoint == expected_token_endpoint

    @pytest.mark.asyncio
    @respx.mock
    async def test_falls_back_to_hardcoded_default_when_fallback_enabled(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A directory lookup miss (e.g. unmapped/unfound ISPB) must not
        crash server startup - with directory_fallback_mode explicitly
        set to 'hardcoded_fallback' (local-dev opt-in - see P0.6), it
        should fall back per-bank instead of excluding the bank."""
        monkeypatch.setattr(settings, "environment", "production")
        monkeypatch.setattr(settings, "directory_fallback_mode", "hardcoded_fallback")
        respx.get(f"{settings.bcb_directory_url}participants").mock(
            return_value=httpx.Response(200, json=[])
        )

        from openfinance_br_mcp.auth.token import TokenStore

        directory = DirectoryClient(
            http_client, base_url=str(settings.bcb_directory_url)
        )
        adapters = await _build_real_adapters(TokenStore(), http_client, directory)

        assert adapters["nubank"].base_url == _NUBANK_BASE
        assert isinstance(adapters["caixa"], CaixaAdapter)

    @pytest.mark.asyncio
    @respx.mock
    async def test_fail_closed_excludes_bank_when_directory_fails_by_default(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression test (P0.6): the default directory_fallback_mode
        is 'fail_closed' - a directory lookup miss must exclude the
        bank from app.adapters entirely, never silently fall back to a
        possibly stale hardcoded URL."""
        monkeypatch.setattr(settings, "environment", "production")
        assert settings.directory_fallback_mode == "fail_closed"
        respx.get(f"{settings.bcb_directory_url}participants").mock(
            return_value=httpx.Response(200, json=[])
        )

        from openfinance_br_mcp.auth.token import TokenStore

        directory = DirectoryClient(
            http_client, base_url=str(settings.bcb_directory_url)
        )
        adapters = await _build_real_adapters(TokenStore(), http_client, directory)

        assert "nubank" not in adapters
        assert "caixa" not in adapters
        assert adapters == {}


class TestAppLifespan:
    """Tests for app_lifespan()'s end-to-end environment branching."""

    @pytest.mark.asyncio
    async def test_mock_environment_yields_mock_adapters(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "environment", "mock")

        async with app_lifespan(server=None) as app:  # type: ignore[arg-type]
            assert all(
                isinstance(a, MockOpenFinanceAdapter) for a in app.adapters.values()
            )

    @pytest.mark.asyncio
    async def test_mock_environment_yields_no_directory(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """There's nothing to resolve in mock mode - the consent tools
        use this to reject start_consent/etc. with a clear error."""
        monkeypatch.setattr(settings, "environment", "mock")

        async with app_lifespan(server=None) as app:  # type: ignore[arg-type]
            assert app.directory is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_sandbox_environment_yields_real_adapters(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "environment", "sandbox")
        # Explicit opt-in to the fallback: an empty sandbox Directory
        # response means every bank fails to resolve, and the default
        # fail_closed behavior (P0.6) would otherwise leave
        # app.adapters empty - this test's intent is verifying
        # "sandbox environment yields real (non-mock) adapter
        # instances", which needs hardcoded_fallback to observe at all.
        monkeypatch.setattr(settings, "directory_fallback_mode", "hardcoded_fallback")
        respx.get(f"{settings.bcb_sandbox_directory_url}participants").mock(
            return_value=httpx.Response(200, json=[])
        )

        async with app_lifespan(server=None) as app:  # type: ignore[arg-type]
            assert isinstance(app.adapters["nubank"], NubankAdapter)
            assert isinstance(app.directory, DirectoryClient)
            assert not isinstance(app.adapters["nubank"], MockOpenFinanceAdapter)

    @pytest.mark.asyncio
    @respx.mock
    async def test_sandbox_environment_excludes_unresolved_banks_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression test (P0.6): with the default fail_closed mode,
        an empty Directory response must leave app.adapters empty
        rather than falling back to hardcoded URLs."""
        monkeypatch.setattr(settings, "environment", "sandbox")
        respx.get(f"{settings.bcb_sandbox_directory_url}participants").mock(
            return_value=httpx.Response(200, json=[])
        )

        async with app_lifespan(server=None) as app:  # type: ignore[arg-type]
            assert app.adapters == {}
