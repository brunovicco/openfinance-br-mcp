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


def test_private_key_jwt_credentials_are_required_outside_mock() -> None:
    with pytest.raises(ValidationError, match="private_key_path"):
        Settings(
            _env_file=None,
            environment="sandbox",
            client_id="client-1",
            private_key_path="",
            private_key_kid="",
        )


def test_client_secret_is_not_required_when_private_key_jwt_is_configured() -> None:
    config = Settings(
        _env_file=None,
        environment="sandbox",
        client_id="client-1",
        client_secret="",
        private_key_path="client.pem",
        private_key_kid="kid-1",
    )

    assert config.client_secret is None


def test_remote_http_requires_origin_allowlist_even_with_oauth() -> None:
    with pytest.raises(ValidationError, match="mcp_http_allowed_origins"):
        Settings(
            _env_file=None,
            environment="mock",
            mcp_transport="streamable-http",
            mcp_http_host="0.0.0.0",  # noqa: S104
            mcp_oauth_issuer_url="https://idp.example.com",
            mcp_oauth_resource_server_url="https://mcp.example.com",
        )


def test_production_forbids_hardcoded_directory_fallback() -> None:
    with pytest.raises(ValidationError, match="fail_closed"):
        Settings(
            _env_file=None,
            environment="production",
            client_id="client-1",
            private_key_path="client.pem",
            private_key_kid="kid-1",
            directory_fallback_mode="hardcoded_fallback",
        )


def test_network_http_requires_mcp_oauth() -> None:
    with pytest.raises(ValidationError, match="mcp_oauth_issuer_url"):
        Settings(
            _env_file=None,
            environment="mock",
            mcp_transport="streamable-http",
            mcp_http_host="0.0.0.0",  # noqa: S104
        )
