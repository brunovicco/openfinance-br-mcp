**English** · [Português](../pt/authorization.md)

# Authorization: two separate token universes

This server handles two entirely independent authorization flows. They
are never allowed to cross, and the code is structured so that crossing
them is not just discouraged but architecturally impossible.

## 1. MCP client authorization (resource-server side)

Who this is for: whatever is calling this MCP server over the
`streamable-http` transport (Claude Desktop, an orchestration agent, a
custom client).

This server does not run its own OAuth Authorization Server. It only
*verifies* access tokens issued by an external OAuth2/OIDC identity
provider, following the "AS/RS separation" pattern the MCP Python SDK
(`mcp.server.auth`) recommends over its older all-in-one
`OAuthAuthorizationServerProvider`.

- Implementation: [`auth/mcp_token_verifier.py`](../../src/openfinance_br_mcp/auth/mcp_token_verifier.py)
  (`JWTTokenVerifier`), wired into `FastMCP` in
  [`server.py`](../../src/openfinance_br_mcp/server.py)'s `_build_mcp_auth()`.
- Verifies: JWS signature (via the issuer's JWKS, fetched through
  standard OIDC discovery), `iss`, `aud` (must equal this server's own
  `MCP_OAUTH_RESOURCE_SERVER_URL` - RFC 8707 audience binding), and
  `exp`.
- Exposes RFC 9728 Protected Resource Metadata automatically (the MCP
  SDK builds this route once `resource_server_url` is configured) at
  `/.well-known/oauth-protected-resource`.
- Unauthenticated or invalid-token requests get a `401` with a
  `WWW-Authenticate: Bearer ...` header pointing at that metadata
  endpoint - also handled entirely by the SDK
  (`mcp.server.auth.middleware.bearer_auth`).

### Configuration

Auth is **off by default**. With `MCP_OAUTH_ISSUER_URL` unset, the HTTP
transport serves without any client authentication - acceptable only
because the default bind host is loopback
(`MCP_HTTP_HOST=127.0.0.1`), which the MCP authorization spec permits
for local/dev use. Set both of the following together to turn auth on:

```bash
MCP_OAUTH_ISSUER_URL=https://your-idp.example.com
MCP_OAUTH_RESOURCE_SERVER_URL=https://your-mcp-server.example.com
MCP_OAUTH_REQUIRED_SCOPES=accounts:read,pix:write   # optional
```

`config.py`'s `validate_mcp_oauth_pair` rejects half-configured setups
(one of the two URLs set without the other) at settings-load time.

### Optional: RFC 8705 mutual-TLS certificate-bound tokens

A stolen bearer token can be replayed from anywhere. RFC 8705 closes
that gap by binding the token to the TLS client certificate presented
when it was issued: the IdP puts a `cnf.x5t#S256` claim (base64url
SHA-256 thumbprint of the client cert's DER encoding) in the token, and
this server must reject it unless the *same* certificate authenticates
the current connection.

- Implementation: [`auth/mtls_binding.py`](../../src/openfinance_br_mcp/auth/mtls_binding.py)
  (`MTLSClientCertMiddleware`, `compute_cert_thumbprint`), enforced in
  `JWTTokenVerifier._check_mtls_binding` (`mcp_token_verifier.py`).
- This server does not terminate mTLS itself for `streamable-http` - it
  expects a reverse proxy/gateway (nginx, Envoy, a cloud load balancer)
  in front of it that validates the client certificate against a
  trusted CA and forwards the PEM certificate via an HTTP header
  (nginx's `$ssl_client_escaped_cert` / AWS ALB's
  `x-amzn-mtls-clientcert` convention: URL-encoded PEM). **That proxy
  must strip or overwrite any client-supplied copy of this header** -
  if a client can set it directly, the binding check is worthless.
- `_run_streamable_http()` in `server.py` wires `MTLSClientCertMiddleware`
  ahead of the SDK's `AuthenticationMiddleware` whenever MCP client
  OAuth is configured, since `TokenVerifier.verify_token(token: str)`
  (the SDK's own protocol) never receives the connection - a
  contextvar is the only channel to get the forwarded certificate from
  ASGI middleware into the verifier.
- Binding is enforced automatically whenever a verified token happens
  to carry a `cnf` claim. To also *reject* tokens that omit `cnf`
  entirely (closing the downgrade path where an attacker just requests
  or replays a non-bound token), set:

```bash
MCP_OAUTH_REQUIRE_MTLS_BINDING=true
MCP_OAUTH_MTLS_CERT_HEADER=x-ssl-client-cert   # matches your proxy's header name
```

## 2. FAPI-BR bank authorization (client-of-the-bank side)

Who this is for: this server itself, acting as a registered Open
Finance Brasil client authenticating to each participating bank's
authorization server, on behalf of a user who has gone through the
consent flow.

- Implementation: `auth/jwt_client_auth.py` (`private_key_jwt`,
  RFC 7523), `auth/par.py` (PAR/JAR), `auth/token_exchange.py`
  (client_credentials and authorization_code grants),
  `auth/id_token.py` (ID token decryption/verification),
  `auth/token.py` (`TokenStore`) and `tools/consent.py` (the
  `start_consent`/`complete_consent`/`check_consent_status`/
  `revoke_consent` MCP tools that drive this flow end-to-end).
- Tokens obtained this way live exclusively in
  `AppContext.token_store` (an in-memory `TokenStore`, keyed by
  `subject_id`), and are used exclusively by bank adapters
  (`adapters/default_adapter.py::_get_token`) when calling a specific
  bank's Open Finance API.

## Why passthrough is structurally impossible here

- **Different HTTP clients.** `JWTTokenVerifier` (MCP client auth) is
  constructed with its own `httpx.AsyncClient` in `server.py`,
  entirely separate from `AppContext.http_client` (bank calls, built
  in `context.py`'s `app_lifespan`). Neither module imports the other.
- **Different token stores.** An MCP client's verified identity lives
  in Starlette's request scope (`scope["user"]`/`scope["auth"]`, an
  `AccessToken` from `mcp.server.auth.provider`) for the duration of
  one HTTP request. A bank token lives in `TokenStore`, keyed by
  `subject_id`, persisting across requests. Tool functions
  (`tools/*.py`) never read the incoming Starlette request at all -
  they only receive `AppContext` via `ctx.request_context.lifespan_context`,
  which has no path back to request headers.
- **Audience binding makes a mistake self-correcting.** Even if some
  future code accidentally tried to send an MCP client token to a
  bank, `JWTTokenVerifier`'s issuer/audience checks mean that token was
  never issued for that bank's audience - the bank's own token
  validation would reject it.
- **Regression-tested.** See
  `tests/unit/test_bank_adapters.py::test_bank_http_calls_never_use_an_mcp_client_token`:
  seeds `TokenStore` with a distinctive FAPI-BR token and a separate,
  never-stored "MCP client token" value, then asserts only the former
  ever appears in an outgoing bank request's `Authorization` header.
