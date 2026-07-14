[English](SOURCES.md) · **Português**

# Fontes

As especificações e referências que esta implementação segue. Isso não é
uma citação exaustiva de cada RFC lida durante a construção do projeto -
é um mapa entre "o que o código faz" e "com o que ele deve estar em
conformidade", útil ao auditar um comportamento específico.

## Open Finance Brasil / BCB

- **Open Finance Brasil** - o programa regulatório em si, sob supervisão
  do Banco Central do Brasil (BCB). Este projeto tem como alvo as
  superfícies de API das Fases 2 (dados), 3 (iniciação de pagamento /
  PIX) e 4 (investimentos).
- **Diretório de Participantes** - o registro que o `DirectoryClient`
  deste projeto (`src/openfinance_br_mcp/directory/client.py`) consulta
  para resolver os endpoints reais e o ISPB de um banco:
  - Produção: `https://data.directory.openbankingbrasil.org.br`
  - Sandbox: `https://data.sandbox.directory.openbankingbrasil.org.br`
    (lista um conjunto de organizações menor e diferente do de produção -
    veja a documentação dos campos em `config.py`).
- **Perfil de segurança FAPI-BR** - a adaptação brasileira do perfil
  Financial-grade API (FAPI) 1.0 Advanced, exigindo autenticação de
  cliente via `private_key_jwt`, PAR, JAR, PKCE, e mTLS ou os mecanismos
  alternativos de DPoP/token vinculado a certificado que este projeto
  implementa.

## RFCs do IETF implementadas

| RFC | Título | Onde |
|-----|--------|------|
| [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749) | The OAuth 2.0 Authorization Framework | `auth/token_exchange.py` |
| [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523) | JWT Profile for OAuth 2.0 Client Authentication (`private_key_jwt`) | `auth/jwt_client_auth.py` |
| [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636) | Proof Key for Code Exchange (PKCE) | `auth/pkce.py` |
| [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705) | Mutual-TLS Client Authentication and Certificate-Bound Access Tokens | `auth/mtls_binding.py` |
| [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707) | Resource Indicators for OAuth 2.0 | `auth/mcp_token_verifier.py` (vinculação de audience) |
| [RFC 9101](https://www.rfc-editor.org/rfc/rfc9101) | JWT-Secured Authorization Request (JAR) | `auth/par.py` |
| [RFC 9126](https://www.rfc-editor.org/rfc/rfc9126) | OAuth 2.0 Pushed Authorization Requests (PAR) | `auth/par.py` |
| [RFC 9728](https://www.rfc-editor.org/rfc/rfc9728) | OAuth 2.0 Protected Resource Metadata | exposto automaticamente pelo SDK do MCP assim que `resource_server_url` é configurado |

## Model Context Protocol

- **[Especificação do MCP](https://modelcontextprotocol.io)** - o
  protocolo que este servidor implementa para expor tools ao Claude e a
  outros clientes MCP, incluindo sua especificação de autorização (o
  padrão de "separação AS/RS", e a proibição explícita de passthrough de
  token sobre a qual a arquitetura deste projeto é construída).
- **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)**
  (pacote `mcp`) - `FastMCP`, `mcp.server.auth.*`, protocolo
  `TokenVerifier`.

## Outras bibliotecas responsáveis pela criptografia

- **[jwcrypto](https://jwcrypto.readthedocs.io/)** - assinatura e
  verificação JWS/JWE/JWT.
- **[cryptography](https://cryptography.io/)** - parsing de certificados
  X.509 (thumbprint mTLS), manipulação de chaves RSA.
- **[DSPy](https://dspy.ai/)** - categorização de transações, tratada
  como um módulo de classificação via LLM.
