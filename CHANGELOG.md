# Changelog

Notable project changes are documented here following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-07-17

Real-bank interoperability remains experimental and unvalidated. See
[VALIDATION.md](VALIDATION.md) for the current validation boundary.

### Added

- Dedicated payment-consent tools with PAR/JAR, PKCE, ID-token validation,
  signed JWS payloads, and persistent PIX idempotency.
- Generated OpenAPI clients for read APIs and new tools for funds, variable
  income, and Treasury securities, bringing the server to 18 tools.
- MCP resource `openfinance://banks/`, prompt `analyze_monthly_spending`, and
  optional URL elicitation for authorization flows.
- MCP-principal-to-subject binding for authenticated Streamable HTTP clients.
- Redis-backed state for tokens, consent, authorization sessions, and
  idempotency across replicas.
- Automated, OIDC-based release workflow for PyPI, the MCP Registry, and
  GitHub Releases, with pinned Actions and artifact smoke tests.

### Changed

- Read operations now use generated typed clients and API-family-specific
  endpoints resolved through the Directory of Participants.
- `initiate_pix` can run outside mock mode after a dedicated authorized payment
  consent and uses a payment-specific access token.
- Docker Compose defaults to credential-free mock mode. Kubernetes examples
  include the OAuth, signing-key, Redis, and writable-cache configuration
  required by the sample deployment.
- README and validation documentation now distinguish simulated institutions
  from experimental real adapters and summarize the available MCP primitives.

### Fixed

- Isolated tokens and consent by bank, subject, purpose, and requested scopes
  to prevent cross-bank or cross-journey reuse.
- Added required FAPI interaction headers and strengthened PAR/JAR, PKCE,
  audience, ACR, and ID-token validation.
- Corrected payment consent to use the separate `payments-consents` and
  `payments-pix` Directory families and their exact Payments API v5 endpoints.
- Verified payment response JWS before trusting bank data and bound each PIX
  request to the exact, single-use consent payload and token namespace.
- Corrected credit-card paths, monetary-value parsing, transaction fields, and
  payment-type enum values using the official schemas.
- Made Directory resolution fail closed by default and resolved endpoints per
  API family instead of reusing the Accounts base URL.
- Corrected MCP contracts for consent scope validation, idempotency metadata,
  and payment-only consent onboarding.
- Required MCP OAuth and an Origin allowlist when Streamable HTTP is exposed
  outside loopback, and bind financial subjects to the token's `iss` + `sub`.

## [0.1.0] - 2026-07-13

### Added

- MCP server with `stdio` and Streamable HTTP transports and 12 initial tools
  for accounts, cards, PIX, investments, and consent.
- FAPI-BR authorization foundations: PAR/JAR, PKCE, `private_key_jwt`, ID-token
  validation, mTLS, and OAuth token exchange.
- Extensible bank-adapter architecture, Directory client, and mock environment
  for ten simulated institutions.
- Optional DSPy transaction categorization, OpenTelemetry tracing, structured
  logging, Docker, Kubernetes, Redis, and CI configuration.

[Unreleased]: https://github.com/brunovicco/openfinance-br-mcp/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/brunovicco/openfinance-br-mcp/releases/tag/v0.2.0
[0.1.0]: https://pypi.org/project/openfinance-br-mcp/0.1.0/
