"""Unit tests for tools/pix.py.

See test_tools_accounts.py's module docstring for the testing approach.
"""

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from openfinance_br_mcp.adapters.mock_adapter import MockOpenFinanceAdapter
from openfinance_br_mcp.auth.idempotency_store import IdempotencyStore
from openfinance_br_mcp.auth.payment_consent import PaymentConsentStatus
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.exceptions import ConsentError, ValidationError
from openfinance_br_mcp.schemas.pix import PixKeyType
from openfinance_br_mcp.tools.pix import initiate_pix, list_pix_keys

SUBJECT_ID = "12345678900"


def _app(
    adapter: MockOpenFinanceAdapter | None,
    *,
    directory: object | None = None,
    token_store: TokenStore | None = None,
    payment_consent_manager: AsyncMock | None = None,
) -> AppContext:
    return AppContext(
        http_client=httpx.AsyncClient(),
        token_store=token_store if token_store is not None else TokenStore(),
        adapters={"nubank": adapter} if adapter else {},
        categorizer=AsyncMock(),
        consent_manager=AsyncMock(),
        authorization_sessions=AsyncMock(),
        principal_bindings=AsyncMock(),
        payment_consent_manager=payment_consent_manager or AsyncMock(),
        idempotency_store=IdempotencyStore(),
        directory=directory,  # type: ignore[arg-type]
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context)
    )


class TestListPixKeys:
    """Tests for list_pix_keys()."""

    @pytest.mark.asyncio
    async def test_returns_keys_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(list_pix_keys)(
            SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
        )

        assert result.bank == "nubank"
        assert result.account_id == "acc-1"
        assert result.pix_keys[0].key == "mock-user@nubank.example"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(list_pix_keys)(
                SUBJECT_ID, "nubank", "acc-1", _fake_ctx(app)
            )


class TestInitiatePixMockMode:
    """initiate_pix in mock mode (directory=None) - no payment consent
    resource exists, so the consent check is skipped entirely."""

    @pytest.mark.asyncio
    async def test_initiates_payment_for_a_known_bank(self) -> None:
        app = _app(MockOpenFinanceAdapter("nubank"))

        result = await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-1",
            _fake_ctx(app),
        )

        assert result.bank == "nubank"
        assert result.payment.payment_id == "mock-pay-idem-key"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_bank(self) -> None:
        app = _app(None)

        with pytest.raises(ValidationError, match="not available"):
            await inspect.unwrap(initiate_pix)(
                SUBJECT_ID,
                "nubank",
                150.00,
                "recipient@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                "idem-key-2",
                _fake_ctx(app),
            )

    @pytest.mark.asyncio
    async def test_identical_replay_returns_cached_result_without_recalling_adapter(
        self,
    ) -> None:
        """A second call with the exact same idempotency_key AND payload
        must return the first call's exact result (same end_to_end_id),
        proving the adapter wasn't invoked a second time."""
        app = _app(MockOpenFinanceAdapter("nubank"))
        args = (
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-3",
            _fake_ctx(app),
        )

        first = await inspect.unwrap(initiate_pix)(*args)
        second = await inspect.unwrap(initiate_pix)(*args)

        assert first == second

    @pytest.mark.asyncio
    async def test_same_key_different_payload_raises_conflict(self) -> None:
        """Reusing an idempotency_key across two *different* payments is a
        client bug the Open Finance Brasil idempotency contract requires
        rejecting outright, not silently returning the unrelated cached
        result for (see auth/idempotency_store.py)."""
        app = _app(MockOpenFinanceAdapter("nubank"))

        await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-4",
            _fake_ctx(app),
        )

        with pytest.raises(ValidationError, match="already used"):
            await inspect.unwrap(initiate_pix)(
                SUBJECT_ID,
                "nubank",
                999.00,
                "someone-else@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                "idem-key-4",
                _fake_ctx(app),
            )


class _FakeResolvedApi:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


class _FakeDirectory:
    """Minimal stand-in for DirectoryClient's methods initiate_pix calls."""

    async def resolve(self, bank_id: str, api_family_type: str) -> _FakeResolvedApi:
        return _FakeResolvedApi(base_url=f"https://{bank_id}.example.com/open-banking")

    async def resolve_token_endpoint(self, bank_id: str) -> str:
        return f"https://{bank_id}.example.com/token"


class TestInitiatePixRealMode:
    """initiate_pix outside mock mode requires an AUTHORISED payment
    consent obtained via start_payment_consent/complete_payment_consent."""

    @pytest.mark.asyncio
    async def test_raises_when_no_payment_token_exists(self) -> None:
        app = _app(
            MockOpenFinanceAdapter("nubank"),
            directory=_FakeDirectory(),
            token_store=TokenStore(),
        )

        with pytest.raises(ConsentError, match="No active payment consent session"):
            await inspect.unwrap(initiate_pix)(
                SUBJECT_ID,
                "nubank",
                150.00,
                "recipient@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                "idem-key-5",
                _fake_ctx(app),
            )

    @pytest.mark.asyncio
    async def test_raises_when_consent_is_not_authorised(self) -> None:
        token_store = TokenStore()
        await token_store.save(
            "nubank",
            SUBJECT_ID,
            TokenResponse({"access_token": "payment-token", "expires_in": 300}),
            purpose="payment",
        )
        payment_consent_manager = AsyncMock()
        payment_consent_manager.get_status.return_value = (
            PaymentConsentStatus.AWAITING_AUTHORISATION
        )
        app = _app(
            MockOpenFinanceAdapter("nubank"),
            directory=_FakeDirectory(),
            token_store=token_store,
            payment_consent_manager=payment_consent_manager,
        )

        with pytest.raises(ConsentError, match="not AUTHORISED"):
            await inspect.unwrap(initiate_pix)(
                SUBJECT_ID,
                "nubank",
                150.00,
                "recipient@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                "idem-key-6",
                _fake_ctx(app),
            )

    @pytest.mark.asyncio
    async def test_succeeds_and_marks_consent_consumed_when_authorised(self) -> None:
        token_store = TokenStore()
        await token_store.save(
            "nubank",
            SUBJECT_ID,
            TokenResponse({"access_token": "payment-token", "expires_in": 300}),
            purpose="payment",
        )
        payment_consent_manager = AsyncMock()
        payment_consent_manager.get_status.return_value = (
            PaymentConsentStatus.AUTHORISED
        )
        app = _app(
            MockOpenFinanceAdapter("nubank"),
            directory=_FakeDirectory(),
            token_store=token_store,
            payment_consent_manager=payment_consent_manager,
        )

        result = await inspect.unwrap(initiate_pix)(
            SUBJECT_ID,
            "nubank",
            150.00,
            "recipient@example.com",
            PixKeyType.EMAIL,
            "acc-1",
            "idem-key-7",
            _fake_ctx(app),
        )

        assert result.bank == "nubank"
        payment_consent_manager.mark_consumed.assert_awaited_once_with(
            "nubank", SUBJECT_ID
        )
