[English](SECURITY.md) · **Português**

# Política de Segurança

## Escopo e aviso

O `openfinance-br-mcp` é um projeto independente, mantido pela comunidade.
Ele **não** é afiliado, endossado ou oficialmente certificado pelo Banco
Central do Brasil (BCB) ou pelo programa Open Finance Brasil. Ele **não**
passou por uma certificação de conformidade FAPI independente nem por uma
auditoria de segurança de terceiros. Revise o código você mesmo e avalie
contra sua própria tolerância a risco antes de apontá-lo para credenciais
reais ou dados bancários reais.

O padrão `ENVIRONMENT=mock` roda inteiramente em memória, sem credenciais
reais, sem chamadas de rede e sem certificados mTLS - essa é a forma
segura de explorar o projeto. Os ambientes `sandbox`/`production` exigem
`CLIENT_ID`/`CLIENT_SECRET`/material mTLS reais, emitidos por uma
instituição participante; trate esses dados exatamente como trataria
qualquer outra credencial bancária de produção.

## Versões suportadas

Este projeto está em fase pré-1.0 (atualmente `0.1.x`). Não há branch LTS
- correções de segurança são aplicadas apenas na `master` e no último
release publicado.

## Reportando uma vulnerabilidade

Por favor, **não** abra uma issue pública no GitHub para uma suspeita de
vulnerabilidade de segurança.

Use o recurso de relato privado de vulnerabilidades do GitHub: acesse a
[aba Security](https://github.com/brunovicco/openfinance-br-mcp/security)
deste repositório e clique em **"Report a vulnerability"**. Isso abre um
rascunho de advisory privado, visível apenas ao mantenedor, para que o
problema não seja divulgado publicamente antes de existir uma correção.

Por favor inclua:

- Uma descrição da vulnerabilidade e seu impacto potencial.
- Passos para reproduzir (uma reprodução mínima é ideal).
- Se afeta o ambiente `mock`, os caminhos de código de
  `sandbox`/`production`, ou ambos.

Nosso objetivo é confirmar o recebimento em poucos dias. Divulgação
coordenada é apreciada - por favor dê tempo para uma correção antes de
qualquer publicação pública sobre o problema.

## Notas de design relevantes para segurança

Se você está auditando este código, os dois limites de segurança mais
importantes são:

- **Separação dos universos de token** - tokens de cliente MCP (quem
  chama este servidor) e tokens bancários FAPI-BR (este servidor chamando
  um banco) são mantidos estruturalmente separados e nunca podem se
  cruzar. Veja [docs/pt/authorization.md](docs/pt/authorization.md).
- **Vinculação a certificado mTLS (RFC 8705)** - opcional, para tokens de
  cliente MCP, aplicada contra um certificado de cliente encaminhado por
  um proxy. O limite de confiança (o reverse proxy precisa remover ou
  sobrescrever o header de certificado de cliente encaminhado) está
  documentado no mesmo arquivo - configurar esse proxy incorretamente
  anula completamente a vinculação.
