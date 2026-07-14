**English** · [Português](CHANGELOG.pt-BR.md)

# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-07-13

Initial public release.

### Added

- MCP server (`stdio` and `streamable-http` transports) exposing 12 tools
  covering Open Finance Brasil Fases 2, 3, and 4: `list_accounts`,
  `get_balance`, `list_transactions`, `list_credit_cards`,
  `get_credit_card_bills`, `list_pix_keys`, `initiate_pix`,
  `list_investments`, `start_consent`, `complete_consent`,
  `check_consent_status`, `revoke_consent`.
- FAPI-BR 2.2.0 authorization flow: PAR/JAR, `private_key_jwt` client
  authentication (RFC 7523), PKCE, ID token decryption/verification,
  authorization_code and client_credentials token exchange.
- `BankAdapter` abstraction with a `DefaultOpenFinanceAdapter` base and
  concrete adapters for 10 institutions (Nubank, Sicoob, Caixa Econômica,
  Banco do Brasil, Bradesco, Itaú Unibanco, Santander, XP, PicPay, BTG
  Pactual), resolved via a `DirectoryClient` against the BCB Directory of
  Participants.
- `MockOpenFinanceAdapter`-backed `mock` environment (default) for a
  credential-free, network-free development loop, since the official BCB
  sandbox is not self-service.
- DSPy + Claude-based transaction categorization (`categorize=true` on
  `list_transactions`).
- MCP client OAuth 2.1 resource-server authentication
  (`JWTTokenVerifier`), audience-bound per RFC 8707, with RFC 9728
  Protected Resource Metadata.
- Optional RFC 8705 mutual-TLS certificate-bound access tokens for MCP
  clients (`MTLSClientCertMiddleware`), for deployments behind a
  proxy/gateway that terminates mTLS.
- Redis-backed `TokenStore`/`ConsentManager` option for horizontal scaling
  across replicas; in-memory by default.
- OpenTelemetry tracing (generic OTLP and Langfuse exporters), structured
  JSON/console logging via structlog.
- Docker, Docker Compose, and Kubernetes manifests for deployment.
- CI pipeline: `black`, `ruff`, `mypy --strict` (on `src/`), and `pytest`
  with an 80% coverage gate.

[0.1.0]: https://github.com/brunovicco/openfinance-br-mcp/releases/tag/v0.1.0
