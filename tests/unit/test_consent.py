"""Unit tests for ConsentManager (consent lifecycle on Open Finance Brasil)."""

import httpx
import pytest
import respx

from openfinance_br_mcp.auth.consent import ConsentManager, ConsentStatus
from openfinance_br_mcp.exceptions import ConsentDeniedError, ConsentError

BANK_BASE_URL = "https://bank.example.com/open-banking"
BANK_ID = "nubank"
SUBJECT_ID = "12345678900"
ACCESS_TOKEN = "cc-token"  # noqa: S105


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


def _consent_response(status: str = "AWAITING_AUTHORISATION") -> dict:
    return {
        "data": {
            "consentId": "urn:bank:C1DD33123",
            "status": status,
            "permissions": ["ACCOUNTS_READ"],
        },
        "links": {"self": f"{BANK_BASE_URL}/consents/v3/consents/urn:bank:C1DD33123"},
    }


class TestCreate:
    """Tests for ConsentManager.create()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_creates_consent_and_returns_consent_id(
        self, http_client: httpx.AsyncClient
    ) -> None:
        route = respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        manager = ConsentManager(http_client)

        consent_id = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        assert consent_id == "urn:bank:C1DD33123"
        sent = route.calls[0].request
        assert sent.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"

    @pytest.mark.asyncio
    @respx.mock
    async def test_reuses_existing_awaiting_consent(
        self, http_client: httpx.AsyncClient
    ) -> None:
        route = respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        manager = ConsentManager(http_client)

        first = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )
        second = await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        assert first == second
        assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_consent_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(400)
        )
        manager = ConsentManager(http_client)

        with pytest.raises(ConsentError, match="Failed to create consent"):
            await manager.create(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                scopes=["accounts"],
                access_token=ACCESS_TOKEN,
            )


class TestGetStatus:
    """Tests for ConsentManager.get_status()."""

    @pytest.mark.asyncio
    async def test_raises_when_no_consent_cached(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = ConsentManager(http_client)

        with pytest.raises(ConsentError, match="No consent found"):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                access_token=ACCESS_TOKEN,
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_current_status(self, http_client: httpx.AsyncClient) -> None:
        respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        respx.get(f"{BANK_BASE_URL}/consents/v3/consents/urn:bank:C1DD33123").mock(
            return_value=httpx.Response(200, json=_consent_response("AUTHORISED"))
        )
        manager = ConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        status = await manager.get_status(
            BANK_ID, SUBJECT_ID, bank_base_url=BANK_BASE_URL, access_token=ACCESS_TOKEN
        )

        assert status == ConsentStatus.AUTHORISED

    @pytest.mark.asyncio
    @respx.mock
    async def test_raises_consent_denied_when_rejected(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        respx.get(f"{BANK_BASE_URL}/consents/v3/consents/urn:bank:C1DD33123").mock(
            return_value=httpx.Response(200, json=_consent_response("REJECTED"))
        )
        manager = ConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        with pytest.raises(ConsentDeniedError, match="denied"):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                access_token=ACCESS_TOKEN,
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error_raises_consent_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        respx.get(f"{BANK_BASE_URL}/consents/v3/consents/urn:bank:C1DD33123").mock(
            return_value=httpx.Response(503)
        )
        manager = ConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        with pytest.raises(ConsentError, match="Error querying consent"):
            await manager.get_status(
                BANK_ID,
                SUBJECT_ID,
                bank_base_url=BANK_BASE_URL,
                access_token=ACCESS_TOKEN,
            )


class TestRevoke:
    """Tests for ConsentManager.revoke()."""

    @pytest.mark.asyncio
    async def test_noop_when_no_consent_cached(
        self, http_client: httpx.AsyncClient
    ) -> None:
        manager = ConsentManager(http_client)
        await manager.revoke(
            BANK_ID, SUBJECT_ID, bank_base_url=BANK_BASE_URL, access_token=ACCESS_TOKEN
        )
        # No exception, nothing to assert beyond "didn't crash".

    @pytest.mark.asyncio
    @respx.mock
    async def test_deletes_consent_and_clears_cache(
        self, http_client: httpx.AsyncClient
    ) -> None:
        respx.post(f"{BANK_BASE_URL}/consents/v3/consents").mock(
            return_value=httpx.Response(201, json=_consent_response())
        )
        delete_route = respx.delete(
            f"{BANK_BASE_URL}/consents/v3/consents/urn:bank:C1DD33123"
        ).mock(return_value=httpx.Response(204))
        manager = ConsentManager(http_client)
        await manager.create(
            BANK_ID,
            SUBJECT_ID,
            bank_base_url=BANK_BASE_URL,
            scopes=["accounts"],
            access_token=ACCESS_TOKEN,
        )

        await manager.revoke(
            BANK_ID, SUBJECT_ID, bank_base_url=BANK_BASE_URL, access_token=ACCESS_TOKEN
        )

        assert delete_route.call_count == 1
        assert await manager._get_cached(BANK_ID, SUBJECT_ID) is None


class TestBuildPermissions:
    """Tests for ConsentManager._build_permissions()."""

    def test_maps_known_scopes(self) -> None:
        permissions = ConsentManager._build_permissions(["accounts", "balances"])
        assert "ACCOUNTS_READ" in permissions
        assert "ACCOUNTS_BALANCES_READ" in permissions

    def test_accounts_scope_alone_does_not_imply_balances(self) -> None:
        """Regression test (P0.8): 'accounts' must grant exactly
        ACCOUNTS_READ, not implicitly transactions/balances/overdraft
        limits too."""
        permissions = ConsentManager._build_permissions(["accounts"])
        assert permissions == ["ACCOUNTS_READ"]

    def test_dedupes_overlapping_scopes(self) -> None:
        permissions = ConsentManager._build_permissions(["accounts", "accounts"])
        assert permissions.count("ACCOUNTS_READ") == 1

    def test_ignores_unknown_scopes(self) -> None:
        permissions = ConsentManager._build_permissions(["not_a_real_scope"])
        assert permissions == []
