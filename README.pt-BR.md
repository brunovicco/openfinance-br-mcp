[English](https://github.com/brunovicco/openfinance-br-mcp/blob/main/README.md) · **Português**

# openfinance-br-mcp

> MCP experimental para o **Open Finance Brasil**, com ambiente mock completo
> e integração FAPI-BR em evolução. Não é certificado nem validado com
> instituições reais; consulte [VALIDATION.md](https://github.com/brunovicco/openfinance-br-mcp/blob/main/VALIDATION.md) antes de usá-lo
> fora de `environment=mock`.

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

O ambiente mock simula Nubank, Sicoob, Caixa, Banco do Brasil, Bradesco,
Itaú, Santander, XP, PicPay e BTG Pactual com dados em memória e sem acesso à
rede. São simulações, não integrações certificadas.

Os adapters reais e a jornada da API de Pagamentos são experimentais e não
validados. Pagamentos usam as famílias v5 `payments-consents`/`payments-pix`,
token por consentimento, verificação JWS das respostas, PAR/JAR, vínculo do
payload ao consentimento e idempotência persistente. `list_pix_keys` é uma
extensão demonstrativa, não um endpoint padronizado pelo Open Finance Brasil.
Consulte [VALIDATION.md](https://github.com/brunovicco/openfinance-br-mcp/blob/main/VALIDATION.md)
para o escopo exato.

## Tools MCP disponíveis

O servidor expõe 18 tools agrupadas por jornada:

- **Contas:** `list_accounts`, `get_balance`, `list_transactions`
- **Cartões:** `list_credit_cards`, `get_credit_card_bills`
- **Investimentos:** `list_investments`, `list_funds`,
  `list_variable_incomes`, `list_treasure_titles`
- **PIX:** `list_pix_keys`, `initiate_pix`
- **Consentimento de dados:** `start_consent`, `complete_consent`,
  `check_consent_status`, `revoke_consent`
- **Consentimento de pagamento:** `start_payment_consent`,
  `complete_payment_consent`, `check_payment_consent_status`

Também publica o resource `openfinance://banks/`, o prompt
`analyze_monthly_spending` e oferece URL elicitation opcional no início dos
fluxos de autorização.

## Instalação rápida

### Pré-requisitos

- Python 3.12 ou 3.13
- [uv](https://github.com/astral-sh/uv) instalado

```bash
# Execute a release publicada no modo mock, sem credenciais
uvx --from openfinance-br-mcp==0.2.0 openfinance-mcp
```

### A partir do código-fonte

```bash
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp

# Opcional: necessário apenas para sandbox/produção ou categorização DSPy
cp .env.example .env

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
      "command": "uvx",
      "args": ["--from", "openfinance-br-mcp==0.2.0", "openfinance-mcp"]
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

## Containers e Kubernetes

```bash
docker compose up openfinance-mcp
docker compose --profile test up
```

O diretório `k8s/` contém um exemplo Streamable HTTP com duas réplicas e estado
compartilhado no Redis. Substitua todos os placeholders de credenciais, chave
de assinatura, emissor OAuth, resource server e domínio antes de aplicá-lo. O
servidor falha de forma segura quando o HTTP é exposto fora de loopback sem
OAuth de cliente MCP.

## Arquitetura

```
Claude (MCP Client)
        │ stdio ou streamable-http
        ▼
openfinance-br-mcp (MCP Server)
  ├── Auth + Consent  (FAPI-BR 2.2.0: private_key_jwt, PAR/JAR, PKCE, mTLS)
  ├── MCP Primitives  (18 tools + 1 resource + 1 prompt)
  │   ├── Schemas de entrada/saída gerados por Pydantic v2
  │   ├── URL elicitation opcional para autorização bancária
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

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `ENVIRONMENT` | ❌ | `mock` (padrão, sem credenciais necessárias), `sandbox` ou `production` |
| `CLIENT_ID` | ⚠️ fora do mock | Client ID registrado na IF |
| `PRIVATE_KEY_PATH` | ⚠️ fora do mock | Chave RSA para assinatura `private_key_jwt`/JAR |
| `PRIVATE_KEY_KID` | ⚠️ fora do mock | `kid` correspondente ao JWKS registrado |
| `MTLS_CERT_PATH` | ⚠️ prod | Caminho do certificado mTLS |
| `MTLS_KEY_PATH` | ⚠️ prod | Chave privada mTLS |
| `ANTHROPIC_API_KEY` | ⚠️ DSPy | Necessário para `categorize=true` |
| `REDIS_URL` | ❌ | Compartilha estado de TokenStore/ConsentManager entre réplicas |
| `MCP_TRANSPORT` | ❌ | `stdio` (padrão) ou `streamable-http` |
| `MCP_HTTP_ALLOWED_ORIGINS` | ⚠️ HTTP remoto | Allowlist obrigatória fora de loopback |
| `LANGFUSE_OTLP_ENDPOINT` | ❌ | Ativa tracing para o Langfuse (com `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`) |
| `LOG_LEVEL` | ❌ | INFO, DEBUG, WARNING (padrão: INFO) |
| `LOG_FORMAT` | ❌ | json ou console (padrão: json) |

Veja [`.env.example`](https://github.com/brunovicco/openfinance-br-mcp/blob/main/.env.example)
para a lista completa.

## Documentação

- [Autorização](https://github.com/brunovicco/openfinance-br-mcp/blob/main/docs/pt/authorization.md) - os dois universos de token e por que eles nunca podem se cruzar
- [Contribuição](https://github.com/brunovicco/openfinance-br-mcp/blob/main/CONTRIBUTING.md) - ambiente de desenvolvimento, CI e novos adapters (em inglês)
- [Segurança](https://github.com/brunovicco/openfinance-br-mcp/blob/main/SECURITY.md) - escopo, aviso e reporte de vulnerabilidades (em inglês)
- [Fontes](https://github.com/brunovicco/openfinance-br-mcp/blob/main/SOURCES.md) - especificações e RFCs adotadas (em inglês)
- [Validação](https://github.com/brunovicco/openfinance-br-mcp/blob/main/VALIDATION.md) - escopo validado e limitações (em inglês)
- [Changelog](https://github.com/brunovicco/openfinance-br-mcp/blob/main/CHANGELOG.md) - histórico de releases (em inglês)
- [Release](https://github.com/brunovicco/openfinance-br-mcp/blob/main/RELEASING.md) - procedimento para mantenedores (em inglês)

## Licença

MIT
