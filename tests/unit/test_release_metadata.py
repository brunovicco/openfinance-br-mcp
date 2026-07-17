"""Release metadata consistency checks."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from openfinance_br_mcp import __version__
from openfinance_br_mcp.config import Settings

_ROOT = Path(__file__).parents[2]


def _server_metadata() -> dict[str, Any]:
    return json.loads((_ROOT / "server.json").read_text(encoding="utf-8"))


def test_release_versions_are_consistent() -> None:
    pyproject = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    server = _server_metadata()

    assert pyproject["project"]["version"] == __version__
    assert Settings.model_fields["server_version"].default == __version__
    assert server["version"] == __version__
    assert server["packages"][0]["version"] == __version__
    assert f"## [{__version__}]" in (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


def test_release_runtime_and_registry_metadata_are_valid() -> None:
    pyproject = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    server = _server_metadata()

    assert pyproject["project"]["requires-python"] == ">=3.12,<3.14"
    assert len(server["description"]) <= 100
    assert server["packages"][0]["identifier"] == "openfinance-br-mcp"


def test_published_installation_commands_use_current_version() -> None:
    expected = f"openfinance-br-mcp=={__version__}"

    for name in (
        "README.md",
        "README.pt-BR.md",
        "RELEASING.md",
        "examples/claude_desktop_config.json",
    ):
        assert expected in (_ROOT / name).read_text(encoding="utf-8")

    deployment = (_ROOT / "k8s" / "deployment.yaml").read_text(encoding="utf-8")
    assert f"openfinance-br-mcp:{__version__}" in deployment
