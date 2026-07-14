[English](../en/authorization.md) · **Português**

# Autorização: dois universos de token separados

Este servidor lida com dois fluxos de autorização inteiramente
independentes. Eles nunca podem se cruzar, e o código é estruturado de
forma que esse cruzamento não é apenas desencorajado, mas
arquiteturalmente impossível.

## 1. Autorização do cliente MCP (lado resource-server)

Para quem é: o que quer que esteja chamando este servidor MCP via o
transporte `streamable-http` (Claude Desktop, um agente de
orquestração, um cliente customizado).

Este servidor não roda seu próprio Authorization Server OAuth. Ele
apenas *verifica* access tokens emitidos por um identity provider
OAuth2/OIDC externo, seguindo o padrão de "separação AS/RS" que o SDK
Python do MCP (`mcp.server.auth`) recomenda em vez do seu antigo
`OAuthAuthorizationServerProvider` que fazia tudo.

- Implementação: [`auth/mcp_token_verifier.py`](../../src/openfinance_br_mcp/auth/mcp_token_verifier.py)
  (`JWTTokenVerifier`), conectado ao `FastMCP` em
  [`server.py`](../../src/openfinance_br_mcp/server.py)'s `_build_mcp_auth()`.
- Verifica: assinatura JWS (via o JWKS do issuer, obtido através do
  discovery OIDC padrão), `iss`, `aud` (deve ser igual ao próprio
  `MCP_OAUTH_RESOURCE_SERVER_URL` deste servidor - vinculação de
  audience conforme RFC 8707) e `exp`.
- Expõe automaticamente o Protected Resource Metadata da RFC 9728 (o
  SDK do MCP constrói essa rota assim que `resource_server_url` é
  configurado) em `/.well-known/oauth-protected-resource`.
- Requisições sem autenticação ou com token inválido recebem um `401`
  com um header `WWW-Authenticate: Bearer ...` apontando para esse
  endpoint de metadata - também tratado inteiramente pelo SDK
  (`mcp.server.auth.middleware.bearer_auth`).

### Configuração

A autenticação fica **desligada por padrão**. Com `MCP_OAUTH_ISSUER_URL`
não definida, o transporte HTTP serve sem nenhuma autenticação de
cliente - aceitável apenas porque o host de bind padrão é loopback
(`MCP_HTTP_HOST=127.0.0.1`), o que a spec de autorização do MCP permite
para uso local/dev. Defina as duas variáveis abaixo juntas para ativar
a autenticação:

```bash
MCP_OAUTH_ISSUER_URL=https://your-idp.example.com
MCP_OAUTH_RESOURCE_SERVER_URL=https://your-mcp-server.example.com
MCP_OAUTH_REQUIRED_SCOPES=accounts:read,pix:write   # opcional
```

`validate_mcp_oauth_pair` em `config.py` rejeita configurações pela
metade (uma das duas URLs definida sem a outra) no momento em que as
configurações são carregadas.

### Opcional: tokens vinculados a certificado mTLS (RFC 8705)

Um bearer token roubado pode ser reproduzido de qualquer lugar. A RFC
8705 fecha essa brecha vinculando o token ao certificado de cliente TLS
apresentado no momento da emissão: o IdP coloca uma claim
`cnf.x5t#S256` (thumbprint SHA-256 em base64url da codificação DER do
certificado do cliente) no token, e este servidor deve rejeitá-lo a
menos que o *mesmo* certificado autentique a conexão atual.

- Implementação: [`auth/mtls_binding.py`](../../src/openfinance_br_mcp/auth/mtls_binding.py)
  (`MTLSClientCertMiddleware`, `compute_cert_thumbprint`), aplicada em
  `JWTTokenVerifier._check_mtls_binding` (`mcp_token_verifier.py`).
- Este servidor não termina mTLS diretamente para o `streamable-http` -
  ele espera um reverse proxy/gateway (nginx, Envoy, um load balancer
  na nuvem) na frente que valide o certificado do cliente contra uma CA
  confiável e o encaminhe via um header HTTP (convenção do
  `$ssl_client_escaped_cert` do nginx / `x-amzn-mtls-clientcert` do AWS
  ALB: PEM com URL-encoding). **Esse proxy precisa remover ou
  sobrescrever qualquer cópia do header enviada pelo próprio cliente**
  - se um cliente puder definir esse header diretamente, a checagem de
  vinculação perde todo o valor.
- `_run_streamable_http()` em `server.py` conecta o
  `MTLSClientCertMiddleware` antes do `AuthenticationMiddleware` do
  SDK sempre que o OAuth do cliente MCP está configurado, já que
  `TokenVerifier.verify_token(token: str)` (o próprio protocolo do SDK)
  nunca recebe a conexão - uma contextvar é o único canal para levar o
  certificado encaminhado do middleware ASGI até o verifier.
- A vinculação é aplicada automaticamente sempre que um token
  verificado carrega uma claim `cnf`. Para também *rejeitar* tokens que
  omitem `cnf` por completo (fechando o caminho de downgrade em que um
  atacante simplesmente solicita ou reproduz um token não vinculado),
  defina:

```bash
MCP_OAUTH_REQUIRE_MTLS_BINDING=true
MCP_OAUTH_MTLS_CERT_HEADER=x-ssl-client-cert   # deve bater com o header do seu proxy
```

## 2. Autorização bancária FAPI-BR (lado cliente-do-banco)

Para quem é: este próprio servidor, atuando como um cliente registrado
do Open Finance Brasil se autenticando junto ao authorization server de
cada banco participante, em nome de um usuário que passou pelo fluxo
de consentimento.

- Implementação: `auth/jwt_client_auth.py` (`private_key_jwt`,
  RFC 7523), `auth/par.py` (PAR/JAR), `auth/token_exchange.py`
  (grants client_credentials e authorization_code),
  `auth/id_token.py` (decriptação/verificação do ID token),
  `auth/token.py` (`TokenStore`) e `tools/consent.py` (as tools MCP
  `start_consent`/`complete_consent`/`check_consent_status`/
  `revoke_consent` que conduzem esse fluxo de ponta a ponta).
- Tokens obtidos dessa forma vivem exclusivamente em
  `AppContext.token_store` (um `TokenStore` em memória, indexado por
  `subject_id`), e são usados exclusivamente pelos adapters de banco
  (`adapters/default_adapter.py::_get_token`) ao chamar a API de Open
  Finance de um banco específico.

## Por que o passthrough é estruturalmente impossível aqui

- **Clientes HTTP diferentes.** `JWTTokenVerifier` (autenticação do
  cliente MCP) é construído com seu próprio `httpx.AsyncClient` em
  `server.py`, inteiramente separado de `AppContext.http_client`
  (chamadas aos bancos, construído em `app_lifespan` de `context.py`).
  Nenhum dos dois módulos importa o outro.
- **Stores de token diferentes.** A identidade verificada de um
  cliente MCP vive no escopo da requisição do Starlette
  (`scope["user"]`/`scope["auth"]`, um `AccessToken` de
  `mcp.server.auth.provider`) durante a duração de uma única
  requisição HTTP. Um token de banco vive no `TokenStore`, indexado por
  `subject_id`, persistindo entre requisições. As funções de tool
  (`tools/*.py`) nunca leem a requisição Starlette recebida - elas só
  recebem o `AppContext` via
  `ctx.request_context.lifespan_context`, que não tem nenhum caminho
  de volta para os headers da requisição.
- **A vinculação de audience torna um erro autocorrigível.** Mesmo que
  algum código futuro tentasse, por acidente, enviar um token de
  cliente MCP para um banco, as checagens de issuer/audience do
  `JWTTokenVerifier` significam que esse token nunca foi emitido para
  a audience daquele banco - a própria validação de token do banco o
  rejeitaria.
- **Testado contra regressão.** Veja
  `tests/unit/test_bank_adapters.py::test_bank_http_calls_never_use_an_mcp_client_token`:
  popula o `TokenStore` com um token FAPI-BR distintivo e um valor
  separado, nunca armazenado, de "token de cliente MCP", depois
  garante que apenas o primeiro aparece no header `Authorization` de
  uma requisição de saída para o banco.
