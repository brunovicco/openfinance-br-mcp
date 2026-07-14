[English](CONTRIBUTING.md) · **Português**

# Contribuindo

Obrigado por considerar contribuir com o `openfinance-br-mcp`. É um projeto
pequeno e guiado por especificações - a maioria das contribuições se
encaixa em uma destas categorias: um novo adapter de banco, uma correção
de bug, uma melhoria de documentação, ou uma nova tool MCP.

## Preparando o ambiente

```bash
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp
uv sync
cp .env.example .env   # padrão é ENVIRONMENT=mock - nenhuma credencial real é necessária
```

O ambiente `mock` (o padrão) roda inteiramente em memória via
`MockOpenFinanceAdapter` - sem chamadas de rede, sem credenciais do BCB,
sem certificados mTLS. Esse é o ciclo de desenvolvimento principal do
dia a dia, já que o sandbox oficial do Open Finance Brasil não é
self-service. Veja [VALIDATION.pt-BR.md](VALIDATION.pt-BR.md) para
entender o que rodar em `mock` prova e o que não prova.

Rodando o servidor localmente:

```bash
uv run openfinance-mcp                          # transporte stdio
uv run openfinance-mcp --transport streamable-http
```

## Antes de abrir um PR

O CI roda exatamente estas quatro checagens
(`.github/workflows/ci.yml`) - rode localmente antes:

```bash
uv run black --check .
uv run ruff check .
uv run mypy src/
uv run pytest tests/
```

A suíte de testes exige um piso de 80% de cobertura
(`--cov-fail-under=80`, definido em `pyproject.toml`). Código novo deve
vir acompanhado de testes - veja os testes existentes em `tests/unit/` e
`tests/integration/` para entender as convenções de teste do projeto
(round-trips reais de criptografia contra chamadas HTTP mockadas via
`respx`, nunca verificação de assinatura mockada; `MockOpenFinanceAdapter`
para testes no nível de adapter).

## Adicionando um novo adapter de banco

1. Crie `src/openfinance_br_mcp/adapters/meu_banco.py`.
2. Herde de `DefaultOpenFinanceAdapter` (ou implemente o protocolo
   `BankAdapter` diretamente, se a API do banco fugir do formato padrão
   do Open Finance Brasil).
3. Sobrescreva `bank_id`, e passe o `base_url`/`token_endpoint` do banco.
4. Registre o ISPB do banco em `_ISPB_BY_BANK`, em `directory/client.py`,
   e registre a classe do adapter em `context.py`.
5. Adicione o banco na tabela "Supported banks" do `README.md` e do
   `README.pt-BR.md`.

## Estilo de código

- Sem comentários explicando *o que* o código faz - os nomes devem deixar
  isso óbvio. Comentários são para o *porquê*, quando genuinamente não é
  óbvio (uma citação de especificação, um workaround, um invariante).
- Siga as convenções de docstring já existentes (estilo Google, usado em
  todo o `src/`).
- Não adicione abstrações, flags de configuração ou tratamento de erro
  para cenários que não podem ocorrer - veja os módulos existentes do
  projeto para calibrar o nível de diretividade esperado.
- Os dois universos de token (autenticação do cliente MCP vs. autenticação
  bancária FAPI-BR) nunca podem se cruzar - veja
  [docs/pt/authorization.md](docs/pt/authorization.md) antes de mexer em
  qualquer coisa em `auth/`.

## Reportando bugs / sugerindo funcionalidades

Abra uma issue no GitHub. Para qualquer coisa que possa ser uma
vulnerabilidade de segurança, veja [SECURITY.md](SECURITY.md) em vez
disso - por favor não abra uma issue pública para esses casos.

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob
a [Licença MIT](LICENSE) do projeto.
