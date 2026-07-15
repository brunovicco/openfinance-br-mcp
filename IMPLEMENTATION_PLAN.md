# Plano de Implementação - Melhorias e correções

Convenção de fases: P0 bloqueia riscos imediatos; P1 exige P0 concluído; P2 exige P1; P3 exige acesso a sandbox real de pelo menos um banco e só faz sentido após P0-P2.

---

## P0 - Bloquear riscos imediatos

### P0.1 Chaves compostas para tokens, consentimentos e locks

**Arquivos:** `auth/token.py`, `auth/consent.py`, `auth/store_protocol.py`, `auth/redis_backend.py`

- Substituir `_KEY_PREFIX + subject_id` por uma chave composta: `openfinance:token:{tenant}:{principal}:{bank_id}:{issuer}:{client_id}:{consent_id}`.
- `TokenStore.save`/`get_valid_token`/`revoke` passam a receber um `TokenKey` (dataclass) em vez de `subject_id: str` cru. Atualizar as três chamadas em `tools/consent.py` (`_require_token`, `complete_consent`, `revoke_consent`) e em `default_adapter.py` (`_get_token`, herdado de `adapters/base.py`).
- Mesma mudança em `ConsentManager` (`auth/consent.py`): a chave de cache deixa de ser só `subject_id`; o objeto de consentimento passa a armazenar explicitamente `bank_id`, `issuer`, `scopes`, `permissions`, `expiration`, `status` (hoje só guarda o payload bruto retornado pelo banco).
- `TokenStore._refresh` hoje recebe `token_endpoint` como parâmetro solto e busca o refresh token só por `subject_id` - depois da mudança, o `token_endpoint` já vem embutido/validado contra o `issuer` da chave, eliminando o cenário de renovar no endpoint errado.
- Lock keys (`_lock_key`) seguem o mesmo esquema composto.

**Critério de aceite:** teste que autoriza o mesmo `subject_id` em dois bancos diferentes e confirma que ambos os tokens coexistem e cada adapter usa apenas o seu.

### P0.2 Consentimento não reutilizável entre bancos/escopos

**Arquivo:** `auth/consent.py`, método `create()` (linha ~148)

- A checagem de reuso hoje é `existing["data"]["status"] in (AWAITING, AUTHORISED)`, sem comparar banco. Trocar a chave de cache (ver P0.1) já resolve o cruzamento entre bancos.
- Adicionar comparação explícita de `scopes`/`permissions`/`bank_id`/`issuer` antes de reusar; um consentimento `AUTHORISED` com escopo diferente do solicitado deve gerar um novo, não ser reaproveitado.

**Critério de aceite:** teste que solicita `["accounts"]` depois `["accounts", "pix"]` para o mesmo subject/banco e confirma que a segunda chamada cria um novo consentimento.

### P0.3 Vincular principal MCP autenticado ao subject_id

**Arquivos:** `auth/mcp_token_verifier.py`, `context.py`, todas as tools em `tools/*.py`

- Hoje `subject_id` é parâmetro livre em `list_accounts`, `initiate_pix`, `check_consent_status` etc; nada liga isso ao `claims["sub"]` do `AccessToken` verificado em `mcp_token_verifier.py`.
- Criar uma tabela de vínculo `mcp_principal → subject_id permitido(s)` (nova classe, ex. `auth/principal_binding.py`, backed pelo mesmo `KeyValueStore`).
- Em transporte `stdio` (uso local, Claude Desktop): manter comportamento atual (não há MCP principal autenticado) mas documentar explicitamente essa exceção.
- Em transporte `streamable-http`: extrair o principal do contexto MCP (via `ctx.request_context`; verificar como o SDK expõe o `AccessToken` verificado no contexto de request) e, antes de cada tool executar, validar que o `subject_id` recebido pertence ao principal. Caso contrário, `ValidationError`/`AuthenticationError`.
- Isso afeta todas as tools que recebem `subject_id`: `tools/accounts.py`, `tools/transactions.py`, `tools/credit_cards.py`, `tools/investments.py`, `tools/pix.py`, `tools/consent.py`. Melhor implementar como decorator (`@require_principal_binding`) próximo de `@translate_errors`/`@traced_tool` para não duplicar a checagem em cada função.

**Critério de aceite:** teste de integração HTTP que autentica como principal A e tenta chamar `list_accounts(subject_id=<CPF de B>)`, esperando 403/erro de validação.

### P0.4 OAuth obrigatório fora de loopback

**Arquivo:** `server.py`, `config.py`

- Verificar configuração atual de `mcp_transport`/bind address. Adicionar checagem de startup: se `mcp_transport == "streamable-http"` e o bind host não for loopback (`127.0.0.1`/`localhost`), exigir `JWTTokenVerifier` configurado (falhar o boot caso contrário).

**Critério de aceite:** teste que sobe o server com `HTTP` + bind `0.0.0.0` sem issuer configurado e espera falha de inicialização.

### P0.5 `x-fapi-interaction-id` em toda chamada protegida

**Arquivo:** `adapters/default_adapter.py` (todas as chamadas `self._http.get/post/delete`), `adapters/base.py`

- Criar helper centralizado em `adapters/base.py`:
  ```python
  def build_fapi_headers(access_token: str) -> dict[str, str]:
      return {
          "Authorization": f"Bearer {access_token}",
          "x-fapi-interaction-id": str(uuid.uuid4()),
      }
  ```
- Substituir todos os `headers={"Authorization": f"Bearer {token}"}` em `default_adapter.py` (7 ocorrências: `get_accounts`, `get_balance`, `list_transactions`, `get_credit_card_accounts`, `get_credit_card_bills`, `list_pix_keys`, `initiate_pix`, `list_investments`) por `build_fapi_headers(token)`.
- Capturar o `x-fapi-interaction-id` da resposta (quando o banco ecoa) e logar via `structlog` para correlação/auditoria.

**Critério de aceite:** teste que inspeciona os headers de toda chamada mockada via `httpx.MockTransport` e confirma presença do header com UUID válido.

### P0.6 Fail-closed quando o Diretório não resolve

**Arquivo:** `context.py`, função `_build_real_adapters` (linha ~182)

- Hoje, falha de `directory.resolve()` cai em `adapter_cls(token_store, http_client)` (defaults hardcoded) com apenas um `log.warning`. Em produção/sandbox isso deve ser fail-closed: banco não resolvido não deve ficar disponível no dicionário `adapters`.
- Adicionar `settings.directory_fallback_mode: Literal["fail_closed", "hardcoded_fallback"]`, default `fail_closed` para `production`/`sandbox`; permitir `hardcoded_fallback` apenas explicitamente (útil em dev).
- Quando fail-closed, o banco simplesmente não entra em `adapters`; tools que recebem `bank` inexistente já tratam isso via `ValidationError("Bank ... is not available")` (ver `tools/accounts.py` linha 51).

**Critério de aceite:** teste que simula `DirectoryError` na resolução e confirma que o banco não aparece em `app.adapters` quando `environment=production`.

### P0.7 `response_mode`, `acr` essencial e ID Token obrigatório

**Arquivos:** `auth/par.py` (linha ~106-119), `tools/consent.py` (linha ~254-260), `auth/id_token.py`

- `par.py`: adicionar `"response_mode": "fragment"` ao dict `request_claims`. Adicionar `claims` essenciais incluindo `acr` (`{"id_token": {"acr": {"essential": True, "values": [...]}}}` conforme o perfil FAPI-BR exigir).
- `tools/consent.py`: trocar
  ```python
  id_token_raw = _single("id_token")
  if id_token_raw and app.directory is not None:
      ...
  ```
  por falha fechada:
  ```python
  id_token_raw = _single("id_token")
  if not id_token_raw:
      raise AuthenticationError("Missing mandatory ID token", code="MISSING_ID_TOKEN")
  if app.directory is None:
      raise ValidationError(...)
  jwks = await app.directory.resolve_jwks(session.bank_id)
  verify_id_token(...)
  ```
- `auth/id_token.py`, `verify_id_token`: adicionar `acr` ao `check_claims` (ou validação pós-decodificação contra valor mínimo esperado) e validar `iat` explicitamente.

**Critério de aceite:** teste que monta um `callback_url` sem `id_token` e confirma que `complete_consent` levanta `AuthenticationError`; teste que confirma `response_mode=fragment` no JWT do request object gerado por `push_authorization_request`.

### P0.8 Corrigir mapa de permissões e separar pagamentos do consentimento de dados

**Arquivo:** `auth/consent.py`, `_build_permissions` (linha ~267) e `CONSENT_SCOPE_MAP` (linha ~46)

- `permission_map` não tem `transactions` nem `pix`. Redesenhar o modelo de escopos simplificados para granularidade correta:
  ```
  accounts, balances, transactions, overdraft_limits,
  credit_card_accounts, credit_card_limits, credit_card_bills, credit_card_transactions,
  bank_fixed_incomes, funds, variable_incomes, treasure_titles
  ```
- Remover `pix` do mapa de consentimento de dados; pagamentos usam a API de Pagamentos com consentimento próprio (ver P2). `CONSENT_SCOPE_MAP["pix"] = "payments"` está semanticamente errado hoje e deve sair daqui.
- Atualizar `tools/consent.py` (`start_consent` docstring e validação de `scopes` de entrada) e qualquer schema Pydantic que valide a lista de scopes aceitos.

**Critério de aceite:** teste parametrizado que, para cada escopo simplificado, confirma que `_build_permissions` retorna exatamente as permissões BCB esperadas (nenhuma a mais, nenhuma a menos).

### P0.9 Desabilitar `initiate_pix` e `list_pix_keys` fora de mock

**Arquivos:** `tools/pix.py`, `context.py` ou `server.py` (registro de tools)

- Curto prazo, antes do rework completo de Pagamentos (P2): ambas as tools devem levantar `ValidationError` explícita quando `settings.environment != "mock"`, similar ao padrão já usado em `_require_directory` (`tools/consent.py` linha 95).
- Atualizar as docstrings das tools para deixar claro que são apenas demonstrativas em modo mock até P2 ser concluído.

**Critério de aceite:** teste que chama `initiate_pix`/`list_pix_keys` com `environment=sandbox` e espera erro claro em vez de uma chamada HTTP real malformada.

---

## P1 - Aderência às APIs oficiais

### P1.1 Clientes gerados a partir dos OpenAPI oficiais

**Nota (verificado ao vivo contra o repositório `github.com/OpenBanking-Brasil/openapi`, clonado localmente em `openapi-spec-tmp/` para inspeção - ver `swagger-apis/<família>/`):** as versões abaixo listadas na redação original desta seção (`consents_v3_3_1`, `accounts_v2_5_0`, `credit_cards_v2_4_0`, `payments_v5_0_0`) eram estimativas não verificadas feitas durante o planejamento inicial. As versões *estáveis* (não beta/rc) realmente publicadas hoje são:

- `consents` 3.3.1 (confirmado - a estimativa original estava certa)
- `accounts` 2.4.2 (2.5.0 só existe como `2.5.0-beta.1`/`2.5.0-beta.2` - ainda não estável)
- `credit-cards` 2.3.1 (pasta do repo chama-se `credit-cards`, mas os `servers.url` do próprio spec confirmam o path `/open-banking/credit-cards-accounts/v2` já usado neste projeto; 2.4.0 só existe como beta)
- `payments` **4.0.0**, não 5.0.0 - a versão 5.0.0 não existe neste repositório. **Além disso, o consentimento de pagamento (`POST/GET /consents`) está definido dentro do MESMO spec/família `payments`, não em uma família separada `payments-consents`** como este projeto assumiu em `auth/payment_consent.py`/`tools/payments.py` - não há nenhuma pasta `payments-consents` no repositório. O `requestBody` de `POST /consents` também exige `Content-Type: application/jwt` (JWS assinado), não JSON puro - hoje `payment_consent.py` envia JSON puro, o que precisa ser corrigido junto com a migração de família.
- `bank-fixed-incomes` 1.1.0 (confirmado)
- `funds` 1.1.0 (confirmado)
- `variable-incomes` 1.3.0 (confirmado)
- `treasure-titles` 1.1.0 (a pasta chama-se `treasure-titles`, não `treasury-direct`/"Tesouro Direto" como referido em P1.3 abaixo)

Criar `clients/` com um cliente por família+versão gerado via `openapi-python-client` a partir desses specs (arquivo `.yml` exato de cada família/versão acima).

- `default_adapter.py` deixa de montar URLs manualmente (`f"{self.base_url}/accounts/v2/accounts"`) e de fazer parsing com `dict.get()` genérico; passa a chamar os métodos tipados do cliente gerado correspondente.
- Corrigir especificamente:
  - path de cartão de crédito `/credit-cards/v2/accounts` → `/credit-cards-accounts/v2/accounts` (já corrigido no P0/P1.2 anterior); adicionar chamada separada para `/credit-cards-accounts/v2/accounts/{id}/limits` em vez de esperar `availableCreditLimit`/`totalCreditLimit` no objeto de conta (confirmado: é endpoint próprio, `operationId: creditCardsGetAccountsCreditCardAccountIdLimits`).
  - remover `list_pix_keys` do escopo genérico Open Finance (não existe na família Contas oficial) ou documentar como extensão proprietária com adapter dedicado.
  - migrar `auth/payment_consent.py`/`tools/payments.py` de `payments-consents` (família inexistente) para `payments` v4, endpoint `/consents` (mesmo host/versão de `/pix/payments`), e assinar o `requestBody` de criação do consentimento como JWS antes de enviar.

### P1.2 Diretório resolve por família de API, adapter recebe catálogo

**Arquivos:** `context.py`, `adapters/base.py`, `adapters/default_adapter.py`

- `_build_real_adapters` hoje resolve só `"accounts"` e reusa o `base_url` para tudo. Substituir por um `BankEndpoints` (dataclass) com um campo por família: `accounts`, `credit_cards_accounts`, `payments`, `consents`, `bank_fixed_incomes`, `funds`, `variable_incomes`.
- `DirectoryClient.resolve()` já é family-aware (aceita `api_family_type`), o problema é só no lado de consumo em `context.py`/`default_adapter.py`. Resolver cada família separadamente no lifespan e injetar o catálogo completo no adapter em vez de um único `base_url`.
- `DefaultOpenFinanceAdapter.__init__` passa a receber `endpoints: BankEndpoints` em vez de `base_url: str`; cada método (`get_accounts`, `get_credit_card_accounts`, etc.) usa o campo correspondente.

### P1.3 Versões atualizadas

- Atualizar paths para as versões estáveis vigentes (ver nota de P1.1 acima): Consentimentos 3.3.1, Contas 2.4.2, Cartão de Crédito 2.3.1 (path `credit-cards-accounts` v2), Pagamentos 4.0.0, Renda Fixa Bancária (`bank-fixed-incomes`) 1.1.0, conforme os clientes gerados em P1.1 forem substituindo as chamadas manuais.
- Implementar adapters para Fundos (`funds` 1.1.0), Renda Variável (`variable-incomes` 1.3.0) e Títulos do Tesouro (`treasure-titles` 1.1.0 - nome real da família no repositório oficial, referida anteriormente aqui como "Tesouro Direto"), hoje declarados no consentimento mas sem implementação (`investments.py` só cobre `bank-fixed-incomes`).

---

## P2 - Jornada de pagamento completa

### P2.1 Consentimento de pagamento dedicado

**Novo módulo:** `auth/payment_consent.py` (paralelo a `auth/consent.py`, não reaproveitando o mesmo `ConsentManager`/; payload e ciclo de vida são diferentes)

- Implementar a sequência oficial: criar consentimento na API de Pagamentos → PAR/JAR com esse `consentId` → autorização do usuário → validar ID Token → troca do `code` → consultar status do consentimento de pagamento → assinar JWS da ordem de pagamento → criar pagamento em `/payments/v5/pix/payments` → consultar status → cancelar quando aplicável.
- Novas tools em `tools/pix.py` (ou novo `tools/payments.py`): `start_payment_consent`, `complete_payment_consent`, `check_payment_status`, `cancel_payment`.

### P2.2 Assinatura JWS das requisições/respostas de Pagamentos

- Adicionar componente de assinatura de payload (reaproveitar `load_private_key`/lógica de `jwt_client_auth.py`) para produzir o JWS exigido pela API de Pagamentos v5, em vez do JSON puro atual em `initiate_pix`.

### P2.3 Idempotência persistente vinculada ao payload assinado

**Arquivos:** `context.py` (`pix_idempotency_cache: dict[str, str]`, linha 130), `tools/pix.py`

- Substituir o `dict` em memória por um registro persistente no `KeyValueStore` compartilhado (mesmo backend Redis usado por `TokenStore`/`ConsentManager`), contendo: `issuer, client_id, bank_id, subject_id, consent_id, idempotency_key, payload_jws_hash, payment_id, last_response`.
- Regra: mesma chave + mesmo hash de payload → retorna resultado anterior; mesma chave + payload diferente → rejeita; emissor incompatível → rejeita.

**Critério de aceite (P2 geral):** suíte de testes contra um mock da API de Pagamentos v5 cobrindo o fluxo feliz completo, idempotência (replay idêntico, replay com payload diferente, replay de outro cliente) e cancelamento.

**Nota (verificado ao vivo contra o repositório oficial, sessão P1.1):** a implementação original do P2 continha dois bugs reais descobertos só ao inspecionar `swagger-apis/payments/4.0.0.yml` diretamente (não uma nota de plano, um bug em código já commitado):

1. `auth/payment_consent.py` chamava `POST {base}/payments/v1/consents` - o path correto é `/payments/v4/consents` (não existe `payments/v5`, e a família de consentimento de pagamento é a própria família `payments`, não uma família separada `payments-consents`/`payments-pix` no Diretório de Participantes - `tools/payments.py` e `tools/pix.py` resolviam essa família inexistente via `app.directory.resolve(bank, "payments-consents")`, o que falharia com `API_FAMILY_NOT_FOUND` contra qualquer banco real).
2. Tanto `POST /consents` quanto `GET /consents/{id}` (e também `POST /pix/payments`/`GET /pix/payments/{id}`, já usados por `initiate_pix`) exigem/retornam `Content-Type: application/jwt` nos dois sentidos - request **e** response são JWS assinado, não JSON puro. O código chamava `response.json()` diretamente nesses quatro pontos, o que levantaria erro de parse contra qualquer banco real (não um "talvez funcione sem verificação", um crash garantido).

Corrigido nesta sessão: os quatro call sites (`default_adapter.py::initiate_pix`, `payment_consent.py::create`/`get_status`) agora assinam o corpo da requisição via `sign_payment_payload` e decodificam a resposta via `decode_payment_response_unverified` (novo em `auth/payment_jws.py`) - decodifica o JWS sem verificar a assinatura do banco, já que nenhum desses call sites tem acesso a um `DirectoryClient` para buscar o JWKS do banco; verificação completa continua rastreada como item de P3, no mesmo espírito do que já estava documentado para a resposta de `initiate_pix`.

---

## P3 - Integração real (pré-requisito: acesso a sandbox de pelo menos um banco)

Sequência a ser tratada como checklist de validação (não código):

1. Configurar SSA, certificados e DCR (novo módulo `auth/dcr.py` - registro dinâmico com o authorization server: obter SSA no Diretório, registrar app, armazenar `client_id`/`registration_access_token`/`registration_client_uri` por `authorization_server_id`, não globalmente como hoje via `settings.client_id` único).
2. Executar contra o motor de testes funcionais oficial do Open Finance Brasil.
3. Executar contratos (P1.1) contra sandbox real.
4. Testar pelo menos uma instituição por authorization server.
5. Registrar evidências por API e versão testada.
6. Testar rotação de certificados, JWKS e refresh tokens.
7. Testar revogação e expiração de consentimento/token.
8. Revisão de segurança independente antes de qualquer reposicionamento como "certificado" ou "pronto para produção".

---

## Ordem de execução

1. P0.1 → P0.2 (dependem uma da outra: a chave composta é pré-requisito para a comparação de escopo/banco funcionar de forma limpa)
2. P0.5, P0.6, P0.7, P0.8, P0.9 podem ser feitos em paralelo entre si e em paralelo a P0.1/P0.2 (tocam arquivos diferentes)
3. P0.3, P0.4 (autenticação multiusuário) podem começar em paralelo, mas o teste de aceite de P0.3 só é significativo depois de P0.1
4. Reposicionamento do README - paralelo a tudo, sem dependências
5. P1 completo só depois de todo P0 mesclado (P1.2 toca os mesmos arquivos que P0.6)
6. P2 depois de P1.1/P1.2 (a jornada de pagamento v5 depende do cliente gerado e do catálogo de endpoints por família)
7. P3 só após P0-P2 e mediante obtenção de credenciais de sandbox reais
