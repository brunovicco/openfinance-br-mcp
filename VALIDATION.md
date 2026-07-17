# Validation

How this project's correctness claims are actually backed, and - just as
important - what has **not** been validated.

## Why this document exists

The official Open Finance Brasil sandbox is not self-service: getting
credentials to run against it requires a registration process this
project's maintainer has not gone through. That single fact shapes almost
every validation decision below - there is no path here to "we ran it
against the real sandbox and it worked."

## What has been validated

- **Unit + integration test suite.** More than 400 tests, ~96% line coverage across
  `src/`, enforced by an 80% CI floor (`pytest --cov-fail-under=80`).
  Coverage is a floor, not a target - the suite is written to exercise
  real failure modes (wrong audience, expired token, mismatched mTLS
  thumbprint, forged signature), not just to hit lines.
- **Real cryptographic round-trips.** Tests that touch JWT/JWS
  verification (`test_mcp_token_verifier.py`, `test_jwt_client_auth.py`,
  etc.) sign real tokens with real keys (via `jwcrypto`) and verify them
  through the actual production verification code path - the crypto
  itself is never mocked, only the HTTP calls around it (via `respx`).
- **Payment safety invariants.** Tests cover exact v5 payment-family
  resolution, signed-response verification, multiple concurrent consents,
  consent/payment payload equality, and single-use reservation under a
  persistent store. These are local contract tests, not bank certification.
- **Mock-environment adapter.** `MockOpenFinanceAdapter` implements the
  same `BankAdapter` protocol every real adapter does, deterministically,
  in-memory. `tests/integration/` exercises full tool-call round trips
  against it, so the MCP-tool-to-adapter contract is validated even
  without network access.
- **Static analysis.** `mypy --strict` on all of `src/`, `ruff` (including
  `S` - flake8-bandit - security lint rules), `black` formatting. All
  three are hard CI gates, not advisory.
- **Spec conformance by direct reading**, not by an official test suite:
  behavior for PAR/JAR, `private_key_jwt`, PKCE, mTLS certificate binding,
  and MCP's resource-server audience binding was implemented and reviewed
  against the RFC text itself (see [SOURCES.md](SOURCES.md)), since no
  independent FAPI-BR conformance suite was available to run against.

## What has NOT been validated

- **No run against the real BCB sandbox or production.** Every
  request/response shape for `sandbox`/`production` environments is
  modeled from the public Open Finance Brasil specification, not
  confirmed against a live institution's actual behavior. Endpoint
  quirks, undocumented field requirements, or spec deviations by a
  specific bank would only surface once someone runs this against a
  real registered client.
- **No independent security audit.** See [SECURITY.md](SECURITY.md) for
  the reporting process if you find something during your own review.
- **No official FAPI 1.0 Advanced / FAPI-BR conformance certification.**
  This project is not a certified FAPI implementation - it aims to
  follow the profile's requirements, but "aims to" is not "certified to."
- **mTLS certificate binding (RFC 8705) assumes a specific proxy
  contract** (the proxy strips/overwrites the forwarded client-cert
  header before this app sees it) that is documented but not itself
  enforced or tested against any specific proxy's real configuration -
  see `docs/en/authorization.md`.

## If you're evaluating this for real use

Start in `mock`, read `docs/en/authorization.md` end to end, and treat
anything past that point (real `CLIENT_ID`/`PRIVATE_KEY_PATH`, real mTLS
certs, a real bank's production endpoint) as something you are
responsible for validating yourself before relying on it with real
financial data.
