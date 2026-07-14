[English](VALIDATION.md) · **Português**

# Validação

Como as afirmações de corretude deste projeto são de fato sustentadas e -
tão importante quanto - o que **não** foi validado.

## Por que este documento existe

O sandbox oficial do Open Finance Brasil não é self-service: obter
credenciais para rodar contra ele exige um processo de cadastro pelo qual
o mantenedor deste projeto não passou. Esse único fato molda quase toda
decisão de validação abaixo - não existe aqui um caminho para "rodamos
contra o sandbox real e funcionou".

## O que foi validado

- **Suíte de testes unitários e de integração.** 342 testes, ~97% de
  cobertura de linhas em `src/`, com um piso de 80% imposto pelo CI
  (`pytest --cov-fail-under=80`). Cobertura é um piso, não uma meta - a
  suíte é escrita para exercitar modos de falha reais (audience errada,
  token expirado, thumbprint mTLS incompatível, assinatura forjada), não
  apenas para tocar linhas.
- **Round-trips criptográficos reais.** Os testes que tocam verificação
  JWT/JWS (`test_mcp_token_verifier.py`, `test_jwt_client_auth.py`, etc.)
  assinam tokens reais com chaves reais (via `jwcrypto`) e os verificam
  através do caminho de código de verificação de produção real - a
  criptografia em si nunca é mockada, apenas as chamadas HTTP ao redor
  dela (via `respx`).
- **Adapter de ambiente mock.** O `MockOpenFinanceAdapter` implementa o
  mesmo protocolo `BankAdapter` que qualquer adapter real implementa, de
  forma determinística, em memória. `tests/integration/` exercita
  round-trips completos de chamadas de tool contra ele, então o contrato
  entre tool MCP e adapter é validado mesmo sem acesso à rede.
- **Análise estática.** `mypy --strict` em todo o `src/`, `ruff`
  (incluindo as regras de lint de segurança `S` do flake8-bandit),
  formatação via `black`. Os três são gates obrigatórios do CI, não
  apenas recomendações.
- **Conformidade com a especificação por leitura direta**, não por uma
  suíte de testes oficial: o comportamento de PAR/JAR, `private_key_jwt`,
  PKCE, vinculação de certificado mTLS e a vinculação de audience do
  resource-server do MCP foi implementado e revisado contra o próprio
  texto das RFCs (veja [SOURCES.pt-BR.md](SOURCES.pt-BR.md)), já que
  nenhuma suíte de conformidade FAPI-BR independente estava disponível
  para rodar.

## O que NÃO foi validado

- **Nenhuma execução contra o sandbox real do BCB ou produção.** Todo
  formato de request/response para os ambientes `sandbox`/`production` é
  modelado a partir da especificação pública do Open Finance Brasil, não
  confirmado contra o comportamento real de uma instituição ao vivo.
  Peculiaridades de endpoint, exigências de campo não documentadas, ou
  desvios de especificação por um banco específico só apareceriam quando
  alguém rodar isso contra um cliente registrado real.
- **Nenhuma auditoria de segurança independente.** Veja
  [SECURITY.md](SECURITY.md) para o processo de reporte caso você
  encontre algo durante sua própria revisão.
- **Nenhuma certificação oficial de conformidade FAPI 1.0 Advanced /
  FAPI-BR.** Este projeto não é uma implementação FAPI certificada - ele
  busca seguir os requisitos do perfil, mas "busca seguir" não é o mesmo
  que "certificado para".
- **A vinculação de certificado mTLS (RFC 8705) assume um contrato
  específico do proxy** (o proxy remove/sobrescreve o header de
  certificado de cliente encaminhado antes que esta aplicação o veja) que
  está documentado mas não é, em si, aplicado ou testado contra a
  configuração real de nenhum proxy específico - veja
  `docs/pt/authorization.md`.

## Se você está avaliando isso para uso real

Comece em `mock`, leia `docs/pt/authorization.md` do início ao fim, e
trate qualquer coisa além desse ponto (`CLIENT_ID`/`CLIENT_SECRET` reais,
certificados mTLS reais, o endpoint de produção real de um banco) como
algo pelo qual você é responsável por validar antes de confiar nisso com
dados financeiros reais.
