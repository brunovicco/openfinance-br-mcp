**English** · [Português](README.pt-BR.md)

<!-- mcp-name: io.github.brunovicco/openfinance-br-mcp -->

# openfinance-br-mcp

> Experimental MCP server for **Open Finance Brasil**, with a complete mock environment and an evolving implementation toward FAPI-BR integration. Not certified, and not yet validated against real institutions - see [VALIDATION.md](VALIDATION.md) and the implementation plan in `IMPLEMENTATION_PLAN.md` before relying on this outside `environment=mock`.

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

Mock adapters are implemented for the ten institutions below - each returns realistic, in-memory sample data with zero credentials or network access, and is the primary way to explore this project today. Real (non-mock) support is experimental: it has not been exercised against any bank's actual sandbox or production environment, is not FAPI-BR certified, and several endpoints/paths are still being brought in line with the official OpenAPI specs (tracked in `IMPLEMENTATION_PLAN.md`).

| Bank | ISPB | Mock adapter | Real integration |
|-------|------|:---:|:---:|
| Nubank | 18236120 | ✅ | experimental, unvalidated |
| Sicoob | 04891850 | ✅ | experimental, unvalidated |
| Caixa Econômica | 00360305 | ✅ | experimental, unvalidated |
| Banco do Brasil | 00000000 | ✅ | experimental, unvalidated |
| Bradesco | 60746948 | ✅ | experimental, unvalidated |
| Itaú Unibanco | 60701190 | ✅ | experimental, unvalidated |
| Santander | 90400888 | ✅ | experimental, unvalidated |
| XP | 33264668 | ✅ | experimental, unvalidated |
| PicPay | 22896431 | ✅ | experimental, unvalidated |
| BTG Pactual | 30306294 | ✅ | experimental, unvalidated |

The Payments API journey is implemented experimentally: dedicated consent, PAR/JAR, JWS, and persistent idempotency. Outside `environment=mock`, `initiate_pix` requires `start_payment_consent` and `complete_payment_consent` to produce an `AUTHORISED` consent. This integration has not yet been validated against a live institution. `list_pix_keys` is not part of the standardized Open Finance Brasil API and should be treated as an adapter-specific demonstration extension.

> New banks: implement `BankAdapter` (or subclass `DefaultOpenFinanceAdapter`) and register it - see "Adding a new bank" below.

## Available MCP tools

| Tool | Description | Fase |
|------|-----------|------|
| `list_accounts` | Lists checking, savings, and prepaid accounts | 2 |
| `get_balance` | Available, blocked, and invested balance | 2 |
| `list_transactions` | Statement with filters and DSPy categorization | 2 |
| `list_credit_cards` | Credit cards and limits | 2 |
| `get_credit_card_bills` | Open and past bills | 2 |
| `list_pix_keys` | Demonstration extension for registered PIX keys | 2 |
| `initiate_pix` | Idempotent PIX payment; dedicated consent outside mock | 3 |
| `list_investments` | Fixed income (CDB, LCI, LCA) | 4 |
| `list_funds` | Investment funds | 4 |
| `list_variable_incomes` | Variable-income investments | 4 |
| `list_treasure_titles` | Treasury securities | 4 |
| `start_consent` | Starts the FAPI-BR consent/authorization flow | - |
| `complete_consent` | Completes consent after the user authorizes at the bank | - |
| `check_consent_status` | Checks the status of an existing consent | - |
| `revoke_consent` | Revokes an existing consent | - |
| `start_payment_consent` | Starts consent for a specific PIX payment | - |
| `complete_payment_consent` | Completes payment authorization | - |
| `check_payment_consent_status` | Checks payment-consent status | - |

Alongside the 18 tools, the server exposes the `openfinance://banks/` resource, the `analyze_monthly_spending` prompt, and optional URL elicitation in both bank-authorization start tools.

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

## Docker

```bash
# Build
docker build -t openfinance-br-mcp .

# Run the tests
docker compose --profile test up

# Run the server
docker compose up openfinance-mcp
```

## Kubernetes

```bash
# Create the namespace
kubectl create namespace fintech

# Apply the configuration (edit the secrets first!)
kubectl apply -f k8s/config-and-secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

Before applying, replace the credential, private-key,
`MCP_OAUTH_ISSUER_URL`, `MCP_OAUTH_RESOURCE_SERVER_URL`, and domain
placeholders. The server fails closed when HTTP is exposed outside loopback
without MCP client OAuth.

Runs `streamable-http` behind 2 replicas, with CLIENT_ID/CLIENT_SECRET/
ANTHROPIC_API_KEY mounted as secret files rather than env vars, and a
shared Redis backend (`REDIS_URL`) so token/consent state is visible
across replicas.

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

## Design principles

- **SOLID**: BankAdapter ABC (O/C, LSP), single-responsibility tools, constructor-based DI
- **12-Factor**: config via env, stateless, logs to stdout
- **Security**: mTLS, SecretStr, in-memory tokens, mandatory PKCE
- **Idempotency**: asyncio.Lock on token refresh, X-Idempotency-Key on PIX
- **DSPy**: transaction categorization framed as an LLM classification problem

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

## Adding a new bank

1. Create `src/openfinance_br_mcp/adapters/my_bank.py`
2. Inherit from `DefaultOpenFinanceAdapter` (or `BankAdapter` directly for a fully custom implementation)
3. Override `bank_id`, and pass `base_url`/`token_endpoint` defaults
4. Add its ISPB to `directory/client.py`'s `_ISPB_BY_BANK` and register the adapter class in `context.py`

## Documentation

- [docs/en/authorization.md](docs/en/authorization.md) - the two token universes (MCP client auth vs. FAPI-BR bank auth), and why they can never cross
- [CONTRIBUTING.md](CONTRIBUTING.md) - dev setup, CI checks, adding a bank adapter
- [SECURITY.md](SECURITY.md) - scope, disclaimer, and how to report a vulnerability
- [SOURCES.md](SOURCES.md) - specs and RFCs this implementation follows
- [VALIDATION.md](VALIDATION.md) - what's actually been validated, and what hasn't (no real BCB sandbox run)
- [CHANGELOG.md](CHANGELOG.md) - release history

## License

MIT
