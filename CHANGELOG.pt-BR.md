[English](CHANGELOG.md) · **Português**

# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui. O formato
segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e este
projeto segue o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

Correções de segurança e correção funcional a partir de uma revisão técnica
interna (veja `IMPLEMENTATION_PLAN.md` para o plano completo por fases e a
justificativa de cada item). A fase P0 (bloqueadores de risco imediato) e
parte da P1 (resolução por família via Diretório) estão incluídas aqui; a
jornada da API de Pagamentos v5 (P2) e a validação em sandbox (P3) são
tratadas separadamente.

### Corrigido

- **Colisão de token/consentimento entre bancos**: `TokenStore` e
  `ConsentManager` agora usam `(bank_id, subject_id)` como chave, em vez de
  apenas `subject_id` - antes, autorizar um segundo banco para o mesmo
  subject (ex.: CPF) podia sobrescrever o token do primeiro banco, e uma
  renovação podia ser tentada no endpoint de token errado.
- **Reuso de consentimento entre bancos/escopos**: `ConsentManager.create()`
  não reutiliza mais um consentimento `AWAITING_AUTHORISATION`/`AUTHORISED`
  em cache a menos que os escopos armazenados cubram o que está sendo
  solicitado, e o reuso agora é isolado por banco.
- **`x-fapi-interaction-id`** agora é enviado em toda chamada a recurso
  protegido (`adapters/base.py::build_fapi_headers`), conforme exigido pelo
  perfil de segurança FAPI-BR.
- **`response_mode=fragment`** e a claim essencial `acr` agora são incluídos
  no request object PAR/JAR (`auth/par.py`); o ID Token passa a ser
  obrigatório em `complete_consent` (antes era opcional) e sua claim `acr` é
  agora validada (`auth/id_token.py`).
- **Mapa de permissões do consentimento**: `accounts` não concede mais
  implicitamente `transactions`/`overdraft_limits`/`balances`; cada uma
  passa a ser um escopo distinto e explícito. PIX/pagamentos removido do
  mapa de escopos do consentimento de dados; a iniciação de pagamento
  exige seu próprio consentimento de pagamento dedicado (ainda não
  implementado, ver P2).
- **Path de cartão de crédito**: corrigido de `/credit-cards/v2/...` para o
  path oficial `/credit-cards-accounts/v2/...`.
- **Falha de resolução do Diretório agora é fail-closed por padrão**
  (`directory_fallback_mode=fail_closed`): um banco cujo endpoint não pode
  ser resolvido via Diretório de Participantes é excluído de
  `app.adapters`, em vez de cair silenciosamente para uma URL fixa. O modo
  opcional `hardcoded_fallback` preserva o comportamento anterior para
  desenvolvimento local.
- **Resolução de endpoints por família de API**: adapters reais agora
  resolvem `credit-cards-accounts`, `payments` e `bank-fixed-incomes`
  independentemente via Diretório, em vez de reutilizar a URL da família
  `accounts` para todo tipo de recurso
  (`DefaultOpenFinanceAdapter.set_family_base_urls`).

### Adicionado

- **Vínculo entre principal MCP e subject_id**
  (`auth/principal_binding.py`, `tools/principal_guard.py`): em
  `streamable-http` com OAuth de cliente MCP configurado, toda tool que
  recebe `subject_id` agora verifica se o chamador autenticado já foi
  vinculado a esse subject por um fluxo de consentimento concluído. Não faz
  nada em `stdio` ou quando o OAuth de cliente MCP não está configurado.
- **OAuth obrigatório fora de loopback**: a inicialização do servidor agora
  falha se `mcp_transport=streamable-http` estiver vinculado a um host que
  não seja loopback sem OAuth de cliente MCP configurado.
- `initiate_pix`/`list_pix_keys` agora são explicitamente restritas a
  `environment=mock` até que a jornada real da API de Pagamentos v5 seja
  implementada.

### Alterado

- README/README.pt-BR reposicionados: a afirmação de "10 bancos, Fases
  2/3/4" foi substituída por uma distinção explícita entre mock e
  integração real por banco.

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
