"""Unit tests for server.py's non-tool-registration logic.

Tool registration itself and full protocol behavior are covered by
tests/integration/test_tool_dispatch.py and
tests/integration/test_http_transport_auth.py.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
import structlog
from mcp.server.transport_security import TransportSecuritySettings

from openfinance_br_mcp.auth.mtls_binding import MTLSClientCertMiddleware
from openfinance_br_mcp.config import settings
from openfinance_br_mcp.server import (
    _build_transport_security,
    _configure_logging,
    _health,
    _run_streamable_http,
    build_server,
    main,
)


class TestConfigureLogging:
    """Tests for _configure_logging()."""

    def test_json_format_does_not_raise(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "log_format", "json")
        monkeypatch.setattr(settings, "log_level", "INFO")

        _configure_logging()
        structlog.get_logger("test").info("smoke_test_json")

    def test_console_format_does_not_raise(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "log_format", "console")
        monkeypatch.setattr(settings, "log_level", "DEBUG")

        _configure_logging()
        structlog.get_logger("test").info("smoke_test_console")


class TestBuildTransportSecurity:
    """Tests for _build_transport_security()."""

    def test_returns_none_for_loopback_host(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "mcp_http_host", "127.0.0.1")

        assert _build_transport_security() is None

    def test_returns_none_for_localhost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "mcp_http_host", "localhost")

        assert _build_transport_security() is None

    def test_returns_none_and_warns_for_non_loopback_without_origins(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "mcp_http_host", "0.0.0.0")  # noqa: S104
        monkeypatch.setattr(settings, "mcp_http_allowed_origins", [])

        assert _build_transport_security() is None

    def test_returns_settings_for_non_loopback_with_origins(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression test for a real bug found deploying to a live k8s
        cluster: allowed_hosts must be the bare host (matched against
        the Host header), NOT the scheme-prefixed origin (matched
        against the Origin header) - the SDK's TransportSecurityMiddleware
        checks these two headers independently. With both set to the
        same scheme-prefixed list, every real request 421'd forever,
        since a bare 'Host: your-domain.com' header can never equal a
        'https://your-domain.com' string. This test previously asserted
        the buggy behavior directly, which is why it went undetected."""
        monkeypatch.setattr(settings, "mcp_http_host", "0.0.0.0")  # noqa: S104
        monkeypatch.setattr(
            settings, "mcp_http_allowed_origins", ["https://example.com"]
        )

        result = _build_transport_security()

        assert isinstance(result, TransportSecuritySettings)
        assert result.enable_dns_rebinding_protection is True
        assert result.allowed_hosts == ["example.com"]
        assert result.allowed_origins == ["https://example.com"]

    def test_allowed_hosts_keeps_port_when_origin_has_one(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "mcp_http_host", "0.0.0.0")  # noqa: S104
        monkeypatch.setattr(
            settings, "mcp_http_allowed_origins", ["http://localhost:18000"]
        )

        result = _build_transport_security()

        assert isinstance(result, TransportSecuritySettings)
        assert result.allowed_hosts == ["localhost:18000"]
        assert result.allowed_origins == ["http://localhost:18000"]


class TestHealth:
    """Tests for the /health route handler."""

    @pytest.mark.asyncio
    async def test_returns_ok_status_with_service_info(self) -> None:
        response = await _health(MagicMock())

        assert response.status_code == 200
        import json

        body = json.loads(response.body)
        assert body["status"] == "ok"
        assert body["service"] == settings.server_name
        assert body["version"] == settings.server_version


def test_server_instructions_explain_safe_payment_sequence() -> None:
    mcp = build_server()

    assert mcp.instructions is not None
    assert "payment consent" in mcp.instructions
    assert "idempotency key" in mcp.instructions


class TestMain:
    """Tests for main(), mocking out server construction/serving."""

    def test_builds_server_and_runs_with_requested_transport(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["openfinance-mcp", "--transport", "stdio"])
        fake_mcp = MagicMock()
        monkeypatch.setattr("openfinance_br_mcp.server.build_server", lambda: fake_mcp)
        monkeypatch.setattr("openfinance_br_mcp.server.configure_tracing", lambda: None)

        main()

        fake_mcp.run.assert_called_once_with(transport="stdio")

    def test_defaults_transport_to_settings_mcp_transport(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """'streamable-http' is dispatched to _run_streamable_http (not
        mcp.run() directly) so MTLSClientCertMiddleware can be wired in -
        see TestRunStreamableHttp for coverage of that function itself."""
        monkeypatch.setattr(settings, "mcp_transport", "streamable-http")
        monkeypatch.setattr(sys, "argv", ["openfinance-mcp"])
        fake_mcp = MagicMock()
        monkeypatch.setattr("openfinance_br_mcp.server.build_server", lambda: fake_mcp)
        monkeypatch.setattr("openfinance_br_mcp.server.configure_tracing", lambda: None)
        fake_run_streamable_http = MagicMock()
        monkeypatch.setattr(
            "openfinance_br_mcp.server._run_streamable_http",
            fake_run_streamable_http,
        )

        main()

        fake_run_streamable_http.assert_called_once_with(fake_mcp)


class TestRunStreamableHttp:
    """Tests for _run_streamable_http()'s mTLS middleware wiring.

    uvicorn.Server.serve() and anyio.run() are mocked out - this is a
    wiring test, not a real server smoke test (that's what
    tests/integration/test_http_transport_auth.py exercises via a
    Starlette TestClient hitting build_server().streamable_http_app()
    directly).
    """

    def test_adds_mtls_middleware_when_auth_is_configured(self) -> None:
        fake_mcp = MagicMock()
        fake_mcp.settings.auth = MagicMock()  # truthy -> auth configured
        fake_app = fake_mcp.streamable_http_app.return_value

        with patch("anyio.run", side_effect=lambda fn: None):
            _run_streamable_http(fake_mcp)

        fake_app.add_middleware.assert_called_once()
        args, _kwargs = fake_app.add_middleware.call_args
        assert args[0] is MTLSClientCertMiddleware

    def test_skips_mtls_middleware_when_auth_is_disabled(self) -> None:
        fake_mcp = MagicMock()
        fake_mcp.settings.auth = None
        fake_app = fake_mcp.streamable_http_app.return_value

        with patch("anyio.run", side_effect=lambda fn: None):
            _run_streamable_http(fake_mcp)

        fake_app.add_middleware.assert_not_called()
