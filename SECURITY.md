# Security Policy

## Scope and disclaimer

`openfinance-br-mcp` is an independent, community project. It is **not**
affiliated with, endorsed by, or officially certified by the Banco
Central do Brasil (BCB) or the Open Finance Brasil program. It has
**not** undergone an independent FAPI conformance certification or a
third-party security audit. Review the code yourself, and evaluate it
against your own risk tolerance, before pointing it at real credentials
or real bank data.

The default `ENVIRONMENT=mock` runs entirely in-memory with no real
credentials, no network calls, and no mTLS certificates - this is the
safe way to explore the project. `sandbox`/`production` environments
require real `CLIENT_ID`/`CLIENT_SECRET`/mTLS material issued by a
participating institution; treat those exactly as you would any other
production banking credential.

## Supported versions

This project is pre-1.0 (currently `0.1.x`). There is no LTS branch -
security fixes land on `master` and the latest tagged release only.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for a suspected security
vulnerability.

Use GitHub's private vulnerability reporting instead: go to the
[Security tab](https://github.com/brunovicco/openfinance-br-mcp/security)
of this repository and click **"Report a vulnerability"**. This opens a
private draft advisory visible only to the maintainer, so the issue isn't
disclosed publicly before a fix is available.

Please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce (a minimal repro is ideal).
- Whether it affects the `mock` environment, the `sandbox`/`production`
  code paths, or both.

We aim to acknowledge reports within a few days. Coordinated disclosure
is appreciated - please allow time for a fix before any public writeup.

## Security-relevant design notes

If you're auditing this codebase, the two most load-bearing security
boundaries are:

- **Token universe separation** - MCP client tokens (whoever calls this
  server) and FAPI-BR bank tokens (this server calling a bank) are kept
  structurally separate and can never cross. See
  [docs/en/authorization.md](docs/en/authorization.md).
- **mTLS certificate binding (RFC 8705)** - optional, for MCP client
  tokens, enforced against a proxy-forwarded client certificate. The
  trust boundary (the reverse proxy must strip/overwrite the forwarded
  client-cert header) is documented in the same file - misconfiguring
  that proxy defeats the binding entirely.
