# Releasing

Releases are created from signed or annotated SemVer tags. The release
workflow validates the source, builds and smoke-tests the distributions,
publishes to PyPI and the MCP Registry, and then creates a GitHub release with
the exact artifacts that were uploaded.

## One-time repository setup

1. In the PyPI project settings for `openfinance-br-mcp`, add a GitHub Trusted
   Publisher with:
   - owner: `brunovicco`
   - repository: `openfinance-br-mcp`
   - workflow: `release.yml`
   - environment: `pypi`
2. In the GitHub repository, create the `pypi` environment. Add required
   reviewers if releases should require manual approval.
3. Keep GitHub Actions OIDC enabled. The MCP Registry publisher also uses
   GitHub OIDC and does not require a long-lived registry token.

The workflow intentionally contains no PyPI password or MCP Registry token.

## Prepare a release

1. Choose a version that has not been published before. PyPI and the MCP
   Registry treat published versions as immutable.
2. Update these version sources together:
   - `pyproject.toml`
   - `src/openfinance_br_mcp/__init__.py`
   - `server.json` (root and package versions)
   - `k8s/deployment.yaml`
   - published-package commands in `README.md` and `README.pt-BR.md`
3. Move the release notes from `Unreleased` to a dated section in
   `CHANGELOG.md`, and update the comparison links.
4. Run the local release gate:

   ```bash
   uv lock --check
   uv run black --check .
   uv run ruff check .
   uv run mypy src/
   uv run pytest tests/
   uv build
   uv run twine check dist/*
   ```

5. Review the built wheel and sdist under `dist/`. Do not publish artifacts
   built from a different commit.

## Publish

After the release commit is on `main`, create and push the matching tag. For
version `0.2.0`:

```bash
git tag -s v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0
```

If signing is not configured, use an annotated tag (`git tag -a`) instead.
The workflow rejects a tag whose name differs from the Python package version.

## Verify

Confirm that all release jobs succeeded, then verify:

- the version is visible on PyPI;
- the GitHub release contains both the wheel and sdist;
- the MCP Registry lists the same version and package identifier;
- `uvx --from openfinance-br-mcp==0.2.0 openfinance-mcp` starts in mock mode.

If a post-publication defect is found, publish a new patch version. Never try
to replace an existing PyPI or MCP Registry version.
