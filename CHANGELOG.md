**English** · [Português](CHANGELOG.pt-BR.md)

# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

Security and correctness fixes from an internal engineering review (see
`IMPLEMENTATION_PLAN.md` for the full phased plan and rationale behind each
item). Phase P0 (immediate risk blockers), part of P1 (per-family Directory
resolution), and P2 (the Payments API v5 journey) are included here; sandbox
validation (P3) is tracked separately.

### Fixed

- **Cross-bank token/consent collision**: `TokenStore` and `ConsentManager`
  now key state by `(bank_id, subject_id)` instead of `subject_id` alone -
  previously, authorizing a second bank for the same subject (e.g. CPF)
  could overwrite the first bank's token, and a refresh could be attempted
  against the wrong bank's token endpoint.
- **Consent reuse across banks/scopes**: `ConsentManager.create()` no longer
  reuses a cached `AWAITING_AUTHORISATION`/`AUTHORISED` consent unless its
  stored scopes are a superset of what's newly requested, and reuse is now
  scoped per bank.
- **`x-fapi-interaction-id`** is now sent on every protected-resource call
  (`adapters/base.py::build_fapi_headers`), as required by the FAPI-BR
  security profile.
- **`response_mode=fragment`** and an essential `acr` ID-token claim are now
  included in the PAR/JAR request object (`auth/par.py`); the ID token is
  mandatory in `complete_consent` (previously optional) and its `acr` claim
  is now verified (`auth/id_token.py`).
- **Consent permission mapping**: `accounts` no longer implicitly grants
  `transactions`/`overdraft_limits`/`balances` permissions; each is now a
  distinct, explicitly-requested scope. PIX/payments removed from the
  data-sharing consent's scope map entirely - payment initiation now
  requires its own dedicated payment consent (see the P2 items below).
- **Credit card path**: corrected `/credit-cards/v2/...` to the officially
  published `/credit-cards-accounts/v2/...`.
- **Directory resolution failures are fail-closed by default**
  (`directory_fallback_mode=fail_closed`): a bank whose endpoint can't be
  resolved via the Directory of Participants is now excluded from
  `app.adapters` rather than silently falling back to a hardcoded URL.
  Opt-in `hardcoded_fallback` mode preserves the old behavior for local dev.
- **Per-API-family endpoint resolution**: real adapters now resolve
  `credit-cards-accounts`, `payments`, and `bank-fixed-incomes` endpoints
  independently via the Directory instead of reusing the `accounts` family's
  base URL for every resource type (`DefaultOpenFinanceAdapter.set_family_base_urls`).

### Added

- **MCP-principal-to-subject_id binding** (`auth/principal_binding.py`,
  `tools/principal_guard.py`): over `streamable-http` with MCP client OAuth
  configured, every tool taking `subject_id` now verifies the authenticated
  caller was previously bound to that subject via a completed consent flow.
  A no-op on `stdio` or when MCP client OAuth isn't configured.
- **OAuth required outside loopback**: server startup now fails if
  `mcp_transport=streamable-http` is bound to a non-loopback host without
  MCP client OAuth configured.
- `list_pix_keys` is now explicitly restricted to `environment=mock` (this
  path isn't published in the official Accounts API family and is
  demonstrative only). `initiate_pix` was also mock-only in this same
  commit; see the P2 items below for how that restriction was lifted.
- **Dedicated payment consent** (`auth/payment_consent.py`,
  `tools/payments.py`): the Payments API has its own consent resource,
  entirely separate from the data-sharing consent - a payment consent
  authorizes exactly one specific payment (amount, creditor, date) and is
  never scope-reused across payments. New tools `start_payment_consent`,
  `complete_payment_consent`, and `check_payment_consent_status` drive this
  flow (PAR/JAR + ID token verification, mirroring `tools/consent.py`).
- **JWS message signing for payments** (`auth/payment_jws.py`):
  `initiate_pix` now signs its request body as a compact JWS with the
  client's own key before sending it, per the FAPI-BR message signing
  profile the Payments API requires on top of the bearer token and mTLS
  channel. Verifying the bank's signed response is implemented
  (`verify_payment_response`) but not yet wired into the adapter - tracked
  for P3.
- **Persistent, cross-replica PIX idempotency** (`auth/idempotency_store.py`):
  replaces the previous in-process `pix_idempotency_cache` dict, which
  never survived a restart and wasn't shared across Kubernetes replicas.
  Also fixes a correctness gap: a replay with an *identical* payload under
  a previously-used `idempotency_key` still returns the cached response,
  but a replay with a *different* payload under the same key now correctly
  raises a conflict error instead of silently returning the wrong cached
  result.

### Changed

- `initiate_pix` is no longer restricted to `environment=mock`. Outside
  mock mode it now requires an `AUTHORISED` payment consent for the
  subject/bank (obtained via `start_payment_consent`/
  `complete_payment_consent`) before it will call the bank, uses a
  `purpose='payment'` access token that's kept strictly separate from the
  data-sharing token (`auth/token.py`'s cache key gained a `purpose`
  dimension for this), and marks the payment consent consumed after a
  successful payment.
- README/README.pt-BR repositioned: the "10 banks, Fases 2/3/4" claim is
  replaced with an explicit mock-vs-real-integration distinction per bank.

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
