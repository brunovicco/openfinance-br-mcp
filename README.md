**English** · [Português](README.pt-BR.md)

<!-- mcp-name: io.github.brunovicco/openfinance-br-mcp -->

# openfinance-br-mcp

> Experimental MCP server for **Open Finance Brasil**, with a complete mock
> environment and evolving FAPI-BR integration. It is not certified or
> validated against real institutions; see [VALIDATION.md](VALIDATION.md)
> before using it outside `environment=mock`.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![uv](https://img.shields.io/badge/managed%20by-uv-blueviolet)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/lint-ruff-orange.svg)](https://github.com/astral-sh/ruff)

---

## What it is

An **MCP Server** that abstracts away the complexity of Open Finance Brasil (FAPI 1.0 Advanced, OAuth2, consent, mTLS) and exposes simple tools to Claude:

```
Claude → "how much did I spend on food in March?"
Claude uses list_transactions(bank=nubank, categorize=true, date_from=2024-03-01)
Claude → "You spent R$ 847.30 on food in March..."
```

## Supported banks

The mock environment simulates Nubank, Sicoob, Caixa, Banco do Brasil,
Bradesco, Itaú, Santander, XP, PicPay, and BTG Pactual with in-memory data and
no network access. These are simulations, not certified integrations.

Real adapters and the Payments API journey are experimental and unvalidated.
Payments use dedicated consent, PAR/JAR, JWS, and persistent idempotency.
`list_pix_keys` is a demonstration extension rather than a standardized Open
Finance Brasil endpoint. See [VALIDATION.md](VALIDATION.md) for the exact scope.

## Available MCP tools

The server exposes 18 tools grouped by journey:

- **Accounts:** `list_accounts`, `get_balance`, `list_transactions`
- **Cards:** `list_credit_cards`, `get_credit_card_bills`
- **Investments:** `list_investments`, `list_funds`,
  `list_variable_incomes`, `list_treasure_titles`
- **PIX:** `list_pix_keys`, `initiate_pix`
- **Data consent:** `start_consent`, `complete_consent`,
  `check_consent_status`, `revoke_consent`
- **Payment consent:** `start_payment_consent`, `complete_payment_consent`,
  `check_payment_consent_status`

It also exposes the `openfinance://banks/` resource, the
`analyze_monthly_spending` prompt, and optional URL elicitation when starting
an authorization flow.

## Quick start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed

```bash
# Clone the repository
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp

# Optional: needed only for sandbox/production or DSPy categorization
cp .env.example .env

# Install dependencies
uv sync

# Run the server
uv run openfinance-mcp
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openfinance-br": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/openfinance-br-mcp", "openfinance-mcp"]
    }
  }
}
```

## Development

```bash
# Install with dev-dependencies
uv sync

# Run the tests
uv run pytest tests/ -v

# Lint and formatting
uv run ruff check src/ tests/
uv run black src/ tests/

# Type check
uv run mypy src/
```

## Containers and Kubernetes

```bash
docker compose up openfinance-mcp
docker compose --profile test up
```

The `k8s/` directory contains a two-replica Streamable HTTP example with
Redis-backed state. Replace every credential, signing-key, OAuth issuer,
resource-server, and domain placeholder before applying it. The server fails
closed when HTTP is exposed outside loopback without MCP client OAuth.

## Architecture

```
Claude (MCP Client)
        │ stdio or streamable-http
        ▼
openfinance-br-mcp (MCP Server)
  ├── Auth + Consent  (FAPI-BR 2.2.0: private_key_jwt, PAR/JAR, PKCE, mTLS)
  ├── MCP Primitives  (18 tools + 1 resource + 1 prompt)
  │   ├── Pydantic v2 input/output schemas
  │   └── Optional URL elicitation for bank authorization
  │   └── Categorizer (DSPy + Claude for transaction classification)
  ├── Bank Adapters   (10 banks - extensible)
  └── Directory Client (resolves real bank endpoints from the BCB
                         Directory of Participants)
        │ HTTPS/mTLS
        ▼
Open Finance BR (BCB) - Directory of Participants
        │
        ▼
  Nubank · Sicoob · Caixa · + 100 participating institutions
```

## Environment variables

| Variable | Required | Description |
|----------|-------------|-----------|
| `ENVIRONMENT` | ❌ | `mock` (default, no credentials needed), `sandbox`, or `production` |
| `CLIENT_ID` | ⚠️ non-mock | Client ID registered with the institution |
| `CLIENT_SECRET` | ⚠️ non-mock | Client secret |
| `PRIVATE_KEY_PATH` | ⚠️ non-mock | RSA private key for `private_key_jwt`/JAR signing |
| `MTLS_CERT_PATH` | ⚠️ prod | Path to the mTLS certificate |
| `MTLS_KEY_PATH` | ⚠️ prod | mTLS private key |
| `ANTHROPIC_API_KEY` | ⚠️ DSPy | Required for `categorize=true` |
| `REDIS_URL` | ❌ | Shares TokenStore/ConsentManager state across replicas |
| `MCP_TRANSPORT` | ❌ | `stdio` (default) or `streamable-http` |
| `LANGFUSE_OTLP_ENDPOINT` | ❌ | Enables tracing to Langfuse (with `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`) |
| `LOG_LEVEL` | ❌ | INFO, DEBUG, WARNING (default: INFO) |
| `LOG_FORMAT` | ❌ | json or console (default: json) |

See `.env.example` for the full list.

## Documentation

- [docs/en/authorization.md](docs/en/authorization.md) - the two token universes (MCP client auth vs. FAPI-BR bank auth), and why they can never cross
- [CONTRIBUTING.md](CONTRIBUTING.md) - dev setup, CI checks, adding a bank adapter
- [SECURITY.md](SECURITY.md) - scope, disclaimer, and how to report a vulnerability
- [SOURCES.md](SOURCES.md) - specs and RFCs this implementation follows
- [VALIDATION.md](VALIDATION.md) - what's actually been validated, and what hasn't (no real BCB sandbox run)
- [CHANGELOG.md](CHANGELOG.md) - release history

## License

MIT
