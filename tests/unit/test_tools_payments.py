"""Unit tests for the payment consent flow MCP tools (tools/payments.py).

Mirrors test_tools_consent.py's approach: a respx-mocked bank plus a
real RSA key pair so the JOSE round-trips (PAR/JAR, ID token) are
genuine, not mocked away.
"""

import inspect
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx
from jwcrypto import jwk
from jwcrypto import jwt as jwcrypto_jwt

from openfinance_br_mcp.auth.authorization_session import AuthorizationSessionStore
from openfinance_br_mcp.auth.payment_consent import (
    PaymentConsentManager,
    payment_token_purpose,
)
from openfinance_br_mcp.auth.payment_jws import sign_payment_payload
from openfinance_br_mcp.auth.token import TokenStore
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.context import AppContext
from openfinance_br_mcp.directory.client import DirectoryClient
from openfinance_br_mcp.exceptions import ConsentDeniedError, ValidationError
from openfinance_br_mcp.schemas.pix import PixKeyType
from openfinance_br_mcp.tools.payments import (
    check_payment_consent_status,
    complete_payment_consent,
    start_payment_consent,
)

DIRECTORY_BASE = "https://data.directory.openbankingbrasil.org.br"
ISSUER = "https://bank.example.com/api/pub/"
TOKEN_ENDPOINT = "https://bank.example.com/api/pub/token"  # noqa: S105
PAR_ENDPOINT = "https://bank.example.com/api/pub/par"
AUTHZ_ENDPOINT = "https://bank.example.com/api/pub/authorize"
JWKS_URL = "https://bank.example.com/api/pub/jwks"
DISCOVERY_URL = "https://bank.example.com/api/pub/.well-known/openid-configuration"
PAYMENTS_BASE = "https://bank.example.com/open-banking"
CONSENTS_URL = f"{PAYMENTS_BASE}/payments/v5/consents"
SUBJECT_ID = "12345678900"


def _nubank_organisation() -> dict[str, object]:
    return {
        "OrganisationId": "org-1",
        "OrganisationName": "NU PAGAMENTOS S.A.",
        "RegistrationId": "18236120",
        "Status": "Active",
        "AuthorisationServers": [
            {
                "AuthorisationServerId": "as-1",
                "Issuer": ISSUER,
                "OpenIDDiscoveryDocument": DISCOVERY_URL,
                "PayloadSigningCertLocationUri": JWKS_URL,
                "Status": "Active",
                "ApiResources": [
                    {
                        "ApiResourceId": "res-1",
                        "ApiVersion": "5.0.0",
                        "ApiFamilyType": "payments-consents",
                        "Status": "Active",
                        "ApiDiscoveryEndpoints": [{"ApiEndpoint": CONSENTS_URL}],
                    }
                ],
            }
        ],
    }


def _mock_directory_and_discovery() -> None:
    respx.get(f"{DIRECTORY_BASE}/participants").mock(
        return_value=httpx.Response(200, json=[_nubank_organisation()])
    )
    respx.get(DISCOVERY_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "issuer": ISSUER,
                "token_endpoint": TOKEN_ENDPOINT,
                "authorization_endpoint": AUTHZ_ENDPOINT,
                "pushed_authorization_request_endpoint": PAR_ENDPOINT,
            },
        )
    )


def _fake_ctx(app_context: AppContext) -> SimpleNamespace:
    return SimpleNamespace(
        request_context=SimpleNamespace(lifespan_context=app_context),
        elicit_url=AsyncMock(),
    )


def _issue_id_token(
    bank_key: jwk.JWK, client_public_key_pem: str, *, nonce: str
) -> str:
    """Builds a JWE(JWS(claims)) ID token exactly like a real FAPI-BR bank
    would - the inner JWT is signed with the bank's own key (verified
    against its JWKS) and the outer JWT is encrypted with the client's
    public key (see auth/id_token.py, P0.7)."""
    now = int(datetime.now(UTC).timestamp())
    inner = jwcrypto_jwt.JWT(
        header={"alg": "PS256", "kid": "bank-kid-1"},
        claims={
            "iss": ISSUER,
            "sub": SUBJECT_ID,
            "aud": "test-client-id",
            "nonce": nonce,
            "acr": "urn:brasil:openbanking:loa2",
            "iat": now,
            "exp": now + 300,
        },
    )
    inner.make_signed_token(bank_key)
    client_public_key = jwk.JWK.from_pem(client_public_key_pem.encode())
    outer = jwcrypto_jwt.JWT(
        header={"alg": "RSA-OAEP", "enc": "A256GCM", "cty": "JWT"},
        claims=inner.serialize(),
    )
    outer.make_encrypted_token(client_public_key)
    return str(outer.serialize())


def _sign_bank_response(bank_key: jwk.JWK, payload: dict[str, object]) -> str:
    token = jwcrypto_jwt.JWT(
        header={"alg": "PS256", "kid": "bank-kid-1"}, claims=payload
    )
    token.make_signed_token(bank_key)
    return str(token.serialize())


def _client_jwks(public_key_pem: str) -> dict[str, object]:
    key = jwk.JWK.from_pem(public_key_pem.encode())
    key.update(kid="test-kid")
    return {"keys": [json.loads(key.export_public())]}


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture(autouse=True)
def _configured_client(
    monkeypatch: pytest.MonkeyPatch, rsa_private_key_path: str
) -> None:
    monkeypatch.setattr(settings, "environment", "sandbox")
    monkeypatch.setattr(settings, "client_id", "test-client-id")
    monkeypatch.setattr(settings, "private_key_path", rsa_private_key_path)
    monkeypatch.setattr(settings, "private_key_kid", "test-kid")


def _app(
    http_client: httpx.AsyncClient, *, directory: DirectoryClient | None
) -> AppContext:
    return AppContext(
        http_client=http_client,
        token_store=TokenStore(),
        adapters={},
        categorizer=AsyncMock(),
        consent_manager=AsyncMock(),
        authorization_sessions=AuthorizationSessionStore(),
        principal_bindings=AsyncMock(),
        payment_consent_manager=PaymentConsentManager(http_client),
        idempotency_store=AsyncMock(),
        directory=directory,
    )


class TestStartPaymentConsentMockMode:
    """start_payment_consent must refuse to run in mock mode."""

    @pytest.mark.asyncio
    async def test_raises_in_mock_mode(
        self, http_client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "environment", "mock")
        app = _app(http_client, directory=None)

        with pytest.raises(ValidationError, match="not applicable in mock mode"):
            await inspect.unwrap(start_payment_consent)(
                SUBJECT_ID,
                "nubank",
                "150.00",
                "someone@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                _fake_ctx(app),
            )


class TestStartPaymentConsent:
    """Tests for start_payment_consent()'s end-to-end orchestration."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_creates_payment_consent_and_returns_par_authorization_url(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        _mock_directory_and_discovery()
        respx.get(JWKS_URL).mock(
            return_value=httpx.Response(200, json=_client_jwks(rsa_public_key_pem))
        )
        respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200, json={"access_token": "cc-token", "expires_in": 300}
            )
        )
        respx.post(CONSENTS_URL).mock(
            return_value=httpx.Response(
                201,
                content=sign_payment_payload(
                    {
                        "data": {
                            "consentId": "urn:bank:PC1",
                            "status": "AWAITING_AUTHORISATION",
                        }
                    }
                ),
            )
        )
        respx.post(PAR_ENDPOINT).mock(
            return_value=httpx.Response(
                201, json={"request_uri": "urn:par:xyz", "expires_in": 60}
            )
        )
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)
        app.principal_bindings.is_bound.return_value = False
        ctx = _fake_ctx(app)

        # A payment-only user has no principal/subject binding yet. Starting
        # the bank authorization flow must remain possible because successful
        # completion is what creates that binding.
        with patch(
            "openfinance_br_mcp.tools.principal_guard.get_access_token",
            return_value=SimpleNamespace(client_id="remote-client", subject=None),
        ):
            result = await start_payment_consent(
                SUBJECT_ID,
                "nubank",
                "150.00",
                "someone@example.com",
                PixKeyType.EMAIL,
                "acc-1",
                ctx,
                request_url_elicitation=True,
            )

        assert result.consent_id == "urn:bank:PC1"
        parsed = urlparse(result.authorization_url)
        assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == AUTHZ_ENDPOINT
        query = parse_qs(parsed.query)
        assert query["request_uri"] == ["urn:par:xyz"]
        ctx.elicit_url.assert_awaited_once()
        assert ctx.elicit_url.await_args.kwargs["url"] == result.authorization_url


class TestCompletePaymentConsent:
    """Tests for complete_payment_consent()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_denied_callback_raises_consent_denied_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        app = _app(http_client, directory=None)
        callback_url = (
            "https://client.example.com/callback"
            "?error=access_denied&error_description=user+said+no&state=abc"
        )

        with pytest.raises(ConsentDeniedError, match="access_denied"):
            await inspect.unwrap(complete_payment_consent)(callback_url, _fake_ctx(app))

    @pytest.mark.asyncio
    async def test_missing_code_or_state_raises_validation_error(
        self, http_client: httpx.AsyncClient
    ) -> None:
        app = _app(http_client, directory=None)
        callback_url = "https://client.example.com/callback?code=abc"

        with pytest.raises(ValidationError, match="missing 'code' or 'state'"):
            await inspect.unwrap(complete_payment_consent)(callback_url, _fake_ctx(app))

    @pytest.mark.asyncio
    @respx.mock
    async def test_completes_exchange_and_saves_payment_purpose_token(
        self, http_client: httpx.AsyncClient, rsa_public_key_pem: str
    ) -> None:
        _mock_directory_and_discovery()
        bank_key = jwk.JWK.generate(kty="RSA", size=2048, kid="bank-kid-1")
        jwks = {"keys": [json.loads(bank_key.export_public())]}
        respx.get(JWKS_URL).mock(return_value=httpx.Response(200, json=jwks))
        respx.post(TOKEN_ENDPOINT).mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "payment-token",
                    "refresh_token": "refresh-token",
                    "expires_in": 300,
                },
            )
        )
        respx.get(f"{CONSENTS_URL}/urn:bank:PC1").mock(
            return_value=httpx.Response(
                200,
                content=_sign_bank_response(
                    bank_key,
                    {
                        "data": {
                            "consentId": "urn:bank:PC1",
                            "status": "AUTHORISED",
                        }
                    },
                ),
            )
        )
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        token_store = TokenStore()
        app = AppContext(
            http_client=http_client,
            token_store=token_store,
            adapters={},
            categorizer=AsyncMock(),
            consent_manager=AsyncMock(),
            authorization_sessions=AuthorizationSessionStore(),
            principal_bindings=AsyncMock(),
            payment_consent_manager=PaymentConsentManager(http_client),
            idempotency_store=AsyncMock(),
            directory=directory,
        )

        # Seed a pending authorization session, as start_payment_consent would.
        from openfinance_br_mcp.auth.authorization_session import PendingAuthorization
        from openfinance_br_mcp.auth.pkce import PKCEChallenge

        pkce = PKCEChallenge.generate()
        await app.authorization_sessions.save(
            "state-1",
            PendingAuthorization(
                bank_id="nubank",
                bank_base_url=CONSENTS_URL,
                consent_id="urn:bank:PC1",
                subject_id=SUBJECT_ID,
                pkce=pkce,
                nonce="nonce-1",
                issuer=ISSUER,
                token_endpoint=TOKEN_ENDPOINT,
                created_at=datetime.now(UTC),
            ),
        )
        # Seed the payment consent manager's cache so get_status() finds
        # it - it was created by start_payment_consent in the real flow.
        await app.payment_consent_manager._set_cached(
            "nubank",
            SUBJECT_ID,
            "urn:bank:PC1",
            {
                "data": {
                    "consentId": "urn:bank:PC1",
                    "status": "AWAITING_AUTHORISATION",
                }
            },
        )

        id_token = _issue_id_token(bank_key, rsa_public_key_pem, nonce="nonce-1")
        callback_url = (
            "https://client.example.com/callback#"
            f"code=auth-code&state=state-1&id_token={id_token}"
        )

        result = await inspect.unwrap(complete_payment_consent)(
            callback_url, _fake_ctx(app)
        )

        assert result.status == "AUTHORISED"
        saved = await token_store.get_valid_token(
            "nubank",
            SUBJECT_ID,
            http_client,
            TOKEN_ENDPOINT,
            purpose=payment_token_purpose("urn:bank:PC1"),
        )
        assert saved.access_token == "payment-token"  # noqa: S105
        with pytest.raises(KeyError):
            await token_store.get_valid_token(
                "nubank", SUBJECT_ID, http_client, TOKEN_ENDPOINT, purpose="data"
            )


class TestCheckPaymentConsentStatus:
    """Tests for check_payment_consent_status()."""

    @pytest.mark.asyncio
    async def test_raises_when_no_active_payment_session(
        self, http_client: httpx.AsyncClient
    ) -> None:
        directory = DirectoryClient(http_client, base_url=DIRECTORY_BASE)
        app = _app(http_client, directory=directory)

        with respx.mock:
            _mock_directory_and_discovery()
            with pytest.raises(Exception, match="No active payment consent session"):
                await inspect.unwrap(check_payment_consent_status)(
                    SUBJECT_ID, "nubank", "urn:bank:PC1", _fake_ctx(app)
                )
