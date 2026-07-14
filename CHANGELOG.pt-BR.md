[English](CHANGELOG.md) · **Português**

# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui. O formato
segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e este
projeto segue o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-07-13

Lançamento público inicial.

### Adicionado

- Servidor MCP (transportes `stdio` e `streamable-http`) expondo 12 tools
  cobrindo as Fases 2, 3 e 4 do Open Finance Brasil: `list_accounts`,
  `get_balance`, `list_transactions`, `list_credit_cards`,
  `get_credit_card_bills`, `list_pix_keys`, `initiate_pix`,
  `list_investments`, `start_consent`, `complete_consent`,
  `check_consent_status`, `revoke_consent`.
- Fluxo de autorização FAPI-BR 2.2.0: PAR/JAR, autenticação de cliente via
  `private_key_jwt` (RFC 7523), PKCE, decriptação/verificação de ID token,
  troca de token via authorization_code e client_credentials.
- Abstração `BankAdapter` com uma base `DefaultOpenFinanceAdapter` e
  adapters concretos para 10 instituições (Nubank, Sicoob, Caixa
  Econômica, Banco do Brasil, Bradesco, Itaú Unibanco, Santander, XP,
  PicPay, BTG Pactual), resolvidos via um `DirectoryClient` contra o
  Diretório de Participantes do BCB.
- Ambiente `mock` (padrão) apoiado no `MockOpenFinanceAdapter`, para um
  ciclo de desenvolvimento sem credenciais e sem rede, já que o sandbox
  oficial do BCB não é self-service.
- Categorização de transações via DSPy + Claude (`categorize=true` em
  `list_transactions`).
- Autenticação OAuth 2.1 do lado resource-server para clientes MCP
  (`JWTTokenVerifier`), com vinculação de audience conforme a RFC 8707 e
  Protected Resource Metadata da RFC 9728.
- Tokens de acesso vinculados a certificado mTLS (RFC 8705), opcionais,
  para clientes MCP (`MTLSClientCertMiddleware`), para deployments atrás
  de um proxy/gateway que termina o mTLS.
- Opção de `TokenStore`/`ConsentManager` apoiados em Redis para escalar
  horizontalmente entre réplicas; em memória por padrão.
- Tracing via OpenTelemetry (exporters genéricos OTLP e Langfuse), logging
  estruturado em JSON/console via structlog.
- Manifests de Docker, Docker Compose e Kubernetes para deployment.
- Pipeline de CI: `black`, `ruff`, `mypy --strict` (em `src/`) e `pytest`
  com um gate de cobertura de 80%.

[0.1.0]: https://github.com/brunovicco/openfinance-br-mcp/releases/tag/v0.1.0
