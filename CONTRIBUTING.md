# Contributing

Thanks for considering a contribution to `openfinance-br-mcp`. This is a
small, spec-driven project - most contributions fall into one of: a new
bank adapter, a bugfix, a documentation improvement, or a new MCP tool.

## Getting set up

```bash
git clone https://github.com/brunovicco/openfinance-br-mcp.git
cd openfinance-br-mcp
uv sync
cp .env.example .env   # defaults to ENVIRONMENT=mock - no real credentials needed
```

The `mock` environment (the default) runs entirely in-memory via
`MockOpenFinanceAdapter` - no network calls, no BCB credentials, no mTLS
certificates. This is the primary day-to-day dev loop, since the official
Open Finance Brasil sandbox is not self-service. See
[VALIDATION.md](VALIDATION.md) for what running in `mock` does and doesn't
prove.

Run the server locally:

```bash
uv run openfinance-mcp                          # stdio transport
uv run openfinance-mcp --transport streamable-http
```

## Before opening a PR

CI runs exactly these four checks (`.github/workflows/ci.yml`) - run them
locally first:

```bash
uv run black --check .
uv run ruff check .
uv run mypy src/
uv run pytest tests/
```

The test suite enforces an 80% coverage floor (`--cov-fail-under=80`, set
in `pyproject.toml`). New code should come with tests - see existing tests
under `tests/unit/` and `tests/integration/` for the project's testing
conventions (real crypto round-trips against `respx`-mocked HTTP, not
mocked signature verification; `MockOpenFinanceAdapter` for adapter-level
tests).

## Adding a new bank adapter

1. Create `src/openfinance_br_mcp/adapters/my_bank.py`.
2. Inherit from `DefaultOpenFinanceAdapter` (or implement the `BankAdapter`
   protocol directly if the bank's API deviates from the standard
   Open Finance Brasil shape).
3. Override `bank_id`, and pass the bank's `base_url`/`token_endpoint`.
4. Register the bank's ISPB in `directory/client.py`'s `_ISPB_BY_BANK`,
   and register the adapter class in `context.py`.
5. Add it to the "Supported banks" table in `README.md` and
   `README.pt-BR.md`.

## Code style

- No comments explaining *what* code does - names should make that
  obvious. Comments are for *why*, when it's genuinely non-obvious (a
  spec citation, a workaround, an invariant).
- Follow existing docstring conventions (Google-style, as used throughout
  `src/`).
- Don't add abstractions, config flags, or error handling for scenarios
  that can't occur - see the project's existing modules for the level of
  directness expected.
- Two token universes (MCP client auth vs. FAPI-BR bank auth) must never
  cross - see [docs/en/authorization.md](docs/en/authorization.md) before
  touching anything in `auth/`.

## Reporting bugs / requesting features

Open a GitHub issue. For anything that might be a security
vulnerability, see [SECURITY.md](SECURITY.md) instead - please don't
open a public issue for those.

## License

By contributing, you agree your contributions will be licensed under the
project's [MIT License](LICENSE).
