**English** · [Português](README.pt-BR.md)

# openfinance-br-mcp

> MCP Server for **Open Finance Brasil** - connects Claude directly to the Banco Central APIs, covering Fases 2, 3, and 4.

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

| Bank | ISPB | Fase 2 | Fase 3 (PIX) | Fase 4 (Investments) |
|-------|------|--------|--------------|----------------------|
| Nubank | 18236120 | ✅ | ✅ | ✅ |
| Sicoob | 04891850 | ✅ | ✅ | ✅ |
| Caixa Econômica | 00360305 | ✅ | ✅ | ✅ |
| Banco do Brasil | 00000000 | ✅ | ✅ | ✅ |
| Bradesco | 60746948 | ✅ | ✅ | ✅ |
| Itaú Unibanco | 60701190 | ✅ | ✅ | ✅ |
| Santander | 90400888 | ✅ | ✅ | ✅ |
| XP | 33264668 | ✅ | ✅ | ✅ |
| PicPay | 22896431 | ✅ | ✅ | ✅ |
| BTG Pactual | 30306294 | ✅ | ✅ | ✅ |

> New banks: implement `BankAdapter` (or subclass `DefaultOpenFinanceAdapter`) and register it - see "Adding a new bank" below.

## Available MCP tools

| Tool | Description | Fase |
|------|-----------|------|
| `list_accounts` | Lists checking, savings, and prepaid accounts | 2 |
| `get_balance` | Available, blocked, and invested balance | 2 |
| `list_transactions` | Statement with filters and DSPy categorization | 2 |
| `list_credit_cards` | Credit cards and limits | 2 |
| `get_credit_card_bills` | Open and past bills | 2 |
| `list_pix_keys` | Registered PIX keys | 2 |
| `initiate_pix` | Idempotent PIX payment | 3 |
| `list_investments` | Fixed income (CDB, LCI, LCA) | 4 |
| `start_consent` | Starts the FAPI-BR consent/authorization flow | - |
| `complete_consent` | Completes consent after the user authorizes at the bank | - |
| `check_consent_status` | Checks the status of an existing consent | - |
| `revoke_consent` | Revokes an existing consent | - |

## Quick start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed

```bash
# Clone the repository
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp

# Configure the environment
cp .env.example .env
# Edit .env with your CLIENT_ID, CLIENT_SECRET, etc.

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
      "args": ["run", "--directory", "/path/to/openfinance-br-mcp", "openfinance-mcp"],
      "env": {
        "CLIENT_ID": "your_client_id",
        "CLIENT_SECRET": "your_client_secret",
        "MTLS_ENABLED": "false"
      }
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
  ├── MCP Tools       (12 tools, input validated with Pydantic v2)
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
