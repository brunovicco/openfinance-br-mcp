feat: implement Payments API v5 journey (P2) - dedicated consent, JWS signing, persistent idempotency

Implements phase P2 from IMPLEMENTATION_PLAN.md: the full Payments API
journey initiate_pix previously bypassed by reusing the data-sharing
consent's token against /payments/v4/pix/payments directly.

New modules:

- auth/idempotency_store.py: persistent, cross-replica IdempotencyStore
  for initiate_pix, replacing the old in-process
  AppContext.pix_idempotency_cache dict (never survived a restart, not
  shared across Kubernetes replicas). Enforces the correct Open
  Finance Brasil contract: a replay with an *identical* payload under
  a previously-used idempotency_key returns the cached response, but a
  replay with a *different* payload under the same key now raises
  IdempotencyConflictError instead of silently returning the wrong
  cached result - the old dict-based cache could not tell these two
  cases apart.
- auth/payment_jws.py: signs outgoing payment request bodies as a
  compact JWS (sign_payment_payload) and verifies signed bank
  responses (verify_payment_response), per the FAPI-BR message signing
  profile the Payments API requires on top of the bearer token and
  mTLS channel. Response verification is wired as a standalone,
  reusable function but not yet called from default_adapter.py (no
  DirectoryClient reference available at that layer to fetch the
  bank's JWKS) - tracked as a P3 follow-up.
- auth/payment_consent.py: PaymentConsentManager, a dedicated
  lifecycle for the Payments API's own consent resource, entirely
  separate from the data-sharing ConsentManager. A payment consent
  authorizes exactly one specific payment (amount, creditor, date) and
  is never scope-reused the way a data consent can be; tracks
  AWAITING_AUTHORISATION / AUTHORISED / REJECTED / CONSUMED.
- tools/payments.py: start_payment_consent, complete_payment_consent,
  check_payment_consent_status - mirrors tools/consent.py's PAR/JAR +
  ID token verification orchestration against the payment consent
  resource instead of the data consent one.

Changed:

- auth/token.py: TokenStore's composite cache key extended with a
  keyword-only purpose parameter ('data' default, or 'payment'). A
  subject can now hold two independent tokens at the same bank
  simultaneously - one bound to the data-sharing consent, one bound to
  a payment consent - without one silently clobbering the other.
  Backward compatible: every existing call site is unaffected since
  purpose defaults to 'data'.
- adapters/base.py: _get_token accepts the same purpose parameter and
  passes it through to TokenStore.
- adapters/default_adapter.py: initiate_pix now fetches a
  purpose='payment' token (never the data-sharing one) and signs the
  request body via sign_payment_payload() before sending it, with
  Content-Type: application/jwt. Documented as a best-effort choice
  (embedded JWS in the body) pending confirmation against each bank's
  actual registration - some may expect the signature as a header
  alongside plain JSON instead (see the module's docstring).
- tools/pix.py: initiate_pix is no longer restricted to
  environment='mock' (lifting part of the P0.9 stopgap for this tool
  specifically; list_pix_keys remains mock-only). Outside mock mode it
  now requires an AUTHORISED payment consent for the subject/bank
  (checked via PaymentConsentManager.get_status), uses the new
  IdempotencyStore instead of the old in-process dict, and marks the
  consent CONSUMED after a successful payment.
- context.py: AppContext gains payment_consent_manager and
  idempotency_store fields, both built in app_lifespan and shared via
  the same pluggable KeyValueStore as TokenStore/ConsentManager (Redis
  in production). pix_idempotency_cache is kept as a deprecated,
  unused field so any external code still reading it doesn't break
  outright.
- server.py: registers the three new payment consent tools.

Tests:

- new: test_idempotency_store.py, test_payment_jws.py,
  test_payment_consent.py, test_tools_payments.py.
- test_tools_pix.py rewritten: mock-mode tests unchanged in spirit but
  updated for the new idempotency contract (identical replay vs.
  conflicting-payload replay are now two distinct tests instead of
  one that asserted the old, looser behavior); added a new test class
  covering the real-mode payment-consent gate (missing token, wrong
  status, success + mark_consumed).
- test_bank_adapters.py: token_store fixture now seeds a
  purpose='payment' token per bank; added a dedicated test asserting
  initiate_pix sends a JWS-signed body with the payment-purpose bearer
  token and the idempotency header.
- test_tool_dispatch.py (integration): tools/list assertion includes
  the 3 new tools; the old idempotency-replay test (which reused a key
  across two *different* payloads and expected the cache to win) is
  replaced with two tests matching the stricter contract; the
  mock-only rejection test is renamed/re-documented to reflect that
  initiate_pix is no longer blanket-disabled outside mock, it now
  requires a payment consent.
- test_tools_accounts.py, test_tools_credit_cards.py,
  test_tools_investments.py, test_transactions.py, test_tools_consent.py:
  AppContext construction updated for the two new required fields.

Docs:

- CHANGELOG.md/CHANGELOG.pt-BR.md: [Unreleased] intro updated to note P2
  is now included (only P3 remains tracked separately); added Added/
  Changed entries for the dedicated payment consent, JWS signing, and
  persistent idempotency; narrowed the existing mock-only bullet to
  list_pix_keys only, since initiate_pix's restriction was lifted.

Not included in this change (tracked in IMPLEMENTATION_PLAN.md): P1.1
(OpenAPI-generated clients), payment response JWS verification
(payment_jws.verify_payment_response exists but isn't called yet - no
DirectoryClient reference in the adapter to fetch JWKS), P3 (sandbox
validation, SSA/DCR, independent security review).
