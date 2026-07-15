"""Tests for configuration normalization and fail-fast validation."""

import pytest
from pydantic import ValidationError

from openfinance_br_mcp.config import Settings


def test_empty_bank_credentials_are_optional_in_mock_mode() -> None:
    config = Settings(
        _env_file=None,
        environment="mock",
        client_id="",
        client_secret="",
    )

    assert config.client_id is None
    assert config.client_secret is None


def test_empty_bank_credentials_are_rejected_outside_mock() -> None:
    with pytest.raises(ValidationError, match="client_id and client_secret"):
        Settings(
            _env_file=None,
            environment="sandbox",
            client_id="",
            client_secret="",
        )


def test_network_http_requires_mcp_oauth() -> None:
    with pytest.raises(ValidationError, match="mcp_oauth_issuer_url"):
        Settings(
            _env_file=None,
            environment="mock",
            mcp_transport="streamable-http",
            mcp_http_host="0.0.0.0",  # noqa: S104
        )
