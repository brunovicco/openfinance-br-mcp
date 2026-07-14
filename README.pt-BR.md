[English](README.md) · **Português**

# openfinance-br-mcp

> MCP Server para o **Open Finance Brasil** - conecta o Claude diretamente às APIs do Banco Central, cobrindo Fases 2, 3 e 4.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![uv](https://img.shields.io/badge/managed%20by-uv-blueviolet)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/lint-ruff-orange.svg)](https://github.com/astral-sh/ruff)

---

## O que é

Um **MCP Server** que abstrai toda a complexidade do Open Finance Brasil (FAPI 1.0 Advanced, OAuth2, consentimento, mTLS) e expõe tools simples para o Claude:

```
Claude → "quanto gastei com alimentação em março?"
Claude usa list_transactions(bank=nubank, categorize=true, date_from=2024-03-01)
Claude → "Você gastou R$ 847,30 com alimentação em março..."
```

## Bancos suportados

| Banco | ISPB | Fase 2 | Fase 3 (PIX) | Fase 4 (Investimentos) |
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

> Novos bancos: implemente `BankAdapter` (ou herde de `DefaultOpenFinanceAdapter`) e registre - veja "Adicionando um novo banco" abaixo.

## Tools MCP disponíveis

| Tool | Descrição | Fase |
|------|-----------|------|
| `list_accounts` | Lista contas corrente, poupança e pré-paga | 2 |
| `get_balance` | Saldo disponível, bloqueado e investido | 2 |
| `list_transactions` | Extrato com filtros e categorização DSPy | 2 |
| `list_credit_cards` | Cartões de crédito e limites | 2 |
| `get_credit_card_bills` | Faturas abertas e anteriores | 2 |
| `list_pix_keys` | Chaves PIX cadastradas | 2 |
| `initiate_pix` | Pagamento PIX com idempotência | 3 |
| `list_investments` | Renda fixa (CDB, LCI, LCA) | 4 |
| `start_consent` | Inicia o fluxo de consentimento/autorização FAPI-BR | - |
| `complete_consent` | Completa o consentimento após autorização no banco | - |
| `check_consent_status` | Consulta o status de um consentimento existente | - |
| `revoke_consent` | Revoga um consentimento existente | - |

## Instalação rápida

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) instalado

```bash
# Clone o repositório
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp

# Configure o ambiente
cp .env.example .env
# Edite .env com seu CLIENT_ID, CLIENT_SECRET etc.

# Instale as dependências
uv sync

# Execute o servidor
uv run openfinance-mcp
```

### Claude Desktop

Adicione ao `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openfinance-br": {
      "command": "uv",
      "args": ["run", "--directory", "/caminho/para/openfinance-br-mcp", "openfinance-mcp"],
      "env": {
        "CLIENT_ID": "seu_client_id",
        "CLIENT_SECRET": "seu_client_secret",
        "MTLS_ENABLED": "false"
      }
    }
  }
}
```

## Desenvolvimento

```bash
# Instala com dev-dependencies
uv sync

# Roda os testes
uv run pytest tests/ -v

# Lint e formatação
uv run ruff check src/ tests/
uv run black src/ tests/

# Type check
uv run mypy src/
```

## Docker

```bash
# Build
docker build -t openfinance-br-mcp .

# Roda (testes)
docker compose --profile test up

# Roda o servidor
docker compose up openfinance-mcp
```

## Kubernetes

```bash
# Cria o namespace
kubectl create namespace fintech

# Aplica configurações (edite os secrets antes!)
kubectl apply -f k8s/config-and-secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

Roda `streamable-http` atrás de 2 réplicas, com CLIENT_ID/CLIENT_SECRET/
ANTHROPIC_API_KEY montados como arquivos de secret em vez de env vars,
e um backend Redis compartilhado (`REDIS_URL`) para que o estado de
token/consentimento fique visível entre réplicas.

## Arquitetura

```
Claude (MCP Client)
        │ stdio ou streamable-http
        ▼
openfinance-br-mcp (MCP Server)
  ├── Auth + Consent  (FAPI-BR 2.2.0: private_key_jwt, PAR/JAR, PKCE, mTLS)
  ├── MCP Tools       (12 tools, input validado por Pydantic v2)
  │   └── Categorizer (DSPy + Claude para classificar transações)
  ├── Bank Adapters   (10 bancos - extensível)
  └── Directory Client (resolve os endpoints reais dos bancos via o
                         Diretório de Participantes do BCB)
        │ HTTPS/mTLS
        ▼
Open Finance BR (BCB) - Diretório de Participantes
        │
        ▼
  Nubank · Sicoob · Caixa · + 100 instituições participantes
```

## Princípios de design

- **SOLID**: BankAdapter ABC (O/C, LSP), tools com SRP, DI via construtor
- **12-Factor**: config via env, stateless, logs em stdout
- **Segurança**: mTLS, SecretStr, tokens em memória, PKCE obrigatório
- **Idempotência**: asyncio.Lock no refresh de tokens, X-Idempotency-Key no PIX
- **DSPy**: categorização de transações como problema de classificação LLM

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `ENVIRONMENT` | ❌ | `mock` (padrão, sem credenciais necessárias), `sandbox` ou `production` |
| `CLIENT_ID` | ⚠️ fora do mock | Client ID registrado na IF |
| `CLIENT_SECRET` | ⚠️ fora do mock | Client secret |
| `PRIVATE_KEY_PATH` | ⚠️ fora do mock | Chave RSA para assinatura `private_key_jwt`/JAR |
| `MTLS_CERT_PATH` | ⚠️ prod | Caminho do certificado mTLS |
| `MTLS_KEY_PATH` | ⚠️ prod | Chave privada mTLS |
| `ANTHROPIC_API_KEY` | ⚠️ DSPy | Necessário para `categorize=true` |
| `REDIS_URL` | ❌ | Compartilha estado de TokenStore/ConsentManager entre réplicas |
| `MCP_TRANSPORT` | ❌ | `stdio` (padrão) ou `streamable-http` |
| `LANGFUSE_OTLP_ENDPOINT` | ❌ | Ativa tracing para o Langfuse (com `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`) |
| `LOG_LEVEL` | ❌ | INFO, DEBUG, WARNING (padrão: INFO) |
| `LOG_FORMAT` | ❌ | json ou console (padrão: json) |

Veja `.env.example` para a lista completa.

## Adicionando um novo banco

1. Crie `src/openfinance_br_mcp/adapters/meu_banco.py`
2. Herde de `DefaultOpenFinanceAdapter` (ou `BankAdapter` diretamente para uma implementação totalmente customizada)
3. Sobrescreva `bank_id`, e passe os defaults de `base_url`/`token_endpoint`
4. Adicione o ISPB em `_ISPB_BY_BANK` de `directory/client.py` e registre a classe do adapter em `context.py`

## Documentação

- [docs/pt/authorization.md](docs/pt/authorization.md) - os dois universos de token (autenticação do cliente MCP vs. autenticação bancária FAPI-BR), e por que eles nunca podem se cruzar
- [CONTRIBUTING.pt-BR.md](CONTRIBUTING.pt-BR.md) - configuração do ambiente de dev, checagens de CI, como adicionar um adapter de banco
- [SECURITY.pt-BR.md](SECURITY.pt-BR.md) - escopo, aviso, e como reportar uma vulnerabilidade
- [SOURCES.pt-BR.md](SOURCES.pt-BR.md) - especificações e RFCs que esta implementação segue
- [VALIDATION.pt-BR.md](VALIDATION.pt-BR.md) - o que de fato foi validado, e o que não foi (nenhuma execução contra o sandbox real do BCB)
- [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md) - histórico de releases

## Licença

MIT
