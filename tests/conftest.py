"""Shared fixtures for the openfinance-br-mcp test suite.

Provides mocks for the HTTP client, token store, adapters, and tools
ready to use in unit and integration tests.

Example:
    >>> async def test_something(mock_token_store, mock_http_client):
    ...     adapter = NubankAdapter(mock_token_store, mock_http_client)
    ...     ...
"""

from datetime import UTC, datetime

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from openfinance_br_mcp.adapters.nubank import NubankAdapter
from openfinance_br_mcp.auth.token import TokenResponse, TokenStore

SUBJECT_ID = "12345678900"
ACCOUNT_ID = "acc_test_001"
CC_ACCOUNT_ID = "cc_test_001"


@pytest.fixture
def valid_token() -> TokenResponse:
    """Valid token with a 1-hour validity.

    Returns:
        TokenResponse with an access_token and refresh_token.
    """
    return TokenResponse(
        {
            "access_token": "eyJhbGciOiJSUzI1NiJ9.test_token",
            "refresh_token": "refresh_test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "_obtained_at": datetime.now(UTC),
        }
    )


@pytest.fixture
async def mock_token_store(valid_token: TokenResponse) -> TokenStore:
    """TokenStore preloaded with a valid token for SUBJECT_ID at 'nubank'.

    Args:
        valid_token: Injected token fixture.

    Returns:
        TokenStore with a valid token ready to use.
    """
    store = TokenStore()
    await store.save("nubank", SUBJECT_ID, valid_token)
    return store


@pytest.fixture
def mock_http_client() -> httpx.AsyncClient:
    """HTTP client for tests without real network access.

    Intended for use alongside the ``@respx.mock`` decorator, which
    intercepts all requests made through this client at the transport
    level - no custom transport needs to be configured here.

    Returns:
        Plain AsyncClient ready to be intercepted by respx.
    """
    return httpx.AsyncClient()


@pytest.fixture
async def nubank_adapter(
    mock_token_store: TokenStore,
    mock_http_client: httpx.AsyncClient,
) -> NubankAdapter:
    """Nubank adapter with mocked dependencies.

    Args:
        mock_token_store: Store with a valid token.
        mock_http_client: Mocked HTTP client.

    Returns:
        NubankAdapter ready for testing.
    """
    return NubankAdapter(mock_token_store, mock_http_client)


# Every generated model's 'links'/'meta' envelope is required and
# strict about its own required fields (Links.self, Meta.totalRecords/
# totalPages/requestDateTime - see clients/<family>/models/{links,meta}.py,
# and tests/unit/test_bank_adapters.py's identical _LINKS/_META) - the
# adapter now routes every request through the generated, typed
# clients under clients/ (P1.1) instead of building the URL/params by
# hand and parsing response.json() loosely, so these fixtures must
# match the real, spec-verified response shape exactly, not just the
# subset this project's own parsing previously happened to read.
_LINKS = {"self": "https://example.com/resource"}
_META = {"totalRecords": 1, "totalPages": 1, "requestDateTime": "2026-01-01T00:00:00Z"}


@pytest.fixture
def sample_account_response() -> dict:
    """JSON response simulating the Nubank accounts API.

    Returns:
        Dictionary in the format returned by the /accounts endpoint.
    """
    return {
        "data": [
            {
                "accountId": ACCOUNT_ID,
                "branchCode": "0001",
                "number": "12345-6",
                "checkDigit": "6",
                "type": "CONTA_DEPOSITO_A_VISTA",
                "brandName": "Nubank",
                "companyCnpj": "18236120000158",
                "compeCode": "260",
            }
        ],
        "links": _LINKS,
        "meta": _META,
    }


@pytest.fixture
def sample_transaction_response() -> dict:
    """JSON response simulating a Nubank transaction statement.

    Returns:
        Dictionary with a list of test transactions.
    """
    return {
        "data": [
            {
                "transactionId": "tx_001",
                "completedAuthorisedPaymentType": "TRANSACAO_EFETIVADA",
                "creditDebitType": "DEBITO",
                "transactionName": "COMPRA IFOOD*REFEICAO",
                "type": "PIX",
                "transactionAmount": {"amount": "45.90", "currency": "BRL"},
                "transactionDateTime": "2024-03-15T00:00:00Z",
            },
            {
                "transactionId": "tx_002",
                "completedAuthorisedPaymentType": "TRANSACAO_EFETIVADA",
                "creditDebitType": "CREDITO",
                "transactionName": "SALARIO EMPRESA XYZ",
                "type": "FOLHA_PAGAMENTO",
                "transactionAmount": {"amount": "5000.00", "currency": "BRL"},
                "transactionDateTime": "2024-03-05T00:00:00Z",
            },
        ],
        "links": _LINKS,
        # 2 items in 'data' above - the shared _META's totalRecords=1
        # would silently under-report this fixture's own item count.
        "meta": {**_META, "totalRecords": 2},
    }


@pytest.fixture
def sample_balance_response() -> dict:
    """JSON response simulating a Nubank account balance.

    Returns:
        Dictionary with available and blocked balance.
    """
    return {
        "data": {
            "availableAmount": {"amount": "1250.75", "currency": "BRL"},
            "blockedAmount": {"amount": "0.00", "currency": "BRL"},
            "automaticallyInvestedAmount": {"amount": "500.00", "currency": "BRL"},
            "updateDateTime": "2026-01-01T00:00:00Z",
        },
        "links": _LINKS,
        "meta": _META,
    }


@pytest.fixture(scope="session")
def _rsa_key_pair() -> tuple[str, str]:
    """Generates a throwaway RSA key pair for private_key_jwt/JAR tests.

    Session-scoped since 2048-bit RSA generation is comparatively slow
    and this key never needs to differ between tests.

    Returns:
        (private_key_pem, public_key_pem) tuple.
    """
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


@pytest.fixture(scope="session")
def rsa_private_key_path(
    tmp_path_factory: pytest.TempPathFactory, _rsa_key_pair: tuple[str, str]
) -> str:
    """Writes the test RSA private key to a temp file and returns its path.

    Returns:
        Filesystem path to a PEM-encoded PKCS8 private key.
    """
    private_pem, _ = _rsa_key_pair
    path = tmp_path_factory.mktemp("keys") / "client_private_key.pem"
    path.write_text(private_pem)
    return str(path)


@pytest.fixture(scope="session")
def rsa_public_key_pem(_rsa_key_pair: tuple[str, str]) -> str:
    """Returns the PEM-encoded public key matching rsa_private_key_path.

    Returns:
        PEM-encoded SubjectPublicKeyInfo public key, for verifying
        JWTs signed with the matching private key in tests.
    """
    _, public_pem = _rsa_key_pair
    return public_pem
