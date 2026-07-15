# Sources

The specifications and references this implementation follows. This is
not an exhaustive citation of every RFC read while building the project -
it's a map from "what the code does" to "what it's supposed to conform
to," useful when auditing a specific piece of behavior.

## Open Finance Brasil / BCB

- **Open Finance Brasil** - the regulatory program itself, run under
  Banco Central do Brasil (BCB) oversight. This project targets its
  Fases 2 (data), 3 (payment initiation / PIX), and 4 (investments) API
  surfaces.
- **Directory of Participants** - the registry this project's
  `DirectoryClient` (`src/openfinance_br_mcp/directory/client.py`)
  queries to resolve a bank's real endpoints and ISPB:
  - Production: `https://data.directory.openbankingbrasil.org.br`
  - Sandbox: `https://data.sandbox.directory.openbankingbrasil.org.br`
    (lists a smaller, different set of organizations than production -
    see `config.py`'s field docs).
- **FAPI-BR security profile** - the Brazilian adaptation of the Financial
  -grade API (FAPI) 1.0 Advanced profile, mandating `private_key_jwt`
  client authentication, PAR, JAR, PKCE, and mTLS or the alternative
  DPoP/cert-bound-token mechanisms this project implements.

## IETF RFCs implemented

| RFC | Title | Where |
|-----|-------|-------|
| [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749) | The OAuth 2.0 Authorization Framework | `auth/token_exchange.py` |
| [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523) | JWT Profile for OAuth 2.0 Client Authentication (`private_key_jwt`) | `auth/jwt_client_auth.py` |
| [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636) | Proof Key for Code Exchange (PKCE) | `auth/pkce.py` |
| [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705) | Mutual-TLS Client Authentication and Certificate-Bound Access Tokens | `auth/mtls_binding.py` |
| [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707) | Resource Indicators for OAuth 2.0 | `auth/mcp_token_verifier.py` (audience binding) |
| [RFC 9101](https://www.rfc-editor.org/rfc/rfc9101) | JWT-Secured Authorization Request (JAR) | `auth/par.py` |
| [RFC 9126](https://www.rfc-editor.org/rfc/rfc9126) | OAuth 2.0 Pushed Authorization Requests (PAR) | `auth/par.py` |
| [RFC 9728](https://www.rfc-editor.org/rfc/rfc9728) | OAuth 2.0 Protected Resource Metadata | exposed automatically by the MCP SDK once `resource_server_url` is configured |

## Model Context Protocol

- **[MCP specification](https://modelcontextprotocol.io)** - the protocol
  this server implements to expose tools to Claude and other MCP
  clients, including its authorization spec (the "AS/RS separation"
  pattern, and the explicit prohibition on token passthrough this
  project's architecture is built around).
- **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)**
  (`mcp` package) - `FastMCP`, `mcp.server.auth.*`, `TokenVerifier`
  protocol.

## Other libraries doing the cryptographic heavy lifting

- **[jwcrypto](https://jwcrypto.readthedocs.io/)** - JWS/JWE/JWT signing
  and verification.
- **[cryptography](https://cryptography.io/)** - X.509 certificate
  parsing (mTLS thumbprinting), RSA key handling.
- **[DSPy](https://dspy.ai/)** - transaction categorization, framed as an
  LLM classification module.
