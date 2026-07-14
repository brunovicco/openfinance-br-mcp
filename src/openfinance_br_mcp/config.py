"""Configuration module for openfinance-br-mcp.

Centralizes all application configuration via environment variables,
following 12-Factor App principle III (Config). No secret should
ever live in the source code.

Example:
    >>> from openfinance_br_mcp.config import settings
    >>> print(settings.server_name)
    'openfinance-br-mcp'
"""

from pathlib import Path
from typing import Literal, Self

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SECRETS_DIR = "/app/secrets"


class Settings(BaseSettings):
    """Application configuration loaded from the environment.

    All sensitive variables are typed as ``SecretStr`` to avoid
    accidental exposure in logs.

    Attributes:
        server_name: Name of the MCP server.
        server_version: Semantic version of the server.
        log_level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_format: Log output format ('json' or 'console').
        bcb_api_base_url: Base URL of the Brazilian Open Finance APIs.
        bcb_directory_url: URL of the BCB production Directory of
            Participants, used by DirectoryClient to resolve real bank
            endpoints.
        bcb_sandbox_directory_url: URL of the BCB sandbox Directory of
            Participants - lists a different, smaller set of
            organisations than production; Nubank/Sicoob/Caixa sandbox
            entries may not be present.
        environment: 'mock' (default) runs entirely in-memory via
            MockOpenFinanceAdapter, with no real credentials, network
            calls, or mTLS certificates required - the primary
            day-to-day dev loop, since the official sandbox is not
            self-service. 'sandbox'/'production' resolve real bank
            endpoints via DirectoryClient and require client_id/
            client_secret.
        client_id: Client ID registered with the participating
            institution. Required unless environment='mock'.
        client_secret: Corresponding client secret. Required unless
            environment='mock'.
        mtls_cert_path: Path to the client mTLS certificate.
        mtls_key_path: Path to the client mTLS private key.
        private_key_path: Path to the RSA private key used for
            private_key_jwt/JAR signing (distinct from the mTLS key).
        private_key_kid: Key ID matching the registered JWKS entry.
        private_key_jwt_alg: JWS signing algorithm (default PS256).
        redirect_uri: Redirect URI for the consent flow.
        consent_expiry_hours: Consent validity, in hours.
        redis_url: Optional Redis URL for sharing TokenStore/
            ConsentManager state across replicas. None means in-memory
            (single-process only) - see auth/redis_backend.py.
        anthropic_api_key: Anthropic API key for the DSPy module.
        dspy_model: LLM model used by DSPy for categorization.
        dspy_cache_enabled: Enables caching of DSPy inferences.
        http_timeout_seconds: Default timeout for HTTP calls.
        http_max_retries: Maximum number of retries on transient failures.
        mcp_transport: MCP transport to serve - 'stdio' for local clients
            (e.g. Claude Desktop) or 'streamable-http' for remote/production
            deployments (e.g. Kubernetes).
        mcp_http_host: Bind host for the 'streamable-http' transport.
        mcp_http_port: Bind port for the 'streamable-http' transport.
        mcp_http_stateless: If true, creates a new transport session per
            request instead of a persistent one - required for horizontal
            scaling behind a plain load balancer with no sticky sessions.
        mcp_http_allowed_origins: Origin header values accepted by the
            'streamable-http' transport, to guard against DNS-rebinding
            attacks. Required (non-empty) whenever ``mcp_http_host`` is not
            a loopback address, since DNS-rebinding protection is only
            auto-enabled for localhost.
        mcp_oauth_issuer_url: OAuth2/OIDC issuer that issues access tokens
            for MCP clients calling this server over 'streamable-http'.
            Unset by default - with no issuer configured, the HTTP
            transport runs without auth (acceptable only because it then
            stays restricted to a loopback bind host, per the MCP
            authorization spec). Set this (and mcp_oauth_resource_server_url)
            once a real identity provider exists to turn auth on. This is
            a completely separate token universe from the FAPI-BR bank
            credentials in auth/ - never conflate an MCP client's token
            with a bank access token (see docs/en/authorization.md).
        mcp_oauth_resource_server_url: This server's own canonical URL,
            used as the required 'aud' (audience) claim on incoming MCP
            client tokens (RFC 8707) and as the resource identifier for
            RFC 9728 Protected Resource Metadata. Required alongside
            mcp_oauth_issuer_url.
        mcp_oauth_required_scopes: OAuth scopes an MCP client's token must
            carry to call any tool. Empty by default (no scope
            requirement) until a real IdP's scope conventions are known.
        mcp_oauth_jwks_cache_ttl_seconds: How long to cache the issuer's
            fetched JWKS before refetching.
        mcp_oauth_require_mtls_binding: If True, MCP client tokens must
            carry an RFC 8705 'cnf.x5t#S256' claim and match the
            client certificate forwarded by the reverse proxy in front
            of this server - tokens without cert binding are rejected.
            Off by default (binding is still enforced whenever a token
            happens to carry the claim; this flag only controls
            whether *lacking* it is also a rejection). See
            auth/mtls_binding.py.
        mcp_oauth_mtls_cert_header: HTTP header the reverse proxy uses
            to forward the URL-encoded PEM client certificate it
            validated via mTLS (nginx's $ssl_client_escaped_cert/AWS
            ALB's x-amzn-mtls-clientcert convention).
        otel_service_name: Service name reported in exported spans.
        otel_exporter_otlp_endpoint: Generic OTLP/HTTP backend (Tempo,
            Jaeger, Honeycomb, etc). Unset by default - tracing stays
            entirely off unless this or langfuse_otlp_endpoint is set.
        otel_exporter_otlp_headers: Extra headers for the generic OTLP
            exporter, OTel's standard 'key1=value1,key2=value2' format.
        langfuse_otlp_endpoint: Langfuse's OTLP endpoint. See
            observability/tracing.py for the exact auth scheme.
        langfuse_public_key: Langfuse project public key.
        langfuse_secret_key: Langfuse project secret key.
        otel_capture_dspy_content: Whether DSPy spans capture categorizer
            prompts/completions. Off by default - see field description.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        secrets_dir=_SECRETS_DIR if Path(_SECRETS_DIR).is_dir() else None,
    )

    # Server
    server_name: str = Field(default="openfinance-br-mcp")
    server_version: str = Field(default="0.1.0")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # BCB/Open Finance
    bcb_api_base_url: AnyHttpUrl = Field(
        default=AnyHttpUrl("https://api.banco.com.br/open-banking")
    )
    bcb_directory_url: AnyHttpUrl = Field(
        default=AnyHttpUrl("https://data.directory.openbankingbrasil.org.br")
    )
    bcb_sandbox_directory_url: AnyHttpUrl = Field(
        default=AnyHttpUrl("https://data.sandbox.directory.openbankingbrasil.org.br")
    )
    environment: Literal["mock", "sandbox", "production"] = Field(default="mock")

    # Client credentials (registered with the participating institution)
    client_id: str | None = Field(
        default=None, description="Client ID registered with the institution"
    )
    client_secret: SecretStr | None = Field(
        default=None, description="Corresponding client secret"
    )

    # mTLS (transport/channel-level, per the separate BCB certificate
    # standard - distinct from private_key_jwt client authentication below)
    mtls_cert_path: str = Field(default="certs/client.crt")
    mtls_key_path: str = Field(default="certs/client.key")
    mtls_enabled: bool = Field(default=True)

    # private_key_jwt client authentication (FAPI-BR 2.2.0 requires this
    # for both the token endpoint and PAR - mTLS/client_secret are not
    # accepted alternatives)
    private_key_path: str | None = Field(
        default=None,
        description=(
            "Path to the client's PEM-encoded RSA private key, used to sign "
            "private_key_jwt client assertions and JAR request objects. "
            "Required outside mock mode once the auth flow is exercised."
        ),
    )
    private_key_kid: str | None = Field(
        default=None,
        description="Key ID (kid) matching the client's registered JWKS entry.",
    )
    private_key_jwt_alg: str = Field(
        default="PS256",
        description=(
            "JWS algorithm for private_key_jwt/JAR signing. PS256 is the "
            "common FAPI baseline choice. Verify your registration's "
            "token_endpoint_auth_signing_alg/request_object_signing_alg "
            "before relying on this default in production."
        ),
    )
    id_token_decryption_key_path: str | None = Field(
        default=None,
        description=(
            "Path to a PEM-encoded RSA private key used only to decrypt "
            "the ID token JWE, if it must differ from private_key_path. "
            "Optional - falls back to private_key_path when unset. The "
            "Open Finance Brasil FAPI security profile requires the "
            "client's registered JWKS to expose a key tagged 'use':'enc' "
            "for ID token encryption, distinct in the JWKS from any "
            "'use':'sig' signing key entry - but doesn't forbid the "
            "underlying RSA key material being the same for both. Set "
            "this only if your bank's registration used genuinely "
            "separate key pairs."
        ),
    )

    # Consent
    redirect_uri: AnyHttpUrl = Field(
        default=AnyHttpUrl("https://localhost:8080/callback")
    )
    consent_expiry_hours: int = Field(default=720, ge=1, le=8760)  # 30-day default

    # Shared state backend (TokenStore/ConsentManager)
    redis_url: str | None = Field(
        default=None,
        description=(
            "Redis connection URL (e.g. 'redis://host:6379/0') for sharing "
            "token/consent state across replicas - see "
            "auth/redis_backend.py. Unset by default: TokenStore/"
            "ConsentManager fall back to an in-memory store, correct for "
            "a single-process/mock-mode deployment but NOT safe across "
            "multiple replicas (k8s/deployment.yaml runs replicas: 2)."
        ),
    )

    # DSPy/LLM
    anthropic_api_key: SecretStr | None = Field(default=None)
    dspy_model: str = Field(default="anthropic/claude-haiku-4-5-20251001")
    dspy_cache_enabled: bool = Field(default=True)

    # HTTP (outbound calls to bank APIs)
    http_timeout_seconds: float = Field(default=30.0, gt=0)
    http_max_retries: int = Field(default=3, ge=0, le=10)

    # MCP transport
    mcp_transport: Literal["stdio", "streamable-http"] = Field(default="stdio")
    mcp_http_host: str = Field(default="127.0.0.1")
    mcp_http_port: int = Field(default=8000, ge=1, le=65535)
    mcp_http_stateless: bool = Field(default=True)
    mcp_http_allowed_origins: list[str] = Field(default_factory=list)

    # MCP client OAuth 2.1 (resource-server side - see module docstring
    # of auth/mcp_token_verifier.py for why this is a separate token
    # universe from the FAPI-BR credentials above)
    mcp_oauth_issuer_url: AnyHttpUrl | None = Field(default=None)
    mcp_oauth_resource_server_url: AnyHttpUrl | None = Field(default=None)
    mcp_oauth_required_scopes: list[str] = Field(default_factory=list)
    mcp_oauth_jwks_cache_ttl_seconds: int = Field(default=900, ge=1)

    # RFC 8705 mutual-TLS certificate-bound access tokens for MCP
    # clients - see auth/mtls_binding.py. Requires a reverse proxy in
    # front of the 'streamable-http' transport that terminates mTLS
    # and forwards the client certificate via mcp_oauth_mtls_cert_header.
    mcp_oauth_require_mtls_binding: bool = Field(default=False)
    mcp_oauth_mtls_cert_header: str = Field(default="x-ssl-client-cert")

    # OpenTelemetry tracing (off by default - a TracerProvider is only
    # built when at least one exporter below is configured; see
    # observability/tracing.py)
    otel_service_name: str = Field(default="openfinance-br-mcp")
    otel_exporter_otlp_endpoint: AnyHttpUrl | None = Field(
        default=None,
        description=(
            "Generic OTLP/HTTP backend (Grafana Tempo, Jaeger, Honeycomb, "
            "or any other OTLP-compatible collector) - standard "
            "OpenTelemetry SDK env var name, so this just works if you "
            "already know the OTel conventions."
        ),
    )
    otel_exporter_otlp_headers: str | None = Field(
        default=None,
        description=(
            "Extra headers for the generic OTLP exporter, in OTel's "
            "standard 'key1=value1,key2=value2' format."
        ),
    )
    langfuse_otlp_endpoint: AnyHttpUrl | None = Field(
        default=None,
        description=(
            "Langfuse's OTLP endpoint, e.g. "
            "'https://cloud.langfuse.com/api/public/otel' (EU) or "
            "'https://us.cloud.langfuse.com/api/public/otel' (US), or a "
            "self-hosted instance's '/api/public/otel' path (v3.22.0+). "
            "Confirmed HTTP-only (no gRPC) against Langfuse's own docs."
        ),
    )
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: SecretStr | None = Field(default=None)
    otel_capture_dspy_content: bool = Field(
        default=False,
        description=(
            "Whether DSPy instrumentation captures categorizer prompts/"
            "completions in spans. Off by default: the categorizer's "
            "prompts embed real transaction descriptions, which can carry "
            "PII (merchant names, counterpart info)."
        ),
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validates that the log level is one of the accepted values.

        Args:
            v: Value provided for log_level.

        Returns:
            Normalized upper-case value.

        Raises:
            ValueError: If the provided level is invalid.
        """
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of: {allowed}")
        return upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validates the log output format.

        Args:
            v: Value provided for log_format.

        Returns:
            Normalized lower-case value.

        Raises:
            ValueError: If the provided format is unsupported.
        """
        allowed = {"json", "console"}
        lower = v.lower()
        if lower not in allowed:
            raise ValueError("log_format must be 'json' or 'console'")
        return lower

    @model_validator(mode="after")
    def validate_credentials_required_outside_mock(self) -> Self:
        """Requires client_id/client_secret unless running in mock mode.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If environment is 'sandbox'/'production' but
                client_id or client_secret is missing.
        """
        if self.environment != "mock" and (
            self.client_id is None or self.client_secret is None
        ):
            raise ValueError(
                "client_id and client_secret are required when "
                f"environment='{self.environment}' (only environment='mock' "
                "can run without real credentials)"
            )
        return self

    @model_validator(mode="after")
    def validate_mcp_oauth_pair(self) -> Self:
        """Requires issuer/resource_server_url together, or neither.

        Mirrors FastMCP's own constructor check (raises if auth settings
        are half-configured) - failing fast here, at settings load time,
        gives a clearer error than whatever FastMCP raises later during
        server construction.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If only one of mcp_oauth_issuer_url/
                mcp_oauth_resource_server_url is set.
        """
        has_issuer = self.mcp_oauth_issuer_url is not None
        has_resource = self.mcp_oauth_resource_server_url is not None
        if has_issuer != has_resource:
            raise ValueError(
                "mcp_oauth_issuer_url and mcp_oauth_resource_server_url must "
                "be set together, or both left unset to run the HTTP "
                "transport without MCP client auth"
            )
        return self

    @model_validator(mode="after")
    def validate_langfuse_credentials(self) -> Self:
        """Requires public/secret keys whenever a Langfuse endpoint is set.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If langfuse_otlp_endpoint is set but
                langfuse_public_key/langfuse_secret_key aren't.
        """
        if self.langfuse_otlp_endpoint is not None and (
            self.langfuse_public_key is None or self.langfuse_secret_key is None
        ):
            raise ValueError(
                "langfuse_public_key and langfuse_secret_key are required "
                "when langfuse_otlp_endpoint is set"
            )
        return self


settings = Settings()
