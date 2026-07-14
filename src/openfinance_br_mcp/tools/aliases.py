"""Shared type aliases for MCP tool signatures.

Centralizing ``BankId`` here means FastMCP auto-generates the same
enum constraint in every tool's JSON Schema from a single source of
truth. Adding a new bank still requires registering its adapter in
``context.py`` (see README "Adding a new bank") - this alias must be
updated in the same change.
"""

from typing import Literal

BankId = Literal[
    "nubank",
    "sicoob",
    "caixa",
    "banco_do_brasil",
    "bradesco",
    "itau",
    "santander",
    "xp",
    "picpay",
    "btg",
]
