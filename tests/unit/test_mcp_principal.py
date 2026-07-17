"""Tests for user-bound MCP principal derivation."""

import pytest
from mcp.server.auth.provider import AccessToken

from openfinance_br_mcp.auth.mcp_principal import principal_from_access_token
from openfinance_br_mcp.exceptions import ValidationError


def _token(*, issuer: str | None, subject: str | None) -> AccessToken:
    claims = {"iss": issuer} if issuer is not None else {}
    return AccessToken(
        token="opaque-test-token",  # noqa: S106
        client_id="shared-oauth-client",
        scopes=[],
        subject=subject,
        claims=claims,
    )


def test_principal_uses_issuer_and_subject_not_client_id() -> None:
    token = _token(issuer="https://idp.example.com", subject="user-1")

    assert principal_from_access_token(token) == "https://idp.example.com::user-1"


@pytest.mark.parametrize(
    ("issuer", "subject"),
    [(None, "user-1"), ("https://idp.example.com", None)],
)
def test_missing_user_identity_fails_closed(
    issuer: str | None, subject: str | None
) -> None:
    with pytest.raises(ValidationError):
        principal_from_access_token(_token(issuer=issuer, subject=subject))
